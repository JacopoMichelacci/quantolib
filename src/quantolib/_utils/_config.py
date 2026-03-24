# file to keep states shared and keep code extensible

SUPPORTED_PROVIDERS = ("yf", "wrds")
SUPPORTED_CACHE_FORMATS = ("parquet", "csv")





ALIAS_PANDAS_TF = {
    "w": "W", "weeks" : "W",

    "d": "D", "day": "D", "days": "D",

    "h": "h", "hr": "h", "hour": "h", "hours": "h",

    "m": "min", "min": "min", "minute": "min", "minutes": "min",

    "s": "s", "sec": "s", "second": "s", "seconds": "s",

    "ms": "ms", "milli": "ms", "millis": "ms",
    "millisecond": "ms", "milliseconds": "ms",

    "us": "us", "micro": "us", "micros": "us",
    "microsecond": "us", "microseconds": "us",

    "ns": "ns", "nano": "ns", "nanos": "ns",
    "nanosecond": "ns", "nanoseconds": "ns",
}