# Contributing to Big Phoney

It's awesome you want to contribute! Make sure to:

1. Follow PEP8 Style Guide
2. Squash your commits before submitting a PR
3. Make sure all the existing tests pass
4. Add your own tests for any significant new features

## TODOS:

* Export Tensorflow models and get rid of Keras as a runtime dependency
* Cache predictions from the prediction model
    * Add a function to save a prediction model's cache to a dictionary
* Add a way for users to load their own dictionaries that work along with the CMU dict
* Add the ability to run preporcessing and G2P conversion in multiple threads
* Improve accuracy and/or speed of prediction model
* Add support for other languages
* Python 2 support
* Improve documentation
* Improve test coverage
