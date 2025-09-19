from sqlalchemy import Column, Integer, String, JSON, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship, mapped_column, Mapped
from datetime import datetime
from typing import Optional

from bot.database.db import Base

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(unique=True)
    name: Mapped[Optional[str]]
    phone: Mapped[Optional[str]]
    address: Mapped[Optional[str]]
    
    carts: Mapped["Carts"] = relationship(back_populates='user', uselist=False)
    order: Mapped["Order"] = relationship(back_populates='user', uselist=False)
    
class Carts(Base):
    __tablename__ = 'carts'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    
    cart_item: Mapped[list["CartItems"]] = relationship(back_populates="cart", uselist=True)
    user: Mapped["User"] = relationship(back_populates='carts', uselist=False)
    
class CartItems(Base):
    __tablename__ = "cart_items"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    cart_id: Mapped[int] = mapped_column(ForeignKey("carts.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int]
    
    product: Mapped["Products"] = relationship(back_populates="cart_item", uselist=False)
    cart: Mapped["Carts"] = relationship(back_populates="cart_item", uselist=False)

class Products(Base):
    __tablename__ = "products"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("category.id"))
    name: Mapped[str]
    description: Mapped[str]
    price: Mapped[float]
    photo_url: Mapped[str]
    
    cart_item: Mapped[list["CartItems"]] = relationship(back_populates="product", uselist=True)
    category: Mapped["Category"] = relationship(back_populates="product", uselist=False)
    order_item: Mapped[list["OredrItem"]] = relationship(back_populates="product", uselist=True)
    
class Category(Base):
    __tablename__ = "category"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    
    product: Mapped[list["Products"]] = relationship(back_populates="category", uselist=True)
    
    
class Order(Base):
    __tablename__ = "order"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    uid: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    delivery_method: Mapped[str]
    status: Mapped[str]
    total_price: Mapped[float]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    order_item: Mapped[list["OredrItem"]] = relationship(back_populates="order", uselist=True)
    user: Mapped["User"] = relationship(back_populates="order", uselist=False)
    
class OredrItem(Base):
    __tablename__ = "order_item"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("order.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int]
    price: Mapped[float]
    
    order: Mapped["Order"] = relationship(back_populates="order_item", uselist=False)
    product: Mapped["Products"] = relationship(back_populates="order_item", uselist=False)