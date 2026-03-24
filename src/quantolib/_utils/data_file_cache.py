import os
import polars as pl
from quantolib._utils._config import SUPPORTED_CACHE_FORMATS, SUPPORTED_PROVIDERS


def check_data_cache(abs_file_path: str) -> bool:
    """
    Check whether a cache file exists, is readable, and contains data.

    Supports quantolib cache formats defined in `SUPPORTED_CACHE_FORMATS`.

    Parameters
    ----------
    abs_file_path : str
        Absolute path of the cache file.

    Returns
    -------
    bool
        True if the file exists and has at least one row, else False.
    """
    if abs_file_path.strip() == "":
        raise ValueError("ERROR(quantolib): abs_file_path must be a non-empty string")

    if not os.path.exists(abs_file_path):
        return False

    ext = abs_file_path.rsplit(".", 1)[-1]

    if ext not in SUPPORTED_CACHE_FORMATS:
        raise ValueError("ERROR(quantolib): unsupported cache file format")

    try:
        if ext == "parquet":
            df = pl.scan_parquet(abs_file_path)
        elif ext == "csv":
            df = pl.scan_csv(abs_file_path)

        return df.limit(1).collect().height > 0

    except Exception:
        return False
    



def get_symbols_missing_cache(
    folder_path: str,
    symbol_list: list[str],
    start_date: str,
    end_date: str = "",
    silence_msg: bool=False,
) -> list[str]:
    """
    Return the list of symbols for which no valid cached data file is found.

    This function checks a folder for files following quantolib's standardized
    naming convention:

        {symbol}_{start_date}_{end_date}_{provider}.ext

    If `end_date` is not provided, the expected file name becomes:

        {symbol}_{start_date}_{provider}.ext

    A symbol is considered missing if:
        - no matching cache file is found for any supported provider / format
        - a matching cache file exists but is empty
        - a matching cache file exists but cannot be read correctly

    Parameters
    ----------
    folder_path : str
        Absolute or relative path to the folder containing cached data files.
    symbols : list[str]
        List of ticker / symbol names to check.
    start_date : str
        Start date used in the standardized file naming convention.
    end_date : str, default=""
        End date used in the standardized file naming convention.
        If left empty, the function looks for files without an end-date segment.
    silence_msg : bool, default=False
        prints when a symbol has valid cache

    Returns
    -------
    list[str]
        List of symbols for which no valid cache match was found.

    Notes
    -----
    - File validation is based on a minimal non-empty check.
    - Supported cache providers are taken from `SUPPORTED_PROVIDERS`.
    - Supported cache formats are taken from `SUPPORTED_CACHE_FORMATS`.
    - This function is useful for avoiding unnecessary redownloads when
      part of the requested universe is already cached.
    """
    if folder_path.strip() == "":
        raise ValueError("ERROR(quantolib): folder_path must be a non-empty string")
    if len(symbol_list) == 0:
        raise ValueError("ERROR(quantolib): symbols must be a non-empty list")

    missing_symbols = []

    for symbol in symbol_list:
        symbol_has_valid_cache = False

        for provider in SUPPORTED_PROVIDERS:
            for ext in SUPPORTED_CACHE_FORMATS:
                file_name = (
                    f"{symbol}_{start_date}_{provider}.{ext}"
                    if end_date == ""
                    else f"{symbol}_{start_date}_{end_date}_{provider}.{ext}"
                )

                abs_file_path = os.path.join(folder_path, file_name)

                if not os.path.exists(abs_file_path):
                    continue

                try:
                    if ext == "parquet":
                        df = pl.scan_parquet(abs_file_path)
                    elif ext == "csv":
                        df = pl.scan_csv(abs_file_path)
                    else:
                        continue

                    if df.limit(1).collect().height > 0:
                        symbol_has_valid_cache = True
                        if not silence_msg:
                            print(f"msg(quantolib): symbol - {symbol} has been "
                                  f"loaded from cache from {abs_file_path}")
                        break

                except Exception:
                    continue

            if symbol_has_valid_cache:
                break

        if not symbol_has_valid_cache:
            missing_symbols.append(symbol)

    return missing_symbols