from fastapi import HTTPException, status, Depends
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
import os
from jwt import PyJWTError
from app.core.database import get_db
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from app.models.user import User
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/user/token")

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    # Convert password to bytes and hash it
    password_bytes = password.encode('utf-8')
    # Generate salt and hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    # Return as string
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)

def create_access_token(data: dict):
    to_encode = data.copy()

    # Expiration time = current time + expiration time 
    expire = datetime.now(timezone.utc) + timedelta(minutes=60)

    # Add expiration to payload
    to_encode.update({"exp": expire})

    if not SECRET_KEY:
        raise ValueError("SECRET_KEY env variable not found")

    # Encoding the token
    encode_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

    return encode_jwt


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