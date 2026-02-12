import pytest
from datetime import datetime
from app.schemas import UserCreate, FootprintCreate

def test_user_create_validation():
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "securepassword123"
    }
    user = UserCreate(**user_data)
    assert user.username == "testuser"
    assert user.email == "test@example.com"

def test_footprint_create_defaults():
    footprint_data = {
        "activity_type": "flight",
        "details": {"distance": 500},
        "entry_date": datetime.now()
    }
    footprint = FootprintCreate(**footprint_data)
    assert footprint.is_recurring is False
    assert footprint.activity_type == "flight"