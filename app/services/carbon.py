from typing import List
from datetime import datetime
from .. import models

# ------------------ CARBON CALCULATIONS ------------------

def calculate_carbon(activity_type: str, details: dict) -> float:
    miles_to_km = 1.60934

    # ------------------ TRANSPORT ------------------
    if activity_type == "flight":
        flight_type = details.get("flight_type", "short")
        distance_km = 500 if flight_type == "short" else 2000
        return distance_km * 0.115

    elif activity_type == "driving":
        commute = details.get("commute", "short")
        km = {"short": 8, "medium": 16, "long": 32}[commute]
        fuel_type = details.get("fuel_type", "petrol")
        factor = 0.192 if fuel_type == "petrol" else 0.171
        return km * factor

    elif activity_type in ["train", "tube"]:
        commute = details.get("commute", "short")
        km = {"short": 8, "medium": 16, "long": 32}[commute]
        return km * 0.041

    elif activity_type == "bus":
        commute = details.get("commute", "short")
        km = {"short": 8, "medium": 16, "long": 32}[commute]
        return km * 0.105

    # ------------------ FOOD ------------------
    elif activity_type == "meat":
        servings = details.get("servings_per_week", 0)
        meat_type = details.get("type", "beef")
        factors = {"beef": 27.0, "lamb": 24.0, "pork": 12.0, "chicken": 6.9, "fish": 6.0}
        avg_kg = 0.2
        return servings * avg_kg * factors.get(meat_type, 10.0)

    elif activity_type == "dairy":
        servings = details.get("servings_per_week", 0)
        dairy_type = details.get("type", "milk")
        factors = {"milk": 1.9, "cheese": 13.5, "butter": 24.0, "yoghurt": 2.2}
        avg_kg = 0.2
        return servings * avg_kg * factors.get(dairy_type, 2.0)

    elif activity_type == "food_waste":
        freq = details.get("frequency", "weekly")
        kg_map = {"rare": 0.5, "weekly": 2.0}
        return kg_map.get(freq, 1.0) * 4.5

    # ------------------ SHOPPING ------------------
    elif activity_type == "clothing":
        frequency = details.get("frequency", "monthly")
        factor_map = {"monthly": 10.0, "weekly": 40.0}
        return factor_map.get(frequency, 10.0)

    elif activity_type == "electronics":
        frequency = details.get("frequency", "rare")
        factor_map = {"rare": 50.0, "frequent": 200.0}
        return factor_map.get(frequency, 50.0)

    elif activity_type == "online_shopping":
        orders = details.get("orders_per_month", 0)
        returns = details.get("returns_per_month", 0)
        return (orders * 1.0) + (returns * 3.0)

    # ------------------ HOUSEHOLD ------------------
    elif activity_type == "electricity_use":
        kwh = details.get("kwh_per_month", 0)
        return kwh * 0.233

    elif activity_type == "gas_use":
        kwh = details.get("kwh_per_month", 0)
        return kwh * 0.184

    elif activity_type == "water_use":
        litres = details.get("litres_per_day", 0)
        return litres * 0.0003 * 30

    # ------------------ WASTE ------------------
    elif activity_type == "plastic_waste":
        bags = details.get("bags_per_week", 0)
        return bags * 0.5 * 52 / 12

    elif activity_type == "general_waste":
        kg_per_week = details.get("kg_per_week", 0)
        return kg_per_week * 52 / 12 * 1.5

    elif activity_type == "recycling":
        percent = details.get("percent", 0)
        return max(0, (100 - percent) * 0.2)

    # ------------------ LIFESTYLE ------------------
    elif activity_type == "streaming":
        hours = details.get("hours_per_week", 0)
        return hours * 0.055 * 4

    elif activity_type == "gaming":
        hours = details.get("hours_per_week", 0)
        return hours * 0.05 * 4

    elif activity_type == "events":
        per_year = details.get("per_year", 0)
        return per_year * 20 / 12

    elif activity_type == "hotel_stays":
        nights = details.get("nights_per_year", 0)
        return nights * 82 / 12

    return 0.0


# ------------------ OFFSET SUGGESTIONS ------------------

def suggest_offsets(carbon_kg: float) -> List[str]:
    suggestions = []

    if carbon_kg < 50:
        suggestions.append("Plant 1 tree (absorbs ~20kg CO₂/year)")
        suggestions.append("Cycle instead of driving once a week")
        suggestions.append("Volunteer at local rewilding project")

    elif carbon_kg < 200:
        suggestions.append("Plant 5 trees")
        suggestions.append("Switch 2 meat meals to vegetarian per week")
        suggestions.append("Join community gardening initiatives")

    elif carbon_kg < 500:
        suggestions.append("Plant 10 trees")
        suggestions.append("Use public transport instead of car twice a week")
        suggestions.append("Upgrade to LED lighting at home")
        suggestions.append("Participate in renewable energy community projects")

    else:
        suggestions.append("Plant 20+ trees")
        suggestions.append("Switch to renewable energy provider")
        suggestions.append("Reduce air travel where possible")
        suggestions.append("Volunteer for habitat restoration programmes")

    return suggestions


# ------------------ POINTS / GAMIFICATION ------------------

def calculate_points(footprint: models.Footprint) -> int:
    return int(min(footprint.carbon_kg * 10, 100))

def get_user_points(user: models.User) -> int:
    return sum(calculate_points(f) for f in user.footprints if getattr(f, "completed", False))
