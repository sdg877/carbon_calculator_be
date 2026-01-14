from typing import Optional, List, Dict
from pydantic import BaseModel
from datetime import datetime


# --- USER SCHEMAS ---
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


# --- FOOTPRINT SCHEMAS ---


class FootprintBase(BaseModel):
    activity_type: str
    details: dict
    entry_date: datetime
    is_recurring: bool = False
    recurrence_frequency: Optional[str] = None


class FootprintCreate(FootprintBase):
    pass


class FootprintResponse(FootprintBase):
    id: int
    carbon_kg: float
    created_at: datetime
    suggested_offsets: Optional[List[str]] = None

    class Config:
        from_attributes = True


class FootprintAverageResponse(BaseModel):
    entry_date: datetime
    carbon_kg: float

    class Config:
        from_attributes = True
