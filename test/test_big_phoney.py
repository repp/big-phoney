import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from big_phoney.big_phoney import BigPhoney


class TestBigPhoney(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestBigPhoney, cls).setUpClass()
        cls.bp = BigPhoney()

    def test_preprocessing(self):
        self.assertEqual(self.bp.apply_preprocessors('$1.00 + $1.99 = $2.99'),
                         'one dollar plus one dollar and ninety-nine cents equals two dollars and ninety-nine cents')
        self.assertEqual(self.bp.apply_preprocessors('My 2 email addresses: ryan_epp@yahoo.com & ryan.epp@gmail.com'),
            'my two email addresses : ryan underscore epp at yahoo dot com and ryan dot epp at gmail dot com')
        self.assertEqual(self.bp.apply_preprocessors('At 2:22 am go to https://www.google.com'),
            'at two twenty-two a m go to h t t p s colon slash slash w w w dot google dot com')
        self.assertEqual(self.bp.apply_preprocessors('£7.89'), 'seven pounds and eighty-nine pence')
        self.assertEqual(self.bp.apply_preprocessors('Mt St. Helens'), 'mount saint helens')
        self.assertEqual(self.bp.apply_preprocessors('no_reply@gmail.com'), 'no underscore reply at gmail dot com')
        self.assertEqual(self.bp.apply_preprocessors('1ft + 2ft = 3ft'), 'one foot plus two feet equals three feet')
        self.assertEqual(self.bp.apply_preprocessors('It\'ll be 7:00am in 1,245.6 seconds'),
                         'it\'ll be seven o\'clock a m in one thousand, two hundred and forty-five point six seconds')

    def test_lookup(self):
        self.assertEqual(self.bp.phonize('cat'), 'K AE1 T')

    def test_predict(self):
        self.assertEqual(self.bp.phonize('lorax'), 'L AO1 R AE0 K S')

    def test_multiple_words(self):
        self.assertEqual(self.bp.phonize('cat lorax'), 'K AE1 T  L AO1 R AE0 K S')

    def test_synoyms(self):
        self.assertEqual(self.bp.count_syllables('cat'), 1)
        self.assertEqual(self.bp.count_syllables('lorax'), 2)


if __name__ == '__main__':
    unittest.main()
