from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.repository.response_repository import ResponseRepository
from app.domain.response.schema import ResponseCreateSchema
from app.domain.response.model import FormResponse, BlockResponse
from app.service.block_analytics_service import BlockAnalyticsService
from uuid import UUID
from datetime import datetime, timezone


class ResponseService:
    def __init__(self, db: Session):
        self.repo = ResponseRepository(db=db)
        self.analytics_service = BlockAnalyticsService(db=db)

    def get_all_responses(self, skip: int, limit: int):
        return self.repo.get_all_responses(skip=skip, limit=limit)

    def create_response(
        self, payload: ResponseCreateSchema, user_id: UUID
    ) -> FormResponse:
        try:
            new_response = FormResponse(
                form_id=payload.form_id,
                respondent_user_id=user_id,
                submitted_ip=payload.submitted_ip,
                status=payload.status,
                started_at=datetime.now(timezone.utc),
                meta_data=payload.meta_data,
            )

            response_blocks: List[BlockResponse] = []
            for q in payload.question_responses:
                response_blocks.append(
                    BlockResponse(
                        response_id=None,
                        form_block_id=q.form_block_id,
                        block_type=q.block_type,
                        value=q.value,
                        time_to_answer_ms=q.time_to_answer_ms,
                    )
                )

            for q in payload.question_responses:
                if q.block_type == "text":
                    self.analytics_service.handle_text_analytics(
                        text=str(q.value["text"]),
                        block_id=q.form_block_id,
                        form_id=payload.form_id,
                    )
                elif q.block_type == "checkbox":
                    self.analytics_service.handle_checkbox_analytics(
                        answer_options=q.value["selected"],
                        block_id=q.form_block_id,
                        form_id=payload.form_id,
                    )
                else:
                    self.analytics_service.handle_mcq_analytics(
                        option=q.value["selected"],
                        block_id=q.form_block_id,
                        form_id=payload.form_id,
                    )

            return self.repo.create_response(
                new_reponse=new_response,
                block_responses=response_blocks,
            )

        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="error",
            )
