import csv
import sys
from typing import Set


def read_csv(file_name: str,
             delimiter: str = ",",
             quotechar: str = '"',
             has_header: bool = True,
             columns_to_keep: Set[str] = None) -> list:
    lines = []
    csv.field_size_limit(sys.maxsize)
    with open(file_name, 'r') as soccer_file:
        data: csv.DictReader = csv.reader(soccer_file, delimiter=delimiter, quotechar=quotechar)
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


def benkekarsch():
    file = "data/materialien/BenkeKarsch.csv"
    rows = read_csv(file, delimiter=";", columns_to_keep={"firstname", "lastname"})
    result_file = "preprocessed_data/negative_bk_samples.txt"
    with open(result_file, "w") as file:
        for row in rows:
            for key, value in row.items():
                if value:
                    file.write(f"{value}\n")


def main():
    benkekarsch()


if __name__ == '__main__':
    main()
