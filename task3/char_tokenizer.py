import json
from typing import List, Dict

import numpy as np


class Tokenizer(object):
    vocab_file: str = "vocab.json"

    def __init__(self, char_dict: Dict[str, int] = None):
        if not char_dict:
            self.char_dict: Dict[str, int] = {"oov": 0}
            offset = len(self.char_dict)
            for index, char_index in enumerate(range(32, 127)):
                self.char_dict[chr(char_index)] = index + offset
        else:
            self.char_dict = char_dict
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

    def save_vocab(self):
        with open(self.vocab_file, "w") as file:
            json.dump(self.char_dict, file)

    @classmethod
    def from_vocab(cls, file_name: str = None) -> 'Tokenizer':
        file_name = file_name or cls.vocab_file
        with open(file_name, "r") as file:
            char_dict = json.load(file)
            return cls(char_dict)

    def tokenize(self, date: str):
        return np.array([self.char_dict.get(char, self.oov_index) for char in date])
