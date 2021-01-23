import enum


class Timespans(enum.Enum):
    minute = '1M'
    hour = '1H'
    day = '1D'
    week = '1w'
    month = '1m'
    quarter = '1q'
    year = '1y'
