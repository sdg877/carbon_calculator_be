from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from datetime import datetime


class UserBase(BaseModel):
    username: str = Field(..., description="Unique username for the account")
    email: str = Field(..., description="User's primary contact email")


class UserCreate(UserBase):
    password: str = Field(
        ..., description="Plain text password (hashed before storage)"
    )


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
    activity_type: str = Field(
        ..., description="Type of activity, e.g., 'flight', 'commute'"
    )
    details: dict = Field(
        ..., description="JSON metadata containing distance, fuel type, etc."
    )
    entry_date: datetime = Field(..., description="The date the activity occurred")
    is_recurring: bool = Field(
        False, description="Whether this activity repeats automatically"
    )
    recurrence_frequency: Optional[str] = Field(
        None, description="Frequency: daily, weekly, monthly"
    )
    recurrence_end_date: Optional[datetime] = Field(
        None, description="When the recurrence stops"
    )


class FootprintCreate(FootprintBase):
    pass


class FootprintResponse(FootprintBase):
    id: int
    carbon_kg: float = Field(
        ..., description="Calculated carbon emissions in kilograms"
    )
    created_at: datetime
    suggested_offsets: Optional[List[str]] = Field(
        None, description="Recommended carbon offset projects"
    )

    class Config:
        from_attributes = True


class FootprintAverageResponse(BaseModel):
    entry_date: datetime
    carbon_kg: float

    class Config:
        from_attributes = True
