from sqlalchemy import Column, String, Numeric, DateTime, Integer, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Customers(Base):
    __tablename__ = 'customers'

    # customer_id = Column(String, primary_key=True, nullable=False)
    customer_unique_id = Column(String, primary_key=True)
    customer_zip_code_prefix = Column(ForeignKey('geolocation.geolocation_zip_code_prefix'), nullable=False)
    # customer_city = Column(String, nullable=False)
    # customer_state = Column(String, nullable=False)


class Geolocation(Base):
    __tablename__ = 'geolocation'

    geolocation_zip_code_prefix = Column(String, primary_key=True)
    # geolocation_lat = Column(Numeric, nullable=False)
    # geolocation_lng = Column(Numeric, nullable=False)
    geolocation_city = Column(String, nullable=False)
    geolocation_state = Column(String, nullable=False)


class OrderItems(Base):
    __tablename__ = 'order_items'

    order_item_id = Column(String, primary_key=True)
    order_id = Column(ForeignKey('orders.order_id'), primary_key=True)
    product_id = Column(ForeignKey('products.product_id'), nullable=False)
    seller_id = Column(ForeignKey('sellers.seller_id'), nullable=False)
    shipping_limit_date = Column(DateTime, nullable=False)
    price = Column(Numeric, nullable=False)
    freight_value = Column(Numeric, nullable=False)


class OrderReviews(Base):
    __tablename__ = 'order_reviews'

    review_id = Column(String, primary_key=True)
    order_id = Column(ForeignKey('orders.order_id'), primary_key=True)
    review_score = Column(Integer, nullable=False)
    review_comment_title = Column(String, nullable=True)
    review_comment_message = Column(String, nullable=True)
    review_creation_date = Column(DateTime, nullable=False)
    review_answer_timestamp = Column(DateTime, nullable=False)


class Orders(Base):
    __tablename__ = 'orders'

    order_id = Column(String, primary_key=True)
    # customer_id = Column(ForeignKey('customers.customer_id'), nullable=False)
    customer_unique_id = Column(ForeignKey('customers.customer_unique_id'), nullable=False)
    order_status = Column(String, nullable=False)
    order_purchase_timestamp = Column(DateTime, nullable=False)
    order_approved_at = Column(DateTime, nullable=True)
    order_delivered_carrier_date = Column(DateTime, nullable=True)
    order_delivered_customer_date = Column(DateTime, nullable=True)
    order_estimated_delivery_date = Column(DateTime, nullable=True)


class OrderPayments(Base):
    __tablename__ = 'order_payments'

    order_id = Column(ForeignKey('orders.order_id'), primary_key=True)
    payment_sequential = Column(Integer, primary_key=True)
    payment_type = Column(String, nullable=False)
    payment_installments = Column(Integer, nullable=False)
    payment_value = Column(Numeric, nullable=False)


class Products(Base):
    __tablename__ = 'products'

    product_id = Column(String, primary_key=True)
    product_category_name = Column(String, nullable=True)
    product_name_lenght = Column(Integer, nullable=True)
    product_description_lenght = Column(Integer, nullable=True)
    product_photos_qty = Column(Integer, nullable=True)
    product_weight_g = Column(Integer, nullable=True)
    product_length_cm = Column(Integer, nullable=True)
    product_height_cm = Column(Integer, nullable=True)
    product_width_cm = Column(Integer, nullable=True)


class Sellers(Base):
    __tablename__ = 'sellers'

    seller_id = Column(String, primary_key=True)
    seller_zip_code_prefix = Column(ForeignKey('geolocation.geolocation_zip_code_prefix'), nullable=False)
    # seller_city = Column(String, nullable=False)
    # seller_state = Column(String, nullable=False)
