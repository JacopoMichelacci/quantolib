import re
import pandas as pd
import polars as pl
import numpy as np

from quantolib._utils._timeframe_utils import alias_pandas_tf, annualized_ts_parameter_scaling


def equity_generator_gbm(
    n_periods: int,
    drift: float,
    vol: float,
    timeframe: str = "1d",
    starting_capital: float = 100_000.0,
    start_date: str | None = None,
    trade_weekends: bool = False,
    seed: int | None = None,
    out_pandas: bool = False,
):
    """
    Generate a synthetic equity curve using Geometric Brownian Motion (GBM).

    The equity series starts at `starting_capital` and evolves according to simulated
    log-returns. By default, the output is returned as a Polars DataFrame.

    Parameters
    ----------
    n_periods : int
        Number of timestamps / equity observations to generate.
    drift : float
        Annualized drift of the GBM process.
    vol : float
        Annualized volatility of the GBM process, interpreted as the standard
        deviation of returns over one year.
    timeframe : str, default="1d"
        Frequency of the generated timestamp series.

        Examples:
        - "1d"
        - "1h"
        - "30m"
        - "15min"
    starting_capital : float, default=100_000.0
        Initial equity level of the simulated series.
    start_date : str | None, default=None
        Start date of the generated timestamp series.

        - if None, defaults to today
        - must be date-only, with no intraday component
        - example: "2026-03-20"
    trade_weekends : bool, default=False
        If False, equity remains flat on weekend timestamps.
        If True, equity evolves on weekends as well.
    seed : int | None, default=None
        Random seed for reproducibility.
    out_pandas : bool, default=False
        If True, return a pandas DataFrame.
        If False, return a Polars DataFrame.

    Returns
    -------
    pl.DataFrame | pd.DataFrame
        DataFrame with:
        - "ts": timestamp column
        - "equity": simulated equity curve

    Notes
    -----
    - Drift and volatility are interpreted as annualized parameters.
    - They are scaled to the selected timeframe before simulation.
    - Equity starts exactly at `starting_capital`.
    - This is mainly useful for testing, demos, and prototyping.
    """
    if not isinstance(n_periods, int) or n_periods <= 0:
        raise ValueError("ERROR(quantolib): n_periods must be a positive integer")
    if vol < 0:
        raise ValueError("ERROR(quantolib): vol must be >= 0")
    if starting_capital <= 0:
        raise ValueError("ERROR(quantolib): starting_capital must be > 0")

    tf = timeframe.strip().lower()

    match = re.fullmatch(r"(\d+)([a-z]+)", tf)
    if match is None:
        raise ValueError(
            "ERROR(quantolib): unsupported timeframe format."
        )

    ts_qty = int(match.group(1))
    unit_raw = match.group(2)

    # sanity checks
    if unit_raw not in alias_pandas_tf:
        raise ValueError("ERROR(quantolib): unsupported timeframe format.")
    if ts_qty <= 0:
        raise ValueError("ERROR(quantolib): unsupported ts_qty, must be > 0")

    pd_unit = alias_pandas_tf[unit_raw]
    pd_freq = f"{ts_qty}{pd_unit}"

    rng = np.random.default_rng(seed)

    # --- start date ---
    if start_date is None:
        start_ts = pd.Timestamp.today().normalize()
    else:
        start_ts = pd.Timestamp(start_date)
        if start_ts != start_ts.normalize():
            raise ValueError("ERROR(quantolib): start_date must be date-only, with no intraday component")

    # --- timestamps ---
    ts = pd.date_range(start=start_ts, periods=n_periods, freq=pd_freq)

    # --- annualized parameter scaling ---
    periods_per_year = annualized_ts_parameter_scaling(pd_unit, ts_qty, trade_weekends)

    drift_step = drift / periods_per_year
    vol_step = vol / np.sqrt(periods_per_year)

    # --- GBM equity generation ---
    # log-return model: ln(S_t / S_{t-1}) ~ N((drift_step - 0.5*vol_step^2), vol_step)
    shocks = rng.normal(
        loc=(drift_step - 0.5 * vol_step**2),
        scale=vol_step,
        size=n_periods - 1,
    )

    # if weekends are not traded, overwrite equity to be flat on those days
    if not trade_weekends:
        weekend_mask = ts[1:].weekday >= 5
        shocks[weekend_mask] = 0.0

    equity = starting_capital * np.exp(np.concatenate(([0.0], np.cumsum(shocks))))

    if out_pandas:
        return pd.DataFrame({
                "ts": ts,
                "equity": equity,
            }
        )

    return pl.DataFrame({
            "ts": ts,
            "equity": equity,
        }
    )