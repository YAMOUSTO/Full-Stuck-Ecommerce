# ~/ecommerce-platform/models.py
from sqlalchemy import Column, Integer, String, Float, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import database

class Category(database.Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    slug = Column(String(255), unique=True, index=True, nullable=True) 

    # This relationship is correct: A Category has many Products.
    products = relationship("Product", back_populates="category")


class User(database.Base):
    __tablename__ = "users"
   
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    role = Column(String(50), default='customer', nullable=False) 

    # This relationship is correct: A User (vendor) has many Products.
    products = relationship("Product", back_populates="owner")
    # You can add a relationship to orders as well if needed
    # orders = relationship("Order", back_populates="user")


class Product(database.Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), index=True, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    image_url = Column(String(255), nullable=True)
    
    # Foreign Keys
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True) 
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships - These link the above foreign keys to the actual model objects
    category = relationship("Category", back_populates="products")
    owner = relationship("User", back_populates="products") # <-- ADD THIS MISSING RELATIONSHIP


class Order(database.Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    total_price = Column(Float, nullable=False)
    
    shipping_address_line1 = Column(String(255), nullable=False)
    shipping_city = Column(String(100), nullable=False)
    shipping_postal_code = Column(String(20), nullable=False)
    shipping_country = Column(String(100), nullable=False)

    status = Column(String(50), default="pending", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    items = relationship("OrderItem", back_populates="order")
    user = relationship("User") # To access user from an order, e.g., my_order.user


class OrderItem(database.Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price_at_time_of_purchase = Column(Float, nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product")