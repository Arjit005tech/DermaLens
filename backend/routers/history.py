from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc

from database import get_db
from models.schemas import Report, User, ReportOut
from routers.auth import get_current_user

router = APIRouter(prefix="/history", tags=["history"])


@router.get("", response_model=list[ReportOut])
def get_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Report)
        .filter(Report.user_id == current_user.id)
        .order_by(desc(Report.created_at))
        .all()
    )
