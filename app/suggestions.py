from fastapi import APIRouter, Query
from typing import List, Dict, Any

router = APIRouter()

def get_offset_suggestions(activity_type: str) -> List[Dict[str, Any]]:
    suggestions = {
        "transport": [
            {
                "title": "Join a tree-planting day",
                "description": "Local councils and groups often run weekend events where you can directly offset emissions by planting trees.",
                "link": "https://www.tcv.org.uk/get-involved/volunteering"
            },
            {
                "title": "Community car-sharing schemes",
                "description": "Offset car journeys by joining a local car club. You’ll reduce overall traffic emissions and support sustainable transport.",
                "link": "https://www.enterprisecarclub.co.uk"
            },
        ],
        "energy": [
            {
                "title": "Support community solar",
                "description": "Invest or volunteer in a cooperative solar farm to help fund renewable energy generation in your area.",
                "link": "https://www.communityenergyengland.org"
            },
            {
                "title": "Retrofit volunteering",
                "description": "Some charities run DIY retrofit and insulation programmes for low-income households — help reduce energy demand directly.",
                "link": "https://www.retrofitacademy.org"
            },
        ],
        "food": [
            {
                "title": "Community gardening",
                "description": "Help grow sustainable food locally, reduce transport emissions, and improve urban green space.",
                "link": "https://www.farmgarden.org.uk"
            },
            {
                "title": "Food redistribution volunteering",
                "description": "Join food waste reduction charities that save surplus food and redistribute it to communities.",
                "link": "https://fareshare.org.uk/volunteer"
            },
        ],
        "default": [
            {
                "title": "Habitat restoration volunteering",
                "description": "Rewilding and conservation projects help absorb CO₂ and restore biodiversity.",
                "link": "https://www.conservationvolunteers.org.uk"
            },
            {
                "title": "Support reforestation charities",
                "description": "If you can’t volunteer, donate to projects that actively restore forests in the UK and abroad.",
                "link": "https://ecologi.com"
            },
        ],
    }

    return suggestions.get(activity_type.lower(), suggestions["default"])


@router.get("/suggestions")
def fetch_suggestions(activity_type: str = Query("default", description="Type of activity (transport, energy, food, etc.)")):
    return {
        "activity_type": activity_type,
        "suggestions": get_offset_suggestions(activity_type)
    }
