from .base import BaseData, one_hot_encoder
import pandas as pd
import re


class InstallmentsPaymentsData(BaseData):
    NAME: str = 'installments_payments'
    FILENAME: str = ['installments_payments.csv']

    def __init__(self) -> None:
        super(InstallmentsPaymentsData, self).__init__()

    def aggregate_by_id(self, nan_as_category=False):
        ins = super(InstallmentsPaymentsData, self).aggregate_by_id(nan_as_category=nan_as_category)

        ins, cat_cols = one_hot_encoder(ins, nan_as_category=nan_as_category)

        # Percentage and difference paid in each installment (amount paid and installment value)
        ins['PAYMENT_PERC'] = ins['AMT_PAYMENT'] / ins['AMT_INSTALMENT']
        ins['PAYMENT_DIFF'] = ins['AMT_INSTALMENT'] - ins['AMT_PAYMENT']

        # Days past due and days before due (no negative values)
        ins['DPD'] = ins['DAYS_ENTRY_PAYMENT'] - ins['DAYS_INSTALMENT']
        ins['DBD'] = ins['DAYS_INSTALMENT'] - ins['DAYS_ENTRY_PAYMENT']
        ins['DPD'] = ins['DPD'].apply(lambda x: x if x > 0 else 0)
        ins['DBD'] = ins['DBD'].apply(lambda x: x if x > 0 else 0)

        # Features: Perform aggregations
        aggregations = {
            'NUM_INSTALMENT_VERSION': ['nunique'],
            'DPD': ['max', 'mean', 'sum'],
            'DBD': ['max', 'mean', 'sum'],
            'PAYMENT_PERC': ['max', 'mean', 'sum', 'var'],
            'PAYMENT_DIFF': ['max', 'mean', 'sum', 'var'],
            'AMT_INSTALMENT': ['max', 'mean', 'sum'],
            'AMT_PAYMENT': ['min', 'max', 'mean', 'sum'],
            'DAYS_ENTRY_PAYMENT': ['max', 'mean', 'sum']
        }
        for cat in cat_cols:
            aggregations[cat] = ['mean']
        ins_agg = ins.groupby('SK_ID_CURR').agg(aggregations)
        ins_agg.columns = pd.Index(['INSTAL_' + e[0] + "_" + e[1].upper() for e in ins_agg.columns.tolist()])

        # Count installments accounts
        ins_agg['INSTAL_COUNT'] = ins.groupby('SK_ID_CURR').size()

        # Control character in columns name
        ins_agg = ins_agg.rename(columns=lambda x: re.sub('[^A-Za-z0-9_]+', '_', x))

        self.data = ins_agg
        return self.data
