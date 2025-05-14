from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: Optional[str] = None
    avatar: Optional[str] = None

class UserCreate(UserBase):
    google_id: Optional[str] = None

class UserResponse(UserBase):
    id: int
    google_id: Optional[str]
    role: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class AuthResponse(BaseModel):
    user: UserResponse
    token: str