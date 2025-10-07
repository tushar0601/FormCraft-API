from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.service.form_service import FormService
from app.domain.form.schema import (
    FormCreateRequestSchema,
    FormRead,
    FormUpdateRequestSchema,
)
from app.core.auth import get_current_user, UserData

router = APIRouter()


def get_form_service(db: Session = Depends(get_db)):
    return FormService(db=db)


@router.get("/", description="Get all the forms", response_model=List[FormRead])
async def get_all_forms(
    skip: int = 0,
    limit: int = 50,
    service: FormService = Depends(get_form_service),
    user: UserData = Depends(get_current_user),
):
    return service.get_all_forms(user_id=user.id, skip=skip, limit=limit)


@router.get("/{slug}", description="Get Form by slug")
async def get_form_by_slug(slug: str, service: FormService = Depends(get_form_service)):
    return service.get_form_by_slug(slug=slug)


@router.post(
    "/",
    description="Create a form",
    response_model=FormRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_form(
    payload: FormCreateRequestSchema,
    service: FormService = Depends(get_form_service),
    user: UserData = Depends(get_current_user),
):
    return service.create_form(payload=payload, user_id=user.id)


@router.put(
    "/",
    description="Update a form",
    response_model=FormRead,
    status_code=status.HTTP_202_ACCEPTED,
)
async def update_form(
    payload: FormUpdateRequestSchema,
    service: FormService = Depends(get_form_service),
    user: UserData = Depends(get_current_user),
):
    return service.update_form(payload=payload, user_id=user.id)
