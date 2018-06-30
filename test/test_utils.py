import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import big_phoney.utils as utils


class TestUtils(unittest.TestCase):

    def test_is_number(self):
        self.assertEqual(utils.is_number(''), False)
        self.assertEqual(utils.is_number('4:00'), False)
        self.assertEqual(utils.is_number('400'), True)
        self.assertEqual(utils.is_number('4,000'), True)
        self.assertEqual(utils.is_number('4,000.001'), True)
        self.assertEqual(utils.is_number('4,000,000.001'), True)
        self.assertEqual(utils.is_number('4a.001'), False)
        self.assertEqual(utils.is_number('cat'), False)

    def test_contains_digits(self):
        self.assertEqual(utils.contains_digits(''), False)
        self.assertEqual(utils.contains_digits('4:00'), True)
        self.assertEqual(utils.contains_digits('400'), True)
        self.assertEqual(utils.contains_digits('4,000,000.001'), True)
        self.assertEqual(utils.contains_digits('4a.001'), True)
        self.assertEqual(utils.contains_digits('cat'), False)
        self.assertEqual(utils.contains_digits('cat dog fist ... - '), False)
        self.assertEqual(utils.contains_digits('cat7'), True)


    def test_sanitize(self):
        self.assertEqual(utils.sanitize('hello'), 'HELLO')
        self.assertEqual(utils.sanitize('hello...'), 'HELLO...')
        self.assertEqual(utils.sanitize("@Y'ALL"), "Y'ALL")
        self.assertEqual(utils.sanitize("838499twenty-four93**&^^!??$$#()"), "TWENTY-FOUR")
        self.assertEqual(utils.sanitize("HELLO WORLD"), "HELLOWORLD")


if __name__ == '__main__':
    unittest.main()
