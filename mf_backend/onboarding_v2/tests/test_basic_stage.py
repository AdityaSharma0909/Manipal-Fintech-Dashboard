from django.test import SimpleTestCase

from onboarding_v2.constants import Profession, Religion
from onboarding_v2.serializers import BasicStageSerializer


class BasicStageSerializerTests(SimpleTestCase):
    def test_accepts_new_profession_enum_key(self):
        serializer = BasicStageSerializer(data={"profession": Profession.PROFESSIONAL})

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["profession"], Profession.PROFESSIONAL)

    def test_normalizes_new_profession_display_label(self):
        serializer = BasicStageSerializer(data={"profession": "Real estate"})

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["profession"], Profession.REAL_ESTATE)

    def test_existing_profession_display_label_still_works(self):
        serializer = BasicStageSerializer(data={"profession": "Unemployed"})

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["profession"], Profession.UNEMPLOYED)

    def test_normalizes_business_profession_typo(self):
        serializer = BasicStageSerializer(data={"profession": "buisness"})

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["profession"], Profession.BUSINESS)

    def test_normalizes_supported_app_profession_labels(self):
        cases = {
            "Ancillary services(self employed)": Profession.ANCILLARY_SERVICES,
            "buisness": Profession.BUSINESS,
            "fin instn/intermediary": Profession.FIN_INSTN_INTERMEDIARY,
            "manufacturing": Profession.MFG,
            "real estate": Profession.REAL_ESTATE,
            "housewife": Profession.HOME_MAKER,
            "other": Profession.OTHERS,
        }

        for profession, expected in cases.items():
            with self.subTest(profession=profession):
                serializer = BasicStageSerializer(data={"profession": profession})

                self.assertTrue(serializer.is_valid(), serializer.errors)
                self.assertEqual(serializer.validated_data["profession"], expected)

    def test_accepts_parsi_zoroastrian_religion(self):
        for religion in ("PARSI", "Parsi", "Zoroastrian"):
            with self.subTest(religion=religion):
                serializer = BasicStageSerializer(data={"religion": religion})

                self.assertTrue(serializer.is_valid(), serializer.errors)
                self.assertEqual(serializer.validated_data["religion"], Religion.PARSI)
