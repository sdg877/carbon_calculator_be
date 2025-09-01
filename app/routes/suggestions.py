from fastapi import APIRouter, Query, HTTPException
from typing import List, Dict, Any

router = APIRouter()

VALID_CATEGORIES = ["transport", "energy", "food", "shopping", "lifestyle", "default"]


def get_offset_suggestions(activity_type: str) -> List[Dict[str, Any]]:
    suggestions = {
        "transport": [
            {
                "title": "Join a tree-planting day",
                "description": "Plant trees locally to offset CO₂ from transport.",
                "link": "https://www.tcv.org.uk/get-involved/volunteering",
            },
            {
                "title": "Community car-sharing schemes",
                "description": "Reduce emissions by sharing rides in your area.",
                "link": "https://www.enterprisecarclub.co.uk",
            },
            {
                "title": "Switch to public transport",
                "description": "Commit to train or bus for regular commutes.",
                "link": "https://www.nationalrail.co.uk/",
            },
            {
                "title": "Offset flight emissions",
                "description": "Donate to verified carbon offset projects for flights.",
                "link": "https://www.goldstandard.org/take-action/offset-your-emissions",
            },
        ],
        "energy": [
            {
                "title": "Support community solar",
                "description": "Invest or volunteer in a local renewable energy project.",
                "link": "https://www.communityenergyengland.org",
            },
            {
                "title": "Home energy retrofits",
                "description": "Help install insulation, draught-proofing or LED lighting for low-income households.",
                "link": "https://www.retrofitacademy.org",
            },
            {
                "title": "Switch to renewable energy",
                "description": "Choose a green energy provider for your home.",
                "link": "https://www.ofgem.gov.uk/energy-switching",
            },
        ],
        "food": [
            {
                "title": "Community gardening",
                "description": "Grow food locally and reduce transport emissions.",
                "link": "https://www.farmgarden.org.uk",
            },
            {
                "title": "Food redistribution volunteering",
                "description": "Help charities save and redistribute surplus food.",
                "link": "https://fareshare.org.uk/volunteer",
            },
            {
                "title": "Switch to plant-based meals",
                "description": "Reduce meat and dairy consumption for a week/month.",
                "link": "https://www.veganuary.com/",
            },
        ],
        "shopping": [
            {
                "title": "Donate or swap clothing",
                "description": "Avoid buying new by donating old items or using clothes swaps.",
                "link": "https://www.traid.org.uk",
            },
            {
                "title": "Buy second-hand electronics",
                "description": "Reduce carbon footprint by reusing devices.",
                "link": "https://www.cex.co.uk/",
            },
            {
                "title": "Reduce online shopping deliveries",
                "description": "Consolidate orders to cut delivery emissions.",
                "link": "https://www.carbontrust.com/resources/carbon-footprint-calculator",
            },
        ],
        "lifestyle": [
            {
                "title": "Limit streaming resolution",
                "description": "Watch HD less often or reduce streaming hours to lower energy use.",
                "link": "https://www.carbontrust.com/resources/carbon-footprint-calculator",
            },
            {
                "title": "Volunteer at events",
                "description": "Assist at local events to support community projects and reduce footprint indirectly.",
                "link": "https://do-it.org/",
            },
        ],
        "default": [
            {
                "title": "Habitat restoration volunteering",
                "description": "Help restore local habitats to absorb CO₂ and support wildlife.",
                "link": "https://www.conservationvolunteers.org.uk",
            },
            {
                "title": "Support reforestation charities",
                "description": "Donate to UK or global tree planting initiatives.",
                "link": "https://ecologi.com",
            },
        ],
    }

    return suggestions.get(activity_type.lower(), suggestions["default"])


@router.get("/suggestions")
def fetch_suggestions(activity_type: str = Query("default", description="...")):
    if activity_type.lower() not in VALID_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid activity type. Must be one of {VALID_CATEGORIES}",
        )
    return {
        "activity_type": activity_type,
        "suggestions": get_offset_suggestions(activity_type),
    }
