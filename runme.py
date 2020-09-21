import json
from datetime import date

import numpy as np
import pandas as pd
import traceback
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
import xgboost as xgb
from sklearn.model_selection import KFold, cross_val_score, train_test_split
from functools import reduce
#do not show warnings
import warnings
warnings.filterwarnings("ignore")


def compute_med_price(series):
    try:
        return np.median([p["price"] for p in reduce(lambda x, y: x+y, series)])
    except Exception as ex:
        print("exception", ex)
        traceback.print_exc()
        return 0

# # un-use
# def compute_max_price(series):
#     try:
#         return np.median([p["price"] for p in reduce(lambda x, y: x+y, series)])
#     except Exception as ex:
#         print("exception", ex)
#         traceback.print_exc()
#         return 0


def analyze_data(
        train_start_date=date(2018, 2, 1),
        train_finish_date=date(2018, 3, 31),
        test_start_date=date(2018, 4, 1),
        test_finish_date=date(2018, 4, 30)
):
    tx_data = pd.read_csv('/Users/lap01203/PycharmProjects/vinid/data/VinIDRecruitChallenge_MLTrack_DataSet.csv')
    tx_data['date'] = pd.to_datetime(tx_data['date'])
    tx_2m = tx_data[(tx_data.date >= train_start_date) & (tx_data.date <= train_finish_date)].reset_index(drop=True)
    tx_next = tx_data[(tx_data.date >= test_start_date) & (tx_data.date <= test_finish_date)].reset_index(drop=True)

    revenue_func = {'revenue': lambda r: [product["salesquantity"] * product["price"] for product in r][0]}
    tx_2m["raw"] = tx_2m["transaction_info"].str.replace("'", '"').apply(json.loads).reset_index(drop=True)
    tx_2m["revenue"] = tx_2m["transaction_info"].str.replace("'", '"').apply(json.loads) \
        .apply(revenue_func).reset_index(drop=True)
    tx_user = tx_2m.groupby("csn").agg({
        "revenue": ["sum", "median", "count"],
        "raw": [compute_med_price]
    }).reset_index()

    # create a dataframe with customer id and last purchase date in tx_2m
    tx_last_purchase = tx_2m.groupby('csn').date.max().reset_index()
    tx_last_purchase.columns = ['csn', 'MaxPurchaseDate']

    # create a dataframe with customer id and first purchase date in tx_next
    tx_next_first_purchase = tx_next.groupby('csn').date.min().reset_index()
    tx_next_first_purchase.columns = ['csn', 'MinPurchaseDate']
    # merge two dataframes
    tx_purchase_dates = pd.merge(tx_last_purchase, tx_next_first_purchase, on='csn', how='left')
    # calculate the time difference in days:
    tx_purchase_dates['NextPurchaseDay'] = (
            tx_purchase_dates['MinPurchaseDate'] - tx_purchase_dates['MaxPurchaseDate']).dt.days
    # calculate the time difference from end month:
    tx_purchase_dates['Diff_end'] = (train_finish_date - tx_purchase_dates['MaxPurchaseDate'].dt.date).dt.days

    tx_user = pd.merge(tx_user, tx_purchase_dates, on='csn', how='left')

    # fill NA values with 999
    tx_user = tx_user.fillna(999)
    class_funcs = {'class': lambda r: 1 if r < 100 else 0}
    tx_user["cate"] = tx_user["NextPurchaseDay"].apply(class_funcs).reset_index(drop=True)

    x, y = tx_user.drop(['cate', 'NextPurchaseDay', "MaxPurchaseDate", "MinPurchaseDate", ('csn', ''), "csn"],
                        axis=1), tx_user.cate

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=123)
    for e in x_train:
        print("field:", e)
    models = [
        ("LR", LogisticRegression(penalty="l2")),
        ("RF", RandomForestClassifier()),
        ("SVC", SVC()),
        ("Dtree", DecisionTreeClassifier()),
        ("XGB", xgb.XGBClassifier()),
        ("KNN", KNeighborsClassifier())]
    # models.append(("NB", GaussianNB()))
    # measure the accuracy
    result = []
    for name, model in models:
        kfold = KFold(n_splits=5, random_state=1234)
        cv_result = cross_val_score(model, x_train, y_train, cv=kfold, scoring="accuracy")
        tmp = np.average(cv_result)
        print(name, tmp)
        result.append(tmp)
    for r in result:
        print(r)


if __name__ == '__main__':
    # analyze_data()
    analyze_data(
        train_start_date=date(2018, 3, 1),
        train_finish_date=date(2018, 4, 30),
        test_start_date=date(2018, 5, 1),
        test_finish_date=date(2018, 5, 31)
    )
