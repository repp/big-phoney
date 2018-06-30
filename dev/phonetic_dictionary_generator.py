import pickle
import os


class PhoneticDictionaryGenerator:

    current_dir = os.path.dirname(os.path.abspath(__file__))
    CMU_DICT_PATH = os.path.join(current_dir, 'dev_data', 'cmudict-0.7b')
    CMU_SYMBOLS_PATH = os.path.join(current_dir, 'dev_data', 'cmudict-0.7b.symbols')

    def __init__(self, skip_word_func):
       self.should_skip_word = skip_word_func 
       self.phonetic_dict = None
       self.symbol_list = None

    def _is_alternate_pho_spelling(self,word):
        # No word has > 9 alternate pronunciations
        return word[-1] == ')' and word[-3] == '(' and word[-2].isdigit() 

    def create_dict_from_cmu(self):
        phonetic_dict = {}
        with open(self.CMU_DICT_PATH, encoding="ISO-8859-1") as cmu_dict:
            for line in cmu_dict:
                
                # Skip commented lines
                if line[0:3] == ';;;': 
                    continue

                word, phonetic = line.strip().split('  ') 
                
                # Alternate pronounciations are formatted: "WORD(#)  F AH0 N EH1 T IH0 K"
                # We don't want to the "(#)" considered as part of the word 
                if self._is_alternate_pho_spelling(word):
                    word = word[:word.find('(')]

                if self.should_skip_word(word):
                    continue

                if not word in phonetic_dict:
                    phonetic_dict[word] = []
                phonetic_dict[word].append(phonetic)

        return phonetic_dict

    def generate_phonetic_dict(self, save_path):
        phonetic_dict = self.create_dict_from_cmu()
        self._save(save_path, phonetic_dict)

    def create_symbol_list_from_cmu(self):
        phone_list = []
        with open(self.CMU_SYMBOLS_PATH) as file:
            for line in file:
                phone_list.append(line.strip())
        return phone_list

    def generate_symbol_list(self, save_path):
        symbol_list = self.create_symbol_list_from_cmu()
        self._save(save_path, symbol_list)

    def _save(self, save_path, data):
        with open(save_path, 'wb') as handle:
            pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)


