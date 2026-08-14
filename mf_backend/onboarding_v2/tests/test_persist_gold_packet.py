from django.test import TestCase

from onboarding_v2.helpers.persistence_helpers import persist_gold
from onboarding_v2.models import ApplicationV2, LeadV2, Packet


class PersistGoldPacketTests(TestCase):
    def setUp(self):
        self.lead = LeadV2.objects.create(
            customer_id="CUST-PACKET-1",
            contact_number="9000003333",
            customer_name="Packet Owner",
            product_category="LOAN",
        )
        self.app = ApplicationV2.objects.create(
            application_id="APP-PACKET-1",
            lead=self.lead,
        )

    def test_persist_gold_keeps_single_packet(self):
        first_packet = Packet.objects.create(application=self.app, packet_id="PKT-OLD-1")
        Packet.objects.create(application=self.app, packet_id="PKT-OLD-2")

        payload = {
            "packet_id": "PKT-NEW",
            "barcode_id": "BAR-1",
            "gross_weight": "100.000",
            "gross_value": "1000000.00",
            "net_adjusted_weight": "98.000",
            "net_adjusted_value": "980000.00",
            "appraiser_id": "APR-1",
            "appraiser_name": "Appraiser One",
            "items": [],
        }

        persist_gold(self.app, payload)

        packets = list(Packet.objects.filter(application=self.app))
        self.assertEqual(len(packets), 1)
        self.assertEqual(packets[0].packet_id, "PKT-NEW")
        self.assertEqual(packets[0].barcode_id, "BAR-1")
        self.assertEqual(packets[0].appraiser_id, "APR-1")
        self.assertEqual(packets[0].appraiser_name, "Appraiser One")
