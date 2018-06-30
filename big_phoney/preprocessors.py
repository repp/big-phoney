import re
import time
import inflect
from .utils import load_pickle_dict, is_number, contains_digits
from .shared_constants import ALLOWED_SYMBOLS, ABBREV_DICT_PATH, QTY_ABBREV_DICT_PATH


class ExpandCurrencySymbols:

    def __init__(self):
        # TODO: get a more complete list of currency prefixes
        self.currency_prefix_symbols = {'$', '¢', '£', '¥', '€', '₹'}
        self.currency_subdivisions = {'$': ('¢', '¢'), '£': ('penny', 'pence'), '€':  ('¢', '¢'), '₹': ('paisa', 'paise')}

    def swap_symbol_order(self, word):
        if word[0] in self.currency_prefix_symbols and is_number(word[1:]):
            symbol = word[0]
            value = word[1:]
            if '.' in value and symbol in self.currency_subdivisions.keys():
                val, subdivision_val = value.split('.')
                plural = int(int(subdivision_val) != 1)
                subdivision = self.currency_subdivisions[symbol][plural]
                front = ''
                if len(val) > 0 and int(val) > 0:
                    front = str(int(val)) + ' ' + symbol
                back = ''
                if len(subdivision_val) > 0 and int(subdivision_val) > 0:
                    back = str(int(subdivision_val)) + ' ' + subdivision
                connector = ''
                if len(front) > 0 and len(back) > 0:
                    connector = ' and '
                return front + connector + back
            else:
                return word[1:] + ' ' + word[0]

        return word

    def process(self, input_string):
        processed_words = [self.swap_symbol_order(word) for word in input_string.split()]
        return ' '.join(processed_words)


class FormatEmailAndURLs:

    def __init__(self):
        self.email_regex = re.compile(r'[^@]+@[^@]+\.[^@]+')
        self.url_regex = re.compile(r'((https?://)|(www))(?:[-\w.]|(?:%[\da-fA-F]{2}))+')

    def is_email(self, input_string):
        return self.email_regex.match(input_string)

    def format_email_address(self, input_string):
        return input_string.replace('.', ' dot ')

    def is_url(self, input_string):
        return self.url_regex.match(input_string)

    def format_url(self, input_string):
        proto_and_subdomain = ''
        # split everything up to first dot
        first_dot_idx = input_string.find('.')
        proto_and_subdomain += ' '.join(list(input_string[:first_dot_idx]))
        proto_and_subdomain = proto_and_subdomain.replace(':', 'colon')

        remaining_input = input_string[first_dot_idx:]
        remaining_input = remaining_input.replace('.', ' dot ')

        return proto_and_subdomain + remaining_input

    def process(self, input_string):
        preprocessed_strings = []
        words = input_string.lower().split()
        for word in words:
            if self.is_email(word):
                preprocessed_strings.append(self.format_email_address(word))
                continue

            if self.is_url(word):
                preprocessed_strings.append(self.format_url(word))
                continue

            preprocessed_strings.append(word)
        return ' '.join(preprocessed_strings).strip()


class ReplaceTimes:

    def __init__(self):
        self.time_formats = ['%H:%M', '%I:%M', '%I:%M%p']

    def get_time_obj(self, input_str):
        for time_fmt in self.time_formats:
            try:
                time_obj = time.strptime(input_str.upper(), time_fmt)
                return time_obj, time_fmt
            except ValueError:
                pass
        return None, None

    @staticmethod
    def time_string_from(time_obj, time_fmt):
        hour = time_obj.tm_hour
        if '%I' in time_fmt and hour > 12:
            hour -= 12

        min = time_obj.tm_min
        if min == 0:
            min_str = "o'clock"
        elif min < 10:
            min_str = 'oh ' + str(min)
        else:
            min_str = str(min)

        am_pm = ''
        if '%p' in time_fmt:
            am_pm = time.strftime('%p', time_obj)
            am_pm = ' '.join(list(am_pm))
        return str(hour) + ' ' + min_str + ' ' + am_pm

    def process(self, input_string):
        preprocessed_strings = []
        i = 0
        words = input_string.lower().split()
        while i < len(words):
            word = words[i]
            time_obj, time_fmt = self.get_time_obj(word)
            if time_obj is not None:
                if i+1 < len(words) and (words[i+1] == 'am' or words[i+1] == 'pm'):
                    i += 1
                    time_obj, time_fmt = self.get_time_obj(word+words[i])
                preprocessed_strings.append(self.time_string_from(time_obj, time_fmt))
            else:
                preprocessed_strings.append(word)
            i += 1

        return ' '.join(preprocessed_strings).strip()


class SpacePadSymbols:

    def __init__(self):
        allowed_symbols_escaped = re.escape(''.join(ALLOWED_SYMBOLS))
        self.not_alphanmueric_nor_allowed_regex = "([^a-z0-9\s" + allowed_symbols_escaped + "])"

    @staticmethod
    def space_pad_regex(input_string, regex):
        return re.sub(regex, r' \1 ', input_string).strip()

    def process(self, input_string):
        return self.space_pad_regex(input_string.lower(), self.not_alphanmueric_nor_allowed_regex)


class ReplaceAbbreviations:

    def __init__(self):
        self.abbreviations_to_words = load_pickle_dict(ABBREV_DICT_PATH)
        self.quantity_abbreviations_to_words = load_pickle_dict(QTY_ABBREV_DICT_PATH)

    def abbrev_replacements(self, word):
        # Quantity Abbreviations
        if word in self.quantity_abbreviations_to_words:
            return self.quantity_abbreviations_to_words[word]
        if word[:-1] in self.quantity_abbreviations_to_words and word[-1] == '.':
            return self.quantity_abbreviations_to_words[word[:-1]]

        # Regular Abbreviations
        if word in self.abbreviations_to_words:
            return self.abbreviations_to_words[word], None
        if word[:-1] in self.abbreviations_to_words and word[-1] == '.':
            return self.abbreviations_to_words[word[:-1]], None

        # Word is not an abbreviation
        return None, None

    def process(self, input_string):
        processed_words = []
        words = input_string.lower().split()
        for i, word in enumerate(words):
            replacement, replacement_plural = self.abbrev_replacements(word)
            if replacement is None:
                processed_words.append(word)
                continue

            if replacement_plural is None or i == 0 or not is_number(words[i-1]):
                processed_words.append(replacement)
                continue

            quantity = float(words[i-1])
            if quantity == 1:
                processed_words.append(replacement)
            else:
                processed_words.append(replacement_plural)

        return ' '.join(processed_words).strip()


class ReplaceNumbers:

    def __init__(self):
        self.inflect_engine = inflect.engine()
        self.digit_group_replacement_func = lambda m: ''.join(self.inflect_engine.number_to_words(s) for s in m.groups())

    def process(self, input_string):
        preprocessed_strings = []
        words = input_string.lower().split()
        for word in words:
            if not contains_digits(word):
                preprocessed_strings.append(word)
                continue
            word_no_digits = re.sub("([\d\.\,]+)", self.digit_group_replacement_func, word)
            preprocessed_strings.append(word_no_digits)
        return ' '.join(preprocessed_strings).strip()
