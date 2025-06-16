from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ....core.database import get_db
from ....core.security import get_current_user, get_password_hash
from ....models.user import User as UserModel
from ....schemas.user import User, UserUpdate

router = APIRouter()

@router.get("/", response_model=List[User])
async def read_users(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    users = db.query(UserModel).all()
    return users

@router.get("/me", response_model=User)
async def read_users_me(
    current_user: UserModel = Depends(get_current_user)
):
    return current_user

@router.put("/me", response_model=User)
async def update_user_me(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    update_data = user_update.model_dump(exclude_unset=True)
    
    update_data.pop('id', None)
    
    if "password" in update_data and update_data["password"]:
        password = update_data["password"]
        if len(password) < 8:
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
        if not any(c.isdigit() for c in password):
            raise HTTPException(status_code=400, detail="Password must contain at least one number")
        
        hashed_password = get_password_hash(password)
        update_data["hashed_password"] = hashed_password
        del update_data["password"]
    
    allowed_fields = {'email', 'full_name', 'hashed_password'}
    
    try:
        for field, value in update_data.items():
            if field in allowed_fields:
                setattr(current_user, field, value)
        
        db.commit()
        db.refresh(current_user)
        return current_user
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )
