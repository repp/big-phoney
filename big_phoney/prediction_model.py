import numpy as np
from keras.models import Model
from keras.layers import Input, LSTM, Dense, Embedding, Dropout, Activation, Bidirectional
from keras.layers import Concatenate, Dot, Reshape, RepeatVector, Lambda
from keras.activations import softmax
from .shared_constants import PREDICTION_MODEL_WEIGHTS_PATH
from .prediction_model_utils import PredictionModelUtils, START_PHONE_SYM, END_PHONE_SYM, MAX_CHAR_SEQ_LEN, MAX_PADDED_PHONE_SEQ_LEN


class PredictionModel:

    def __init__(self, search_width=3):
        self.hidden_nodes = 256
        self.search_width = search_width
        self.utils = PredictionModelUtils()
        self.training_model, self.encoder, self.decoder = self._build_model()
        self.load_weights(PREDICTION_MODEL_WEIGHTS_PATH)

    def _build_model(self):
        emb_size = 256
        dropout = 0.5
        recurrent_dropout = 0.2

        # Attention Mechanism Layers
        attn_repeat = RepeatVector(MAX_CHAR_SEQ_LEN)
        attn_concat = Concatenate(axis=-1)
        attn_dense1 = Dense(int(self.hidden_nodes/2), activation="tanh")
        attn_dense2 = Dense(1, activation="relu")
        attn_softmax = Lambda(lambda x: softmax(x,axis=1))
        attn_dot = Dot(axes = 1)

        def get_context(encoder_outputs, h_prev):
            h_prev = attn_repeat(h_prev)
            concat = attn_concat([encoder_outputs, h_prev])
            e = attn_dense1(concat)
            e = attn_dense2(e)
            attention_weights = attn_softmax(e)
            context = attn_dot([attention_weights, encoder_outputs])
            return context

        # Shared Components - Encoder
        char_inputs = Input(shape=(MAX_CHAR_SEQ_LEN,))
        char_embedding_layer = Embedding(self.utils.char_token_count, emb_size, input_length=MAX_CHAR_SEQ_LEN)
        encoder = Bidirectional(LSTM(self.hidden_nodes, return_sequences=True, recurrent_dropout=recurrent_dropout))

        # Shared Components - Decoder
        decoder = LSTM(self.hidden_nodes, return_state=True, recurrent_dropout=recurrent_dropout)
        phone_embedding_layer = Embedding(self.utils.phone_token_count, emb_size)
        embedding_reshaper = Reshape((1,emb_size,))
        context_phone_concat = Concatenate(axis=-1)
        context_phone_dense = Dense(self.hidden_nodes*3, activation="relu")
        output_layer = Dense(self.utils.phone_token_count, activation='softmax')

        # Training Model - Encoder
        char_embeddings = char_embedding_layer(char_inputs)
        char_embeddings = Activation('relu')(char_embeddings)
        char_embeddings = Dropout(dropout)(char_embeddings)
        encoder_outputs = encoder(char_embeddings)

        # Training Model - Attention Decoder
        h0 = Input(shape=(self.hidden_nodes,))
        c0 = Input(shape=(self.hidden_nodes,))
        h = h0 # hidden state
        c = c0 # cell state

        phone_inputs = []
        phone_outputs = []

        for t in range(MAX_PADDED_PHONE_SEQ_LEN):
            phone_input = Input(shape=(None,))
            phone_embeddings = phone_embedding_layer(phone_input)
            phone_embeddings = Dropout(dropout)(phone_embeddings)
            phone_embeddings = embedding_reshaper(phone_embeddings)

            context = get_context(encoder_outputs, h)
            phone_and_context = context_phone_concat([context, phone_embeddings])
            phone_and_context = context_phone_dense(phone_and_context)

            decoder_output, h, c = decoder(phone_and_context, initial_state=[h, c])
            decoder_output = Dropout(dropout)(decoder_output)
            phone_output = output_layer(decoder_output)

            phone_inputs.append(phone_input)
            phone_outputs.append(phone_output)

        training_model = Model(inputs=[char_inputs, h0, c0] + phone_inputs, outputs=phone_outputs)

        # Testing Model - Encoder
        testing_encoder_model = Model(char_inputs, encoder_outputs)

        # Testing Model - Decoder
        test_prev_phone_input = Input(shape=(None,))
        test_phone_embeddings = phone_embedding_layer(test_prev_phone_input)
        test_phone_embeddings = embedding_reshaper(test_phone_embeddings)

        test_h = Input(shape=(self.hidden_nodes,), name='test_h')
        test_c = Input(shape=(self.hidden_nodes,), name='test_c')

        test_encoding_input = Input(shape=(MAX_CHAR_SEQ_LEN, self.hidden_nodes*2,))
        test_context = get_context(test_encoding_input, test_h)
        test_phone_and_context = Concatenate(axis=-1)([test_context, test_phone_embeddings])
        test_phone_and_context = context_phone_dense(test_phone_and_context)

        test_seq, out_h, out_c = decoder(test_phone_and_context, initial_state=[test_h, test_c])
        test_out = output_layer(test_seq)

        testing_decoder_model = Model([test_prev_phone_input, test_h, test_c, test_encoding_input], [test_out,out_h,out_c])

        return training_model, testing_encoder_model, testing_decoder_model

    def load_weights(self, weights_path):
        # Loading the weights for the training model also applies them to the
        # encoder/decoder since they share components.
        self.training_model.load_weights(weights_path)

    def predict(self, word):
        char_id_input_seq = self.utils.word_to_char_ids(word.upper())
        return self.predict_from_char_ids(char_id_input_seq)

    def predict_from_char_ids(self, char_id_seq):
        return self.beam_search(char_id_seq)

    def beam_search(self, input_char_seq):
        a = self.encoder.predict(input_char_seq)

        h = np.zeros((1, self.hidden_nodes))
        c = np.zeros((1, self.hidden_nodes))

        all_seqs = []
        all_seq_scores = []

        live_seqs = [[self.utils.phone_to_id[START_PHONE_SYM]]]
        live_scores = [0]
        live_states = [[h, c]]

        while len(live_seqs) > 0:
            new_live_seqs = []
            new_live_scores = []
            new_live_states = []

            for sidx, seq in enumerate(live_seqs):
                target_seq = np.array([[seq[-1]]])
                output_token_probs, h, c = self.decoder.predict([target_seq] + live_states[sidx] + [a])

                best_token_indices = output_token_probs[0, :].argsort()[-self.search_width:]

                for token_index in best_token_indices:
                    new_seq = seq + [token_index]
                    prob = output_token_probs[0, :][token_index]
                    new_seq_score = live_scores[sidx] - np.log(prob)
                    if self.utils.id_to_phone[token_index] == END_PHONE_SYM or len(new_seq) > MAX_PADDED_PHONE_SEQ_LEN:
                        all_seqs.append(new_seq)
                        all_seq_scores.append(new_seq_score)
                        continue
                    new_live_seqs.append(new_seq)
                    new_live_scores.append(new_seq_score)
                    new_live_states.append([h, c])

            while len(new_live_scores) > self.search_width:
                worst_seq_score_idx = np.array(new_live_scores).argsort()[-1]
                del new_live_seqs[worst_seq_score_idx]
                del new_live_scores[worst_seq_score_idx]
                del new_live_states[worst_seq_score_idx]

            live_seqs = new_live_seqs
            live_scores = new_live_scores
            live_states = new_live_states

        best_idx = np.argmin(all_seq_scores)

        pronunciation = ''
        for i in all_seqs[best_idx]:
            pronunciation += self.utils.id_to_phone[i] + ' '

        return pronunciation.strip()

