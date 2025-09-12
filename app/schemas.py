from typing import Optional, List, Dict
from pydantic import BaseModel
from datetime import datetime

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class FootprintBase(BaseModel):
    activity_type: str
    carbon_kg: float
    details: Optional[Dict] = None

class FootprintCreate(FootprintBase):
    pass

class FootprintResponse(FootprintBase):
    id: int
    user_id: int
    created_at: datetime
    suggested_offsets: Optional[List[str]] = []

    class Config:
        from_attributes = True

class FootprintAverageResponse(BaseModel):
    created_at: datetime
    carbon_kg: float
    
    class Config:
        from_attributes = True
