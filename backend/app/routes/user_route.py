from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from schemas.user import *
from models.user import User
from typing import List
from core.database import get_db
from core.security import *
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv
import jwt
from jwt import PyJWTError
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")

router = APIRouter(prefix="/api/v1/auth", tags=["Users"])

# all users = will be deleted later as it's not needed
@router.get("/users", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()

    return users

# register new user
@router.post("/user/register", response_model=UserResponse)
def user_register(user:UserCreate, db: Session = Depends(get_db)):
    # check if user already exists
    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash the password
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

# login user
@router.post("/user/login", response_model=Token)
def user_login(user: UserLogin, db: Session = Depends(get_db)):
    # check for user
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid credentials"
        )
    
    # check password
    if not verify_password(user.password, str(db_user.hashed_password)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid credentials"
        )
    
    # issue access token
    access_token = create_access_token(data={"sub": db_user.email})

    return Token(access_token=access_token)

# Get current user
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:

        # decode token
        if not SECRET_KEY:
            raise ValueError("SECRET_KEY env variable not found")
    
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    
        # extracting the email from payload
        email = payload.get("sub")

        if email is None:
            raise credentials_exception

        # check for email
        db_user = db.query(User).filter(User.email == email).first()

        if not db_user:
            raise credentials_exception
    except PyJWTError:
        raise credentials_exception
    
    return db_user