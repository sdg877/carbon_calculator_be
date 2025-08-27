from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, models, auth
from ..database import get_db
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(prefix="/footprints", tags=["Footprints"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


def calculate_carbon(activity_type: str, details: dict) -> float:
    if activity_type == "flight":
        distance = details.get("distance_km", 0)
        return distance * 0.115
    elif activity_type == "driving":
        km = details.get("distance_km", 0)
        fuel_type = details.get("fuel_type", "petrol")
        factor = 0.192 if fuel_type == "petrol" else 0.171
        return km * factor
    elif activity_type == "train":
        km = details.get("distance_km", 0)
        return km * 0.041
    return 0


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = auth.decode_access_token(token)
    if not payload or 'sub' not in payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user_id = int(payload['sub'])
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user



@router.post("/", response_model=schemas.FootprintResponse)
def create_footprint(
    footprint: schemas.FootprintCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    carbon_kg = calculate_carbon(footprint.activity_type, footprint.details)
    db_footprint = models.Footprint(
        activity_type=footprint.activity_type,
        carbon_kg=carbon_kg,
        user_id=user.id
    )
    db.add(db_footprint)
    db.commit()
    db.refresh(db_footprint)
    return db_footprint

