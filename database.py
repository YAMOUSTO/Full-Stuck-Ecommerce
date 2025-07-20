import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL")


if SQLALCHEMY_DATABASE_URL is None:
    print("DATABASE_URL not found, using local SQLite database 'local_dev.db'")
    SQLALCHEMY_DATABASE_URL = "sqlite:///./local_dev.db"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    # This is for Neon/PostgreSQL in production
    print("DATABASE_URL found, connecting to PostgreSQL.")
    engine = create_engine(SQLALCHEMY_DATABASE_URL)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# This function remains exactly the same!
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()