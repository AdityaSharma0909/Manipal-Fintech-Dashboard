import unittest

from onboarding_v2.saas import _split_name, _split_name_with_title


class NameSplitTests(unittest.TestCase):
    def test_split_two_parts(self):
        first, middle, last = _split_name("Rahul Gupta")
        self.assertEqual(first, "Rahul")
        self.assertEqual(middle, "")
        self.assertEqual(last, "Gupta")

    def test_split_three_parts(self):
        first, middle, last = _split_name("Aishwary Kumar Sinha")
        self.assertEqual(first, "Aishwary")
        self.assertEqual(middle, "Kumar")
        self.assertEqual(last, "Sinha")

    def test_split_title_is_ignored(self):
        first, middle, last = _split_name("Mr. HARNAM SINGH JAMWAL")
        self.assertEqual(first, "HARNAM")
        self.assertEqual(middle, "SINGH")
        self.assertEqual(last, "JAMWAL")

    def test_split_title_only_returns_empty(self):
        first, middle, last = _split_name("Mr.")
        self.assertEqual(first, "")
        self.assertEqual(middle, "")
        self.assertEqual(last, "")

    def test_split_collapses_whitespace(self):
        first, middle, last = _split_name("  Mir   Mannan  ")
        self.assertEqual(first, "Mir")
        self.assertEqual(middle, "")
        self.assertEqual(last, "Mannan")

    def test_split_name_with_title(self):
        title, first, middle, last = _split_name_with_title("Mr. HARNAM SINGH JAMWAL")
        self.assertEqual(title, "Mr")
        self.assertEqual(first, "HARNAM")
        self.assertEqual(middle, "SINGH")
        self.assertEqual(last, "JAMWAL")

    def test_split_name_with_title_only(self):
        title, first, middle, last = _split_name_with_title("Mrs.")
        self.assertEqual(title, "Mrs")
        self.assertEqual(first, "")
        self.assertEqual(middle, "")
        self.assertEqual(last, "")
