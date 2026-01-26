from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime
from datetime import timedelta
from .. import models, schemas, auth
from ..database import get_db
from ..services.carbon import calculate_carbon, suggest_offsets

router = APIRouter(prefix="/footprints", tags=["Footprints"])


def get_current_user(
    token: str = Depends(auth.oauth2_scheme), db: Session = Depends(get_db)
):
    return auth.get_current_user(token, db)


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
    offsets = suggest_offsets(carbon_kg)

    first_footprint = models.Footprint(
        activity_type=footprint.activity_type,
        carbon_kg=carbon_kg,
        user_id=user.id,
        details=footprint.details,
        entry_date=footprint.entry_date,
        is_recurring=footprint.is_recurring,
        recurrence_frequency=footprint.recurrence_frequency,
        suggested_offsets=offsets,
    )
    db.add(first_footprint)

    if footprint.is_recurring:
        start_date = footprint.entry_date

        max_allowed_future = start_date + timedelta(days=365)
        requested_end = footprint.recurrence_end_date or (
            start_date + timedelta(weeks=26)
        )

        end_limit = min(requested_end, max_allowed_future)

        current_date = start_date
        entries_count = 0

        while current_date < end_limit and entries_count < 366:
            current_date += timedelta(days=1)
            should_add = False

            if footprint.recurrence_frequency == "daily":
                should_add = True
            elif (
                footprint.recurrence_frequency == "weekday"
                and current_date.weekday() < 5
            ):
                should_add = True
            elif (
                footprint.recurrence_frequency == "weekly"
                and (current_date - start_date).days % 7 == 0
            ):
                should_add = True
            elif footprint.recurrence_frequency == "monthly":
                if current_date.day == start_date.day:
                    should_add = True

            if should_add:
                future_footprint = models.Footprint(
                    activity_type=footprint.activity_type,
                    carbon_kg=carbon_kg,
                    user_id=user.id,
                    details=footprint.details,
                    entry_date=current_date,
                    is_recurring=True,
                    recurrence_frequency=footprint.recurrence_frequency,
                    suggested_offsets=offsets,
                )
                db.add(future_footprint)
                entries_count += 1

    try:
        db.commit()
        db.refresh(first_footprint)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

    return first_footprint


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
    daily_user_totals = (
        db.query(
            models.Footprint.user_id,
            func.date(models.Footprint.created_at).label("created_at_date"),
            func.sum(models.Footprint.carbon_kg).label("total_carbon_kg"),
        )
        .group_by(models.Footprint.user_id, "created_at_date")
        .subquery()
    )

    daily_average_footprints = (
        db.query(
            func.date(daily_user_totals.c.created_at_date).label("created_at"),
            func.avg(daily_user_totals.c.total_carbon_kg).label("carbon_kg"),
        )
        .group_by("created_at")
        .order_by("created_at")
        .all()
    )

    formatted_results = [
        {"created_at": row.created_at, "carbon_kg": row.carbon_kg}
        for row in daily_average_footprints
    ]

    return formatted_results


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