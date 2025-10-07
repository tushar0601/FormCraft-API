from typing import List, Optional
from sqlalchemy.orm import Session, selectinload
from app.domain.response.model import FormResponse, BlockResponse

class ResponseRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_responses(self, skip: int, limit: int):
        return (
            self.db.query(FormResponse)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def create_response(self, new_reponse: FormResponse, block_responses: List[BlockResponse]) -> FormResponse:
        self.db.add(new_reponse)
        self.db.flush() 

        for b in block_responses:
            if b.response_id is None:
                b.response_id = new_reponse.id

        self.db.add_all(block_responses)
        self.db.commit()
        self.db.refresh(new_reponse)
        return new_reponse
