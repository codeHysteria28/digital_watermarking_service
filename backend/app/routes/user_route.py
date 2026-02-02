from fastapi import APIRouter, HTTPException, status, Depends
from schemas.user import UserCreate, UserBase, UserResponse
from models.User import User
from typing import List
from core.database import get_db
from core.security import hash_password
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/v1/users", tags=["users"])

# all users = will be deleted later as it's not needed
@router.get("/users", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()

    return users

@router.post("/users", response_model=UserResponse)
def create_user(user:UserCreate, db: Session = Depends(get_db)):
    # check if user already exists
    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already regisstered"
        )
    
    # Hash the passowrd
    hashed_password = hash_password(user.password)

    # Create new user
    new_user = User(
        email=user.email,
        name=user.name,
        hashed_password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user