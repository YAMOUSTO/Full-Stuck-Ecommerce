from sqlalchemy import Column, Integer, String, Float, Text, Boolean, ForeignKey, DateTime # Add ForeignKey
from sqlalchemy.orm import relationship # Add relationship
from datetime import datetime

import database

class Category(database.Base): # New Category model
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    slug = Column(String(255), unique=True, index=True, nullable=True) 

    products = relationship("Product", back_populates="category")


class Product(database.Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), index=True, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    image_url = Column(String(255), nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True) 
    category = relationship("Category", back_populates="products")


class User(database.Base):
    __tablename__ = "users"
    # ... (existing User model columns remain the same)
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    
class Order(database.Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Nullable if you allow guest checkouts
    total_price = Column(Float, nullable=False)
    
    # Basic shipping information
    shipping_address_line1 = Column(String(255), nullable=False)
    shipping_city = Column(String(100), nullable=False)
    shipping_postal_code = Column(String(20), nullable=False)
    shipping_country = Column(String(100), nullable=False)

    status = Column(String(50), default="pending", nullable=False) # e.g., pending, processing, shipped, delivered
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to OrderItem
    items = relationship("OrderItem", back_populates="order")
    # Relationship to User
    user = relationship("User") # Add a back_populates on User model if you want two-way relationship


class OrderItem(database.Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price_at_time_of_purchase = Column(Float, nullable=False) # Important to capture price at time of order

    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product")