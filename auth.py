from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel # Not strictly needed here if TokenData is only internal

from sqlalchemy.orm import Session
# from . import database, models # This was the old relative import style
import database # Correct direct import
import models   # Correct direct import

# --- Configuration ---
SECRET_KEY = "XvhjdskjikdsjHJHDQSKLFJKLQJKHklds;:jqmhfdqkjkldjqlkkdhqkdjqkfqhiohdkbkk qhlkmhdkfhkqehihpyitttwdb"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

class TokenData(BaseModel): # This is fine here, or could be in a schemas.py
    email: Optional[str] = None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    # 'sub' (subject) in data dict is where user.email is placed in main.py login endpoint
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user_by_email(db: Session, email: str) -> Optional[models.User]: # Correctly type-hinted with models.User
    return db.query(models.User).filter(models.User.email == email).first()


# --- Dependency to get current user ---
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(database.get_db) # Correctly uses database.get_db
) -> models.User: # Correctly type-hinted with models.User
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email_from_token: str = payload.get("sub") # Expecting "sub" to hold the email
        if email_from_token is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception
    
    # user = get_user_by_email(db, email=token_data.email) # If using TokenData
    user = get_user_by_email(db, email=email_from_token) # Simpler if using email_from_token directly
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return user

async def get_current_active_user(current_user: models.User = Depends(get_current_user)) -> models.User:

    if not current_user.is_active: # Redundant if already checked in get_current_user
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user

#async def get_current_admin_user(current_user: models.User = Depends(get_current_active_user)) -> models.User:
# 
#    if not current_user.is_admin:
#        raise HTTPException(
#            status_code=status.HTTP_403_FORBIDDEN,
#            detail="The user does not have admin privileges to perform this action."
#        )
#    return current_user


def require_admin(current_user: models.User = Depends(get_current_active_user)):
    
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Admin privileges required.")
    return current_user

def require_vendor_or_admin(current_user: models.User = Depends(get_current_active_user)):
    
    if current_user.role not in ['vendor', 'admin']:
        raise HTTPException(status_code=403, detail="Vendor or Admin privileges required.")
    return current_user