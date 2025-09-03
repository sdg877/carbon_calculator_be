from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from sqlalchemy.orm import Session
from .. import auth, models, schemas
from ..database import SessionLocal
from typing import List
from app import models, schemas, auth
from datetime import datetime


router = APIRouter(prefix="", tags=["Users"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        username=user.username, email=user.email, hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/login", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Update last login timestamp
    user.last_login_at = datetime.utcnow()
    db.commit()

    access_token = auth.create_access_token({"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/", response_model=List[schemas.UserResponse])
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users


@router.get("/profile", response_model=schemas.UserResponse)
def read_users_me(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    return current_user


@router.post("/update-password", status_code=200)
def update_password(
    password_data: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    """
    Update the current user's password.
    Expects JSON: { "new_password": "..." }
    """
    new_password = password_data.get("new_password")
    if not new_password:
        raise HTTPException(status_code=400, detail="New password is required")

    hashed_password = auth.get_password_hash(new_password)
    current_user.hashed_password = hashed_password

    db.commit()
    return {"detail": "Password updated successfully"}
