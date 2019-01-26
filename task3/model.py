from typing import List

from tensorflow.python.keras import Sequential, Model as KerasModel
from tensorflow.python.keras.layers import LSTM, Dense, Embedding
from tensorflow.python.keras.utils import plot_model
from tensorflow.python.keras.models import load_model

from char_tokenizer import Tokenizer
from data_preprocessor import DataPreprocessor
from prediction_sequence import PredictionSequence


class Model(object):
    def __init__(self):
        self.embedding_size = 3
        self.epochs = 10
        self.data_sequence = DataPreprocessor(64, train=True)
        self.val_sequence = DataPreprocessor(64, train=False)
        self.history = None
        self.model_path: str = None
        self.model: KerasModel = None

    def build(self):
        self.model = Sequential()
        self.model.add(Embedding(self.data_sequence.vocab_size(), self.embedding_size))
        self.model.add(LSTM(self.embedding_size))
        self.model.add(Dense(1, activation='sigmoid'))

        self.model.compile('adam', loss='binary_crossentropy', metrics=['accuracy'])
        self.model.summary()

        try:
            file_name = 'model'
            plot_model(self.model, to_file=f'{file_name}.png', show_shapes=True)
            print(f"Model built. Saved {file_name}.png\n")
        except (ImportError, FileNotFoundError):
            print(f"Skipping plotting of model due to missing dependencies.")

    def train(self, path: str = None):
        self.history = self.model.fit_generator(self.data_sequence,
                                                epochs=self.epochs,
                                                shuffle=True,
                                                validation_data=self.val_sequence)
        self.model_path = path or f"models/model_emb{self.embedding_size}_epochs{self.epochs}.hdf5"
        self.model.save(self.model_path)
        self.data_sequence.tokenizer.save_vocab()

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
        predictions = self.model.predict_generator(pred_sequence)
        for index, sample in enumerate(pred_sequence.samples):
            prediction = predictions[index][0]
            print(f"Predicted for sample {sample}: {prediction}")
