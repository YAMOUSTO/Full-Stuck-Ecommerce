# main.py

# --- Imports ---
from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi import status
from pydantic import BaseModel
from typing import List, Optional
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta, datetime
import os
from sqlalchemy.orm import Session, joinedload

# <<< CHANGE 1: Import Cloudinary library
import cloudinary
import cloudinary.uploader

# Your existing local module imports
import models
import database
import auth

# --- Configuration ---

# <<< CHANGE 2: Configure Cloudinary using Environment Variables.
# We will set these in the Vercel dashboard.
cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
    secure=True
)

# --- Pydantic Schemas (No changes needed, these are perfect) ---
class UserInProduct(BaseModel):
    id: int
    full_name: Optional[str] = None
    email: str
    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    image_url: Optional[str] = None
    category_id: Optional[int] = None

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    owner: UserInProduct
    class Config:
        from_attributes = True

class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    class Config:
        from_attributes = True

class UserBase(BaseModel):
    email: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str
    role: str = 'customer'

class UserLogin(BaseModel):
    email: str
    password: str

class User(UserBase):
    id: int
    is_active: bool
    role: str
    is_admin: bool = False
    class Config:
        from_attributes = True

class UserUpdate(UserBase):
    full_name: Optional[str] = None
    password: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class OrderItemBase(BaseModel):
    product_id: int
    quantity: int

class OrderItemCreate(OrderItemBase):
    pass

class ProductInOrder(BaseModel):
    id: int
    name: str
    image_url: Optional[str] = None
    class Config:
        from_attributes = True

class OrderItem(OrderItemBase):
    id: int
    price_at_time_of_purchase: float
    product: ProductInOrder
    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    shipping_address_line1: str
    shipping_city: str
    shipping_postal_code: str
    shipping_country: str

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

class Order(OrderBase):
    id: int
    user_id: Optional[int] = None
    total_price: float
    status: str
    created_at: datetime
    items: List[OrderItem]
    class Config:
        from_attributes = True

# <<< CHANGE 3: The automatic database table creation is REMOVED.
# You should run migrations manually one time from your local machine
# against the production PlanetScale database before deploying.

# --- FastAPI Application Instance ---
app = FastAPI(
    title="E-commerce API with MySQL",
    description="API for managing products, orders, etc. for an e-commerce platform.",
    version="0.3.0",
)

# --- CORS Middleware ---
# <<< CHANGE 4: Updated CORS origins for Vercel
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
VERCEL_PROJECT_NAME = os.getenv("VERCEL_PROJECT_NAME")

origins = [
    "http://localhost:5173", # Your local frontend
    "http://127.0.0.1:5173",
]
if FRONTEND_URL:
    origins.append(FRONTEND_URL)
if VERCEL_PROJECT_NAME:
    # Allows all Vercel preview deployments to work
    origins.append(f"https://{VERCEL_PROJECT_NAME.lower()}-*.vercel.app")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Helper Function for Image Saving ---
# <<< CHANGE 5: Replaced local file save with Cloudinary upload function.
def save_upload_file_to_cloudinary(upload_file: UploadFile, product_name: str) -> Optional[str]:
    if not upload_file:
        return None
    try:
        # Sanitize product name for use in public_id
        safe_product_name = "".join(c if c.isalnum() or c in ['_','-'] else '' for c in product_name.replace(' ', '_'))
        # Upload to Cloudinary, creating a clean public_id and organizing into a folder
        result = cloudinary.uploader.upload(
            upload_file.file,
            folder="ecommerce_products",
            public_id=f"{safe_product_name}_{os.urandom(4).hex()}"
        )
        return result.get("secure_url")
    except Exception as e:
        print(f"Error uploading image to Cloudinary: {e}")
        # Raising an HTTPException is better for FastAPI to handle
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not upload image.")
    finally:
        upload_file.file.close()


# --- API Endpoints ---
# Endpoints that don't handle files require no changes.
# The changes are in POST and PUT for products.

@app.post("/api/auth/register", response_model=User)
async def register_user(user_input: UserCreate, db: Session = Depends(database.get_db)):
    db_user = auth.get_user_by_email(db, email=user_input.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    if user_input.role not in ['customer', 'vendor']:
        raise HTTPException(status_code=400, detail="Invalid role specified. Must be 'customer' or 'vendor'.")
    hashed_password = auth.get_password_hash(user_input.password)
    db_user_model = models.User(
        email=user_input.email,
        hashed_password=hashed_password,
        full_name=user_input.full_name,
        role=user_input.role
    )
    try:
        db.add(db_user_model)
        db.commit()
        db.refresh(db_user_model)
        return db_user_model
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Could not register user.")

@app.post("/api/auth/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = auth.get_user_by_email(db, email=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

# ... (All your other endpoints like orders, users/me, etc., are pasted here) ...
# I am including all of them for completeness.

@app.get("/api/orders", response_model=List[Order])
async def get_user_orders(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    user_orders = db.query(models.Order).options(
        joinedload(models.Order.items).joinedload(models.OrderItem.product)
    ).filter(models.Order.user_id == current_user.id).order_by(models.Order.created_at.desc()).all()
    return user_orders

@app.get("/api/orders/{order_id}", response_model=Order)
async def get_user_order_details(order_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    db_order = db.query(models.Order).options(
        joinedload(models.Order.items).joinedload(models.OrderItem.product)
    ).filter(models.Order.id == order_id, models.Order.user_id == current_user.id).first()
    if db_order is None:
        raise HTTPException(status_code=404, detail=f"Order with ID {order_id} not found.")
    return db_order

@app.post("/api/orders", response_model=Order, status_code=201)
async def create_new_order(order_input: OrderCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    if not order_input.items:
        raise HTTPException(status_code=400, detail="Cannot create an empty order.")
    product_ids = [item.product_id for item in order_input.items]
    try:
        db_products = db.query(models.Product).filter(models.Product.id.in_(product_ids)).all()
        product_map = {p.id: p for p in db_products}
        if len(db_products) != len(product_ids):
            missing_ids = set(product_ids) - set(product_map.keys())
            raise HTTPException(status_code=404, detail=f"Products not found: {list(missing_ids)}")
        total_price = 0
        order_items_to_create = []
        for item_in_cart in order_input.items:
            product_from_db = product_map[item_in_cart.product_id]
            item_total = product_from_db.price * item_in_cart.quantity
            total_price += item_total
            order_items_to_create.append(
                models.OrderItem(
                    product_id=product_from_db.id,
                    quantity=item_in_cart.quantity,
                    price_at_time_of_purchase=product_from_db.price
                ))
        new_order = models.Order(user_id=current_user.id, total_price=total_price, **order_input.model_dump(exclude={"items"}))
        new_order.items.extend(order_items_to_create)
        db.add(new_order)
        db.commit()
        db.refresh(new_order)
        return new_order
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error creating order for user {current_user.email}: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while processing your order.")

@app.get("/api/users/me", response_model=User)
async def read_users_me(current_user: models.User = Depends(auth.get_current_active_user)):
    return current_user

@app.put("/api/users/me", response_model=User)
async def update_current_user_details(user_update_input: UserUpdate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_active_user)):
    user_data_to_update = user_update_input.model_dump(exclude_unset=True)
    if not user_data_to_update:
        raise HTTPException(status_code=400, detail="No update data provided.")
    for key, value in user_data_to_update.items():
        if hasattr(current_user, key) and value is not None:
            setattr(current_user, key, value)
    try:
        db.add(current_user)
        db.commit()
        db.refresh(current_user)
        return current_user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Could not update user profile.")

@app.get("/")
async def read_root():
    return {"message": "Welcome to the E-commerce API! Visit /docs for API documentation."}

# <<< CHANGE 6: Updated product creation to use Cloudinary
@app.post("/api/products", response_model=Product, status_code=201)
async def create_new_product(
    name: str = Form(...),
    price: float = Form(...),
    description: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_vendor_or_admin)
):
    image_url_to_save = None
    if image:
        image_url_to_save = save_upload_file_to_cloudinary(image, name)

    db_product = models.Product(
        name=name, description=description, price=price,
        image_url=image_url_to_save, owner_id=current_user.id
    )
    try:
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product
    except Exception as e:
        db.rollback()
        # No local file cleanup needed anymore!
        print(f"Error creating product in database: {e}")
        raise HTTPException(status_code=500, detail="Could not create product in database.")

@app.get("/api/products/search", response_model=List[Product])
async def search_products(query: str, db: Session = Depends(database.get_db)):
    if not query.strip():
        return []
    search_term = f"%{query.strip()}%"
    try:
        from sqlalchemy import or_
        db_products = db.query(models.Product).filter(
            or_(models.Product.name.ilike(search_term), models.Product.description.ilike(search_term))
        ).all()
        return db_products
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while searching for products.")

@app.get("/api/products", response_model=List[Product])
async def get_all_products(db: Session = Depends(database.get_db)):
    try:
        db_products = db.query(models.Product).options(
            joinedload(models.Product.category), joinedload(models.Product.owner)
        ).all()
        return db_products
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while fetching products.")

@app.get("/api/products/{product_id}", response_model=Product)
async def get_one_product(product_id: int, db: Session = Depends(database.get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")
    return db_product

# <<< CHANGE 7: Updated product update to use Cloudinary
@app.put("/api/products/{product_id}", response_model=Product)
async def update_one_product(
    product_id: int, name: Optional[str] = Form(None), description: Optional[str] = Form(None),
    price: Optional[float] = Form(None), image: Optional[UploadFile] = File(None),
    db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.require_vendor_or_admin)
):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    if current_user.role == 'vendor' and db_product.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this product")

    update_data = {k: v for k, v in {"name": name, "description": description, "price": price}.items() if v is not None}

    if image:
        # For a full solution, you would delete the old image from Cloudinary here.
        # This requires storing the image's public_id from Cloudinary in your DB.
        new_image_url = save_upload_file_to_cloudinary(image, name or db_product.name)
        update_data["image_url"] = new_image_url

    for key, value in update_data.items():
        setattr(db_product, key, value)

    try:
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Could not update product.")

@app.delete("/api/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_one_product(product_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.require_vendor_or_admin)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if db_product is None:
        # Already gone, or never existed. Idempotent.
        return None
    if current_user.role == 'vendor' and db_product.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this product")
    # For a full solution, you would also delete the image from Cloudinary here.
    try:
        db.delete(db_product)
        db.commit()
        return None
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Could not delete product.")

@app.get("/api/categories", response_model=List[Category])
async def get_all_categories(db: Session = Depends(database.get_db)):
    return db.query(models.Category).all()

@app.post("/api/categories", response_model=Category, status_code=201)
async def create_new_category(category_input: CategoryCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.require_admin)):
    db_category = db.query(models.Category).filter(models.Category.name == category_input.name).first()
    if db_category:
        raise HTTPException(status_code=400, detail="Category with this name already exists.")
    new_category = models.Category(name=category_input.name)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category
# --- Uvicorn run command (for reference, typically run from terminal) ---
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)