from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, ForeignKeyConstraint
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.base import Base
import uuid
from app.domain.form.model import BlockTypeEnum
from enum import Enum

class ResponseStatusEnum(str, Enum):
    IN_PROGRESS = "in_progress"
    SUBMITTED   = "submitted"
    SPAM        = "spam"
    DELETED     = "deleted"

class FormResponse(Base):
    __tablename__ = "form_responses"
    __table_args__ = {"schema": "form"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    form_id = Column(UUID(as_uuid=True), ForeignKey("form.forms.id", ondelete="CASCADE"), nullable=False)
    respondent_user_id = Column(UUID(as_uuid=True), nullable=True)
    submitted_ip = Column(String, nullable=True)
    status = Column(sa.Enum(ResponseStatusEnum, name="response_status_enum", schema="form"), nullable=False, default=ResponseStatusEnum.SUBMITTED)
    started_at = Column(DateTime(timezone=True), server_default=sa.func.now(), nullable=False)
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    meta_data = Column(JSONB, nullable=False, server_default=sa.text("'{}'::jsonb"))
    created_at = Column(DateTime(timezone=True), server_default=sa.func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False)

    blocks = relationship("BlockResponse", back_populates="response", cascade="all, delete-orphan", lazy="selectin")

class BlockResponse(Base):
    __tablename__ = "block_responses"
    __table_args__ = (
        sa.UniqueConstraint("response_id", "form_block_id", name="uq_block_responses_response_block"),
        {"schema": "form"},
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    response_id = Column(UUID(as_uuid=True), ForeignKey("form.form_responses.id", ondelete="CASCADE"), nullable=False)
    form_block_id = Column(UUID(as_uuid=True), ForeignKey("form.form_blocks.id", ondelete="RESTRICT"), nullable=False)
    block_type = Column(sa.Enum(BlockTypeEnum, name="block_type_enum", schema="form"), nullable=False)
    value = Column(JSONB, nullable=False, server_default=sa.text("'{}'::jsonb"))
    time_to_answer_ms = Column(Integer, nullable=True)
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=sa.func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False)

    response = relationship("FormResponse", back_populates="blocks", lazy="joined")
