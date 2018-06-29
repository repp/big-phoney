import numpy as np
from shared_constants import PHONETIC_SYMBOLS_PATH, ALLOWED_CHARS
from utils import load_pickle_dict

START_PHONE_SYM = '\t'
END_PHONE_SYM = '\n'

MIN_CHAR_SEQ_LEN = 2
MAX_CHAR_SEQ_LEN = 20
MAX_PHONE_SEQ_LEN = 19
# Phone Sequences are padded with Start/End tokens
MAX_PADDED_PHONE_SEQ_LEN = MAX_PHONE_SEQ_LEN + 2


class PredictionModelUtils:

    def __init__(self):
        self.chars = self._char_list()
        self.phones = self._phone_list()
        self.char_token_count = len(self.chars)
        self.phone_token_count = len(self.phones)
        self.char_to_id, self.id_to_char = self._id_mappings_from_list(self.chars)
        self.phone_to_id, self.id_to_phone = self._id_mappings_from_list(self.phones)

    @staticmethod
    def _char_list():
        return [''] + ALLOWED_CHARS

    def _phone_list(self):
        edge_symbols = [START_PHONE_SYM, END_PHONE_SYM]
        cmu_symbols = load_pickle_dict(PHONETIC_SYMBOLS_PATH)
        return [''] + edge_symbols + cmu_symbols

    @staticmethod
    def _id_mappings_from_list(str_list):
        str_to_id = {s: i for i, s in enumerate(str_list)}
        id_to_str = {i: s for i, s in enumerate(str_list)}
        return str_to_id, id_to_str

    def word_to_char_ids(self, word):
        word_vec = np.zeros((MAX_CHAR_SEQ_LEN))
        for t, char in enumerate(word):
            word_vec[t] = self.char_to_id[char]
        return np.array([word_vec])

