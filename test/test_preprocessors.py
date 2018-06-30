import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import big_phoney.preprocessors as preprocessors


class TestPreprocessors(unittest.TestCase):

    def test_currency_symbol_prefixes(self):
        symbol_order_fixer = preprocessors.ExpandCurrencySymbols()
        self.assertEqual(symbol_order_fixer.process('$20'), '20 $')
        self.assertEqual(symbol_order_fixer.process('$20.01'), '20 $ and 1 ¢')
        self.assertEqual(symbol_order_fixer.process('£99.99'), '99 £ and 99 pence')
        self.assertEqual(symbol_order_fixer.process('₹99.01'), '99 ₹ and 1 paisa')
        self.assertEqual(symbol_order_fixer.process('€100.00'), '100 €')
        self.assertEqual(symbol_order_fixer.process('¢.99'), '.99 ¢')
        self.assertEqual(symbol_order_fixer.process('.99¢'), '.99¢')
        self.assertEqual(symbol_order_fixer.process('$.99'), '99 ¢')
        self.assertEqual(symbol_order_fixer.process('the $ sign'), 'the $ sign')

    def test_space_padding(self):
        space_padder = preprocessors.SpacePadSymbols()
        self.assertEqual(space_padder.process('©2018'), '© 2018')
        self.assertEqual(space_padder.process('(mr. fox)'), '( mr. fox )')

    def test_abbreviations(self):
        abbrev_preproc = preprocessors.ReplaceAbbreviations()
        self.assertEqual(abbrev_preproc.process('© 2018'), 'copyright 2018')
        self.assertEqual(abbrev_preproc.process('( Mr. Fox )'), '( mister fox )')
        self.assertEqual(abbrev_preproc.process('1 $'), '1 dollar')
        self.assertEqual(abbrev_preproc.process('2 $'), '2 dollars')
        self.assertEqual(abbrev_preproc.process('7 kb'), '7 kilobytes')
        self.assertEqual(abbrev_preproc.process(' ½ + ⅓ = ⅚ '), 'one-half plus one-third equals five-sixths')

    def test_times(self):
        time_preproc = preprocessors.ReplaceTimes()
        self.assertEqual(time_preproc.process('4:00'), "4 o'clock")
        self.assertEqual(time_preproc.process('4:00pm'), "4 o'clock P M")
        self.assertEqual(time_preproc.process('4:00 PM'), "4 o'clock P M")
        self.assertEqual(time_preproc.process('12:25'), "12 25")
        self.assertEqual(time_preproc.process('12:05'), "12 oh 5")

    def test_numbers(self):
        number_preproc = preprocessors.ReplaceNumbers()
        self.assertEqual(number_preproc.process('sk8r'), 'skeightr')
        self.assertEqual(number_preproc.process('80'), 'eighty')
        self.assertEqual(number_preproc.process('8 0'), 'eight zero')
        self.assertEqual(number_preproc.process('one 1,024.25'), 'one one thousand and twenty-four point two five')

    def test_emails_and_urls(self):
        web_preproc = preprocessors.FormatEmailAndURLs()
        self.assertEqual(web_preproc.process('ryan_epp@yahoo.com'), 'ryan_epp@yahoo dot com')
        self.assertEqual(web_preproc.process('https://www.google.com'), 'h t t p s colon / / w w w dot google dot com')
        self.assertEqual(web_preproc.process('www.google.com'), 'w w w dot google dot com')

if __name__ == '__main__':
    unittest.main()
