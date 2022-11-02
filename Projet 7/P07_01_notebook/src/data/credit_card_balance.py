from .base import BaseData, one_hot_encoder
import pandas as pd
import re


class CreditCardBalanceData(BaseData):
    NAME: str = 'credit_card_balance'
    FILENAME: str = ['credit_card_balance.csv']

    def __init__(self) -> None:
        super(CreditCardBalanceData, self).__init__()

    def aggregate_by_id(self, nan_as_category=False):
        cc = super(CreditCardBalanceData, self).aggregate_by_id(nan_as_category=nan_as_category)

        cc = one_hot_encoder(cc, nan_as_category=nan_as_category)[0]

        # General aggregations
        cc.drop(['SK_ID_PREV'], axis= 1, inplace = True)
        cc_agg = cc.groupby('SK_ID_CURR').agg(['min', 'max', 'mean', 'sum', 'var'])
        cc_agg.columns = pd.Index(['CC_' + e[0] + "_" + e[1].upper() for e in cc_agg.columns.tolist()])

        # Count credit card lines
        cc_agg['CC_COUNT'] = cc.groupby('SK_ID_CURR').size()

        # Control character in columns name
        cc_agg = cc_agg.rename(columns=lambda x: re.sub('[^A-Za-z0-9_]+', '_', x))

        self.data = cc_agg
        return self.data
