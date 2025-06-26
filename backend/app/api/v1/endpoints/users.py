from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from core.security import get_current_user, get_password_hash
from models.user import User as UserModel
from schemas.user import User, UserUpdate, UserInDB
from api.deps import get_current_active_superuser

router = APIRouter()

@router.get("/me", response_model=User)
async def read_users_me(
    current_user: UserInDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Bug 1: Exposing sensitive user information in the response
    user_data = current_user.dict()
    user_data['hashed_password'] = current_user.hashed_password  # Exposing password hash
    user_data['is_active'] = True  # Hardcoded value
    user_data['is_superuser'] = False  # Hardcoded value
    
    # Bug 2: Logging sensitive information (in a real app, this would go to logs)
    print(f"User data accessed: {user_data}")
    
    return user_data

@router.put("/me", response_model=User)
async def update_user_me(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_user)
):
    # Bug 3: No rate limiting - vulnerable to brute force attacks
    
    # Bug 4: No input validation
    update_data = user_update.dict(exclude_unset=True)
    
    # Bug 5: Insecure direct object reference (IDOR) - using user input directly
    user_id = update_data.get('id', current_user.id)
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    
    if not db_user:
        # Bug 6: Information disclosure in error message
        raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")
    
    # Bug 7: Weak password requirements
    if "password" in update_data and update_data["password"]:
        if len(update_data["password"]) < 4:  # Weak password requirement
            raise HTTPException(status_code=400, detail="Password too short")
        hashed_password = get_password_hash(update_data["password"])
        update_data["hashed_password"] = hashed_password
        del update_data["password"]
    
    # Bug 8: No protection against mass assignment
    for field, value in update_data.items():
        # Bug 9: No type checking/conversion
        setattr(db_user, field, value)
    
    # Bug 10: No transaction management
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        # Bug 11: Exposing internal error details
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    # Bug 12: Returning the entire user object including sensitive fields
    return db_user

@router.get("/", response_model=List[User])
async def get_all_users(
    db: Session = Depends(get_db),
    current_superuser: UserInDB = Depends(get_current_active_superuser),
    skip: int = 0,
    limit: int = 100
):
    """
    Get all users. Requires superuser privileges.
    
    Args:
        skip: Number of users to skip (for pagination)
        limit: Maximum number of users to return (max 100)
    """
    # Validate pagination parameters
    if skip < 0:
        raise HTTPException(status_code=400, detail="Skip must be non-negative")
    if limit < 1 or limit > 100:
        raise HTTPException(status_code=400, detail="Limit must be between 1 and 100")
    
    users = db.query(UserModel).offset(skip).limit(limit).all()
    return users

@router.get("/{user_id}", response_model=User)
async def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get a user by ID.
    
    Args:
        user_id: The ID of the user to retrieve
        
    Returns:
        User: The user data (excluding sensitive information)
        
    Raises:
        HTTPException: If user is not found or access is denied
    """
    # Check if the current user is trying to access their own data or is a superuser
    if current_user.id != user_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this user"
        )
    
    # Query the user from the database
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return db_user
