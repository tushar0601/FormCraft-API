import uuid
import sqlalchemy as sa
from sqlalchemy import Column, String, DateTime, ForeignKeyConstraint, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from enum import Enum
from app.db.base import Base


class StatusEnum(str, Enum):
    DRAFT = "Draft"
    PUBLISHED = "Published"


class AccessEnum(str, Enum):
    PUBLIC = "PUBLIC"
    LOGIN_REQUIRED = "LOGIN_REQUIRED"


class Form(Base):
    __tablename__ = "forms"
    __table_args__ = (
        sa.UniqueConstraint("slug", name="uq_forms_slug"),
        sa.Index("ix_forms_status", "status"),
        sa.Index("ix_forms_access", "access"),
        {"schema": "form"},
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    slug = Column(String(200), nullable=False)

    status = Column(
        sa.Enum(StatusEnum, name="status_enum", native_enum=True, schema="form"),
        nullable=False,
        default=StatusEnum.DRAFT,
    )
    access = Column(
        sa.Enum(AccessEnum, name="access_enum", native_enum=True, schema="form"),
        nullable=False,
        default=AccessEnum.PUBLIC,
    )

    created_by = Column(UUID(as_uuid=True), nullable=True)
    published_at = Column(DateTime(timezone=True))
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=sa.func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
    )


class BlockTypeEnum(str, Enum):
    TEXT = "text"
    LONG_TEXT = "long_text"
    SINGLE_CHOICE = "single_choice"
    MULTICHOICE = "multichoice"
    CHECKBOX = "checkbox"
    DATE = "date"
    NUMBER = "number"


class FormBlock(Base):
    __tablename__ = "form_blocks"
    __table_args__ = (
        ForeignKeyConstraint(
            ["form_id"],
            ["form.forms.id"],
            name="fk_form_blocks_form_id",
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("form_id", "order", name="uq_form_blocks_form_order"),
        sa.Index("ix_form_blocks_form_id", "form_id"),
        sa.Index("ix_form_blocks_form_id_order", "form_id", "order"),
        sa.Index("ix_form_blocks_type", "type"),
        {"schema": "form"},
    )
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    form_id = Column(UUID(as_uuid=True), nullable=False)
    sort_order = Column("order", Integer, nullable=False)
    name = Column(String(10000), nullable=True)
    block_type = Column(
        "type",
        sa.Enum(
            BlockTypeEnum,
            name="block_type_enum",
            native_enum=True,
            schema="form",
        ),
        nullable=False,
    )
    config = Column(JSONB, nullable=False, server_default=sa.text("'{}'::jsonb"))

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
    )
    form = relationship("Form", backref="blocks", passive_deletes=True, lazy="selectin")
