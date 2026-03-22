alias_pandas_tf = {
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


def annualized_ts_parameter_scaling(
    ts_unit: str,
    ts_qty: int,
    trade_weekends: bool=False,
):
    """
    Compute the number of periods per year implied by a timeframe.
    Used to scale annualized parameters to the selected timeframe.

    args:
    -----
        ts_unit: str
            the string part of the timestamp string 
        ts_qty: int
            the quantity part of the timestamp string
    """
    if ts_unit == "W":
        periods_per_year = 52 / ts_qty
    elif ts_unit == "D":
        periods_per_year = (365 if trade_weekends else 252) / ts_qty
    elif ts_unit == "h":
        periods_per_year = ((365 if trade_weekends else 252) * 24) / ts_qty
    elif ts_unit == "min":
        periods_per_year = ((365 if trade_weekends else 252) * 24 * 60) / ts_qty
    elif ts_unit == "s":
        periods_per_year = ((365 if trade_weekends else 252) * 24 * 60 * 60) / ts_qty
    elif ts_unit == "ms":
        periods_per_year = ((365 if trade_weekends else 252) * 24 * 60 * 60 * 1_000) / ts_qty
    elif ts_unit == "us":
        periods_per_year = ((365 if trade_weekends else 252) * 24 * 60 * 60 * 1_000_000) / ts_qty
    elif ts_unit == "ns":
        periods_per_year = ((365 if trade_weekends else 252) * 24 * 60 * 60 * 1_000_000_000) / ts_qty
    else:
        raise ValueError("ERROR(quantolib): unsupported timeframe format.")

    return periods_per_year