import sys
import os
import csv
import pickle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from big_phoney.shared_constants import PHONETIC_DICT_PATH, PHONETIC_SYMBOLS_PATH, ABBREV_DICT_PATH, QTY_ABBREV_DICT_PATH
from phonetic_dictionary_generator import PhoneticDictionaryGenerator


def csv_to_pkl_dict(csv_path, pkl_dict_path):
    with open(csv_path, mode='r') as csv_handle:
        reader = csv.reader(csv_handle)
        pkl_dict = {}
        for row in reader:
            row_key = row[0].strip()
            row_vals = [val.strip() for val in row[1:]]
            if len(row_vals) == 1:
                pkl_dict[row_key] = row_vals[0]
            else:
                pkl_dict[row_key] = row_vals
    with open(pkl_dict_path, 'wb') as pkl_handle:
        pickle.dump(pkl_dict, pkl_handle, protocol=pickle.HIGHEST_PROTOCOL)


def should_skip_lookup_dict(word):
    return not word[0].isalpha() 


gen = PhoneticDictionaryGenerator(should_skip_lookup_dict)
gen.generate_phonetic_dict(PHONETIC_DICT_PATH)
gen.generate_symbol_list(PHONETIC_SYMBOLS_PATH)


current_dir = os.path.dirname(os.path.abspath(__file__))
ABBREV_CSV_PATH = os.path.join(current_dir, 'dev_data', 'abbreviations.csv')
csv_to_pkl_dict(ABBREV_CSV_PATH, ABBREV_DICT_PATH)


QTY_ABBREV_CSV_PATH = os.path.join(current_dir, 'dev_data', 'quantity_abbreviations.csv')
csv_to_pkl_dict(QTY_ABBREV_CSV_PATH, QTY_ABBREV_DICT_PATH)


print('Dictionaries Created Successfully!')
