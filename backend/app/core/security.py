import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

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