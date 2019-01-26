import csv
import sys
from csv import DictReader
from random import shuffle
from typing import List, Tuple

import numpy as np
from tensorflow.python.keras.preprocessing.sequence import pad_sequences

from tensorflow.python.keras.utils import Sequence

from char_tokenizer import Tokenizer


class DataPreprocessor(Sequence):

    def __init__(self, batch_size: int = 32):
        self.batch_size = batch_size
        self.tokenizer = Tokenizer()
        samples = self.positive_samples() + self.negative_samples()
        shuffle(samples)
        self.train_data = np.asarray([self.tokenizer.tokenize(date) for date, label in samples])
        self.labels = np.asarray([label for date, label in samples])

    def __len__(self):
        return int(np.ceil(len(self.train_data) / float(self.batch_size)))

    def __getitem__(self, batch_index: int):
        x_batch = self.train_data[batch_index * self.batch_size:(batch_index + 1) * self.batch_size]
        x_batch = pad_sequences(x_batch, padding="post", value=0)
        y_batch = self.labels[batch_index * self.batch_size:(batch_index + 1) * self.batch_size]
        return x_batch, y_batch

    def vocab_size(self) -> int:
        return self.tokenizer.vocab_size()

    def read_facebook_data(self) -> List[str]:
        file_name = "data/materialien/facebook_foursquare_gowalla_sna.csv"
        lines = self.read_csv(file_name)
        samples = []
        for line in lines:
            phone = line["Phone"]
            zipcode = line["Zip"]
            lat = line["Latitude"]
            long = line["Longitude"]
            samples += [f"{sample.strip()}\n" for sample in [phone, zipcode, lat, long] if sample]
        return samples

    def read_soccer_file(self) -> List[str]:
        file_name = "data/soccer/match.csv"
        lines = self.read_csv(file_name)
        dates = [named_row['date'] for named_row in lines]
        return dates

    def read_csv(self, file_name: str, delimiter: str = ",", quotechar: str = '"', has_header: bool = True) -> list:
        lines = []
        csv.field_size_limit(sys.maxsize)
        with open(file_name, 'r') as soccer_file:
            data: DictReader = csv.reader(soccer_file, delimiter=delimiter, quotechar=quotechar)
            if has_header:
                header = next(data)
                for row in data:
                    padded_row = row + ((len(header) - len(row)) * [None])
                    named_row = {name: padded_row[index] for index, name in enumerate(header)}
                    lines.append(named_row)
            else:
                lines = [row for row in data]
        return lines

    def positive_samples(self) -> List[Tuple[str, float]]:
        samples = []
        path = "preprocessed_data"
        full_file = f"{path}/positive_date_samples.txt"
        sample_file = f"{path}/pos_sample.txt"
        with open(sample_file, "r") as date_file:
            for line in date_file:
                samples.append((line.strip(), 1.0))
        return samples

    def negative_samples(self) -> List[Tuple[str, float]]:
        path = "preprocessed_data"
        full_file = f"{path}/negative_fb_samples.txt"
        sample_file = f"{path}/neg_sample.txt"
        samples = []
        with open(sample_file, "r") as fb_file:
            for line in fb_file:
                samples.append((line.strip(), 0.0))
        return samples


if __name__ == "__main__":
    seq = DataPreprocessor()
    fb = seq.read_facebook_data()
    print(len(fb))
    with open("facebook_samples.txt", "w") as file:
        file.writelines(fb)
