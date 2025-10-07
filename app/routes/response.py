from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.service.response_service import ResponseService
from app.domain.response.schema import (
    FormResponseRead,
    ResponseCreateSchema,
)
from app.core.auth import get_current_user, UserData

router = APIRouter()


def get_response_service(db: Session = Depends(get_db)):
    return ResponseService(db=db)


@router.get(
    "/", description="Get all the Responses", response_model=List[FormResponseRead]
)
async def get_all_responses(
    skip: int = 0,
    limit: int = 50,
    service: ResponseService = Depends(get_response_service),
):
    return service.get_all_responses(skip=skip, limit=limit)


@router.post(
    "/",
    description="Create a reponse",
    response_model=FormResponseRead,
    status_code=201,
)
async def create_form(
    payload: ResponseCreateSchema,
    service: ResponseService = Depends(get_response_service),
    user: UserData = Depends(get_current_user),
):
    return service.create_response(payload=payload, user_id=user.id)
