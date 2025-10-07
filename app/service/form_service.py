from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from uuid import UUID
from fastapi import HTTPException, status

from app.utils.service_utils import generate_slug
from app.repository.form_repository import FormRepository
from app.domain.form.schema import FormCreateRequestSchema, FormUpdateRequestSchema
from app.domain.form.model import Form, FormBlock


class FormService:
    def __init__(self, db: Session):
        self.repo = FormRepository(db=db)

    def get_all_forms(self, user_id: UUID, skip: int, limit: int):
        return self.repo.get_all_forms(user_id=user_id, skip=skip, limit=limit)

    def get_form_by_slug(self, slug: str) -> Form:
        form = self.repo.get_by_slug(slug)
        if not form:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Form not found"
            )
        return form

    def update_form(self, payload: FormUpdateRequestSchema, user_id: UUID) -> Form:
        form = self.repo.get_by_slug(payload.slug)
        if form is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Form does not exist"
            )

        form.title = payload.title
        form.access = payload.access
        form.status = payload.status
        form.created_by = user_id
        form_blocks: List[FormBlock] = []
        for q in payload.questions:
            form_blocks.append(
                FormBlock(
                    form_id=form.id,
                    sort_order=q.question_order,
                    name=q.title,
                    block_type=q.type,
                    config=q.config,
                )
            )

        return self.repo.update_form(new_form=form, form_blocks=form_blocks)

    def create_form(self, payload: FormCreateRequestSchema, user_id: UUID) -> Form:
        try:
            new_slug = generate_slug()
            new_form = Form(
                title=payload.title,
                slug=new_slug,
                status=payload.status,
                access=payload.access,
                created_by=user_id,
            )

            form_blocks: List[FormBlock] = []
            for q in payload.questions:
                form_blocks.append(
                    FormBlock(
                        form_id=None,
                        sort_order=q.question_order,
                        name=q.title,
                        block_type=q.type,
                        config=q.config,
                    )
                )

            return self.repo.create_form(new_form=new_form, form_blocks=form_blocks)

        except IntegrityError as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A form with this slug already exists.",
            )
