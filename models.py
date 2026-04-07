from sqlalchemy import Column, Integer, String, Boolean, ForeignKey , Float
from sqlalchemy.orm import relationship

from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user") 
    is_active = Column(Boolean, default=True)

    # --- NEW COLUMNS FOR PHONE AUTH ---
    phone_number = Column(String, unique=True, index=True, nullable=True)
    otp_code = Column(String, nullable=True)

    vendor_profile = relationship("Vendor", back_populates="owner", uselist=False)

class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)
    business_name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)

    owner = relationship("User", back_populates="vendor_profile")
    # --- NEW: Link the shop to its inventory ---
    products = relationship("Product", back_populates="vendor")

# --- NEW: Product Table ---
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    vendor_id = Column(Integer, ForeignKey("vendors.id"))

    vendor = relationship("Vendor", back_populates="products")

# --- NEW: Shopping Cart Table ---
class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1)

    user = relationship("User")
    product = relationship("Product")

# --- NEW: Order and OrderItem Tables ---
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(String, default="completed") # In a real app, this might start as 'pending'

    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price_at_purchase = Column(Float, nullable=False) # Snapshot the price in case the vendor changes it later!

    order = relationship("Order", back_populates="items")
    product = relationship("Product")