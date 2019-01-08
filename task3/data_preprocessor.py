import csv
from csv import DictReader
import numpy as np

from tensorflow.python.keras.utils import Sequence

from char_tokenizer import Tokenizer


class DataPreprocessor(Sequence):

    def __init__(self, file_name: str, batch_size: int = 32):
        self.batch_size = batch_size
        self.tokenizer = Tokenizer()
        self.lines = []
        with open(file_name, 'r') as soccer_file:
            data: DictReader = csv.reader(soccer_file, delimiter=',', quotechar='"')
            header = next(data)
            for row in data:
                named_row = {name: row[index] for index, name in enumerate(header)}
                self.lines.append(named_row)

        self.tokenizer.fit([named_row['date'] for named_row in self.lines])
        self.train_data = np.asarray([self.tokenizer.tokenize(named_row['date']) for named_row in self.lines])
        self.labels = np.asarray([1.] * len(self.train_data))

    def __len__(self):
        return int(np.ceil(len(self.train_data) / float(self.batch_size)))

    def __getitem__(self, batch_index: int):
        x_batch = self.train_data[batch_index * self.batch_size:(batch_index + 1) * self.batch_size]
        y_batch = self.labels[batch_index * self.batch_size:(batch_index + 1) * self.batch_size]
        return x_batch, y_batch

    def vocab_size(self) -> int:
        return self.tokenizer.vocab_size()
