import os
import string

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))

PHONETIC_DICT_PATH = os.path.join(PACKAGE_DIR, 'data', 'bp-phonetic-dict.pkl')
PHONETIC_SYMBOLS_PATH = os.path.join(PACKAGE_DIR, 'data', 'bp-phonetic-symbols.pkl')

PREDICTION_MODEL_WEIGHTS_PATH = os.path.join(PACKAGE_DIR, 'data', 'prediction_model_weights.hdf5')

ABBREV_DICT_PATH = os.path.join(PACKAGE_DIR, 'data', 'bp-abbrev-dict.pkl')
QTY_ABBREV_DICT_PATH = os.path.join(PACKAGE_DIR, 'data', 'bp-qty-abbrev-dict.pkl')
ALLOWED_SYMBOLS = [".", "-", "'"]
ALLOWED_CHARS = ALLOWED_SYMBOLS + list(string.ascii_uppercase)
