from typing import List

from keras.callbacks import ModelCheckpoint
from keras.layers import LSTM, Dense, Embedding
from keras.utils import plot_model
from keras.models import load_model, Sequential, Model as KerasModel

from char_tokenizer import Tokenizer
from data_preprocessor import DataPreprocessor
from prediction_sequence import PredictionSequence


class Model(object):
    def __init__(self):
        self.embedding_size = 3
        self.epochs = 10
        self.data_sequence = DataPreprocessor(64, train=True)
        self.data_sequence.tokenizer.save_vocab()
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
        self.model_path = path or f"models/model_emb{self.embedding_size}_epochs{self.epochs}.hdf5"
        checkpoint = ModelCheckpoint(f"models/checkpoint_emb{self.embedding_size}_epochs" + '{epoch:02d}.hdf5', verbose=1)
        self.history = self.model.fit_generator(self.data_sequence,
                                                callbacks=[checkpoint],
                                                epochs=self.epochs,
                                                steps_per_epoch=len(self.data_sequence),
                                                # shuffle=True,
                                                validation_data=self.val_sequence,
                                                max_queue_size=1024,
                                                validation_steps=len(self.val_sequence))

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
            prediction = predictions[index][0]
            print(f"Predicted for sample {sample}: {prediction}")
