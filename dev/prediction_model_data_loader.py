import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import re
from prediction_model_utils import PredictionModelUtils, START_PHONE_SYM, END_PHONE_SYM, MIN_CHAR_SEQ_LEN, MAX_CHAR_SEQ_LEN, MAX_PADDED_PHONE_SEQ_LEN
from phonetic_dictionary_generator import PhoneticDictionaryGenerator


class PredictionModelDataLoader:

    def __init__(self):
        self.utils = PredictionModelUtils()
        self.phonetic_dict = self._training_phone_dict()

    def load_training_examples(self):
        char_seqs = []
        phone_seqs = []
        phone_seqs_1_hot = []

        for word, pronuns in self.phonetic_dict.items():
            word_matrix = np.zeros((MAX_CHAR_SEQ_LEN))
            for t, char in enumerate(word):
                word_matrix[t] = self.utils.char_to_id[char]
            for pronun in pronuns:
                phones = [START_PHONE_SYM] + pronun.split() + [END_PHONE_SYM]
                pronun_matrix_1_hot = np.zeros((MAX_PADDED_PHONE_SEQ_LEN, self.utils.phone_token_count))
                pronun_matrix = np.zeros((MAX_PADDED_PHONE_SEQ_LEN))
                for t, phone in enumerate(phones):
                    pronun_matrix_1_hot[t, :] = self._phone_to_1_hot(phone)
                    pronun_matrix[t] = self.utils.phone_to_id[phone]

                char_seqs.append(word_matrix)
                phone_seqs.append(pronun_matrix)
                phone_seqs_1_hot.append(pronun_matrix_1_hot)

        return np.array(char_seqs), np.array(phone_seqs), np.array(phone_seqs_1_hot)

    def _training_phone_dict(self):
        allowed_chars = self.utils.chars
        illegal_char_regex = '[^'+re.escape(''.join(allowed_chars))+']'

        def should_skip(word):
            if not word[0].isalpha():  # skip symbols
                return True
            if word[-1] == '.':  # skip abbreviations
                return True
            if re.search(illegal_char_regex, word):
                return True
            if len(word) > MAX_CHAR_SEQ_LEN:
                return True
            if len(word) < MIN_CHAR_SEQ_LEN:
                return True
            return False

        dict_gen = PhoneticDictionaryGenerator(should_skip)
        return dict_gen.create_dict_from_cmu()

    def _phone_to_1_hot(self, phone):
        phone_id = self.utils.phone_to_id[phone]
        hot_vec = np.zeros((self.utils.phone_token_count))
        hot_vec[phone_id] = 1.
        return hot_vec

    def id_vec_to_word(self, emb_char_seq):
        word = ''
        for char_id in emb_char_seq[0]:
            char = self.utils.id_to_char[char_id]
            word += char
        return word.strip()

    def pronunciations(self, word):
        return self.phonetic_dict[word]
