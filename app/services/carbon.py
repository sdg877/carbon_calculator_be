from typing import Dict, List  # Fixed: added List
from fastapi import HTTPException

# ------------------ CONSTANTS ------------------
VALID_ACTIVITIES = {
    "flight",
    "driving",
    "train",
    "tube",
    "bus",
    "meat",
    "dairy",
    "food_waste",
    "clothing",
    "electronics",
    "online_shopping",
    "electricity_use",
    "gas_use",
    "water_use",
    "plastic_waste",
    "general_waste",
    "recycling",
    "streaming",
    "gaming",
    "events",
    "hotel_stays",
}

TRANSPORT_FACTORS = {
    "flight": {"short": 500, "long": 2000, "factor": 0.115},
    "driving": {"short": 8, "medium": 16, "long": 32, "petrol": 0.192, "other": 0.171},
    "train": 0.041,
    "tube": 0.041,
    "bus": 0.105,
}

FOOD_FACTORS = {
    "meat": {
        "beef": 27.0,
        "lamb": 24.0,
        "pork": 12.0,
        "chicken": 6.9,
        "fish": 6.0,
        "avg_kg": 0.2,
    },
    "dairy": {
        "milk": 1.9,
        "cheese": 13.5,
        "butter": 24.0,
        "yoghurt": 2.2,
        "avg_kg": 0.2,
    },
    "food_waste": {"rare": 0.5, "weekly": 2.0},
}

SHOPPING_FACTORS = {
    "clothing": {"monthly": 10.0, "weekly": 40.0},
    "electronics": {"rare": 50.0, "frequent": 200.0},
    "online_shopping": {"order_factor": 1.0, "return_factor": 3.0},
}

HOUSEHOLD_FACTORS = {
    "electricity_use": 0.233,
    "gas_use": 0.184,
    "water_use": 0.0003 * 30,
}

WASTE_FACTORS = {
    "plastic_waste": 0.5 * 52 / 12,
    "general_waste": 1.5 * 52 / 12,
    "recycling": 0.2,
}

LIFESTYLE_FACTORS = {
    "streaming": 0.055 * 4,
    "gaming": 0.05 * 4,
    "events": 20 / 12,
    "hotel_stays": 82 / 12,
}


# ------------------ FUNCTIONS ------------------
def calculate_carbon(activity_type: str, details: Dict) -> float:
    """
    Calculate carbon footprint (kg CO2) based on activity type and details.
    """
    if activity_type not in VALID_ACTIVITIES:
        raise HTTPException(
            status_code=400, detail=f"Invalid activity_type: {activity_type}"
        )

    if not isinstance(details, dict):
        raise HTTPException(status_code=400, detail="Details must be a dictionary")

    try:
        if activity_type == "flight":
            distance_km = TRANSPORT_FACTORS["flight"].get(
                details.get("flight_type", "short"), 500
            )
            return round(distance_km * TRANSPORT_FACTORS["flight"]["factor"], 1)

        elif activity_type == "driving":
            commute = details.get("commute", "short")
            km = TRANSPORT_FACTORS["driving"].get(commute, 8)
            fuel_type = details.get("fuel_type", "petrol")
            factor = (
                TRANSPORT_FACTORS["driving"]["petrol"]
                if fuel_type == "petrol"
                else TRANSPORT_FACTORS["driving"]["other"]
            )
            return round(km * factor, 1)

        elif activity_type in ["train", "tube"]:
            commute = details.get("commute", "short")
            km = {"short": 8, "medium": 16, "long": 32}.get(commute, 8)
            return round(km * TRANSPORT_FACTORS[activity_type], 1)

        elif activity_type == "bus":
            commute = details.get("commute", "short")
            km = {"short": 8, "medium": 16, "long": 32}.get(commute, 8)
            return round(km * TRANSPORT_FACTORS["bus"], 1)

        elif activity_type == "meat":
            servings = float(details.get("servings_per_week", 0))
            meat_type = details.get("type", "beef")
            factor = FOOD_FACTORS["meat"].get(meat_type, 27.0)
            return round(servings * FOOD_FACTORS["meat"]["avg_kg"] * factor, 1)

        elif activity_type == "dairy":
            servings = float(details.get("servings_per_week", 0))
            dairy_type = details.get("type", "milk")
            factor = FOOD_FACTORS["dairy"].get(dairy_type, 1.9)
            return round(servings * FOOD_FACTORS["dairy"]["avg_kg"] * factor, 1)

        elif activity_type == "food_waste":
            freq = details.get("frequency", "weekly")
            return round(FOOD_FACTORS["food_waste"].get(freq, 1.0) * 4.5, 1)

        elif activity_type == "clothing":
            frequency = details.get("frequency", "monthly")
            return round(SHOPPING_FACTORS["clothing"].get(frequency, 10.0), 1)

        elif activity_type == "electronics":
            frequency = details.get("frequency", "rare")
            return round(SHOPPING_FACTORS["electronics"].get(frequency, 50.0), 1)

        elif activity_type == "online_shopping":
            orders = float(details.get("orders_per_month", 0))
            returns = float(details.get("returns_per_month", 0))
            return round(
                orders * SHOPPING_FACTORS["online_shopping"]["order_factor"]
                + returns * SHOPPING_FACTORS["online_shopping"]["return_factor"],
                1,
            )

        elif activity_type in ["electricity_use", "gas_use", "water_use"]:
            val = float(
                details.get(
                    (
                        "litres_per_day"
                        if activity_type == "water_use"
                        else "kwh_per_month"
                    ),
                    0,
                )
            )
            return round(val * HOUSEHOLD_FACTORS[activity_type], 1)

        elif activity_type == "plastic_waste":
            bags = float(details.get("bags_per_week", 0))
            return round(bags * WASTE_FACTORS["plastic_waste"], 1)

        elif activity_type == "general_waste":
            kg = float(details.get("kg_per_week", 0))
            return round(kg * WASTE_FACTORS["general_waste"], 1)

        elif activity_type == "recycling":
            percent = float(details.get("percent", 0))
            return round(max(0, (100 - percent) * WASTE_FACTORS["recycling"]), 1)

        elif activity_type in ["streaming", "gaming"]:
            hours = float(details.get("hours_per_week", 0))
            return round(hours * LIFESTYLE_FACTORS[activity_type], 1)

        elif activity_type == "events":
            per_year = float(details.get("per_year", 0))
            return round(per_year * LIFESTYLE_FACTORS["events"], 1)

        elif activity_type == "hotel_stays":
            nights = float(details.get("nights_per_year", 0))
            return round(nights * LIFESTYLE_FACTORS["hotel_stays"], 1)

        return 0.0

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Calculation error: {str(e)}")


def suggest_offsets(carbon_kg: float) -> List[str]:  # Fixed: capital List
    """
    Return a list of offset suggestions based on carbon footprint (kg CO2).
    """
    if carbon_kg < 50:
        return [
            "Plant 1 tree (absorbs ~20kg CO₂/year)",
            "Cycle instead of driving once a week",
            "Volunteer with local environmental group",
        ]
    elif carbon_kg < 200:
        return [
            "Plant 5 trees",
            "Switch 2 meat meals to vegetarian per week",
            "Join a community gardening project",
        ]
    elif carbon_kg < 500:
        return [
            "Plant 10 trees",
            "Use public transport instead of car twice a week",
            "Upgrade to LED lighting at home",
        ]
    else:
        return [
            "Plant 20+ trees",
            "Switch to renewable energy provider",
            "Reduce air travel where possible",
        ]
