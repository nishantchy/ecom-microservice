from fastapi import APIRouter, HTTPException, status, Depends, Request
from sqlmodel import Session
from .. import models
from app.configs.database import get_db
from app.utils import oauth2
from app.schemas.verify import TokenUserInfo

router = APIRouter(
    prefix="/api/verify-token",
    tags=["Verification"]
)

@router.post("/")
async def verify_token(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    token = data.get("token")
    if not token:
        raise HTTPException(status_code=400, detail="Token is required")
    try:
        user_id = oauth2.verify_access_token(token, HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        ))
        user = db.get(models.User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return TokenUserInfo(
            user_id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            street=user.street,
            city=user.city,
            province=user.province,
            postal_code=user.postal_code,
            country=user.country,
            phone_number=user.phone_number 
        )
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid or expired token")