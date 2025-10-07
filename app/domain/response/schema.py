from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.domain.response.model import ResponseStatusEnum
from app.domain.form.model import BlockTypeEnum

class ResponseBlockCreateSchema(BaseModel):
    form_block_id: UUID
    block_type: BlockTypeEnum
    value: Dict[str,Any] = {}
    time_to_answer_ms: int

class ResponseCreateSchema(BaseModel):
    form_id: UUID
    submitted_ip: str
    status: ResponseStatusEnum
    meta_data: Dict[str, Any] = {}
    question_responses: List[ResponseBlockCreateSchema]

class BlockResponseRead(BaseModel):
    id: UUID
    form_block_id: UUID
    block_type: BlockTypeEnum
    value: Dict[str, Any]
    submitted_at: Optional[datetime] = None
    class Config: orm_mode = True

class FormResponseRead(BaseModel):
    id: UUID
    form_id: UUID
    submitted_at: Optional[datetime] = None
    submitted_ip: Optional[str] = None
    respondent_user_id: Optional[UUID] = None
    meta_data: Dict[str, Any] = {}
    blocks: List[BlockResponseRead] = []
    class Config: orm_mode = True