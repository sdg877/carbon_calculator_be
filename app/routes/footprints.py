from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict
from datetime import datetime
from .. import models, schemas, auth
from ..database import get_db
from ..services.carbon import calculate_carbon, suggest_offsets, get_user_points

router = APIRouter(prefix="/footprints", tags=["Footprints"])

# ------------------ USER DEPENDENCY ------------------
def get_current_user(token: str = Depends(auth.oauth2_scheme), db: Session = Depends(get_db)):
    return auth.get_current_user(token, db)


# ------------------ ROUTES ------------------

@router.get("/", response_model=List[schemas.FootprintResponse])
def get_user_footprints(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return db.query(models.Footprint).filter(models.Footprint.user_id == user.id).all()


@router.post("/", response_model=schemas.FootprintResponse)
def create_footprint(footprint: schemas.FootprintCreate, db: Session = Depends(get_db),
                     user: models.User = Depends(get_current_user)):
    carbon_kg = calculate_carbon(footprint.activity_type, footprint.details)
    db_footprint = models.Footprint(activity_type=footprint.activity_type,
                                    carbon_kg=carbon_kg,
                                    user_id=user.id)
    try:
        db.add(db_footprint)
        db.commit()
        db.refresh(db_footprint)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

    offsets = suggest_offsets(carbon_kg)
    return {"id": db_footprint.id,
            "activity_type": db_footprint.activity_type,
            "carbon_kg": db_footprint.carbon_kg,
            "suggested_offsets": offsets}


@router.post("/bulk", response_model=List[schemas.FootprintResponse])
def create_multiple_footprints(footprints: List[schemas.FootprintCreate], db: Session = Depends(get_db),
                               user: models.User = Depends(get_current_user)):
    if not footprints:
        raise HTTPException(status_code=400, detail="No footprints provided")

    db_objects = []
    try:
        for footprint in footprints:
            carbon_kg = calculate_carbon(footprint.activity_type, footprint.details)
            db_footprint = models.Footprint(activity_type=footprint.activity_type,
                                            carbon_kg=carbon_kg,
                                            user_id=user.id)
            db.add(db_footprint)
            db_objects.append(db_footprint)
        db.commit()
        for obj in db_objects:
            db.refresh(obj)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

    return db_objects


@router.patch("/{footprint_id}/complete", response_model=dict)
def mark_footprint_completed(footprint_id: int, db: Session = Depends(get_db),
                             user: models.User = Depends(get_current_user)):
    footprint = db.query(models.Footprint).filter(models.Footprint.id == footprint_id,
                                                  models.Footprint.user_id == user.id).first()
    if not footprint:
        raise HTTPException(status_code=404, detail="Footprint not found")

    if footprint.completed:
        return {"detail": "Footprint already completed"}

    footprint.completed = True
    footprint.completed_at = datetime.utcnow()
    db.commit()
    db.refresh(footprint)
    return {"detail": f"Footprint {footprint_id} marked as completed"}


@router.delete("/bulk", response_model=dict)
def bulk_delete_footprints(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    deleted_count = db.query(models.Footprint).filter(models.Footprint.user_id == user.id).delete(synchronize_session=False)
    db.commit()
    return {"detail": f"Deleted {deleted_count} footprints for user {user.username}"}


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
def get_user_gamification(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    footprints = db.query(models.Footprint).filter(models.Footprint.user_id == user.id).all()
    completed_footprints = [f for f in footprints if getattr(f, "completed", False)]
    total_points = get_user_points(user)
    monthly_progress = get_monthly_progress(footprints)

    return {
        "total_footprints": len(footprints),
        "completed_footprints": len(completed_footprints),
        "points": total_points,
        "monthly_progress": monthly_progress,
    }
