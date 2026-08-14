from django.test import TestCase
from onboarding_v2.CreditScoreRange import CreditScoreRange
from onboarding_v2.signzy_experian import get_credit_score_details


class CreditScoreRangeTests(TestCase):
    def setUp(self):
        CreditScoreRange.objects.bulk_create([
            CreditScoreRange(id=1, min_score=0, max_score=300, score_color="#FF0000", score_band="Bad"),
            CreditScoreRange(id=2, min_score=301, max_score=500, score_color="#FF8000", score_band="Poor"),
            CreditScoreRange(id=3, min_score=501, max_score=650, score_color="#FFD700", score_band="Average"),
            CreditScoreRange(id=4, min_score=651, max_score=750, score_color="#9ACD32", score_band="Good"),
            CreditScoreRange(id=5, min_score=751, max_score=900, score_color="#008000", score_band="Excellent"),
        ])

    def test_credit_score_range(self):
        self.assertEqual(
            get_credit_score_details("720"),
            ("651-750", "#9ACD32", "Good"),
        )

    def test_credit_score_range_fallback(self):
        self.assertEqual(
            get_credit_score_details("999"),
            ("No Range", "#000000", "Unknown"),
        )
