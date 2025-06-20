from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    
    # Optional settings with defaults
    ENVIRONMENT: str = "production"
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.validate_settings()
    
    def validate_settings(self):
        """Validate critical settings"""
        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL environment variable is required")
        
        if not self.JWT_SECRET:
            raise ValueError("JWT_SECRET environment variable is required")
        
        # Validate DATABASE_URL format for Supabase
        if "supabase.co" in self.DATABASE_URL:
            required_parts = ["postgresql://", "@", ".supabase.co", ":5432"]
            for part in required_parts:
                if part not in self.DATABASE_URL:
                    raise ValueError(f"Invalid Supabase DATABASE_URL format. Missing: {part}")
        
        print("Configuration validation passed")

# Create settings instance
try:
    settings = Settings()
except Exception as e:
    print(f"Configuration error: {e}")
    print("\nMake sure you have a .env file with:")
    print("DATABASE_URL=postgresql://postgres:[password]@db.[ref].supabase.co:5432/postgres")
    print("JWT_SECRET=your-secret-key")
    raise