import os
import pandas as pd
import polars as pl
import yfinance as yf
from tqdm import tqdm

from quantolib._utils.data_file_cache import get_symbols_missing_cache


def pull_ohlcv_yf(
    folder_path: str,
    tickers: list[str],
    separate: bool,
    start_date: str,
    end_date: str = "",
    timeframe: str = "1d",
    auto_adjust: bool = False,
    filename: str | None = None,
    to_csv: bool = False,
):
    """
    Pull stock data from Yahoo Finance and save it to disk.

    If separate=True:
        - one file per ticker
        - no symbol column

    If separate=False:
        - one single concatenated file
        - symbol column is added
        - filename must be provided

    Output filenames always include start_date.
    If end_date is provided, it is also included.
    """
    if folder_path.strip() == "":
        raise ValueError("ERROR(quantolib): folder_path must be a non-empty string")
    if len(tickers) == 0:
        raise ValueError("ERROR(quantolib): tickers must be a non-empty list")
    if not all(isinstance(t, str) and t.strip() != "" for t in tickers):
        raise ValueError("ERROR(quantolib): all tickers must be non-empty strings")
    if not separate and filename is None:
        raise ValueError("ERROR(quantolib): filename must be provided when separate=False")

    # creates dir and doesnt crash if directory is already there
    os.makedirs(folder_path, exist_ok=True)

    ext = "csv" if to_csv else "parquet"
    provider = "yf"

    all_dfs = []

    # keep only tickers that have no matching cache
    tickers = get_symbols_missing_cache(folder_path, tickers, start_date, end_date)

    for ticker in tqdm(tickers, desc="Pulling tickers from yfinance "):
        df = yf.download(
            tickers=ticker,
            start=start_date,
            end=end_date if end_date != "" else None,
            interval=timeframe,
            auto_adjust=auto_adjust,
            progress=False,
        )

        if df.empty:
            print(f"warning(quantolib): no data returned for ticker '{ticker}'")
            continue

        df = df.reset_index()

        # flatten multiindex columns if present
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]

        # data cleaning and standardization in polars lazy
        df = (
            pl.from_pandas(df).lazy()
            .rename({
                "Date": "date",
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
                "Volume": "volume",
            })
            .with_columns(
                pl.col("date").cast(pl.Datetime),
                pl.col("open").cast(pl.Float64),
                pl.col("high").cast(pl.Float64),
                pl.col("low").cast(pl.Float64),
                pl.col("close").cast(pl.Float64),
                pl.col("volume").cast(pl.Float64),
            )
            .filter(pl.col("volume") != 0)
            .sort("date")
        )

        if separate:
            df = df.select(["date", "open", "high", "low", "close", "volume"])

            out_name = (f"{ticker}_{start_date}_{provider}.{ext}" if end_date == "" 
                        else f"{ticker}_{start_date}_{end_date}_{provider}.{ext}")
            
            out_path = os.path.join(folder_path, out_name)

            # output files
            if to_csv:
                df.sink_csv(out_path)
            else:
                df.sink_parquet(out_path)

        else:
            # add symbol col if concatenating all tickers together
            df = (
                df.with_columns(pl.lit(ticker).alias("symbol"))
                .select(["date", "symbol", "open", "high", "low", "close", "volume"])
            )
            all_dfs.append(df)

    if not separate:
        if len(all_dfs) == 0:
            raise ValueError("ERROR(quantolib): no data was downloaded for any ticker")

        # concat all lazy dfs
        final_df = pl.concat(all_dfs, how="vertical").sort("date")

        out_name = f"{filename}_{start_date}.{ext}" if end_date == "" else f"{filename}_{start_date}_{end_date}.{ext}"
        out_path = os.path.join(folder_path, out_name)

        # output files
        if to_csv:
            final_df.sink_csv(out_path)
        else:
            final_df.sink_parquet(out_path)