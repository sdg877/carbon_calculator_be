from typing import Dict
from fastapi import HTTPException

# ------------------ CONSTANTS ------------------
VALID_ACTIVITIES = {
    "flight", "driving", "train", "tube", "bus",
    "meat", "dairy", "food_waste",
    "clothing", "electronics", "online_shopping",
    "electricity_use", "gas_use", "water_use",
    "plastic_waste", "general_waste", "recycling",
    "streaming", "gaming", "events", "hotel_stays"
}

TRANSPORT_FACTORS = {
    "flight": {"short": 500, "long": 2000, "factor": 0.115},
    "driving": {"short": 8, "medium": 16, "long": 32, "petrol": 0.192, "other": 0.171},
    "train": 0.041,
    "tube": 0.041,
    "bus": 0.105
}

FOOD_FACTORS = {
    "meat": {"beef": 27.0, "lamb": 24.0, "pork": 12.0, "chicken": 6.9, "fish": 6.0, "avg_kg": 0.2},
    "dairy": {"milk": 1.9, "cheese": 13.5, "butter": 24.0, "yoghurt": 2.2, "avg_kg": 0.2},
    "food_waste": {"rare": 0.5, "weekly": 2.0}
}

SHOPPING_FACTORS = {
    "clothing": {"monthly": 10.0, "weekly": 40.0},
    "electronics": {"rare": 50.0, "frequent": 200.0},
    "online_shopping": {"order_factor": 1.0, "return_factor": 3.0}
}

HOUSEHOLD_FACTORS = {
    "electricity_use": 0.233,
    "gas_use": 0.184,
    "water_use": 0.0003 * 30
}

WASTE_FACTORS = {
    "plastic_waste": 0.5 * 52 / 12,
    "general_waste": 1.5 * 52 / 12,
    "recycling": 0.2
}

LIFESTYLE_FACTORS = {
    "streaming": 0.055 * 4,
    "gaming": 0.05 * 4,
    "events": 20 / 12,
    "hotel_stays": 82 / 12
}

# ------------------ FUNCTIONS ------------------
def calculate_carbon(activity_type: str, details: Dict) -> float:
    """
    Calculate carbon footprint (kg CO2) based on activity type and details.
    Raises HTTPException if input is invalid.
    """
    if activity_type not in VALID_ACTIVITIES:
        raise HTTPException(status_code=400, detail=f"Invalid activity_type: {activity_type}")

    if not isinstance(details, dict):
        raise HTTPException(status_code=400, detail="Details must be a dictionary")

    try:
        # ------------------ TRANSPORT ------------------
        if activity_type == "flight":
            distance_km = TRANSPORT_FACTORS["flight"].get(details.get("flight_type", "short"), 500)
            return distance_km * TRANSPORT_FACTORS["flight"]["factor"]

        elif activity_type == "driving":
            commute = details.get("commute", "short")
            km = TRANSPORT_FACTORS["driving"].get(commute, 8)
            fuel_type = details.get("fuel_type", "petrol")
            factor = TRANSPORT_FACTORS["driving"]["petrol"] if fuel_type == "petrol" else TRANSPORT_FACTORS["driving"]["other"]
            return km * factor

        elif activity_type in ["train", "tube"]:
            commute = details.get("commute", "short")
            km = {"short": 8, "medium": 16, "long": 32}.get(commute, 8)
            return km * TRANSPORT_FACTORS[activity_type]

        elif activity_type == "bus":
            commute = details.get("commute", "short")
            km = {"short": 8, "medium": 16, "long": 32}.get(commute, 8)
            return km * TRANSPORT_FACTORS["bus"]

        # ------------------ FOOD ------------------
        elif activity_type == "meat":
            try:
                servings = float(details.get("servings_per_week", 0))
            except (TypeError, ValueError):
                raise HTTPException(status_code=400, detail="Invalid value for servings_per_week")

            meat_type = details.get("type", "beef")
            if meat_type not in FOOD_FACTORS["meat"]:
                raise HTTPException(status_code=400, detail=f"Invalid meat type: {meat_type}")

            factor = FOOD_FACTORS["meat"][meat_type]
            avg_kg = FOOD_FACTORS["meat"]["avg_kg"]
            return servings * avg_kg * factor

        elif activity_type == "dairy":
            try:
                servings = float(details.get("servings_per_week", 0))
            except (TypeError, ValueError):
                raise HTTPException(status_code=400, detail="Invalid value for servings_per_week")

            dairy_type = details.get("type", "milk")
            if dairy_type not in FOOD_FACTORS["dairy"]:
                raise HTTPException(status_code=400, detail=f"Invalid dairy type: {dairy_type}")

            factor = FOOD_FACTORS["dairy"][dairy_type]
            avg_kg = FOOD_FACTORS["dairy"]["avg_kg"]
            return servings * avg_kg * factor

        elif activity_type == "food_waste":
            freq = details.get("frequency", "weekly")
            return FOOD_FACTORS["food_waste"].get(freq, 1.0) * 4.5

        # ------------------ SHOPPING ------------------
        elif activity_type == "clothing":
            frequency = details.get("frequency", "monthly")
            return SHOPPING_FACTORS["clothing"].get(frequency, 10.0)

        elif activity_type == "electronics":
            frequency = details.get("frequency", "rare")
            return SHOPPING_FACTORS["electronics"].get(frequency, 50.0)

        elif activity_type == "online_shopping":
            orders = details.get("orders_per_month", 0)
            returns = details.get("returns_per_month", 0)
            return orders * SHOPPING_FACTORS["online_shopping"]["order_factor"] + returns * SHOPPING_FACTORS["online_shopping"]["return_factor"]

        # ------------------ HOUSEHOLD ------------------
        elif activity_type in ["electricity_use", "gas_use", "water_use"]:
            key = activity_type
            try:
                if key == "water_use":
                    val = float(details.get("litres_per_day", 0))
                else:
                    val = float(details.get("kwh_per_month", 0))
            except (TypeError, ValueError):
                raise HTTPException(status_code=400, detail=f"Invalid numeric value for {key}")

            return val * HOUSEHOLD_FACTORS[key]

        # ------------------ WASTE ------------------
        elif activity_type == "plastic_waste":
            try:
                bags = float(details.get("bags_per_week", 0))
            except (TypeError, ValueError):
                raise HTTPException(status_code=400, detail="Invalid value for bags_per_week")
            return bags * WASTE_FACTORS["plastic_waste"]

        elif activity_type == "general_waste":
            try:
                kg_per_week = float(details.get("kg_per_week", 0))
            except (TypeError, ValueError):
                raise HTTPException(status_code=400, detail="Invalid value for kg_per_week")
            return kg_per_week * WASTE_FACTORS["general_waste"]

        elif activity_type == "recycling":
            try:
                percent = float(details.get("percent", 0))
            except (TypeError, ValueError):
                raise HTTPException(status_code=400, detail="Invalid value for percent")
            return max(0, (100 - percent) * WASTE_FACTORS["recycling"])
      
        # ------------------ LIFESTYLE ------------------
        elif activity_type in ["streaming", "gaming"]:
            try:
                hours = float(details.get("hours_per_week", 0))
            except (TypeError, ValueError):
                raise HTTPException(status_code=400, detail=f"Invalid value for hours_per_week for {activity_type}")
            return hours * LIFESTYLE_FACTORS[activity_type]

        elif activity_type == "events":
            try:
                per_year = float(details.get("per_year", 0))
            except (TypeError, ValueError):
                raise HTTPException(status_code=400, detail="Invalid value for per_year")
            return per_year * LIFESTYLE_FACTORS["events"]

        elif activity_type == "hotel_stays":
            try:
                nights = float(details.get("nights_per_year", 0))
            except (TypeError, ValueError):
                raise HTTPException(status_code=400, detail="Invalid value for nights_per_year")
            return nights * LIFESTYLE_FACTORS["hotel_stays"]
        else:
            return 0.0

    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Missing or invalid key in details: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating carbon footprint: {e}")


def suggest_offsets(carbon_kg: float) -> list[str]:
    """
    Return a list of offset suggestions based on carbon footprint (kg CO2).
    """
    if carbon_kg < 50:
        return [
            "Plant 1 tree (absorbs ~20kg CO₂/year)",
            "Cycle instead of driving once a week",
            "Volunteer with local environmental group"
        ]
    elif carbon_kg < 200:
        return [
            "Plant 5 trees",
            "Switch 2 meat meals to vegetarian per week",
            "Join a community gardening project"
        ]
    elif carbon_kg < 500:
        return [
            "Plant 10 trees",
            "Use public transport instead of car twice a week",
            "Upgrade to LED lighting at home",
            "Participate in local habitat restoration volunteering"
        ]
    else:
        return [
            "Plant 20+ trees",
            "Switch to renewable energy provider",
            "Reduce air travel where possible",
            "Contribute to reforestation charities"
        ]


def calculate_points(carbon_kg: float) -> int:
    """Example gamification: 10 points per kg CO2 offset, capped at 100 points."""
    return int(min(carbon_kg * 10, 100))


def get_user_points(user) -> int:
    """Sum points for all completed footprints of a user."""
    return sum(calculate_points(f.carbon_kg) for f in getattr(user, "footprints", []) if getattr(f, "completed", False))
