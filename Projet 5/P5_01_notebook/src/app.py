import numpy as np
import pandas as pd
from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from unidecode import unidecode

import model

DATABASE_URL = 'sqlite:///../db/olist.db'


def init_db(uri):
    engine = create_engine(uri)
    db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
    model.Base.query = db_session.query_property()
    model.Base.metadata.drop_all(bind=engine)
    model.Base.metadata.create_all(bind=engine)
    return db_session


def insert_geolocation(session):
    try:
        data = pd.read_csv("../data/olist_geolocation_dataset_lite.csv", sep=',', header=0, parse_dates=True)
        data['geolocation_city'] = data['geolocation_city'].apply(lambda x: unidecode(str(x).lower()))
        data['geolocation_state'] = data['geolocation_state'].apply(lambda x: unidecode(str(x).lower()))
        data.drop_duplicates(inplace=True)
        for row_dict in data.replace({np.nan: None}).to_dict(orient="records"):
            record = model.Geolocation(**row_dict)
            session.add(record)
        session.commit()
    except Exception as error:
        logger.exception(error)
        session.rollback()
        return
    logger.info('[geolocation] OK')


def insert_customers(session):
    try:
        data = pd.read_csv("../data/olist_customers_dataset_lite.csv", sep=',', header=0)
        data.drop_duplicates(inplace=True)
        for row_dict in data.replace({np.nan: None}).to_dict(orient="records"):
            record = model.Customers(**row_dict)
            session.add(record)
        session.commit()
    except Exception as error:
        logger.exception(error)
        session.rollback()
        return
    logger.info('[customers] OK')


def insert_sellers(session):
    try:
        data = pd.read_csv("../data/olist_sellers_dataset_lite.csv", sep=',', header=0)
        for row_dict in data.replace({np.nan: None}).to_dict(orient="records"):
            record = model.Sellers(**row_dict)
            session.add(record)
        session.commit()
    except Exception as error:
        logger.exception(error)
        session.rollback()
        return
    logger.info('[sellers] OK')


def insert_orders(session):
    try:
        data = pd.read_csv("../data/olist_orders_dataset_lite.csv", sep=',', header=0,
                           parse_dates=['order_purchase_timestamp',
                                        'order_approved_at',
                                        'order_delivered_carrier_date',
                                        'order_delivered_customer_date',
                                        'order_estimated_delivery_date'
                                        ])
        for row_dict in data.replace({np.nan: None}).to_dict(orient="records"):
            record = model.Orders(**row_dict)
            session.add(record)
        session.commit()
    except Exception as error:
        logger.exception(error)
        session.rollback()
        return
    logger.info('[orders] OK')


def insert_reviews(session):
    try:
        data = pd.read_csv("../data/olist_order_reviews_dataset_update.csv", sep=',', header=0,
                           parse_dates=['review_creation_date', 'review_answer_timestamp'])
        for row_dict in data.replace({np.nan: None}).to_dict(orient="records"):
            record = model.OrderReviews(**row_dict)
            session.add(record)
        session.commit()
    except Exception as error:
        logger.exception(error)
        session.rollback()
        return
    logger.info('[reviews] OK')


def insert_items(session):
    try:
        data = pd.read_csv("../data/olist_order_items_dataset.csv", sep=',', header=0,
                           parse_dates=['shipping_limit_date'])
        for row_dict in data.replace({np.nan: None}).to_dict(orient="records"):
            record = model.OrderItems(**row_dict)
            session.add(record)
        session.commit()
    except Exception as error:
        logger.exception(error)
        session.rollback()
        return
    logger.info('[items] OK')


def insert_payments(session):
    try:
        data = pd.read_csv("../data/olist_order_payments_dataset.csv", sep=',', header=0)
        for row_dict in data.replace({np.nan: None}).to_dict(orient="records"):
            record = model.OrderPayments(**row_dict)
            session.add(record)
        session.commit()
    except Exception as error:
        logger.exception(error)
        session.rollback()
        return
    logger.info('[payments] OK')


def insert_products(session):
    try:
        data = pd.read_csv("../data/olist_products_dataset.csv", sep=',', header=0)
        for row_dict in data.replace({np.nan: None}).to_dict(orient="records"):
            record = model.Products(**row_dict)
            session.add(record)
        session.commit()
    except Exception as error:
        logger.exception(error)
        session.rollback()
        return
    logger.info('[products] OK')


def main():
    session = init_db(DATABASE_URL)
    insert_geolocation(session)
    insert_customers(session)
    insert_sellers(session)
    insert_orders(session)
    insert_reviews(session)
    insert_items(session)
    insert_payments(session)
    insert_products(session)


if __name__ == "__main__":
    main()
