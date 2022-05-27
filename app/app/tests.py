"""
Sample tests
"""
from django.test import SimpleTestCase

from app import calc


class CalcTests(SimpleTestCase):
    """test the calc modul"""
    def test_add_numbers(self):
        """test adding numbers together"""
        res = calc.add(5, 6)

        self.assertEqual(res, 11)

    def test_subtract_numbers(self):
        """test subtracting numbers"""
        res = calc.sub(2, 4)

        self.assertEqual(res, -2)
