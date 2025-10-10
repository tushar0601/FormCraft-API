from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.domain.analytics.model import BlockAnalytics
from app.domain.analytics.schema import (
    BlockAnalyticsResponse,
    TextAnalyser,
    SentimentCounts,
)
from app.utils.analytics_utils import analyze_text
from app.repository.block_analytics_repository import BlockAnalyticsRepository
from collections import Counter


class BlockAnalyticsService:

    def __init__(self, db: Session):
        self.repo = BlockAnalyticsRepository(db=db)

    def get_by_block_id(self, block_id: UUID):
        data = self.repo.get_by_block_id(block_id=block_id)
        if data is None:
            return None

        return BlockAnalyticsResponse.model_validate(data)

    def handle_text_analytics(self, text: str, block_id: UUID, form_id: UUID):
        ta = analyze_text(text=text)

        block_row = self.repo.get_by_block_id(block_id=block_id)

        if not block_row:
            kw_counts = Counter()
            for k in ta.top_keywords or []:
                if not k:
                    continue
                kw_counts[k] += 1

            analyser_data = TextAnalyser(
                avg_length=float(ta.length),
                total=1,
                sentiment_counts=SentimentCounts(
                    positive=ta.sentiment_counts.positive,
                    negative=ta.sentiment_counts.negative,
                    neutral=ta.sentiment_counts.neutral,
                ),
                keyword_counts=dict(kw_counts),
                top_keywords=[],
            )
            sorted_items = sorted(
                analyser_data.keyword_counts.items(), key=lambda kv: (-kv[1], kv[0])
            )
            analyser_data.top_keywords = [k for k, _ in sorted_items[:10]]

            payload = BlockAnalytics(
                form_id=form_id,
                block_id=block_id,
                details=analyser_data.model_dump(),
                block_type="text",
            )

            try:
                return self.repo.create(entity=payload)
            except IntegrityError:
                block_row = self.repo.get_by_block_id(block_id=block_id)
                if not block_row:
                    raise HTTPException(
                        status_code=409, detail="Block analytics creation race"
                    )

        analyser_data = TextAnalyser(**(block_row.details or {}))

        old_total = analyser_data.total
        old_avg = float(analyser_data.avg_length or 0.0)
        new_len = float(ta.length)
        new_total = old_total + 1
        new_avg = (old_avg * old_total + new_len) / new_total

        analyser_data.avg_length = new_avg
        analyser_data.total = new_total

        for key in ta.top_keywords or []:
            if not key:
                continue
            analyser_data.keyword_counts[key] = (
                analyser_data.keyword_counts.get(key, 0) + 1
            )

        sorted_items = sorted(
            analyser_data.keyword_counts.items(), key=lambda kv: (-kv[1], kv[0])
        )
        analyser_data.top_keywords = [k for k, _ in sorted_items[:10]]

        sc = ta.sentiment_counts
        analyser_data.sentiment_counts.positive += sc.positive
        analyser_data.sentiment_counts.neutral += sc.neutral
        analyser_data.sentiment_counts.negative += sc.negative

        block_row.details = analyser_data.model_dump()

        try:
            return self.repo.update(block_row)
        except SQLAlchemyError:
            self.repo.db.rollback()
            raise HTTPException(status_code=500, detail="Failed to update analytics")
