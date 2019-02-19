from pathlib import Path

from typing import List
from datetime import datetime, timedelta


class DateAugmentor(object):

    def __init__(self, begin_year: int, end_year: int, result_file: str):
        self.begin_year = begin_year
        self.end_year = end_year
        self.result_file = result_file

    def generate_date(self):
        begin = datetime(year=self.begin_year, month=1, day=1)
        end = datetime(year=self.end_year, month=1, day=1)
        step = timedelta(days=1)
        Path(self.result_file).touch(exist_ok=True)
        with open(self.result_file, "a") as file:
            while begin < end:
                formats = self.datetime_to_str(begin)
                # formats_with_noise = list(chain(*[self.add_noise(form) for form in formats]))
                file.writelines([f"{line}\n" for line in formats])
                begin += step

    def datetime_to_str(self, date: datetime) -> List[str]:
        """
        Reference: https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
        """
        days = [["%d"], ["%a", "%d"], ["%A", "%d"]]
        # output of weekdays depends on locale.getlocale()
        months = ["%b", "%B", "%m"]
        years = ["%y", "%Y"]
        clocks = [["%H", "%M", "%S"], ["%X"]]
        timezones = [["%z"], ["%z", "%Z"]]
        full_dates = [["%x"], ["%c"], ["%x", "%X"]]
        separators = [",", ";", "/", ".", " ", ":", "-", "|"]

        result_formats = []

        for date_seperator in separators:
            for day in days:
                for month in months:
                    for year in years:
                        day_format = " ".join(day)
                        separator = date_seperator
                        date_formats = [f"{year}",
                                        f"{day_format}{separator}{month}{separator}{year}",
                                        f"{month}{separator}{day_format}{separator}{year}",
                                        f"{year}{separator}{month}{separator}{day_format}",
                                        f"{year}{separator}{day_format}{separator}{month}"]
                        result_formats += date_formats
                        # we don't want the time and timezone stuff at the moment
                        # for date_format in date_formats:
                        #     for clock_separator in separators:
                        #         for clock in clocks:
                        #             clock_format = clock_separator.join(clock)
                        #             result_formats.append(f"{date_format} {clock_format}")
                        #             for timezone in timezones:
                        #                 timezone_format = " ".join(timezone)
                        #                 result_formats.append(f"{date_format} {clock_format} {timezone_format}")
        result_formats += [" ".join(date_format) for date_format in full_dates]
        return [date.strftime(date_format) for date_format in result_formats]

    def add_noise(self, date_format: str) -> List[str]:
        result = [date_format]
        noises = [
            ["(", ")"],
            ["(", ")."],
            [" ", " "]
        ]
        for prefix, suffix in noises:
            result.append(f"{prefix}{date_format}{suffix}")
        return result

    def generate_false_samples(self, date_format: str) -> List[str]:
        return [date_format]


if __name__ == "__main__":
    augmentor = DateAugmentor(begin_year=1900, end_year=2100, result_file="dates")
    augmentor.generate_date()
