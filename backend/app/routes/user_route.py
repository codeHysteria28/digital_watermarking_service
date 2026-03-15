from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.user import *
from app.models.user import User
from app.models.evidence_image import EvidenceImage
from app.models.verification_log import VerificationLog
from typing import List
from app.core.database import get_db
from app.core.security import *
from sqlalchemy.orm import Session
from sqlalchemy import func as sql_func
import os
from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

router = APIRouter(prefix="/api/v1/auth", tags=["Users"])

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

@router.post("/user/token", response_model=Token, include_in_schema=False)
def user_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == form_data.username).first()
    if not db_user or not verify_password(form_data.password, str(db_user.hashed_password)):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return Token(access_token=create_access_token(data={"sub": db_user.email}))

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

# user profile
@router.get("/user/profile", response_model=UserProfile)
def user_profile(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Count total images uploaded by this user
    total_images = db.query(sql_func.count(EvidenceImage.id)).filter(
        EvidenceImage.user_id == user.id
    ).scalar() or 0

    # Count total verifications performed by this user
    total_verifications = db.query(sql_func.count(VerificationLog.id)).filter(
        VerificationLog.verified_by_user_id == user.id
    ).scalar() or 0

    # count images grouped by status
    status_counts = db.query(
        EvidenceImage.status, sql_func.count(EvidenceImage.id)
    ).filter(
        EvidenceImage.user_id == user.id
    ).group_by(EvidenceImage.status).all()

    images_by_status = {status.value: count for status, count in status_counts}

    # Build a dict from the ORM object + computed fields
    profile_data = {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "total_images_uploaded": total_images,
        "total_verifications": total_verifications,
        "images_by_status": images_by_status
    }

    return UserProfile.model_validate(profile_data)