import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# --- Configuration Section ---

# This will hold our final database URL
SQLALCHEMY_DATABASE_URL = ""

# This will hold special connection arguments, like SSL for PlanetScale
connect_args = {}

# Check if we are in the Vercel production environment
# We check for the "DB_HOST" variable, which we will set on Vercel
if "DB_HOST" in os.environ:
    # --- PRODUCTION CONFIGURATION (for Vercel) ---
    db_user = os.environ.get("DB_USERNAME")
    db_pass = os.environ.get("DB_PASSWORD")
    db_host = os.environ.get("DB_HOST")
    db_name = os.environ.get("DB_DATABASE")
    
    # Build the database URL for PlanetScale (using pymysql driver)
    SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{db_user}:{db_pass}@{db_host}/{db_name}"

    connect_args = {
        "ssl_ca": "/etc/ssl/certs/ca-certificates.crt"
    }
    
else:
    # --- LOCAL DEVELOPMENT CONFIGURATION ---
    # If not on Vercel, use your local database URL.
    SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:Activepass123@127.0.0.1:3306/ecommerce_database_db"


# --- SQLAlchemy Engine Setup ---

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=connect_args, # Pass the SSL args here
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# This function is used by your API routes to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()