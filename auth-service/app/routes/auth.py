from fastapi import APIRouter, HTTPException, status, Depends, Request
from sqlmodel import Session, select
from .. import models
from app.configs.database import get_db
from fastapi.security import OAuth2PasswordRequestForm
from app.utils import oauth2
from app.utils.password import verify

router = APIRouter(
    prefix="/api/login",
    tags=["Authentication"]
)

@router.post("/", status_code=status.HTTP_200_OK)
async def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.exec(select(models.User).where(models.User.email == user_credentials.username)).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
    
    if not verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
    
    access_token = oauth2.create_access_token(data={"user_id": user.id})

    return {"access_token": access_token, "token_type": "bearer"}

