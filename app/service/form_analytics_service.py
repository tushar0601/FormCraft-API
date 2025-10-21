from typing import List
from uuid import UUID
from sqlalchemy.orm import Session

from app.domain.analytics.schema import FormAnalyserMainResponse, FormBlockMainResponse
from app.repository.form_analytics_repository import FormAnalyticsRepository


class FormAnalyticsService:

    def __init__(self, db: Session):
        self.repo = FormAnalyticsRepository(db=db)

    def get_main_page_data(self, user_id: UUID) -> FormAnalyserMainResponse:
        rows = self.repo.get_main_page_rows(user_id=user_id)

        form_data: List[FormBlockMainResponse] = [
            FormBlockMainResponse(
                form_id=r.form_id,
                title=r.title,
                response_count=(r.response_count or 0),
                completion_rate=(
                    float(r.completion_rate) if r.completion_rate is not None else 0.0
                ),
                type=r.type,
                created_at=r.created_at,
            )
            for r in rows
        ]

        total_forms = len(form_data)
        total_responses = sum(item.response_count for item in form_data)
        avg_completion_rate = (
            round(sum(item.completion_rate for item in form_data) / total_forms, 2)
            if total_forms > 0
            else 0.0
        )

        return FormAnalyserMainResponse(
            total_forms=total_forms,
            total_responses=total_responses,
            avg_completion_rate=avg_completion_rate,
            form_data=form_data,
        )
