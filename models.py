from sqlalchemy import Column, Integer, String, Boolean, DateTime, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from .db import Base
import datetime

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, default='customer')
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    weight_gram = Column(DECIMAL(10,3), nullable=False)
    cost_per_gram = Column(DECIMAL(12,2), nullable=False, default=0)
    profit_percent = Column(DECIMAL(5,2), nullable=False, default=10)
    is_available = Column(Boolean, default=True)
    is_future_item = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class ProductImage(Base):
    __tablename__ = 'product_images'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    url = Column(String)
    is_primary = Column(Boolean, default=False)

class Inventory(Base):
    __tablename__ = 'inventory'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer, default=0)

class GoldRate(Base):
    __tablename__ = 'gold_rates'
    id = Column(Integer, primary_key=True)
    rate_per_gram = Column(DECIMAL(12,2), nullable=False)
    source = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    total_amount = Column(DECIMAL(12,2), nullable=False)
    total_weight = Column(DECIMAL(12,3), nullable=False)
    payment_method = Column(String)
    status = Column(String, default='pending')
    gold_rate_per_gram = Column(DECIMAL(12,2), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class OrderItem(Base):
    __tablename__ = 'order_items'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    unit_price = Column(DECIMAL(12,2), nullable=False)
    profit_percent = Column(DECIMAL(5,2), nullable=False)
    quantity = Column(Integer, nullable=False)
    subtotal = Column(DECIMAL(12,2), nullable=False)
    product_snapshot_name = Column(String)
    product_snapshot_weight = Column(DECIMAL(10,3))
