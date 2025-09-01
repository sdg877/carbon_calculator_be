import sys
import os
import pytest
from fastapi import HTTPException

# Ensure the 'app' package can be found
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.carbon import calculate_carbon, suggest_offsets


def test_calculate_carbon_valid_driving():
    details = {"commute": "medium", "fuel_type": "petrol"}
    carbon = calculate_carbon("driving", details)
    assert isinstance(carbon, float)
    assert carbon > 0


def test_calculate_carbon_invalid_activity():
    with pytest.raises(HTTPException) as exc:
        calculate_carbon("flying_boat", {})
    assert exc.value.status_code == 400


def test_calculate_carbon_missing_details_key():
    details = {"fuel_type": "petrol"}  # commute missing
    carbon = calculate_carbon("driving", details)
    # should use default commute 'short' = 8 km * factor
    assert carbon == 8 * 0.192


def test_suggest_offsets_ranges():
    low = suggest_offsets(30)
    mid = suggest_offsets(150)
    high = suggest_offsets(300)
    very_high = suggest_offsets(600)

    assert "Plant 1 tree" in low[0]
    assert "Plant 5 trees" in mid[0]
    assert "Plant 10 trees" in high[0]
    assert "Plant 20+" in very_high[0]
