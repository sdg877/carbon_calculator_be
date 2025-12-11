import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict
from datetime import datetime
from .. import models, schemas, auth
from ..database import get_db
from ..services.carbon import calculate_carbon, suggest_offsets, get_user_points

router = APIRouter(prefix="/footprints", tags=["Footprints"])


# ------------------ USER DEPENDENCY ------------------
def get_current_user(
    token: str = Depends(auth.oauth2_scheme), db: Session = Depends(get_db)
):
    return auth.get_current_user(token, db)


# ------------------ ROUTES ------------------


@router.get("/", response_model=List[schemas.FootprintResponse])
def get_user_footprints(
    db: Session = Depends(get_db), user: models.User = Depends(get_current_user)
):
    return db.query(models.Footprint).filter(models.Footprint.user_id == user.id).all()


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
        user_id=user.id,
        details=footprint.details,
    )
    try:
        db.add(db_footprint)
        db.commit()
        db.refresh(db_footprint)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

    offsets = suggest_offsets(carbon_kg)
    db_footprint.suggested_offsets = offsets
    db.commit()
    db.refresh(db_footprint)

    return db_footprint


@router.post("/bulk", response_model=List[schemas.FootprintResponse])
def create_multiple_footprints(
    footprints: List[schemas.FootprintCreate],
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    if not footprints:
        raise HTTPException(status_code=400, detail="No footprints provided")

    db_objects = []
    try:
        for footprint in footprints:
            carbon_kg = calculate_carbon(footprint.activity_type, footprint.details)
            db_footprint = models.Footprint(
                activity_type=footprint.activity_type,
                carbon_kg=carbon_kg,
                user_id=user.id,
            )
            db.add(db_footprint)
            db_objects.append(db_footprint)
        db.commit()
        for obj in db_objects:
            db.refresh(obj)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

    return db_objects


@router.delete("/bulk", response_model=dict)
def bulk_delete_footprints(
    db: Session = Depends(get_db), user: models.User = Depends(get_current_user)
):
    deleted_count = (
        db.query(models.Footprint)
        .filter(models.Footprint.user_id == user.id)
        .delete(synchronize_session=False)
    )
    db.commit()
    return {"detail": f"Deleted {deleted_count} footprints for user {user.username}"}


@router.get("/all", response_model=List[schemas.FootprintAverageResponse])
def get_all_footprints(
    db: Session = Depends(get_db), user: models.User = Depends(get_current_user)
):
    # Subquery to calculate each user's daily total
    daily_user_totals = (
        db.query(
            models.Footprint.user_id,
            func.date(models.Footprint.created_at).label("created_at_date"),
            func.sum(models.Footprint.carbon_kg).label("total_carbon_kg"),
        )
        .group_by(models.Footprint.user_id, "created_at_date")
        .subquery()
    )

    # Main query to calculate the daily average of those user totals
    daily_average_footprints = (
        db.query(
            func.date(daily_user_totals.c.created_at_date).label("created_at"),
            func.avg(daily_user_totals.c.total_carbon_kg).label("carbon_kg"),
        )
        .group_by("created_at")
        .order_by("created_at")
        .all()
    )

    # Format the results to match the schema
    formatted_results = [
        {"created_at": row.created_at, "carbon_kg": row.carbon_kg}
        for row in daily_average_footprints
    ]

    return formatted_results


# ------------------ GAMIFICATION ------------------


def get_monthly_progress(footprints: List[models.Footprint]) -> Dict[str, float]:
    """Returns monthly CO₂ totals for a user."""
    from collections import defaultdict

    monthly_totals = defaultdict(float)
    for f in footprints:
        if hasattr(f, "created_at") and f.created_at:
            month = f.created_at.strftime("%Y-%m")
        else:
            month = datetime.utcnow().strftime("%Y-%m")
        monthly_totals[month] += f.carbon_kg
    return dict(monthly_totals)


@router.get("/gamification", response_model=None)
def get_user_gamification(
    db: Session = Depends(get_db), user: models.User = Depends(get_current_user)
):
    footprints = (
        db.query(models.Footprint).filter(models.Footprint.user_id == user.id).all()
    )
    completed_footprints = [f for f in footprints if getattr(f, "completed", False)]
    total_points = get_user_points(user)
    monthly_progress = get_monthly_progress(footprints)

    return {
        "total_footprints": len(footprints),
        "completed_footprints": len(completed_footprints),
        "points": total_points,
        "monthly_progress": monthly_progress,
    }


@router.get("/self", response_model=List[schemas.FootprintResponse])
def get_my_footprints(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    footprints = (
        db.query(models.Footprint)
        .filter(models.Footprint.user_id == current_user.id)
        .all()
    )
    return footprints
