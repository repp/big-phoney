import re
import os
import pickle
from .shared_constants import ALLOWED_CHARS


def safe_split(phrase):

    def substring_indexes(substring, string):
        last_found = -1  # Begin at -1 so the next position to search from is 0
        while True:
            # Find next index of substring, by starting after its last known position
            last_found = string.find(substring, last_found + 1)
            if last_found == -1:
                break  # All occurrences have been found
            yield last_found

    def replace_periods_with_spaces(phrase):
        for period_idx in list(substring_indexes('.', phrase)):
            if not (phrase[period_idx-1].isdigit() and phrase[period_idx+1].isdigit()):
                char_list = list(phrase)
                char_list[period_idx] = ' '
                phrase = ''.join(char_list)
        return phrase

    phrase = replace_periods_with_spaces(phrase)
    return re.split('[\s\-_—]+', phrase.strip())


def sanitize(word):
    allowed_chars = re.escape(''.join(ALLOWED_CHARS))
    return re.sub(r"[^"+allowed_chars+"]", '', word.upper())


def is_number(word):
    return len(word) != 0 and not bool(re.search('[^\d\.,]', word))


def contains_digits(word):
    return len(word) != 0 and bool(re.search('(\d+)', word))


def count_phonemes_with_emphasis(phonetic_sp):

    def phone_has_emphasis(phone):
        if len(phone) == 0:
            return False
        return phone.strip()[-1].isdigit()

    count = 0
    for phone in phonetic_sp.split():
        if phone_has_emphasis(phone):
            count += 1
    return count


def load_pickle_dict(dict_path):
    if not os.path.isfile(dict_path):
        raise FileNotFoundError('The dictionary file is missing. Generate it by running '
                                '`python dev/generate_dictionaries.py`')
    with open(dict_path, 'rb') as handle:
        return pickle.load(handle)

