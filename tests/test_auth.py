import sys
import os
from datetime import timedelta
import pytest

# Ensure the 'app' package can be found
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import auth
from fastapi import HTTPException


def test_password_hash_and_verify():
    password = "mypassword123"
    hashed = auth.get_password_hash(password)
    assert hashed != password
    assert auth.verify_password(password, hashed)


def test_create_and_decode_token():
    data = {"sub": "1"}  # use string, not int
    token = auth.create_access_token(data, expires_delta=timedelta(minutes=5))
    payload = auth.decode_access_token(token)
    assert payload["sub"] == "1"



def test_decode_invalid_token():
    with pytest.raises(HTTPException) as exc:
        auth.decode_access_token("invalidtoken")
    assert exc.value.status_code == 401
