from typing import List, Dict

import numpy as np


class Tokenizer(object):

    def __init__(self):
        self.char_dict: Dict[str, int] = {}
        self.index = 0

    def fit(self, dates: List[str]):
        for date in dates:
            for char in date:
                if char not in self.char_dict:
                    self.char_dict[char] = self.index
                    self.index += 1

    def vocab_size(self) -> int:
        return len(self.char_dict)

    def tokenize(self, date: str):
        return np.array([self.char_dict[char] for char in date])