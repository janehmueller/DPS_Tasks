from typing import List, Dict

import numpy as np


class Tokenizer(object):

    def __init__(self):
        self.char_dict: Dict[str, int] = {"oov": 0}
        offset = len(self.char_dict)
        for index, char_index in enumerate(range(32, 127)):
            self.char_dict[chr(char_index)] = index + offset
        self.index = len(self.char_dict)

    def fit(self, dates: List[str]):
        for date in dates:
            for char in date:
                if char not in self.char_dict:
                    self.char_dict[char] = self.index
                    self.index += 1

    def vocab_size(self) -> int:
        return len(self.char_dict)

    @property
    def oov_index(self) -> int:
        return 0

    def tokenize(self, date: str):
        return np.array([self.char_dict.get(char, self.oov_index) for char in date])
