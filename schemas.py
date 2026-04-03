from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str = "user"

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: str
    is_active: bool

    class Config:
        from_attributes = True

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