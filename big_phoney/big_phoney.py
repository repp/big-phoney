from .phonetic_dictionary import PhoneticDictionary
from .prediction_model import PredictionModel
from .shared_constants import PREDICTION_MODEL_WEIGHTS_PATH
from .preprocessors import *
from . import utils


class BigPhoney:

    DEFAULT_PREPROCESSORS = [ExpandCurrencySymbols, FormatEmailAndURLs, ReplaceTimes,  SpacePadSymbols,
                             ReplaceAbbreviations, ReplaceNumbers]

    def __init__(self, preprocessors=DEFAULT_PREPROCESSORS):
        self.preprocessors = [preprocessor_class() for preprocessor_class in preprocessors]
        self.phonetic_dict = PhoneticDictionary()
        self.pred_model = PredictionModel()
        self.pred_model.load_weights(PREDICTION_MODEL_WEIGHTS_PATH)

    def apply_preprocessors(self, input_string):
        preprocessed_string = input_string
        for preprocessor in self.preprocessors:
            preprocessed_string = preprocessor.process(preprocessed_string)
        return preprocessed_string

    def phonize(self, input_string):
        phones = []
        preprocessed_string = self.apply_preprocessors(input_string)
        words = utils.safe_split(preprocessed_string)
        for word in words:
            word = utils.sanitize(word)
            phonetic_sp = self._phonize_word(word)
            if len(phonetic_sp) > 0:
                phones.append(phonetic_sp)

        return '  '.join(phones)

    def _phonize_word(self, word):
        dict_sp = self.phonetic_dict.lookup(word)
        if dict_sp is not None:
            return dict_sp
        return self.pred_model.predict(word)

    def count_syllables(self, input_string):
        phonetic_sp = self.phonize(input_string)
        return utils.count_phonemes_with_emphasis(phonetic_sp)

