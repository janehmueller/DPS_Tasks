from typing import List, Dict, Tuple

import numpy as np
import csv
from csv import DictReader

from tensorflow.python.keras import Sequential
from tensorflow.python.keras.layers import LSTM, Dense, Embedding
from tensorflow.python.keras.utils import plot_model

from char_tokenizer import Tokenizer
from data_preprocessor import DataPreprocessor

soccer = 'data/match.csv'
tokenizer = Tokenizer()


def read_file() -> List[Dict[str, str]]:
    lines = []
    with open(soccer, 'r') as soccer_file:
        data: DictReader = csv.reader(soccer_file, delimiter=',', quotechar='"')
        header = next(data)
        for row in data:
            named_row = {name: row[index] for index, name in enumerate(header)}
            lines.append(named_row)
    return lines


def augment_date(date) -> Tuple[np.ndarray, np.ndarray]:
    # TODO
    pass


def extract_date(date: str) -> np.ndarray:
    result = []
    # element = ""
    for char in date:
        result.append(ord(char))
    #     if char.isdigit():
    #         element += char
    #     elif element:
    #         result.append(int(element))
    #         element = ""
    # if element:
    #     result.append(int(element))
    return np.asarray(result)


def train_data_gen(batch_size: int = 32):
    lines = []
    with open(soccer, 'r') as soccer_file:
        data: DictReader = csv.reader(soccer_file, delimiter=',', quotechar='"')
        header = next(data)
        for row in data:
            named_row = {name: row[index] for index, name in enumerate(header)}
            lines.append(named_row)

    tokenizer.fit([named_row['date'] for named_row in lines])

    train_data = [tokenizer.tokenize(named_row['date']) for named_row in lines]
    return np.asarray(train_data), np.asarray([1.] * len(train_data))
    #
    # while True:
    #     i = 0
    #     dates = []
    #     labels = []
    #     for named_row in lines:
    #         date = tokenizer.tokenize(named_row['date'])
    #         label = 1.0
    #         dates.append(date)
    #         labels.append(label)
    #         if i >= batch_size - 1:
    #             yield np.asarray(dates), np.asarray(labels)
    #             dates = []
    #             labels = []
    #             i = 0
    #         else:
    #             i += 1


def main():
    # data_generator = train_data_gen()

    embedding_size = 3
    data_sequence = DataPreprocessor(soccer, 32)

    # x_train, y_train = train_data_gen()

    model = Sequential()
    model.add(Embedding(data_sequence.vocab_size(), embedding_size))
    model.add(LSTM(embedding_size))
    model.add(Dense(1, activation='sigmoid'))

    model.compile('rmsprop', loss='binary_crossentropy', metrics=['accuracy'])

    file_name = 'model'
    plot_model(model, to_file=f'{file_name}.png', show_shapes=True)
    print(f"Model built. Saved {file_name}.png\n")
    #
    history = model.fit_generator(data_sequence,
                                  epochs=5,
                                  shuffle=True)

    # history = model.fit(x_train, y_train, batch_size=32, epochs=5, shuffle=True)


if __name__ == '__main__':
    main()
