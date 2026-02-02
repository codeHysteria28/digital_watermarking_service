from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

# Base schema for shared fields
class UserBase(BaseModel):
    email: EmailStr = Field(
        ...,
        min_length=1,
        max_length=255,
        description="User email",
        examples=["test@email.com", "john.doe@gmail.com"]
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="User name",
        examples=["John Doe", "JohnDoe1965"]
    )

# Schema for creating a user (registration)
class UserCreate(UserBase):
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="User's password"
    )

# Schema for login
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
# Schema for API responses
    id: int
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

# Schema for token response (after login)
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: int | None = None
    email: str | None = None