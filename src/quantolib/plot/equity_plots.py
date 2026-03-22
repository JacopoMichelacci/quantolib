import matplotlib.pyplot as plt
import polars as pl
import pandas as pd
import numpy as np

import quantolib as ql


def plot_equity_over_time(
    date_serie,
    equity_serie_dict,
    title: str = "",
    figsize: tuple = (7, 4),
    xlabel: str = "date",
    x_rotation: int = 0,
    ylabel: str = "equity",
    xy_ticksize: int = 8,
    lineweight: float = 0.6
):
    """
    This function should be used for equity plots over time.

    equity_serie_dict --> {"equity_name": equity_series, ...} or single series
    (will be matched to ylabel as key of dict)
    """

    # ---- dates ----
    date_serie = ql.OCContainer1D(date_serie).to_numpy()

    # ---- equity input ----
    # if single series-like, transform into dict
    if isinstance(equity_serie_dict, (pl.DataFrame, pd.DataFrame, pl.Series, pd.Series, list, tuple, np.ndarray)):
        equity_serie_dict = {f"{ylabel}": equity_serie_dict}

    # if still not dict, crash
    if not isinstance(equity_serie_dict, dict):
        raise ValueError("ERROR(quantolib): equity series passed not in handled types")

    # transform each equity serie into a numpy array
    final_dict = {}
    for label, v in equity_serie_dict.items():
        final_dict[label] = ql.OCContainer1D(v).to_numpy()

    # ---- warning check lengths ----
    n_dates = len(date_serie)
    for label, v in final_dict.items():
        if len(v) != n_dates:
            print(f"warning(quantolib): length mismatch between dates ({n_dates}) and '{label}' ({len(v)})")

    # ---- plot ----
    plt.figure(figsize=figsize)
    for label, equity in final_dict.items():
        plt.plot(date_serie, equity, label=label, lw=lineweight)

    plt.title(title)
    plt.xlabel(xlabel)
    plt.tick_params(axis="x", labelsize=xy_ticksize)
    plt.tick_params(axis="x", labelrotation=x_rotation)
    plt.ylabel(ylabel)
    plt.tick_params(axis="y", labelsize=xy_ticksize)

    plt.legend()
    plt.grid(alpha=0.5)
    plt.tight_layout()
    plt.show()