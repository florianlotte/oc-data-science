import os
import pandas as pd
from sqlalchemy import create_engine


# One-hot encoding for categorical columns with get_dummies
def one_hot_encoder(df, nan_as_category = True):
    original_columns = list(df.columns)
    categorical_columns = [col for col in df.columns if df[col].dtype == 'object']
    df = pd.get_dummies(df, columns= categorical_columns, dummy_na= nan_as_category)
    new_columns = [c for c in df.columns if c not in original_columns]
    return df, new_columns


class BaseData:
    NAME: str = None
    PATH: str = './data/tables/'
    FILENAME: list[str] = None

    def __init__(self) -> None:
        self.raw_data = pd.DataFrame()
        self.data = None

    def load(self, path: str = None) -> pd.DataFrame:
        _path = path or self.PATH
        assert(self.FILENAME is not None)
        for _filename in self.FILENAME:
            _fullpath = _path + _filename
            print(f'Loading {_fullpath}')
            assert(os.path.exists(_fullpath))
            _df = pd.read_csv(_fullpath)
            print(f'{_fullpath} loaded {_df.shape}')
            self.raw_data = pd.concat([self.raw_data, _df], ignore_index=True)
        return self.raw_data

    def clean(self) -> pd.DataFrame:
        print(f'Cleaning {self.NAME}')
        return self.data

    def refine(self) -> pd.DataFrame:
        print(f'Refining {self.NAME}')
        return self.data

    def aggregate_by_id(self, nan_as_category):
        print(f'Aggregate by ID {self.NAME}')
        self.data = self.raw_data.copy()
        return self.data
