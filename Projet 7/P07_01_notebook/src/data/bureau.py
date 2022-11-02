from .base import BaseData, one_hot_encoder
import pandas as pd
import re


class BureauData(BaseData):
    NAME: str = 'bureau'
    FILENAME: str = ['bureau.csv']

    def __init__(self) -> None:
        super(BureauData, self).__init__()
        self.bureau_balance_data = BureauBalanceData()

    def load(self, path: str = None) -> pd.DataFrame:
        self.bureau_balance_data.load()
        super(BureauData, self).load(path=path)
        return self.raw_data

    def aggregate_by_id(self, nan_as_category=False):
        bureau = super(BureauData, self).aggregate_by_id(nan_as_category=nan_as_category)
        bb_agg = self.bureau_balance_data.aggregate_by_id(nan_as_category=nan_as_category)

        bureau, bureau_cat = one_hot_encoder(bureau, nan_as_category)

        bureau = bureau.join(bb_agg, how='left', on='SK_ID_BUREAU')
        bureau.drop(['SK_ID_BUREAU'], axis=1, inplace=True)

        # Bureau and bureau_balance numeric features
        num_aggregations = {
            'DAYS_CREDIT': ['min', 'max', 'mean', 'var'],
            'DAYS_CREDIT_ENDDATE': ['min', 'max', 'mean'],
            'DAYS_CREDIT_UPDATE': ['mean'],
            'CREDIT_DAY_OVERDUE': ['max', 'mean'],
            'AMT_CREDIT_MAX_OVERDUE': ['mean'],
            'AMT_CREDIT_SUM': ['max', 'mean', 'sum'],
            'AMT_CREDIT_SUM_DEBT': ['max', 'mean', 'sum'],
            'AMT_CREDIT_SUM_OVERDUE': ['mean'],
            'AMT_CREDIT_SUM_LIMIT': ['mean', 'sum'],
            'AMT_ANNUITY': ['max', 'mean'],
            'CNT_CREDIT_PROLONG': ['sum'],
            'MONTHS_BALANCE_MIN': ['min'],
            'MONTHS_BALANCE_MAX': ['max'],
            'MONTHS_BALANCE_SIZE': ['mean', 'sum']
        }

        # Bureau and bureau_balance categorical features
        cat_aggregations = {}
        for cat in bureau_cat:
            cat_aggregations[cat] = ['mean']
        bb_stat = [c for c in bb_agg.columns.tolist() if c.endswith('_MEAN')]
        for cat in bb_stat:
            cat_aggregations[cat] = ['mean']

        bureau_agg = bureau.groupby('SK_ID_CURR').agg({**num_aggregations, **cat_aggregations})
        bureau_agg.columns = pd.Index(['BURO_' + e[0] + "_" + e[1].upper() for e in bureau_agg.columns.tolist()])

        # Bureau: Active credits - using only numerical aggregations
        active = bureau[bureau['CREDIT_ACTIVE_Active'] == 1]
        active_agg = active.groupby('SK_ID_CURR').agg(num_aggregations)
        active_agg.columns = pd.Index(['ACTIVE_' + e[0] + "_" + e[1].upper() for e in active_agg.columns.tolist()])
        bureau_agg = bureau_agg.join(active_agg, how='left', on='SK_ID_CURR')

        # Bureau: Closed credits - using only numerical aggregations
        closed = bureau[bureau['CREDIT_ACTIVE_Closed'] == 1]
        closed_agg = closed.groupby('SK_ID_CURR').agg(num_aggregations)
        closed_agg.columns = pd.Index(['CLOSED_' + e[0] + "_" + e[1].upper() for e in closed_agg.columns.tolist()])
        bureau_agg = bureau_agg.join(closed_agg, how='left', on='SK_ID_CURR')

        # Control character in columns name
        bureau_agg = bureau_agg.rename(columns=lambda x: re.sub('[^A-Za-z0-9_]+', '_', x))

        self.data = bureau_agg
        return self.data


class BureauBalanceData(BaseData):
    NAME: str = 'bureau_balance'
    FILENAME: str = ['bureau_balance.csv']

    def __init__(self) -> None:
        super(BureauBalanceData, self).__init__()

    def aggregate_by_id(self, nan_as_category):
        bb = super(BureauBalanceData, self).aggregate_by_id(nan_as_category=nan_as_category)

        bb, bb_cat = one_hot_encoder(bb, nan_as_category)

        # Bureau balance: Perform aggregations and merge with bureau.csv
        bb_aggregations = {'MONTHS_BALANCE': ['min', 'max', 'size']}
        for col in bb_cat:
            bb_aggregations[col] = ['mean']
        bb_agg = bb.groupby('SK_ID_BUREAU').agg(bb_aggregations)
        bb_agg.columns = pd.Index([e[0] + "_" + e[1].upper() for e in bb_agg.columns.tolist()])

        # Control character in columns name
        bb_agg = bb_agg.rename(columns=lambda x: re.sub('[^A-Za-z0-9_]+', '_', x))

        self.data = bb_agg
        return self.data
