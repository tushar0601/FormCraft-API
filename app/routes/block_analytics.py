from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from uuid import UUID

from app.core.auth import get_current_user, UserData
from app.service.block_analytics_service import BlockAnalyticsService


router = APIRouter()


def get_form_service(db: Session = Depends(get_db)) -> BlockAnalyticsService:
    return BlockAnalyticsService(db=db)

@router.get("/form-analysis")
async def get_main_page_data(
    form_id: UUID,
    service: BlockAnalyticsService = Depends(get_form_service),
    user: UserData = Depends(get_current_user),
):
    return service.get_analytics_data(form_id=form_id)