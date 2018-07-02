# Big Phoney

[![Build Status](https://travis-ci.org/repp/big-phoney.svg?branch=master)](https://travis-ci.org/repp/big-phoney) [![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

Big Phoney is a python module that generates phonetic pronunciations from english words.
For example, given the word "dinosaur", Big Phoney will return "D AY1 N AH0 S AO2 R". This is sometimes called
"Grapheme-to-Phoneme Conversion" or G2P. Big Phoney works for any word, even those that don't appear in the dictionary and it's
designed to handle special cases like currency and abbreviations.

Phonetic pronunciations are represented using the [ARPAbet phoneme set](https://en.wikipedia.org/wiki/ARPABET).

Big Phoney can also count the number of syllables in any english word.

### How it Works

When possible, pronunciations come from a dictionary which contains 134,000 words. Slang, proper-nouns, and made-up
words that don't appear in the standard dictionary are predicted using a model. You can read more about the
[pronunciation prediction model on Kaggle](https://www.kaggle.com/reppic/predicting-english-pronunciations).

Additionally, Big Phoney has a number of configurable preprocessors to handle
cases where proper pronunciation requires special knowledge. For example "$5.00" is pronounced "F AY1 V  D AA1 L ER0 Z".
Currently, Big Phoney can handle: numbers, currency, times, symbols, abbreviations, email addresses, and urls.

### Accuracy

For any of the 134,000 words found in the dictionary, you can expect 100% accurate pronunciations and syllable counts. For words not found
in the dictionary, you can expect syllable counts to be accurate 98.1% of the time and pronunciations to be perfectly
accurate 75.4% of the time. Even when a predicted pronunciation isn't completely correct, it's often very close.

## Installation
**Install with PyPI:**
```
pip install big-phoney
```
**Install from source:**
```
git clone https://github.com/repp/big-phoney.git
cd big_phoney
python setup.py install
```
## Usage
First, import Big Phoney:
```python
from big_phoney import BigPhoney
```
Next, create an instance of the main class:
```python
phoney = BigPhoney()
```
This will load the phonetic dictionary and prediction model into memory. It may take a second. It's in your best interest
to *not* create multiple instances of this class.

Call `phonize` to generate phonetic spellings from words.
```python
phoney.phonize('pterodactyl')  # --> 'T EH2 R OW0 D AE1 K T AH0 L'

# Works with multiple words. Individual pronunciations are seperate by 2 spaces:
phoney.phonize('tyrannosaurus rex')  # --> 'T IH0 R AE0 N AH0 S AO1 R AH0 S  R EH1 K S'
```

Call `count_syllables` to get the number of syllables in a word or phrase.
```python
phoney.count_syllables('bird')  # --> 1
phoney.count_syllables('triceratops')  # --> 4

# Given multiple words, Big Phoney returns the total number of syllables:
phoney.count_syllables('welcome to jurassic park')  # --> 7

# If you want a list of syllable counts, try something like:
[phoney.count_syllables(word) for word in 'welcome to jurassic park'.split()]  # --> [2,1,3,1]

```

## Preprocessors
Big Phoney has a number of default preprocessors designed to improve pronunciation results in special cases.
```python
DEFAULT_PREPROCESSORS = [ExpandCurrencySymbols, FormatEmailAndURLs, ReplaceTimes,  SpacePadSymbols,
                             SpacePadNumbers, ReplaceAbbreviations, ReplaceNumbers]
```
By default all of the above preprocessors are applied. You can add and remove them when creating a Big Phoney instance
with the `preprocessors` keyword argument:
```python
phoney = BigPhoney(preprocessors=[ReplaceNumbers])  # Only preprocess numbers
```
To skip preprocessing entirely, just pass an empty list:
```python
phoney = BigPhoney(preprocessors=[])  # No preprocessing
```
Be careful when adjusting the default preprocessors. Their order is important as some rely on other 'upstream' processors to be most effective.

To test a preprocessor setup, use the `apply_preprocessors` method:
```python
phoney = BigPhoney()  # Use default preprocessors
phoney.apply_preprocessors('£7.89')  # --> 'seven pounds and eighty-nine pence'
phoney.apply_preprocessors('Mt St. Helens')  # --> 'mount saint helens'
phoney.apply_preprocessors('no_reply@gmail.com')  # --> 'no underscore reply at gmail dot com'
phoney.apply_preprocessors('1ft + 2ft = 3ft')  # --> 'one foot plus two feet equals three feet'
phoney.apply_preprocessors("It'll be 7:00am in 1,245.6 seconds")  # --> 'it'll be seven o'clock a m in one-thousand, two hundred and forty-five point six seconds'
```
Writing your own preprocessors is easy. Any class with a `process` method that inputs and outputs a single string is valid. For example:
```python
class DummyPreprocessor:

    def process(self, input_string):
        # do some preprocessing here!
        return input_string
```

## Other Options
As mentioned, Big Phoney uses a dictionary and a model to generate pronunciations, if you only want to use one or
the other, you can create instances of each individually:

```python
from big_phoney import PhoneticDictionary
phonetic_dict = PhoneticDictionary()
phonetic_dict.lookup('paleontologist')  # --> 'P EY2 L IY0 AH0 N T AA1 L AH0 JH IH0 S T' ✅
phonetic_dict.lookup('fakeosaur')  # --> None ❌
```

```python
from big_phoney import PredictionModel
pred_model = PredictionModel()
pred_model.predict('paleontologist')  # --> 'P EY2 L IY0 AH0 N T AA1 L AH0 JH IH0 S T' ✅
phonetic_dict.lookup('fakeosaur')  # --> 'F EY1 K OW0 S AO2 R' ✅
```
The dictionary is faster and always correct but won't always return a result. The model is slower and less reliably accurate
but it will always return *something* no matter what you throw at it. In most cases, you should just stick with
the `BigPhoney` class.

## Contributing
If you want to contribute to this project that's great! Make sure to check out dev/README.md for more info.

## Acknowledgements
The dictionary and data used to train the phonetic prediction model came from the
[CMU Pronunciation Dictionary](http://www.speech.cs.cmu.edu/cgi-bin/cmudict).
