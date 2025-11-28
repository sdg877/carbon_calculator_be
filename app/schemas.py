from typing import Optional, List, Dict
from pydantic import BaseModel
from datetime import datetime


class UserBase(BaseModel):
    username: str
    email: str 


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str


class FootprintBase(BaseModel):
    activity_type: str
    details: Optional[Dict] = None


class FootprintCreate(FootprintBase):
    pass


class FootprintResponse(FootprintBase):
    id: int
    user_id: int
    carbon_kg: float
    created_at: datetime
    suggested_offsets: Optional[List[str]] = []

    class Config:
        from_attributes = True


class FootprintAverageResponse(BaseModel):
    created_at: datetime
    carbon_kg: float

    class Config:
        from_attributes = True
