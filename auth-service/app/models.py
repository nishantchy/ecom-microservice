from sqlmodel import SQLModel, Field
from datetime import datetime
from pydantic import EmailStr
from typing import Optional

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    street: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    phone_number: str
    created_at: datetime = Field(default_factory=datetime.now)