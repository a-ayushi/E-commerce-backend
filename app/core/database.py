from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


#database connection
SQLALCHEMY_DATABASE_URL = "sqlite:///./ecommerce.db"

#create a session
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
) 

# Create a session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


# Dependency
def get_db():
    db = SessionLocal() # creates a db connection
    try:
        yield db # gives that connect to code that needs it
    finally:
        db.close()