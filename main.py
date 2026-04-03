from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from jose import jwt, JWTError

import models
import schemas
import security
from database import engine, get_db

# Create tables if they don't exist
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Interior Marketplace API")

# 1. Define the allowed origins (Your Vercel Link + Localhost)
origins = [
    "https://my-frontend-ivory-theta.vercel.app",
    "http://localhost:3000",
]

# 2. Add the middleware to the FastAPI app instance
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,           # Allows your specific sites
    allow_credentials=True,
    allow_methods=["*"],              # Allows GET, POST, etc.
    allow_headers=["*"],              # Allows all headers
)

# Tell FastAPI where the wristbands are handed out
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@app.get("/")
def health_check():
    return {"status": "online", "message": "API is running."}

@app.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pwd = security.get_password_hash(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed_pwd, role=user.role)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = security.create_access_token(data={"sub": str(user.id), "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}

# Tell FastAPI where the wristbands are handed out
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# THE BOUNCER FUNCTION
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode the wristband to read the data inside
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    # Look up the user in the database to make sure they still exist
    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
        
    return user

# --- NEW PROTECTED ROUTE ---
@app.get("/users/me", response_model=schemas.UserResponse)
def get_my_profile(current_user: models.User = Depends(get_current_user)):
    # Notice we don't have to search the database here! 
    # The Bouncer (get_current_user) already did the hard work.
    return current_user

# --- NEW: Add a Product ---
@app.post("/products", response_model=schemas.ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product: schemas.ProductCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    # 1. Check if they have permission
    if current_user.role != "vendor":
        raise HTTPException(status_code=403, detail="Only vendors can add products.")
        
    # 2. Check if they have actually opened a shop yet
    vendor_profile = db.query(models.Vendor).filter(models.Vendor.user_id == current_user.id).first()
    if not vendor_profile:
        raise HTTPException(status_code=400, detail="You must create a vendor profile before adding products.")
        
    # 3. Create the product and link it to their shop ID
    new_product = models.Product(
        name=product.name,
        description=product.description,
        price=product.price,
        vendor_id=vendor_profile.id
    )
    
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    return new_product

# --- NEW: Create Vendor Profile ---
@app.post("/vendors/profile", response_model=schemas.VendorResponse, status_code=status.HTTP_201_CREATED)
def create_vendor_profile(
    vendor: schemas.VendorCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user) # <-- The Bouncer!
):
    # 1. Check if the user is actually a vendor
    if current_user.role != "vendor":
        raise HTTPException(status_code=403, detail="Only vendors can create a shop profile.")
    
    # 2. Check if they already have a shop profile
    existing_profile = db.query(models.Vendor).filter(models.Vendor.user_id == current_user.id).first()
    if existing_profile:
        raise HTTPException(status_code=400, detail="You already have a vendor profile.")
        
    # 3. Create the new shop
    new_vendor = models.Vendor(
        business_name=vendor.business_name,
        description=vendor.description,
        user_id=current_user.id
    )
    
    db.add(new_vendor)
    db.commit()
    db.refresh(new_vendor)
    
    return new_vendor

# --- NEW: Public Storefront (View All Products) ---
@app.get("/products", response_model=list[schemas.ProductResponse])
def get_all_products(db: Session = Depends(get_db)):
    # Fetch every single product from the database
    products = db.query(models.Product).all()
    return products