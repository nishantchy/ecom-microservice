from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import select
from app.configs.database import get_db
from .. import models
from app.schemas import users
from app.utils.password import hash
from app.utils.oauth2 import get_current_user

router = APIRouter(
    prefix="/api/users",
    tags = ["Users"]
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=users.UserResponse)
async def create_user(user: users.UserCreate, db=Depends(get_db)):
    try:
        hashed_password = hash(user.password)
        user.password = hashed_password
        new_user = models.User(**user.model_dump())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Could not create user. " + str(e))


@router.get("/", response_model=list[users.UserResponse])
async def get_users(db=Depends(get_db)):
    users_list = db.exec(select(models.User)).all()
    return users_list


@router.get("/{user_id}", response_model=users.UserResponseDetailed)
async def get_user(user_id: int, db=Depends(get_db)):
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=users.UserResponse)
async def update_user(user_id: int, user_update: users.UserUpdate, db=Depends(get_db), current_user=Depends(get_current_user)):
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this user.")
    try:
        for field, value in user_update.model_dump(exclude_unset=True).items():
            setattr(user, field, value)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Could not update user. " + str(e))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db=Depends(get_db), current_user=Depends(get_current_user)):
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this user.")
    try:
        db.delete(user)
        db.commit()
        return None
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Could not delete user. " + str(e))