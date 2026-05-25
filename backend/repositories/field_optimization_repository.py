from backend.entities.field_optimization import FieldOptimization
from sqlmodel import Session, select
from typing import Optional, List

class FieldOptimizationRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, opt: FieldOptimization) -> int:
        """Save FieldOptimization to the SQLModel database"""
        self.session.add(opt)
        self.session.commit()
        self.session.refresh(opt)
        return opt.id

    def find_latest(self) -> Optional[FieldOptimization]:
        """Fetch the latest FieldOptimization"""
        statement = select(FieldOptimization).order_by(FieldOptimization.execution_date.desc()).limit(1)
        return self.session.exec(statement).first()

    def find_all(self, limit: int = None) -> List[FieldOptimization]:
        """Fetch all FieldOptimizations"""
        statement = select(FieldOptimization).order_by(FieldOptimization.execution_date.desc())
        if limit is not None:
            statement = statement.limit(limit)
        return list(self.session.exec(statement).all())