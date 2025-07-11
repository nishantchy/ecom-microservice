from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    PRODUCTS_API: str = os.getenv("PRODUCTS_API")
    AUTH_SERVICE: str = os.getenv("AUTH_SERVICE")
    RABBITMQ_URL: str = os.getenv("RABBITMQ_URL")
    REDIS_URL: str = os.getenv("REDIS_URL")

    class Config:
        env_file = ".env"

settings = Settings()