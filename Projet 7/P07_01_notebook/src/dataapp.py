import pandas as pd
import numpy as np

from .data import *


class App:
    def __init__(self):
        self.df = pd.DataFrame()
        self.cleaned_df = None
        self.application_data = ApplicationData()
        self.bureau_data = BureauData()
        self.credit_card_balance_data = CreditCardBalanceData()
        self.installments_payments_data = InstallmentsPaymentsData()
        self.post_cash_balance_data = PosCashBalanceData()
        self.previous_application = PreviousApplicationData()

    def load(self):
        self.application_data.load()
        self.bureau_data.load()
        self.credit_card_balance_data.load()
        self.installments_payments_data.load()
        self.post_cash_balance_data.load()
        self.previous_application.load()

    def aggregate_by_id(self):
        _df = self.application_data.aggregate_by_id()
        print("Shape après aggregation :", _df.shape)
        bureau = self.bureau_data.aggregate_by_id()
        _df = _df.join(bureau, how='left', on='SK_ID_CURR')
        print("Shape après aggregation :", _df.shape)
        prev = self.previous_application.aggregate_by_id()
        _df = _df.join(prev, how='left', on='SK_ID_CURR')
        print("Shape après aggregation :", _df.shape)
        pos = self.post_cash_balance_data.aggregate_by_id()
        _df = _df.join(pos, how='left', on='SK_ID_CURR')
        print("Shape après aggregation :", _df.shape)
        ins = self.installments_payments_data.aggregate_by_id()
        _df = _df.join(ins, how='left', on='SK_ID_CURR')
        print("Shape après aggregation :", _df.shape)
        cc = self.credit_card_balance_data.aggregate_by_id()
        _df = _df.join(cc, how='left', on='SK_ID_CURR')
        print("Shape après aggregation :", _df.shape)
        self.df = _df
        print("Shape finale :", self.df.shape)
        return self.df

    def clean(self):
        _df = self.df.copy()
        print('Clean data...')
        print ('Nombre de colonnes: {}'.format(_df.shape[1]))
        # Calcul de la proportion de données manquantes pour chaque colonne
        null_prop = _df.isnull().sum(axis=0).sum()/len(_df)/len(_df.columns)*100
        _df.isnull().sum(axis=0).sort_values()/len(_df)*100
        print("Le pourcentage moyen de valeurs manquantes est de {:.2f}%".format(null_prop))
        col_fill = _df.notnull().sum(axis=0)/len(_df)*100
        col_gte_90 = col_fill[col_fill >= 90]
        col_lt_90 = col_fill[col_fill < 90]
        col_lt_90.drop('TARGET', inplace=True)
        print("Nombre de colonnes avec un taux de remplissage minimum de {:.2f}%: {}".format(90, len(col_gte_90)))
        print("Drop empty columns")
        print("Replace infinite value by NAN")
        _df.replace([np.inf, -np.inf], np.nan, inplace=True)
        _df = _df.drop(columns=col_lt_90.index, axis=1)
        self.cleaned_df = _df
        return self.cleaned_df

    def save(self, filename, path='./data/'):
        print('Save data...')
        self.cleaned_df.to_csv(path + filename, index=False)


def main():
    app = App()
    app.load()
    app.aggregate_by_id()
    app.clean()
    return app


if __name__ == "__main__":
    main()
