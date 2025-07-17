from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi import status
from pydantic import BaseModel
from typing import List, Optional
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordRequestForm 
from datetime import timedelta
from datetime import datetime

import shutil  
import os
from pathlib import Path

from sqlalchemy.orm import Session, joinedload


import models
import database
import auth

# --- Configuration ---
UPLOAD_DIR = Path("static/images/products")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)  

# Add a minimal User schema for nesting inside the Product response

class UserInProduct(BaseModel):
    id: int
    full_name: Optional[str] = None
    email: str
    class Config:
        from_attributes = True

# --- Pydantic Schemas ---
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

class UserCreate(UserBase): # For registration
    password: str 
    role: str = 'customer'

class UserLogin(BaseModel): # For login
    email: str 
    password: str

class User(UserBase): 
    id: int
    is_active: bool
    role: str
    is_admin: bool = False
    

class Config:
    from_attributes = True


class  UserUpdate(UserBase): # For updating user details
    full_name: Optional[str] = None
    password: Optional[str] = None  
    

class Token(BaseModel): # For returning JWT token
    access_token: str
    token_type: str

class TokenData(BaseModel): # For data encoded in the JWT
    email: Optional[str] = None


# --- Schemas for Order Items ---
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

class OrderItem(OrderItemBase): # For response
    id: int
    price_at_time_of_purchase: float
    product: ProductInOrder
    

    class Config:
        from_attributes = True

# --- Schemas for Orders ---
class OrderBase(BaseModel):
    # Shipping details from the client
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

# --- Database Initialization ---
try:
    database.Base.metadata.create_all(bind=database.engine)
    print("Database tables created successfully (if they didn't exist).")
except Exception as e:
    print(f"Error creating database tables: {e}")
   


# --- FastAPI Application Instance ---
app = FastAPI(
    title="E-commerce API with MySQL",
    description="API for managing products, orders, etc. for an e-commerce platform.",
    version="0.3.0", 
)

# --- Static Files Mounting ---

app.mount("/static_images", StaticFiles(directory="static/images"), name="static_images")

# --- CORS Middleware ---
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

origins = [
    "http://localhost:5173", 
    "http://localhost:8080", 
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8080",
     FRONTEND_URL, 
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)


# --- Helper Function for Image Saving ---
def save_upload_file(upload_file: UploadFile, destination_dir: Path) -> Optional[str]:
    if not upload_file:
        return None
    try:
        # Sanitize filename slightly, add uniqueness
        original_filename = Path(upload_file.filename)
        safe_stem = "".join(c if c.isalnum() or c in ['_','-'] else '_' for c in original_filename.stem)
        unique_filename = f"{safe_stem}_{os.urandom(4).hex()}{original_filename.suffix}"
        
        file_path = destination_dir / unique_filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        # Return a URL path that can be used with the static files mount
        return f"/static_images/products/{unique_filename}"
    except Exception as e:
        print(f"Error saving image '{upload_file.filename}': {e}")
        return None
    finally:
        upload_file.file.close() 


# --- API Endpoints ---
@app.post("/api/auth/register", response_model=User)
async def register_user(user_input: UserCreate, db: Session = Depends(database.get_db)):
    db_user = auth.get_user_by_email(db, email=user_input.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Validate role
    if user_input.role not in ['customer', 'vendor']:
        raise HTTPException(status_code=400, detail="Invalid role specified. Must be 'customer' or 'vendor'.")

    hashed_password = auth.get_password_hash(user_input.password)
    db_user_model = models.User(
        email=user_input.email,
        hashed_password=hashed_password,
        full_name=user_input.full_name,
        role=user_input.role # <-- SET THE ROLE FROM INPUT
    )
    # ... (rest of your existing try/except block to save user)
    try:
        db.add(db_user_model)
        db.commit()
        db.refresh(db_user_model)
        return db_user_model
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Could not register user.")
    

@app.post("/api/auth/login", response_model=Token) # Or name it /api/auth/token
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), # Expects x-www-form-urlencoded data
    db: Session = Depends(database.get_db)
):
    user = auth.get_user_by_email(db, email=form_data.username) # form_data.username is the email
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create JWT token
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    # Store user's email (or ID) in the "sub" (subject) field of the token
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# --- NEW: Endpoints for fetching user's orders ---

@app.get("/api/orders", response_model=List[Order]) 
async def get_user_orders(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):   
  
    user_orders = db.query(models.Order).options(
        joinedload(models.Order.items).joinedload(models.OrderItem.product) # Eager load items and their products
    ).filter(models.Order.user_id == current_user.id).order_by(models.Order.created_at.desc()).all()
    return user_orders


@app.get("/api/orders/{order_id}", response_model=Order) 
async def get_user_order_details(
    order_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Retrieve the details of a specific order, ensuring it belongs to the current user.
    """
    db_order = db.query(models.Order).options(
        joinedload(models.Order.items).joinedload(models.OrderItem.product) # Eager load items and their products
    ).filter(
        models.Order.id == order_id,
        models.Order.user_id == current_user.id
    ).first()

    if db_order is None:
       
        raise HTTPException(status_code=404, detail=f"Order with ID {order_id} not found.")
    
    return db_order


@app.post("/api/orders", response_model=Order, status_code=201)
async def create_new_order(
    order_input: OrderCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_active_user) # Require user to be logged in
):
    """
    Create a new order from cart items and shipping details.
    """
    if not order_input.items:
        raise HTTPException(status_code=400, detail="Cannot create an empty order.")

    product_ids = [item.product_id for item in order_input.items]
    
    # Use a transaction to ensure all or nothing is saved
    try:
      
        db_products = db.query(models.Product).filter(models.Product.id.in_(product_ids)).all()
     # Create a dictionary for quick price lookup
        product_map = {p.id: p for p in db_products}

        # Check if any requested product ID was not found in the database
        if len(db_products) != len(product_ids):
            found_ids = {p.id for p in db_products}
            missing_ids = set(product_ids) - found_ids
            raise HTTPException(
                status_code=404, 
                detail=f"Products not found: {list(missing_ids)}"
            )

        # 2. Calculate total price on the backend based on current prices
        total_price = 0
        order_items_to_create = []
        for item_in_cart in order_input.items:
            product_from_db = product_map[item_in_cart.product_id]
            
            # Create an OrderItem with the price at the time of purchase
            item_total = product_from_db.price * item_in_cart.quantity
            total_price += item_total
            
            order_items_to_create.append(
                models.OrderItem(
                    product_id=product_from_db.id,
                    quantity=item_in_cart.quantity,
                    price_at_time_of_purchase=product_from_db.price
                )
            )

        # 3. Create the main Order record
        new_order = models.Order(
            user_id=current_user.id,
            total_price=total_price,
            shipping_address_line1=order_input.shipping_address_line1,
            shipping_city=order_input.shipping_city,
            shipping_postal_code=order_input.shipping_postal_code,
            shipping_country=order_input.shipping_country,
            # 'status' and 'created_at' have defaults
        )
        
        # 4. Associate the OrderItems with the new Order
        new_order.items.extend(order_items_to_create)

        # 5. Add to session and commit the transaction
        db.add(new_order)
        db.commit()
        db.refresh(new_order) # Refresh to get the new order ID and relationships loaded

        return new_order

    except HTTPException:
        # Re-raise HTTPExceptions from our checks
        raise
    except Exception as e:
        db.rollback() # Rollback the transaction on any other error
        print(f"Error creating order for user {current_user.email}: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while processing your order.")

# Endpoint to get current authenticated user's details
@app.get("/api/users/me", response_model=User)
async def read_users_me(current_user: models.User = Depends(auth.get_current_active_user)):
    return current_user




@app.put("/api/users/me", response_model=User) # Returns the updated User schema
async def update_current_user_details(
    user_update_input: UserUpdate, # Pydantic model for the request body
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_active_user) # Ensures user is authenticated
):
    """
    Update the current authenticated user's profile information.
    For now, only allows updating 'full_name'.
    """
    user_data_to_update = user_update_input.model_dump(exclude_unset=True) # Only get provided fields

    if not user_data_to_update:
        raise HTTPException(status_code=400, detail="No update data provided.")

    updated_fields_count = 0
    for key, value in user_data_to_update.items():
        if hasattr(current_user, key) and value is not None: # Check if field exists and value is provided
            setattr(current_user, key, value)
            updated_fields_count += 1
    
    if updated_fields_count == 0:
         # This case might occur if all provided values were None or fields didn't exist
        raise HTTPException(status_code=400, detail="No valid fields provided for update or values were null.")


    try:
        db.add(current_user) # SQLAlchemy tracks changes on the current_user object
        db.commit()
        db.refresh(current_user)
        
        # IMPORTANT: If email was updated and email is used in the JWT 'sub' claim,
        # the current token will still contain the OLD email.
        # For simplicity, we are not handling email updates or token re-issuance here.
        # If email can be updated, you'd typically re-issue a token or advise user to re-login.

        return current_user
    except Exception as e:
        db.rollback()
        print(f"Error updating user {current_user.email}: {e}")
        # Be careful about exposing too much detail from DB errors (e.g., unique constraint violation if email was updated)
        raise HTTPException(status_code=500, detail="Could not update user profile.")

@app.get("/")
async def read_root():
    return {"message": "Welcome to the E-commerce API with MySQL! Visit /docs for API documentation."}

@app.post("/api/products", response_model=Product, status_code=201)
async def create_new_product(
    name: str = Form(...),
    price: float = Form(...),
    description: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_vendor_or_admin)
):
    print(f"Product created by user: {current_user.email}")
    image_url_to_save: Optional[str] = None
    saved_image_path: Optional[Path] = None

    if image:
        image_url_to_save = save_upload_file(image, UPLOAD_DIR)
        if not image_url_to_save:
            # Decide if product creation should fail if image saving fails
            raise HTTPException(status_code=500, detail="Could not save product image.")
        # Store full path for potential cleanup if DB operation fails
        saved_image_path = UPLOAD_DIR / image_url_to_save.split('/')[-1]


    db_product = models.Product(
        name=name,
        description=description,
        price=price,
        image_url=image_url_to_save,
        owner_id=current_user.id
    )

    try:
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product
    except Exception as e:
        db.rollback()
        # Cleanup: If image was saved but DB operation failed, delete the saved image
        if saved_image_path and saved_image_path.exists():
            try:
                saved_image_path.unlink()
                print(f"Cleaned up image {saved_image_path} after DB error.")
            except Exception as e_del:
                print(f"Error cleaning up image {saved_image_path}: {e_del}")
        
        print(f"Error creating product in database: {e}")
        raise HTTPException(status_code=500, detail="Could not create product in database.")


# ~/ecommerce-platform/main.py
# ... (imports and existing code) ...

# --- API Endpoints ---
# ... (your existing auth endpoints and root / endpoint) ...

# NEW: Search Endpoint - place it before the /api/products/{product_id} route
@app.get("/api/products/search", response_model=List[Product])
async def search_products(query: str, db: Session = Depends(database.get_db)):
    """
    Search for products by name or description based on a query string.
    """
    if not query.strip():
        # Return empty list if query is just whitespace
        return []
    
    search_term = f"%{query.strip()}%" # Add wildcards for partial matching
    
    try:
        # Use SQLAlchemy's 'ilike' for case-insensitive search
        # 'or_' is used to search in multiple columns
        from sqlalchemy import or_
        
        db_products = db.query(models.Product).filter(
            or_(
                models.Product.name.ilike(search_term),
                models.Product.description.ilike(search_term)
            )
        ).all()
        
        return db_products
    except Exception as e:
        print(f"Error during product search: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while searching for products.")

# ... (your existing GET /api/products, GET /api/products/{id}, POST, PUT, DELETE endpoints) ...


@app.get("/api/products", response_model=List[Product])
async def get_all_products(db: Session = Depends(database.get_db)):
    try:
        db_products = db.query(models.Product).options(
    joinedload(models.Product.category),
    joinedload(models.Product.owner)
    ).all()
        
        return db_products
    
    except Exception as e:
        print(f"Error fetching all products: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching products.")


@app.get("/api/products/{product_id}", response_model=Product)
async def get_one_product(product_id: int, db: Session = Depends(database.get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")
    return db_product


@app.put("/api/products/{product_id}", response_model=Product)
async def update_one_product(
    product_id: int,
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_vendor_or_admin)
):
    print(f"Product updated by user: {current_user.email}")
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()

    if db_product is None:
        raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")
    
    if current_user.role == 'vendor' and db_product.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this product")
    
    update_data = {}
    if name is not None:
        update_data["name"] = name
    if description is not None:
        update_data["description"] = description
    if price is not None:
        update_data["price"] = price
    
    new_image_url: Optional[str] = None
    new_saved_image_path: Optional[Path] = None
    old_image_path_to_delete: Optional[Path] = None

    if image:
        # If there's an existing image, mark it for deletion
        if db_product.image_url:
            old_image_filename = db_product.image_url.split('/')[-1]
            old_image_path_to_delete = UPLOAD_DIR / old_image_filename
        
        # Save the new image
        new_image_url = save_upload_file(image, UPLOAD_DIR)
        if not new_image_url:
            raise HTTPException(status_code=500, detail="Could not save new product image for update.")
        
        update_data["image_url"] = new_image_url
        new_saved_image_path = UPLOAD_DIR / new_image_url.split('/')[-1]

    # Apply updates to the model object
    for key, value in update_data.items():
        setattr(db_product, key, value)
    
    try:
        db.add(db_product) # or just db.flush() if only updating existing, then db.commit()
        db.commit()
        db.refresh(db_product)

        # If commit was successful and an old image was marked, delete it now
        if old_image_path_to_delete and old_image_path_to_delete.exists():
            try:
                old_image_path_to_delete.unlink()
                print(f"Successfully deleted old image: {old_image_path_to_delete}")
            except Exception as e_del:
                # Log this error, but the main operation succeeded
                print(f"Error deleting old image {old_image_path_to_delete} after successful update: {e_del}")
        
        return db_product
    except Exception as e:
        db.rollback()
        # Cleanup: If a new image was saved but DB update failed, delete the new image
        if new_saved_image_path and new_saved_image_path.exists():
            try:
                new_saved_image_path.unlink()
                print(f"Cleaned up new image {new_saved_image_path} after DB update error.")
            except Exception as e_del:
                print(f"Error cleaning up new image {new_saved_image_path}: {e_del}")

        print(f"Error updating product {product_id} in database: {e}")
        raise HTTPException(status_code=500, detail="Could not update product.")


@app.delete("/api/products/{product_id}", status_code=204) # 204 No Content
async def delete_one_product(
    product_id: int, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_vendor_or_admin)
    ):

    print(f"Product deleted by user: {current_user.email}")
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()

    if db_product is None:
        raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found, cannot delete.")

    if current_user.role == 'vendor' and db_product.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this product")

    image_path_to_delete: Optional[Path] = None
    if db_product.image_url:
        image_filename = db_product.image_url.split('/')[-1]
        image_path_to_delete = UPLOAD_DIR / image_filename

    try:
        db.delete(db_product)
        db.commit()
        
        if image_path_to_delete and image_path_to_delete.exists():
            try:
                image_path_to_delete.unlink()
                print(f"Successfully deleted image: {image_path_to_delete} for product {product_id}")
            except Exception as e_del:             
                print(f"Error deleting image file {image_path_to_delete} for product {product_id}: {e_del}")
        
        return None 
    except Exception as e:
        db.rollback()
        print(f"Error deleting product {product_id} from database: {e}")
        raise HTTPException(status_code=500, detail="Could not delete product from database.")

@app.get("/api/categories", response_model=List[Category])
async def get_all_categories(db: Session = Depends(database.get_db)):
   
    db_categories = db.query(models.Category).all()
    return db_categories

# Endpoint to create a new category (protected)
@app.post("/api/categories", response_model=Category, status_code=201)
async def create_new_category(
    category_input: CategoryCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.require_admin)
):
  
    # Optional: Check if category already exists
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