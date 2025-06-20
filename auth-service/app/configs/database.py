from sqlmodel import Session, create_engine, SQLModel
from app.configs.config import settings
import time
from sqlmodel import text

# Enhanced engine configuration for Supabase
def create_database_engine():
    database_url = settings.DATABASE_URL
    
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is required")

    if "sslmode" not in database_url and "supabase.co" in database_url:
        separator = "&" if "?" in database_url else "?"
        database_url += f"{separator}sslmode=require"
    
    engine = create_engine(
        database_url,
        echo=False,  
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True, 
        pool_recycle=300,   
        connect_args={
            "connect_timeout": 10,
            "application_name": "fastapi-app"
        }
    )
    
    return engine

# Create the engine
engine = create_database_engine()

def test_connection(max_retries=3):
    """Test database connection with retries"""
    for attempt in range(max_retries):
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                print("Database connection successful")
                return True
        except Exception as e:
            print(f"Connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt 
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print("All connection attempts failed")
                raise
    return False

def create_db_and_tables():
    """Create database tables with connection retry"""
    try:
        test_connection()
        
        # Create tables
        SQLModel.metadata.create_all(engine)
        print("Database tables created successfully")
    except Exception as e:
        print(f"Failed to create database tables: {e}")
        raise

def get_db():
    """Database session dependency with proper error handling"""
    try:
        with Session(engine) as session:
            yield session
    except Exception as e:
        print(f"Database session error: {e}")
        raise

if __name__ == "__main__":
    create_db_and_tables()