from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException, status
from typing import Dict, List
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.domain.analytics.model import BlockAnalytics
from app.domain.analytics.schema import (
    BlockAnalyticsResponse,
    TextAnalyser,
    SentimentCounts,
    CheckBoxAnalyser,
    MCQAnalyser,
)
from app.utils.analytics_utils import analyze_text
from app.repository.block_analytics_repository import BlockAnalyticsRepository
from collections import Counter
from collections import defaultdict


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
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Block analytics creation failed",
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
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update analytics",
            )

    def handle_checkbox_analytics(
        self,
        answer_options: List[int],
        block_id: UUID,
        form_id: UUID,
    ):
        block_row = self.repo.get_by_block_id(block_id=block_id)

        if not block_row:
            total_selected = len(answer_options)
            answered = 1

            opts: Dict[int, int] = defaultdict(int)
            for ans in answer_options:
                opts[ans] += 1

            new_analyser_data = CheckBoxAnalyser(
                options_count=dict(opts),
                avg_selected=float(total_selected) / float(answered),
                total_selected=total_selected,
                answered=answered,
            )

            payload = BlockAnalytics(
                form_id=form_id,
                block_id=block_id,
                details=new_analyser_data.model_dump(),
                block_type="checkbox",
            )
            try:
                return self.repo.create(entity=payload)
            except IntegrityError:
                block_row = self.repo.get_by_block_id(block_id=block_id)
                if not block_row:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Block analytics creation race",
                    )

        analyser_data = CheckBoxAnalyser(**(block_row.details or {}))

        new_total_selected = analyser_data.total_selected
        new_answered = analyser_data.answered
        new_options_count: Dict[int, int] = dict(analyser_data.options_count or {})

        for ans in answer_options:
            new_options_count[ans] = new_options_count.get(ans, 0) + 1

        new_answered += 1
        new_total_selected += len(answer_options)

        new_avg = (
            float(new_total_selected) / float(new_answered) if new_answered else 0.0
        )

        analyser_data.options_count = new_options_count
        analyser_data.total_selected = new_total_selected
        analyser_data.answered = new_answered
        analyser_data.avg_selected = new_avg

        block_row.details = analyser_data.model_dump()
        block_row.block_type = block_row.block_type or "checkbox"

        try:
            return self.repo.update(block_row)
        except SQLAlchemyError:
            self.repo.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update analytics",
            )

    def handle_mcq_analytics(self, option: int, block_id: UUID, form_id: UUID):
        block_row = self.repo.get_by_block_id(block_id=block_id)

        if not block_row:
            analyser_data = MCQAnalyser(
                options_count={option: 1},
                most_chosen=option,
                answered=1,
            )
            payload = BlockAnalytics(
                form_id=form_id,
                block_id=block_id,
                details=analyser_data.model_dump(),
                block_type="mcq",
            )
            try:
                return self.repo.create(entity=payload)
            except IntegrityError:
                block_row = self.repo.get_by_block_id(block_id=block_id)
                if not block_row:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Block analytics creation race",
                    )

        analyser_data = MCQAnalyser(**(block_row.details or {}))

        new_options_count: Dict[int, int] = dict(analyser_data.options_count or {})
        new_options_count[option] = new_options_count.get(option, 0) + 1

        new_answered = analyser_data.answered + 1

        most_chosen = max(new_options_count.items(), key=lambda kv: (kv[1], -kv[0]))[0]

        analyser_data.options_count = new_options_count
        analyser_data.answered = new_answered
        analyser_data.most_chosen = most_chosen

        block_row.details = analyser_data.model_dump()
        block_row.block_type = block_row.block_type or "mcq"

        try:
            return self.repo.update(block_row)
        except SQLAlchemyError:
            self.repo.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update analytics",
            )
