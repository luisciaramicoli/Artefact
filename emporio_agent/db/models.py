from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    Text,
    DateTime,
    Boolean,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Category(Base):
    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, index=True)
    price_brl = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=False)
    description = Column(Text, nullable=True)
    stock_quantity = Column(Integer, default=0)
    status = Column(String(50), default="active", index=True)  # active, discontinued, out_of_stock
    specs = Column(Text, nullable=True)  # JSON string
    created_at = Column(String(50), nullable=True)

    category = relationship("Category", back_populates="products")
    promotions = relationship("Promotion", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")


class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False, index=True)
    phone = Column(String(50), nullable=False, index=True)
    email = Column(String(150), nullable=False, index=True)
    city = Column(String(100), nullable=True)

    orders = relationship("Order", back_populates="customer")


class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    order_date = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False, index=True)  # delivered, in_transit, processing, cancelled
    total_brl = Column(Float, nullable=False)
    payment_method = Column(String(50), nullable=False)
    tracking_code = Column(String(100), nullable=True, index=True)
    estimated_delivery = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)

    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False)
    quantity = Column(Integer, default=1)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")


class Promotion(Base):
    __tablename__ = "promotions"

    promotion_id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False)
    discount_percent = Column(Integer, nullable=False)
    description = Column(String(150), nullable=True)
    is_active = Column(Integer, default=0, index=True)  # 1 for active, 0 for inactive

    product = relationship("Product", back_populates="promotions")


class ConversationSession(Base):
    __tablename__ = "conversations"

    id = Column(String(64), primary_key=True)  # UUID
    title = Column(String(200), default="Nova Conversa")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    messages = relationship("ConversationMessage", back_populates="conversation", cascade="all, delete-orphan")


class ConversationMessage(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(String(64), ForeignKey("conversations.id"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # user, assistant, system, tool
    content = Column(Text, nullable=False)
    tool_calls = Column(Text, nullable=True)  # JSON string of tool calls / details if assistant
    created_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("ConversationSession", back_populates="messages")
