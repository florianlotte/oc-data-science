from .base import BaseData, one_hot_encoder
import pandas as pd
import re


class PosCashBalanceData(BaseData):
    NAME: str = 'pos_cash_balance'
    FILENAME: str = ['POS_CASH_balance.csv']

    def __init__(self) -> None:
        super(PosCashBalanceData, self).__init__()

    def aggregate_by_id(self, nan_as_category=False):
        pos = super(PosCashBalanceData, self).aggregate_by_id(nan_as_category=nan_as_category)

        pos, cat_cols = one_hot_encoder(pos, nan_as_category=nan_as_category)

        # Features
        aggregations = {
            'MONTHS_BALANCE': ['max', 'mean', 'size'],
            'SK_DPD': ['max', 'mean'],
            'SK_DPD_DEF': ['max', 'mean']
        }
        for cat in cat_cols:
            aggregations[cat] = ['mean']

        pos_agg = pos.groupby('SK_ID_CURR').agg(aggregations)
        pos_agg.columns = pd.Index(['POS_' + e[0] + "_" + e[1].upper() for e in pos_agg.columns.tolist()])

        # Count pos cash accounts
        pos_agg['POS_COUNT'] = pos.groupby('SK_ID_CURR').size()

        # Control character in columns name
        pos_agg = pos_agg.rename(columns=lambda x: re.sub('[^A-Za-z0-9_]+', '_', x))

        self.data = pos_agg
        return self.data
