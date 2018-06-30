import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from tqdm import tqdm
from keras.callbacks import ModelCheckpoint, EarlyStopping
from sklearn.model_selection import train_test_split
from big_phoney.prediction_model import PredictionModel
from big_phoney.prediction_model_data_loader import PredictionModelDataLoader
from big_phoney.utils import count_phonemes_with_emphasis


class PredictionModelTrainer:

    TEST_SIZE = 0.2

    def __init__(self):
        self.data_loader = PredictionModelDataLoader()
        char_input, phone_input, phone_output = self.data_loader.load_training_examples()
        self.char_input_train, self.char_input_test = self._train_test_split(char_input)
        self.phone_input_train, self.phone_input_test = self._train_test_split(phone_input)
        self.phone_output_train, self.phone_output_test = self._train_test_split(phone_output)

    def _train_test_split(self, data):
        return train_test_split(data, test_size=self.TEST_SIZE, random_state=42)

    def train(self, prediction_model, weights_path, validation_size=0.2, epochs=100):
        h0 = np.zeros((self.char_input_train.shape[0], prediction_model.hidden_nodes))
        c0 = np.zeros((self.char_input_train.shape[0], prediction_model.hidden_nodes))
        inputs = list(self.phone_input_train.swapaxes(0, 1))
        outputs = list(self.phone_output_train.swapaxes(0, 1))

        callbacks = []
        if validation_size > 0:
            checkpointer = ModelCheckpoint(filepath=weights_path, verbose=1, save_best_only=True)
            stopper = EarlyStopping(monitor='val_loss', patience=3)
            callbacks = [checkpointer, stopper]

        prediction_model.training_model.compile(optimizer='adam', loss='categorical_crossentropy')
        prediction_model.training_model.fit([self.char_input_train, h0, c0] + inputs, outputs,
                                            batch_size=256,
                                            epochs=epochs,
                                            validation_split=validation_size,
                                            callbacks=callbacks)

        if validation_size == 0:
            prediction_model.training_model.save_weights(weights_path)

    def is_correct(self, word, test_pronunciation):
        correct_pronuns = self.data_loader.pronunciations(word)
        for correct_pronun in correct_pronuns:
            if test_pronunciation == correct_pronun:
                return True
        return False

    def is_syllable_count_correct(self, word, test_pronunciation):
        correct_pronuns = self.data_loader.pronunciations(word)
        for correct_pronun in correct_pronuns:
            if count_phonemes_with_emphasis(test_pronunciation) == count_phonemes_with_emphasis(correct_pronun):
                return True
        return False

    def evaluate(self, prediction_model):
        test_example_count = len(self.char_input_test)
        correct_syllable_counts = 0
        perfect_predictions = 0

        for example_idx in tqdm(range(test_example_count)):
            example_char_seq = self.char_input_test[example_idx:example_idx + 1]
            predicted_pronun = prediction_model.predict_from_char_ids(example_char_seq)
            example_word = self.data_loader.id_vec_to_word(example_char_seq)

            perfect_predictions += self.is_correct(example_word, predicted_pronun)
            correct_syllable_counts += self.is_syllable_count_correct(example_word, predicted_pronun)

        syllable_acc = correct_syllable_counts / test_example_count
        perfect_acc = perfect_predictions / test_example_count

        print('Syllable Accuracy: %s%%' % round(syllable_acc * 100, 1))
        print('Perfect Accuracy: %s%%' % round(perfect_acc * 100, 1))


if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dev_weights_path = os.path.join(current_dir, 'dev_data', 'dev_prediction_model_weights.hdf5')

    # Training
    model = PredictionModel()
    model.training_model.summary()
    model_trainer = PredictionModelTrainer()
    model_trainer.train(model, dev_weights_path)

    # Evaluation
    model.load_weights(dev_weights_path)
    model_trainer.evaluate(model)
