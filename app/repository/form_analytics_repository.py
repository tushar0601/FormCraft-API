# repository.py
from typing import List, Tuple
from uuid import UUID
from sqlalchemy import cast, Integer, Float
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.domain.analytics.model import FormAnalytics
from app.domain.form.model import Form


class FormAnalyticsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_main_page_rows(self, user_id: UUID) -> List[Tuple]:
        completion_rate = cast(
            FormAnalytics.details.op("->>")("completion_rate"), Float
        ).label("completion_rate")

        response_count = cast(
            FormAnalytics.details.op("->>")("response_count"), Integer
        ).label("response_count")

        formatted_created_at = func.to_char(Form.created_at, "Mon DD, YYYY").label(
            "created_at"
        )
        rows = (
            self.db.query(
                Form.title.label("title"),
                Form.id.label("form_id"),
                response_count,
                completion_rate,
                Form.access.label("type"),
                formatted_created_at,
            )
            .outerjoin(FormAnalytics, Form.id == FormAnalytics.form_id)
            .filter(Form.created_by == user_id)
            .order_by(Form.created_at.desc())
            .all()
        )
        return rows
