import csv
import sys
from random import shuffle
from typing import List, Tuple, Set

import numpy as np
from tensorflow.python.keras.utils import to_categorical
from tensorflow.python.keras.preprocessing.sequence import pad_sequences
from tensorflow.python.keras.utils import Sequence

from char_tokenizer import Tokenizer


class DataPreprocessor(Sequence):

    def __init__(self, batch_size: int = 32, train: bool = True, enc_dec=False, pad_to=None):
        self.train = train
        self.batch_size = batch_size
        self.tokenizer = Tokenizer()
        samples = self.positive_samples() + self.negative_samples()
        shuffle(samples)
        self.train_data = np.asarray([self.tokenizer.tokenize(date) for date, label in samples])
        self.labels = np.asarray([label for date, label in samples])
        self.enc_dec = enc_dec
        self.pad_to = pad_to

    def __len__(self):
        return int(np.ceil(len(self.train_data) / float(self.batch_size)))

    def __getitem__(self, batch_index: int):
        x_batch = self.train_data[batch_index * self.batch_size:(batch_index + 1) * self.batch_size]
        x_batch = pad_sequences(x_batch, padding="post", value=0, maxlen=self.pad_to, truncating="post")
        y_batch = self.labels[batch_index * self.batch_size:(batch_index + 1) * self.batch_size]
        if self.enc_dec:
            y_batch = to_categorical(x_batch, num_classes=self.vocab_size())
        return x_batch, y_batch

    def vocab_size(self) -> int:
        return self.tokenizer.vocab_size()

    @classmethod
    def read_facebook_data(cls) -> List[str]:
        file_name = "data/materialien/facebook_foursquare_gowalla_sna.csv"
        columns = {"Phone", "Zip", "Latitude", "Longitude", "Name", "Street"}
        lines = cls.read_csv(file_name, columns_to_keep=columns)
        samples = []
        for line in lines:
            for key, value in line.items():
                if value:
                    samples.append(f"{value.strip()}\n")
        return samples

    @classmethod
    def read_soccer_file(cls) -> List[str]:
        file_name = "data/soccer/match.csv"
        lines = cls.read_csv(file_name, columns_to_keep={"date"})
        dates = [named_row["date"] for named_row in lines if named_row["date"]]
        return dates

    @staticmethod
    def read_csv(file_name: str,
                 delimiter: str = ",",
                 quotechar: str = '"',
                 has_header: bool = True,
                 columns_to_keep: Set[str] = None) -> list:
        lines = []
        csv.field_size_limit(sys.maxsize)
        with open(file_name, 'r') as file:
            data: csv.DictReader = csv.reader(file, delimiter=delimiter, quotechar=quotechar)
            if has_header:
                header = next(data)
                for row in data:
                    padded_row = row + ((len(header) - len(row)) * [None])
                    named_row = {name: padded_row[index] for index, name in enumerate(header)}
                    if columns_to_keep:
                        named_row = {key: value for key, value in named_row.items() if key in columns_to_keep}
                    lines.append(named_row)
            else:
                lines = [row for row in data]
        return lines

    def positive_samples(self) -> List[Tuple[str, float]]:
        samples = []
        path = "preprocessed_data"
        if self.train:
            file = f"{path}/pos_samples_train.txt"
        else:
            file = f"{path}/pos_samples_val.txt"
        with open(file, "r") as date_file:
            for line in date_file:
                samples.append((line.strip(), 1.0))
        return samples

    def negative_samples(self) -> List[Tuple[str, float]]:
        path = "preprocessed_data"
        if self.train:
            file = f"{path}/neg_samples_train.txt"
        else:
            file = f"{path}/neg_samples_val.txt"
        samples = []
        with open(file, "r") as fb_file:
            for line in fb_file:
                samples.append((line.strip(), 0.0))
        return samples


if __name__ == "__main__":
    fb = DataPreprocessor.read_facebook_data()
    print(len(fb))
    with open("facebook_samples.txt", "w") as file:
        file.writelines(fb)
