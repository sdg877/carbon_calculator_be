from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, models, auth
from ..database import get_db
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(prefix="/footprints", tags=["Footprints"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

def calculate_carbon(activity_type: str, details: dict) -> float:
    """
    Estimate CO2 emissions (kg CO₂e).
    Distances are given in miles (converted internally to km).
    Weights in kg, energy in kWh, water in litres, time in hours.
    """
    # Conversion
    miles_to_km = 1.60934  

    # ------------------ TRANSPORT ------------------
    if activity_type == "flight":
        distance_miles = details.get("distance_miles", 0)
        distance_km = distance_miles * miles_to_km
        return distance_km * 0.115

    elif activity_type == "driving":
        miles = details.get("distance_miles", 0)
        km = miles * miles_to_km
        fuel_type = details.get("fuel_type", "petrol")
        factor = 0.192 if fuel_type == "petrol" else 0.171
        return km * factor

    elif activity_type == "train":
        miles = details.get("distance_miles", 0)
        km = miles * miles_to_km
        return km * 0.041

    elif activity_type == "bus":
        miles = details.get("distance_miles", 0)
        km = miles * miles_to_km
        return km * 0.105

    elif activity_type == "motorbike":
        miles = details.get("distance_miles", 0)
        km = miles * miles_to_km
        return km * 0.103

    elif activity_type == "taxi":
        miles = details.get("distance_miles", 0)
        km = miles * miles_to_km
        return km * 0.209

    # ------------------ HOUSEHOLD ENERGY ------------------
    elif activity_type == "electricity":
        kwh = details.get("kwh", 0)
        return kwh * 0.233

    elif activity_type == "gas_heating":
        kwh = details.get("kwh", 0)
        return kwh * 0.184

    elif activity_type == "water_heating":
        litres = details.get("litres", 0)
        return litres * 0.05

    # ------------------ FOOD ------------------
    elif activity_type == "meat":
        meat_type = details.get("type", "beef")
        kg = details.get("kg", 0)
        factors = {
            "beef": 27.0,
            "lamb": 24.0,
            "pork": 12.0,
            "chicken": 6.9,
            "fish": 6.0,
        }
        return kg * factors.get(meat_type, 10.0)

    elif activity_type == "dairy":
        dairy_type = details.get("type", "milk")
        kg = details.get("kg", 0)
        factors = {
            "milk": 1.9,
            "cheese": 13.5,
            "butter": 24.0,
            "yoghurt": 2.2,
        }
        return kg * factors.get(dairy_type, 2.0)

    elif activity_type == "plant_based":
        food_type = details.get("type", "vegetables")
        kg = details.get("kg", 0)
        factors = {
            "vegetables": 2.0,
            "grains": 1.4,
            "legumes": 0.9,
            "fruit": 1.1,
        }
        return kg * factors.get(food_type, 1.5)

    elif activity_type == "food_waste":
        kg = details.get("kg", 0)
        return kg * 4.5

    # ------------------ SHOPPING ------------------
    elif activity_type == "clothing":
        clothing_type = details.get("type", "tshirt")
        quantity = details.get("quantity", 1)
        factors = {
            "tshirt": 2.6,
            "jeans": 33.0,
            "shoes": 14.0,
            "coat": 50.0,
        }
        return quantity * factors.get(clothing_type, 10.0)

    elif activity_type == "electronics":
        device = details.get("type", "smartphone")
        quantity = details.get("quantity", 1)
        factors = {
            "smartphone": 70.0,
            "laptop": 200.0,
            "tv": 350.0,
            "console": 90.0,
        }
        return quantity * factors.get(device, 100.0)

    elif activity_type == "online_shopping":
        items = details.get("items", 1)
        returns = details.get("returns", 0)
        return (items * 1.0) + (returns * 3.0)

    # ------------------ DIGITAL & LEISURE ------------------
    elif activity_type == "streaming":
        hours = details.get("hours", 0)
        return hours * 0.15

    elif activity_type == "gaming":
        hours = details.get("hours", 0)
        return hours * 0.05

    elif activity_type == "event":
        hours = details.get("hours", 0)
        attendance = details.get("people", 1)
        return hours * attendance * 0.1

    # ------------------ PETS ------------------
    elif activity_type == "pet":
        pet_type = details.get("type", "dog")
        years = details.get("years", 1)
        factors = {
            "dog": 770,
            "cat": 310,
        }
        return years * factors.get(pet_type, 500)

    return 0.0




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

