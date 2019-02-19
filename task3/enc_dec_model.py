from typing import List

from tensorflow.python.keras import backend as K
from tensorflow.python.keras import Model, Input
from tensorflow.python.keras.callbacks import ModelCheckpoint
from tensorflow.python.keras.layers import LSTM, Dense, Embedding, Lambda, Reshape, Concatenate
from tensorflow.python.keras.utils import plot_model
from tensorflow.python.keras.models import load_model, Model as KerasModel

from char_tokenizer import Tokenizer
from data_preprocessor import DataPreprocessor
from prediction_sequence import PredictionSequence


###
# Encoder-Decoder Model (DPfS)
# Model to learn date-normality.
# In a data preparation setting, possible noise should be removed.
###

class EncDecModel:
    def __init__(self):
        # Definition of hyper parameter, data sources and other class variables
        self.embedding_dim = 3
        self.lstm_hidden_dim = self.embedding_dim
        self.max_decoder_length = 25
        self.epochs = 10
        self.data_sequence = DataPreprocessor(64, train=True, enc_dec=True, pad_to=self.max_decoder_length)
        self.data_sequence.tokenizer.save_vocab()
        self.val_sequence = DataPreprocessor(64, train=False, enc_dec=True, pad_to=self.max_decoder_length)
        self.history = None
        self.model_path: str = None
        self.model: KerasModel = None

    def build(self):
        # Embedding-layer to transform input into 3D-space.
        input_embedding = Embedding(self.data_sequence.vocab_size(), self.embedding_dim)

        # Inputs
        encoder_inputs = Input(shape=(None,))
        encoder_inputs_emb = input_embedding(encoder_inputs)

        # Encoder LSTM
        encoder = LSTM(self.lstm_hidden_dim, return_state=True)
        encoder_outputs, state_h, state_c = encoder(encoder_inputs_emb)
        state = [state_h, state_c]  # state will be used to initialize the decoder

        # Start vars (emulates a constant input)
        def constant(input_batch, size):
            batch_size = K.shape(input_batch)[0]
            return K.tile(K.ones((1, size)), (batch_size, 1))

        decoder_in = Lambda(constant, arguments={'size': self.embedding_dim})(encoder_inputs_emb)  # "start word"

        # Definition of further layers to be used in the model (decoder and mapping to vocab-sized vector)
        decoder_lstm = LSTM(self.lstm_hidden_dim, return_sequences=False, return_state=True)
        decoder_dense = Dense(self.data_sequence.vocab_size(), activation='softmax')

        chars = []  # Container for single results during the loop
        for i in range(self.max_decoder_length):
            # Reshape necessary to match LSTMs interface, cell state will be reintroduced in the next iteration
            decoder_in = Reshape((1, self.embedding_dim))(decoder_in)
            decoder_in, hidden_state, cell_state = decoder_lstm(decoder_in, initial_state=state)
            state = [hidden_state, cell_state]

            # Mapping
            decoder_out = decoder_dense(decoder_in)

            # Reshaping and storing for later concatenation
            char = Reshape((1, self.data_sequence.vocab_size()))(decoder_out)
            chars.append(char)

            # Teacher forcing. During training the original input will be used as input to the decoder
            decoder_in_train = Lambda(lambda x, ii: x[:, -ii], arguments={'ii': i+1})(encoder_inputs_emb)
            decoder_in = Lambda(lambda x, y: K.in_train_phase(y, x), arguments={'y': decoder_in_train})(decoder_in)

        # Single results are joined together (axis 1 vanishes)
        decoded_seq = Concatenate(axis=1)(chars)

        self.model = Model(encoder_inputs, decoded_seq, name="enc_dec")
        self.model.compile(optimizer='adam', loss='categorical_crossentropy')
        self.model.summary()

        try:
            file_name = 'enc_dec_model'
            plot_model(self.model, to_file=f'{file_name}.png', show_shapes=True)
            print(f"Model built. Saved {file_name}.png\n")
        except (ImportError, FileNotFoundError):
            print(f"Skipping plotting of model due to missing dependencies.")

    def train(self, path: str = None):
        self.model_path = path or f"enc_dec_models/model_emb{self.embedding_dim}_epochs{self.epochs}.hdf5"
        checkpoint = ModelCheckpoint(f"enc_dec_models/checkpoint_emb{self.embedding_dim}_epochs" + '{epoch:02d}.hdf5',
                                     verbose=1)

        # self.data_sequence - in this case y is one hot encoded with vocab size
        self.history = self.model.fit_generator(self.data_sequence,
                                                callbacks=[checkpoint],
                                                epochs=self.epochs,
                                                shuffle=True,
                                                validation_data=self.val_sequence,
                                                max_queue_size=1024)
        self.model.save(self.model_path)

    def predict(self, data: List[str] = None, model_path: str = None):
        if self.model is None and model_path is not None:
            print(f"Loading model from {model_path}.")
            self.model = load_model(model_path)
            self.data_sequence.tokenizer = Tokenizer.from_vocab()
        elif self.model is None:
            print(f"No model file provided. Training new model.")
            self.build()
            self.train()

        pred_sequence = PredictionSequence(self.data_sequence, data)
        predictions = self.model.predict_generator(pred_sequence, steps=len(pred_sequence))
        for index, sample in enumerate(pred_sequence.samples):
            prediction = [K.argmax(char) for char in predictions[index]]
            print(f"Predicted for sample {sample}: {prediction}")
