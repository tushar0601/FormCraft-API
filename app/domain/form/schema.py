from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.domain.form.model import AccessEnum, StatusEnum, BlockTypeEnum


class Question(BaseModel):
    question_order: int = Field(ge=0)
    title: str = Field(min_length=1, max_length=200)
    type: BlockTypeEnum
    config: Dict[str, Any] = {}


class FormCreateRequestSchema(BaseModel):
    title: Optional[str] = ""
    status: StatusEnum = StatusEnum.DRAFT
    access: AccessEnum = AccessEnum.PUBLIC
    questions: List[Question] = []


class FormUpdateRequestSchema(BaseModel):
    title: Optional[str] = ""
    status: StatusEnum = StatusEnum.DRAFT
    access: AccessEnum = AccessEnum.PUBLIC
    questions: List[Question] = []
    id: UUID
    slug: str


class FormBlockRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    form_id: UUID
    sort_order: int
    name: Optional[str] = None
    block_type: BlockTypeEnum
    config: Dict[str, Any]
    updated_at: datetime


class FormRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    title: str
    slug: str
    status: StatusEnum
    access: AccessEnum
    created_by: Optional[UUID] = None
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    blocks: List[FormBlockRead] = []
