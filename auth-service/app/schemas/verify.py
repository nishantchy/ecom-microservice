from pydantic import BaseModel, EmailStr
from typing import Optional

class TokenUserInfo(BaseModel):
    user_id: int
    username: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    phone_number: Optional[str] = None