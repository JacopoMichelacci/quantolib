import pytest

from quantolib.utils._timeframe_utils import alias_pandas_tf, annualized_ts_parameter_scaling


def test_alias_pandas_tf_expected_mappings():
    assert alias_pandas_tf["w"] == "W"
    assert alias_pandas_tf["weeks"] == "W"

    assert alias_pandas_tf["d"] == "D"
    assert alias_pandas_tf["day"] == "D"
    assert alias_pandas_tf["days"] == "D"

    assert alias_pandas_tf["h"] == "h"
    assert alias_pandas_tf["hr"] == "h"
    assert alias_pandas_tf["hour"] == "h"
    assert alias_pandas_tf["hours"] == "h"

    assert alias_pandas_tf["m"] == "min"
    assert alias_pandas_tf["min"] == "min"
    assert alias_pandas_tf["minute"] == "min"
    assert alias_pandas_tf["minutes"] == "min"

    assert alias_pandas_tf["s"] == "s"
    assert alias_pandas_tf["sec"] == "s"
    assert alias_pandas_tf["second"] == "s"
    assert alias_pandas_tf["seconds"] == "s"

    assert alias_pandas_tf["ms"] == "ms"
    assert alias_pandas_tf["milli"] == "ms"
    assert alias_pandas_tf["millis"] == "ms"
    assert alias_pandas_tf["millisecond"] == "ms"
    assert alias_pandas_tf["milliseconds"] == "ms"

    assert alias_pandas_tf["us"] == "us"
    assert alias_pandas_tf["micro"] == "us"
    assert alias_pandas_tf["micros"] == "us"
    assert alias_pandas_tf["microsecond"] == "us"
    assert alias_pandas_tf["microseconds"] == "us"

    assert alias_pandas_tf["ns"] == "ns"
    assert alias_pandas_tf["nano"] == "ns"
    assert alias_pandas_tf["nanos"] == "ns"
    assert alias_pandas_tf["nanosecond"] == "ns"
    assert alias_pandas_tf["nanoseconds"] == "ns"


def test_annualized_ts_parameter_scaling_weekly():
    assert annualized_ts_parameter_scaling("W", 1) == 52
    assert annualized_ts_parameter_scaling("W", 2) == 26


def test_annualized_ts_parameter_scaling_daily():
    assert annualized_ts_parameter_scaling("D", 1, trade_weekends=False) == 252
    assert annualized_ts_parameter_scaling("D", 1, trade_weekends=True) == 365
    assert annualized_ts_parameter_scaling("D", 2, trade_weekends=False) == 126


def test_annualized_ts_parameter_scaling_hourly():
    assert annualized_ts_parameter_scaling("h", 1, trade_weekends=False) == 252 * 24
    assert annualized_ts_parameter_scaling("h", 2, trade_weekends=True) == (365 * 24) / 2


def test_annualized_ts_parameter_scaling_minutely():
    assert annualized_ts_parameter_scaling("min", 1, trade_weekends=False) == 252 * 24 * 60
    assert annualized_ts_parameter_scaling("min", 30, trade_weekends=True) == (365 * 24 * 60) / 30


def test_annualized_ts_parameter_scaling_seconds():
    assert annualized_ts_parameter_scaling("s", 1, trade_weekends=False) == 252 * 24 * 60 * 60


def test_annualized_ts_parameter_scaling_milliseconds():
    assert annualized_ts_parameter_scaling("ms", 1, trade_weekends=False) == 252 * 24 * 60 * 60 * 1_000


def test_annualized_ts_parameter_scaling_microseconds():
    assert annualized_ts_parameter_scaling("us", 1, trade_weekends=False) == 252 * 24 * 60 * 60 * 1_000_000


def test_annualized_ts_parameter_scaling_nanoseconds():
    assert annualized_ts_parameter_scaling("ns", 1, trade_weekends=False) == 252 * 24 * 60 * 60 * 1_000_000_000


def test_annualized_ts_parameter_scaling_unsupported_unit_raises():
    with pytest.raises(ValueError, match="ERROR\\(quantolib\\): unsupported timeframe format."):
        annualized_ts_parameter_scaling("bad_unit", 1)