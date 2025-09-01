from typing import Dict

def calculate_carbon(activity_type: str, details: Dict) -> float:
    """
    Calculate carbon footprint (kg CO2) based on activity type and details.
    """
    # ------------------ TRANSPORT ------------------
    if activity_type == "flight":
        distance_km = 500 if details.get("flight_type", "short") == "short" else 2000
        return distance_km * 0.115

    elif activity_type == "driving":
        commute = details.get("commute", "short")
        km = {"short": 8, "medium": 16, "long": 32}.get(commute, 8)
        factor = 0.192 if details.get("fuel_type", "petrol") == "petrol" else 0.171
        return km * factor

    elif activity_type in ["train", "tube"]:
        commute = details.get("commute", "short")
        km = {"short": 8, "medium": 16, "long": 32}.get(commute, 8)
        return km * 0.041

    elif activity_type == "bus":
        commute = details.get("commute", "short")
        km = {"short": 8, "medium": 16, "long": 32}.get(commute, 8)
        return km * 0.105

    # ------------------ FOOD ------------------
    if activity_type == "meat":
        servings = details.get("servings_per_week", 0)
        factors = {"beef": 27.0, "lamb": 24.0, "pork": 12.0, "chicken": 6.9, "fish": 6.0}
        avg_kg = 0.2
        return servings * avg_kg * factors.get(details.get("type", "beef"), 10.0)

    elif activity_type == "dairy":
        servings = details.get("servings_per_week", 0)
        factors = {"milk": 1.9, "cheese": 13.5, "butter": 24.0, "yoghurt": 2.2}
        avg_kg = 0.2
        return servings * avg_kg * factors.get(details.get("type", "milk"), 2.0)

    elif activity_type == "food_waste":
        freq = details.get("frequency", "weekly")
        kg_map = {"rare": 0.5, "weekly": 2.0}
        return kg_map.get(freq, 1.0) * 4.5

    # ------------------ SHOPPING ------------------
    if activity_type == "clothing":
        factor_map = {"monthly": 10.0, "weekly": 40.0}
        return factor_map.get(details.get("frequency", "monthly"), 10.0)

    elif activity_type == "electronics":
        factor_map = {"rare": 50.0, "frequent": 200.0}
        return factor_map.get(details.get("frequency", "rare"), 50.0)

    elif activity_type == "online_shopping":
        orders = details.get("orders_per_month", 0)
        returns = details.get("returns_per_month", 0)
        return orders + returns * 3.0

    # ------------------ HOUSEHOLD ------------------
    if activity_type == "electricity_use":
        return details.get("kwh_per_month", 0) * 0.233

    elif activity_type == "gas_use":
        return details.get("kwh_per_month", 0) * 0.184

    elif activity_type == "water_use":
        return details.get("litres_per_day", 0) * 0.0003 * 30

    # ------------------ WASTE ------------------
    if activity_type == "plastic_waste":
        return details.get("bags_per_week", 0) * 0.5 * 52 / 12

    elif activity_type == "general_waste":
        return details.get("kg_per_week", 0) * 52 / 12 * 1.5

    elif activity_type == "recycling":
        percent = details.get("percent", 0)
        return max(0, (100 - percent) * 0.2)

    # ------------------ LIFESTYLE ------------------
    if activity_type == "streaming":
        return details.get("hours_per_week", 0) * 0.055 * 4

    elif activity_type == "gaming":
        return details.get("hours_per_week", 0) * 0.05 * 4

    elif activity_type == "events":
        return details.get("per_year", 0) * 20 / 12

    elif activity_type == "hotel_stays":
        return details.get("nights_per_year", 0) * 82 / 12

    return 0.0


def suggest_offsets(carbon_kg: float) -> list[str]:
    """
    Return a list of offset suggestions based on carbon footprint.
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
