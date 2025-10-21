from sqlalchemy.orm import Session
from sqlalchemy import cast, Integer, Float
from uuid import UUID
from app.domain.analytics.model import BlockAnalytics, FormAnalytics
from app.domain.form.model import FormBlock


class BlockAnalyticsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_block_id(self, block_id: UUID) -> BlockAnalytics | None:
        return (
            self.db.query(BlockAnalytics)
            .filter(BlockAnalytics.block_id == block_id)
            .one_or_none()
        )

    def create(self, entity: BlockAnalytics) -> BlockAnalytics:
        self.db.add(entity)
        self.db.flush()
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def update(self, entity: BlockAnalytics) -> BlockAnalytics:
        self.db.flush()
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def get_analytics_data(self, form_id: UUID):
        total_response = cast(
            FormAnalytics.details.op("->>")("total_response"), Integer
        ).label("total_response")

        completion_rate = cast(
            FormAnalytics.details.op("->>")("completion_rate"), Float
        ).label("completion_rate")

        query = (
            self.db.query(
                FormAnalytics.form_id.label("form_id"),
                total_response,
                completion_rate,
                BlockAnalytics.details.label("block_analytics_details"),
                FormBlock.id.label("block_id"),
                FormBlock.name.label("block_title"),
                FormBlock.config.label("block_details"),
                FormBlock.block_type.label("block_type"),
                FormBlock.sort_order.label("block_order"),
            )
            .select_from(FormAnalytics)
            .outerjoin(BlockAnalytics, BlockAnalytics.form_id == FormAnalytics.form_id)
            .outerjoin(FormBlock, FormBlock.id == BlockAnalytics.block_id)
            .filter(FormAnalytics.form_id == form_id)
            .order_by(FormBlock.sort_order)
        )
        return query.all()
