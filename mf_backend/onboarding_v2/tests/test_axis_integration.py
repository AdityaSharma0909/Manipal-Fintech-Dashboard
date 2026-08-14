import json
import os
import tempfile
from unittest.mock import Mock, patch

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from django.test import TestCase, override_settings
from rest_framework.test import APIClient, APITestCase

from onboarding_v2.models import BankBranch, LeadV2, PincodeMaster
from onboarding_v2.integrations.axis.client import AxisClient
from onboarding_v2.integrations.axis.crypto import encrypt_and_sign, load_jose_keys
from onboarding_v2.integrations.axis.exceptions import AxisRequestError
from onboarding_v2.integrations.axis.mapping import build_axis_create_lead_data
from onboarding_v2.integrations.axis.settings import AxisEnvConfig
from onboarding_v2.serializers import LeadCreateSerializer
from users.models import User


def _write_pem(data: bytes) -> str:
    f = tempfile.NamedTemporaryFile(delete=False)
    f.write(data)
    f.flush()
    f.close()
    return f.name


@override_settings(
    MIGRATION_MODULES={"onboarding_v2": None, "users": None, "lead": None, "lender": None},
    AUTHENTICATION_BACKENDS=("django.contrib.auth.backends.ModelBackend",),
    MIDDLEWARE=[],
    REST_FRAMEWORK={
        "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
        "DEFAULT_AUTHENTICATION_CLASSES": [],
    },
)
class AxisIntegrationUnitTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        public_key = private_key.public_key()

        priv_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        pub_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        cls._priv_path = _write_pem(priv_pem)
        cls._pub_path = _write_pem(pub_pem)

    @classmethod
    def tearDownClass(cls):
        for p in (getattr(cls, "_priv_path", None), getattr(cls, "_pub_path", None)):
            if p:
                try:
                    os.unlink(p)
                except OSError:
                    pass
        super().tearDownClass()

    def _config(self) -> AxisEnvConfig:
        # For unit tests, use the same keypair for both sides.
        return AxisEnvConfig(
            env="UAT",
            base_url="https://example.invalid/api/v2/CRMNext",
            ibm_client_id="id",
            ibm_client_secret="secret",
            channel_id="ESB",
            service_id="AE.ESB.CRMNXT.SSTP.001",
            service_version="1.0",
            username="alwebuser",
            password="pass",
            mtls_cert_file=None,
            mtls_key_file=None,
            verify_ssl=True,
            axis_encrypt_public_key_pem_file=self._pub_path,
            partner_sign_private_key_pem_file=self._priv_path,
            partner_decrypt_private_key_pem_file=self._priv_path,
            axis_verify_public_key_pem_file=self._pub_path,
            timeout_seconds=5,
        )

    def test_crypto_roundtrip_encrypt_sign_then_verify_decrypt(self):
        keys = load_jose_keys(
            axis_encrypt_public_key_pem_file=self._pub_path,
            partner_sign_private_key_pem_file=self._priv_path,
            partner_decrypt_private_key_pem_file=self._priv_path,
            axis_verify_public_key_pem_file=self._pub_path,
        )
        payload = {"Data": {"hello": "world"}, "Risks": {}}
        token = encrypt_and_sign(keys=keys, payload_json=json.dumps(payload))

        from onboarding_v2.integrations.axis.crypto import verify_and_decrypt

        decrypted = verify_and_decrypt(keys=keys, token=token)
        self.assertEqual(json.loads(decrypted), payload)

    def test_mapping_builds_required_axis_fields(self):
        BankBranch.objects.create(
            bank_name="Axis Bank",
            branch_name="MG Road",
            sol_id="SOL123",
        )
        lead = LeadV2.objects.create(
            contact_number="9999999999",
            customer_name="Alice B Doe",
            email_address="alice@example.com",
            pincode="560001",
            product_category="LOAN",
            bank="Axis Bank",
            bank_branch="MG Road",
            metadata={
                "city": "Bangalore",
                "state": "Karnataka",
                "dob": "1991-01-01",
                "pan_number": "ABCDE1234F",
                "address1": "Line1",
                "address2": "Line2",
                "address3": "Line3",
            },
        )

        mapped = build_axis_create_lead_data(lead=lead, config=self._config()).axis_data
        self.assertEqual(mapped["firstName"], "Alice")
        self.assertEqual(mapped["middleName"], "B")
        self.assertEqual(mapped["lastName"], "Doe")
        self.assertEqual(mapped["mobilePhone"], "9999999999")
        self.assertEqual(mapped["pinCode"], "560001")
        self.assertEqual(mapped["panNumber"], "ABCDE1234F")
        self.assertEqual(mapped["branch"], "SOL123")

    def test_mapping_resolves_sol_id_from_pincode_lookup_selection(self):
        PincodeMaster.objects.create(pincode="313001", district="Udaipur")
        BankBranch.objects.create(
            bank_name="Another Bank",
            branch_name="Udaipur",
            district="Udaipur",
            sol_id="WRONG-BANK-SOL",
        )
        BankBranch.objects.create(
            bank_name="Axis Bank",
            branch_name="Udaipur",
            district="Another District",
            sol_id="WRONG-DISTRICT-SOL",
        )
        BankBranch.objects.create(
            bank_name="Axis Bank",
            branch_name="Udaipur",
            district="Udaipur",
            sol_id="AXIS-UDAIPUR-SOL",
        )
        lead = LeadV2.objects.create(
            contact_number="7889102102",
            customer_name="Test User",
            pincode="313001",
            product_category="LOAN",
            bank="Axis Bank",
            bank_branch="Udaipur",
        )

        mapped = build_axis_create_lead_data(lead=lead, config=self._config()).axis_data

        self.assertEqual(mapped["branch"], "AXIS-UDAIPUR-SOL")

    def test_explicit_lead_sol_id_takes_precedence_for_axis_branch(self):
        serializer = LeadCreateSerializer(data={
            "contact_number": "7889102102",
            "customer_name": "Test User",
            "product_category": "LOAN",
            "product_subcategory": "GOLD_LOAN",
            "lead_type": "BANK_LEAD",
            "pincode": "313001",
            "bank": "Axis Bank",
            "bank_branch": "Udaipur",
            "sol_id": "1234",
        })
        self.assertTrue(serializer.is_valid(), serializer.errors)

        lead = LeadV2(**serializer.validated_data)
        mapped = build_axis_create_lead_data(lead=lead, config=self._config()).axis_data

        self.assertEqual(lead.metadata["sol_id"], "1234")
        self.assertEqual(mapped["branch"], "1234")

    def test_client_posts_encrypted_and_parses_decrypted_json(self):
        cfg = self._config()
        client = AxisClient(cfg)

        keys = load_jose_keys(
            axis_encrypt_public_key_pem_file=self._pub_path,
            partner_sign_private_key_pem_file=self._priv_path,
            partner_decrypt_private_key_pem_file=self._priv_path,
            axis_verify_public_key_pem_file=self._pub_path,
        )

        def fake_post(url, headers=None, data=None, timeout=None, cert=None, verify=None):
            # Validate that body is a compact JWS with 3 dots
            self.assertIsInstance(data, str)
            self.assertGreaterEqual(data.count("."), 2)

            # Return an encrypted+signed response with expected JSON shape.
            if url.endswith("/login"):
                resp_obj = {"Data": {"token": "TKN", "expiresOn": "2099-01-01T00:00:00+00:00"}, "Risk": {}, "Meta": {}}
            else:
                resp_obj = {"Data": {"isSuccess": "true", "leadId": "123"}, "Risk": {}, "Meta": {}}
            token = encrypt_and_sign(keys=keys, payload_json=json.dumps(resp_obj))
            resp = Mock()
            resp.status_code = 200
            resp.text = token
            return resp

        client._session.post = fake_post  # type: ignore[attr-defined]

        out = client.create_lead(lead_data={"firstName": "A", "middleName": ".", "lastName": "B"})
        self.assertEqual(out["Data"]["isSuccess"], "true")

    def test_client_preserves_decrypted_axis_error_message(self):
        cfg = self._config()
        client = AxisClient(cfg)

        keys = load_jose_keys(
            axis_encrypt_public_key_pem_file=self._pub_path,
            partner_sign_private_key_pem_file=self._priv_path,
            partner_decrypt_private_key_pem_file=self._priv_path,
            axis_verify_public_key_pem_file=self._pub_path,
        )

        duplicate_message = (
            "Lead id 680805623 with the same Mobile number 7003458375 "
            "already exists for Gold Loan product."
        )

        def fake_post(url, headers=None, data=None, timeout=None, cert=None, verify=None):
            if url.endswith("/login"):
                resp_obj = {"Data": {"token": "TKN", "expiresOn": "2099-01-01T00:00:00+00:00"}, "Risk": {}, "Meta": {}}
                status_code = 200
            else:
                resp_obj = {"Data": {"errorCode": "400", "message": duplicate_message}, "Risk": {}, "Meta": {}}
                status_code = 400
            token = encrypt_and_sign(keys=keys, payload_json=json.dumps(resp_obj))
            resp = Mock()
            resp.status_code = status_code
            resp.text = token
            return resp

        client._session.post = fake_post  # type: ignore[attr-defined]

        with self.assertRaises(AxisRequestError) as ctx:
            client.create_lead(lead_data={"firstName": "A", "middleName": ".", "lastName": "B"})

        self.assertEqual(ctx.exception.status_code, 400)
        self.assertEqual(ctx.exception.partner_message, duplicate_message)
        self.assertEqual(ctx.exception.decrypted_response["Data"]["message"], duplicate_message)


@override_settings(
    MIGRATION_MODULES={"onboarding_v2": None},
    AUTHENTICATION_BACKENDS=("django.contrib.auth.backends.ModelBackend",),
    MIDDLEWARE=[],
    REST_FRAMEWORK={
        "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
        "DEFAULT_AUTHENTICATION_CLASSES": [],
    },
)
class AxisLeadCreateViewTests(APITestCase):
    def setUp(self) -> None:
        super().setUp()
        self.client = APIClient()
        self.user = User.objects.create_user(username="axis-agent-1", password="Pass@123")
        self.client.force_authenticate(user=self.user)

    @patch("onboarding_v2.views.leads.sendToAxis")
    def test_axis_partner_message_returns_bad_request(self, mock_send_to_axis) -> None:
        duplicate_message = (
            "Lead id 680805623 with the same Mobile number 7003458375 "
            "already exists for Gold Loan product."
        )
        mock_send_to_axis.side_effect = AxisRequestError(
            "Axis request failed for /create-lead",
            status_code=400,
            partner_message=duplicate_message,
        )

        payload = {
            "contact_number": "7003458375",
            "customer_name": "Tamoghna sao",
            "product_category": "LOAN",
            "product_subcategory": "GOLD_LOAN",
            "lead_type": "BANK_LEAD",
            "amount": 0,
            "pincode": "400055",
            "source": "SELF",
            "lending_partner": "Axis Bank",
            "bank": "Axis Bank",
            "bank_branch": "Vakola",
            "dob": "1996-05-23",
            "pan_number": "CTEPP4713L",
            "is_pan_verified": False,
        }

        resp = self.client.post("/api/v2/onboarding/leads/", data=payload, format="json")

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(
            resp.json().get("error_msg"),
            "There is already an existing Lead No: 680805623 for mobile no :7003458375.",
        )
        self.assertFalse(LeadV2.objects.filter(contact_number="7003458375").exists())
