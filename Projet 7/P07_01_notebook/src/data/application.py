from .base import BaseData, one_hot_encoder
import numpy as np
import pandas as pd
import re


class ApplicationData(BaseData):
    NAME: str = 'application'
    FILENAME: str = ['application_train.csv', 'application_test.csv']

    def __init__(self) -> None:
        super(ApplicationData, self).__init__()

    def aggregate_by_id(self, nan_as_category=False) -> pd.DataFrame:
        df = super(ApplicationData, self).aggregate_by_id(nan_as_category=nan_as_category)

        # Optional: Remove 4 applications with XNA CODE_GENDER (train set)
        df.drop(df[df['CODE_GENDER'] == 'XNA'].index)

        # Categorical features with Binary encode (0 or 1; two categories)
        for bin_feature in ['CODE_GENDER', 'FLAG_OWN_CAR', 'FLAG_OWN_REALTY']:
            df[bin_feature] = pd.factorize(df[bin_feature])[0]
        
        # Categorical features with One-Hot encode
        df = one_hot_encoder(df, nan_as_category)[0]

        # NaN values for DAYS_EMPLOYED: 365.243 -> nan
        df['DAYS_EMPLOYED'].replace(365243, np.nan, inplace=True)

        # Some simple new features (percentages)
        df['DAYS_EMPLOYED_PERC'] = df['DAYS_EMPLOYED'] / df['DAYS_BIRTH']
        df['INCOME_CREDIT_PERC'] = df['AMT_INCOME_TOTAL'] / df['AMT_CREDIT']
        df['INCOME_PER_PERSON'] = df['AMT_INCOME_TOTAL'] / df['CNT_FAM_MEMBERS']
        df['ANNUITY_INCOME_PERC'] = df['AMT_ANNUITY'] / df['AMT_INCOME_TOTAL']
        df['PAYMENT_RATE'] = df['AMT_ANNUITY'] / df['AMT_CREDIT']

        # Control character in columns name
        df = df.rename(columns=lambda x: re.sub('[^A-Za-z0-9_]+', '_', x))

        self.data = df
        return self.data
