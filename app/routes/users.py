from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas, auth
from datetime import datetime

router = APIRouter(prefix="", tags=["Users"])

@router.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        last_login_at=datetime.utcnow(),
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
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user.last_login_at = datetime.utcnow()
    db.commit()
    db.refresh(user)

    access_token = auth.create_access_token({"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/profile", response_model=schemas.UserResponse)
def read_users_me(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    return current_user


@router.put("/profile", response_model=schemas.UserResponse)
def update_profile(
    updates: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):

    if updates.username:
        existing_user = (
            db.query(models.User)
            .filter(
                models.User.username == updates.username,
                models.User.id != current_user.id,
            )
            .first()
        )
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already taken")
        current_user.username = updates.username

    if updates.email:
        existing_email = (
            db.query(models.User)
            .filter(
                models.User.email == updates.email, models.User.id != current_user.id
            )
            .first()
        )
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already used")
        current_user.email = updates.email

    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/update-password", status_code=200)
def update_password(
    password_data: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    new_password = password_data.get("new_password")
    if not new_password:
        raise HTTPException(status_code=400, detail="New password is required")

    hashed_password = auth.get_password_hash(new_password)
    db_user = db.query(models.User).filter(models.User.id == current_user.id).first()
    db_user.hashed_password = hashed_password
    db.commit()
    db.refresh(db_user)

    return {"detail": "Password updated successfully"}
