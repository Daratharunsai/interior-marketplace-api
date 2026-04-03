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
