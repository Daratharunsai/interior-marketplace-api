from typing import Optional
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: str
    password: str
    role: str = "customer"  # <-- ADD THIS LI

class UserResponse(BaseModel):
    id: int
    email: str
    role: str
    is_active: bool
    phone_number: Optional[str] = None
    address: Optional[str] = None

    class Config:
        from_attributes = True

# 2. NEW: Create a blueprint for UPDATING a profile
class UserUpdate(BaseModel):
    phone_number: Optional[str] = None
    address: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

# --- NEW: Product Schemas ---
class ProductCreate(BaseModel):
    name: str
    description: str = None
    price: float

class ProductResponse(BaseModel):
    id: int
    name: str
    description: str = None
    price: float
    vendor_id: int

    class Config:
        from_attributes = True

# --- Vendor Schemas ---
class VendorCreate(BaseModel):
    business_name: str
    description: str = None

class VendorResponse(BaseModel):
    id: int
    business_name: str
    description: str = None
    user_id: int

    class Config:
        from_attributes = True

# --- NEW: Shopping Cart Schemas ---
class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = 1

class CartItemResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int

    class Config:
        from_attributes = True

# --- NEW: Nested Cart Schema ---
class CartItemWithProduct(CartItemResponse):
    product: ProductResponse  

    class Config:
        from_attributes = True

# --- NEW: Order Schemas ---
class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    price_at_purchase: float

    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    id: int
    user_id: int
    total_amount: float
    status: str
    items: list[OrderItemResponse] = []

    class Config:
        from_attributes = True

# --- NEW: Product Update Schema ---
class ProductUpdate(BaseModel):
    name: str = None
    description: str = None
    price: float = None

# --- NEW: Phone Auth Schemas ---
class PhoneOTPRequest(BaseModel):
    phone_number: str

class PhoneOTPVerify(BaseModel):
    phone_number: str
    otp: str