from typing import List

import numpy as np
from keras.preprocessing.sequence import pad_sequences

from keras.utils import Sequence

from char_tokenizer import Tokenizer
from data_preprocessor import DataPreprocessor


class PredictionSequence(Sequence):

    def __init__(self, preprocessor: DataPreprocessor, samples: List[str] = None):
        self.batch_size = preprocessor.batch_size
        self.tokenizer: Tokenizer = preprocessor.tokenizer
        if samples:
            self.samples = samples
        else:
            self.samples = self.positive_samples() + self.negative_samples()
        self.test_data = np.asarray([self.tokenizer.tokenize(date) for date in self.samples])

    def __len__(self):
        return int(np.ceil(len(self.test_data) / float(self.batch_size)))

    def __getitem__(self, batch_index: int):
        x_batch = self.test_data[batch_index * self.batch_size:(batch_index + 1) * self.batch_size]
        x_batch = pad_sequences(x_batch, padding="post", value=0)
        return x_batch

    def vocab_size(self) -> int:
        return self.tokenizer.vocab_size()

    def positive_samples(self) -> List[str]:
        samples = []
        path = "preprocessed_data"
        full_file = f"{path}/positive_date_samples.txt"
        test_file = f"{path}/pos_sample_test.txt"
        with open(test_file, "r") as date_file:
            for line in date_file:
                samples.append(line.strip())
        return samples

    def negative_samples(self) -> List[str]:
        path = "preprocessed_data"
        full_file = f"{path}/negative_fb_samples.txt"
        test_file = f"{path}/neg_sample_test.txt"
        samples = []
        with open(test_file, "r") as fb_file:
            for line in fb_file:
                samples.append(line.strip())
        return samples
