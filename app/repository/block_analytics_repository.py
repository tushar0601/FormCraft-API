from sqlalchemy.orm import Session
from uuid import UUID
from app.domain.analytics.model import BlockAnalytics


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
