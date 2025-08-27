from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        orm_mode = True


class LoginRequest(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class FootprintCreate(BaseModel):
    activity_type: str
    details: dict


class FootprintResponse(BaseModel):
    id: int
    activity_type: str
    carbon_kg: float
    user_id: int

    class Config:
        from_attributes = True
