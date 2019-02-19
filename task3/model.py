import json
from typing import List

from tensorflow.python.keras.callbacks import ModelCheckpoint
from tensorflow.python.keras.layers import LSTM, Dense, Embedding
from tensorflow.python.keras.utils import plot_model
from tensorflow.python.keras.models import load_model, Sequential, Model as KerasModel

from char_tokenizer import Tokenizer
from data_preprocessor import DataPreprocessor
from prediction_sequence import PredictionSequence


class Model(object):
    def __init__(self):
        self.embedding_size = 3
        self.epochs = 10
        self.hidden_state_size = 16
        self.data_sequence = DataPreprocessor(64, train=True)
        self.data_sequence.tokenizer.save_vocab()
        self.val_sequence = DataPreprocessor(64, train=False)
        self.history = None
        self.model_path: str = None
        self.model: KerasModel = None

    def build(self):
        self.model = Sequential()
        self.model.add(Embedding(self.data_sequence.vocab_size(), self.embedding_size))
        self.model.add(LSTM(self.hidden_state_size))
        self.model.add(Dense(1, activation='sigmoid'))

        self.model.compile('adam', loss='binary_crossentropy', metrics=['acc'])
        self.model.summary()

        try:
            file_name = 'model'
            plot_model(self.model, to_file=f'{file_name}.png', show_shapes=True)
            print(f"Model built. Saved {file_name}.png\n")
        except (ImportError, FileNotFoundError, OSError):
            print(f"Skipping plotting of model due to missing dependencies.")

    def train(self, path: str = None):
        self.model_path = path or f"models/model_emb{self.embedding_size}_epochs{self.epochs}.hdf5"
        checkpoint = ModelCheckpoint(f"models/checkpoint_emb{self.embedding_size}_epochs" + '{epoch:02d}.hdf5', verbose=1)
        self.history = self.model.fit_generator(self.data_sequence,
                                                callbacks=[checkpoint],
                                                epochs=self.epochs,
                                                shuffle=True,
                                                validation_data=self.val_sequence,
                                                max_queue_size=1024)

        self.model.save(self.model_path)
        self.plot_training()

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

    def plot_training(self):
        """Plot graphs"""
        # Load the training statistics (model.history)
        # Plot training loss and accuracy
        history = self.history.history
        json.dump(history, open(f"model_history_backup_e{self.epochs}.json", "w"))
        epochs = range(1, self.epochs + 1)

        f = plt.figure()
        plt.plot(range(10), range(10), "o")
        plt.show()

        fig = plt.figure()
        plt.plot(epochs, history['loss'], 'bo', label='Training loss')
        plt.plot(epochs, history['val_loss'], 'b', label='Validation loss')
        plt.title('Training and validation loss')
        plt.xlabel('Epochs')
        plt.ylabel('Loss')
        plt.legend()
        fig.savefig(f"plot_loss_e{self.epochs}.pdf", bbox_inches='tight')
        plt.clf()

        # Plot validation loss and accuracy
        fig = plt.figure()
        plt.plot(epochs, history['acc'], 'bo', label='Training acc')
        plt.plot(epochs, history['val_acc'], 'b', label='Validation acc')
        plt.title('Training and validation accuracy')
        plt.xlabel('Epochs')
        plt.ylabel('Accuracy')
        plt.legend()
        fig.savefig(f"plot_acc_e{self.epochs}.pdf", bbox_inches='tight')
