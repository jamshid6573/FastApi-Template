from pydantic import BaseModel
from datetime import datetime
from typing import Literal

class UserResponseSchema(BaseModel):
    id: int
    username: str
    email: str
    avatar: str
    role: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        
