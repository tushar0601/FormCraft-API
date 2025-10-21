from datetime import datetime
from typing import Optional, Any, Dict, List
from uuid import UUID
from pydantic import BaseModel, Field


class AnalyticsBase(BaseModel):
    details: dict[str, Any] = Field(default_factory=dict)


class FormAnalyticsBase(AnalyticsBase):
    form_id: UUID


class FormAnalyticsResponse(FormAnalyticsBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True


class BlockAnalyticsBase(AnalyticsBase):
    form_id: UUID
    block_id: UUID
    block_type: Optional[str] = None


class BlockAnalyticsResponse(BlockAnalyticsBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True


class SentimentCounts(BaseModel):
    positive: int
    neutral: int
    negative: int


class TextAnalyser(BaseModel):
    avg_length: float
    total: int
    sentiment_counts: SentimentCounts
    keyword_counts: Dict[str, int]
    top_keywords: List[str]


class CheckBoxAnalyser(BaseModel):
    options_count: Dict[int, int]
    avg_selected: float
    total_selected: int
    answered: int


class MCQAnalyser(BaseModel):
    options_count: Dict[int, int]
    most_chosen: int
    answered: int


class FormBlockMainResponse(BaseModel):
    form_id: UUID
    title: str
    response_count: int
    completion_rate: float
    type: str
    created_at: str


class FormAnalyserMainResponse(BaseModel):
    total_forms: int
    total_responses: int
    avg_completion_rate: float
    form_data: List[FormBlockMainResponse]
