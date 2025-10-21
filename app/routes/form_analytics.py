from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db


from app.core.auth import get_current_user, UserData
from app.service.form_analytics_service import FormAnalyticsService
from app.domain.analytics.schema import FormAnalyserMainResponse

router = APIRouter()


def get_form_service(db: Session = Depends(get_db)) -> FormAnalyticsService:
    return FormAnalyticsService(db=db)


@router.get("/main-page")
async def get_main_page_data(
    service: FormAnalyticsService = Depends(get_form_service),
    user: UserData = Depends(get_current_user),
) -> FormAnalyserMainResponse:
    return service.get_main_page_data(user_id=user.id)
