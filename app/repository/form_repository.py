from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session, selectinload
from app.domain.form.model import Form, FormBlock


class FormRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_forms(self, user_id: UUID, skip: int, limit: int):
        return (
            self.db.query(Form)
            .filter(Form.created_by == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_slug(self, slug: str) -> Optional[Form]:
        return (
            self.db.query(Form)
            .options(selectinload(Form.blocks))
            .filter(Form.slug == slug)
            .first()
        )

    def create_form(self, new_form: Form, form_blocks: List[FormBlock]) -> Form:
        self.db.add(new_form)
        self.db.flush()

        for b in form_blocks:
            if b.form_id is None:
                b.form_id = new_form.id

        self.db.add_all(form_blocks)
        self.db.commit()
        self.db.refresh(new_form)
        return new_form

    def update_form(self, new_form: Form, form_blocks: List[FormBlock]) -> Form:
        self.db.add(new_form)
        self.db.flush()

        self.db.add_all(form_blocks)
        self.db.commit()
        self.db.refresh(new_form)
        return new_form
