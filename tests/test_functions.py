
import unittest
import sys
sys.path.append('..')
from functions import *


class TestAnything(unittest.TestCase):

    def test_is_valid_security_term(self):
        s = ""
        self.assertFalse(is_valid_security_term(s), "Should be False")
        s = None
        self.assertFalse(is_valid_security_term(s), "Should be False")
        s = " "
        self.assertFalse(is_valid_security_term(s), "Should be False")
        tokens  = ['3-Year', '13-Week', '26-Week', '4-Week', '8-Week', '17-Week', '7-Year', 
        '2-Year', '5-Year', '52-Week', '10-Year', '44-Day',  '35-Day', 
         '16-Day', '20-Year', '30-Year', '119-Day', '21-Day']
        for t in tokens:
            self.assertTrue(is_valid_security_term(t), f"Should be True for {t}")
        

    def test_term_to_days(self):
        x = [ ["3-Year", 1095], ["1-Year", 365], ["1-weeks", 7]]
        for a in x:
            self.assertEqual(single_term_to_days(a[0]),a[1], f"Should be {a[1]}")

    def test_multi_term_to_days(self):
        """
        '9-Year 11-Month', '1-Year 11-Month',
         '9-Year 8-Month','19-Year 10-Month'
        """
        multi = [ ['29-Year 6-Month', 10765],['29-Year 10-Month', 10885], 
        ['9-Year 10-Month', 3585],['1-Year 10-Month',665], 
        ['4-Year 10-Month',1760], ['19-Year 11-Month',7265], ['29-Year 11-Month',10915],
        ['9-Year 11-Month',3615], ['1-Year 11-Month', 695], ['9-Year 8-Month',3525], ['19-Year 10-Month',7235] ]
        for a in multi:
            r = multi_term_to_days(a[0])
            self.assertEqual(r,a[1], f"Applied to {a[0]} should be {a[1]} but got {r}")

if __name__ == '__main__':
    unittest.main()
