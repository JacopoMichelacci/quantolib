import os
import polars as pl


def check_cache(abs_file_path: str) -> bool:
    """
    Check whether a cached data file exists and is non-empty.

    works only with .parquet and .csv formats

    Returns:
        - True  -> file exists and has at least 1 row
        - False -> file missing / empty / unreadable
    """
    if abs_file_path.strip() == "":
        raise ValueError("ERROR(quantolib): file_path must be a non-empty string")

    if not os.path.exists(abs_file_path):
        return False

    try:
        if abs_file_path.endswith(".parquet"):
            df = pl.scan_parquet(abs_file_path)
        elif abs_file_path.endswith(".csv"):
            df = pl.scan_csv(abs_file_path)
        else:
            raise ValueError("ERROR(quantolib): unsupported cache file format")
        
        return (df.limit(1).collect().height > 0)

    except Exception:
        return False