import pandas as pd
import polars as pl
import numpy as np


class OCContainer1D:
    """
    Ordered Contiguous Container Class.

    Transforms common containers into standard ones.
    """

    def __init__(self, data):
        if data is None:
            raise ValueError("ERROR(quantolib): data passed cannot be None")

        if np.isscalar(data):
            raise ValueError("ERROR(quantolib): scalar data passed, expected 1D container")

        if not isinstance(data, (list, tuple, range, pl.DataFrame, pd.DataFrame, pl.Series, pd.Series, pd.Index, np.ndarray)):
            raise ValueError("ERROR(quantolib): data passed not in handled types")

        self.data = self.normalize_1d(data)

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)

    def __repr__(self):
        return f"OCContainer1D(len={len(self.data)}, dtype={self.data.dtype})"

    # turn data into 1d array
    @staticmethod
    def normalize_1d(data) -> np.ndarray:
        """
        This function turns most common ordered contiguous containers into a 1D numpy array.

        data types handled:
            - pd/pl DataFrame (must be 1 column) and Series
            - pd.Index / pd.DatetimeIndex
            - python list, tuple, range
            - numpy arrays
        """
        if data is None:
            raise ValueError("ERROR(quantolib): data passed cannot be None")

        if np.isscalar(data):
            raise ValueError("ERROR(quantolib): scalar data passed, expected 1D container")

        if isinstance(data, pl.DataFrame):
            if data.width != 1:
                raise ValueError(f"ERROR(quantolib): Polars DataFrame must have 1 column, got {data.width}. Columns: {data.columns}")
            data = data.to_series(0)

        elif isinstance(data, pd.DataFrame):
            if data.shape[1] != 1:
                raise ValueError(f"ERROR(quantolib): Pandas DataFrame must have 1 column, got {data.shape[1]}. Columns: {list(data.columns)}")
            data = data.iloc[:, 0]

        if isinstance(data, pl.Series):
            arr = data.to_numpy()
        elif isinstance(data, (pd.Series, pd.Index)):
            arr = data.to_numpy()
        else:
            arr = np.asarray(data)

        if arr.ndim != 1:
            raise ValueError(f"ERROR(quantolib): expected 1D data, got ndim={arr.ndim}")

        return arr

    # functions to turn data into standard types
    def to_numpy(self):
        return self.data.copy()

    def to_list(self):
        return self.data.tolist()

    def to_pandas(self):
        return pd.Series(self.data)

    def to_polars(self):
        return pl.Series(self.data)