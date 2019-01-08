from tensorflow.python.keras import Sequential
from tensorflow.python.keras.layers import LSTM, Dense, Embedding
from tensorflow.python.keras.utils import plot_model

from data_preprocessor import DataPreprocessor

soccer = 'data/match.csv'


def main():
    embedding_size = 3
    data_sequence = DataPreprocessor(soccer, 32)

    model = Sequential()
    model.add(Embedding(data_sequence.vocab_size(), embedding_size))
    model.add(LSTM(embedding_size))
    model.add(Dense(1, activation='sigmoid'))

    model.compile('rmsprop', loss='binary_crossentropy', metrics=['accuracy'])

    file_name = 'model'
    plot_model(model, to_file=f'{file_name}.png', show_shapes=True)
    print(f"Model built. Saved {file_name}.png\n")

    history = model.fit_generator(data_sequence,
                                  epochs=5,
                                  shuffle=True)


if __name__ == '__main__':
    main()
