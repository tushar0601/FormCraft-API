import uuid
import sqlalchemy as sa
from sqlalchemy import Column, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.base import Base


NOW = sa.func.now()
EMPTY_JSONB = sa.text("'{}'::jsonb")

class FormAnalytics(Base):
    __tablename__ = "form_analytics"
    __table_args__ = (
        UniqueConstraint("form_id", name="uq_form_analytics_form_id"),
        Index("ix_form_analytics_details", "details", postgresql_using="gin"),
        {"schema": "analytics"},
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    form_id = Column(
        UUID(as_uuid=True),
        ForeignKey("form.forms.id", ondelete="CASCADE"), 
        nullable=False,
        index=True,
    )
    details = Column(JSONB, nullable=False, server_default=EMPTY_JSONB)

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=NOW,
        server_onupdate=NOW,  
    )
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=NOW)


class BlockAnalytics(Base):
    __tablename__ = "block_analytics"
    __table_args__ = (
        UniqueConstraint("block_id", name="uq_block_analytics_block_id"),
        Index("ix_block_analytics_form_id", "form_id"),
        Index("ix_block_analytics_details", "details", postgresql_using="gin"),
        {"schema": "analytics"},
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    form_id = Column(
        UUID(as_uuid=True),
        ForeignKey("form.forms.id", ondelete="CASCADE"), 
        nullable=False,
    )
    block_id = Column(
        UUID(as_uuid=True),
        ForeignKey("form.form_blocks.id", ondelete="CASCADE"),
        nullable=False,
    )

    block_type = Column(sa.String(32), nullable=True)

    details = Column(JSONB, nullable=False, server_default=EMPTY_JSONB)

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=NOW,
        server_onupdate=NOW,
    )
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=NOW)
