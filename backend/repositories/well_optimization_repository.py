from backend.entities.well_optimization import WellOptimization
from backend.entities.field_optimization import FieldOptimization
from sqlmodel import Session, select
from typing import List

class WellOptimizationRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, result: WellOptimization) -> bool:
        """Save a WellOptimization entity to SQLModel database"""
        try:
            self.session.add(result)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise e

    def find_by_optimization_id(self, opt_id: int) -> List[WellOptimization]:
        """Find WellOptimizations by field optimization ID"""
        statement = select(WellOptimization).where(WellOptimization.field_optimization_id == opt_id)
        return list(self.session.exec(statement).all())

    def find_latest(self, limit: int = None) -> List[WellOptimization]:
        """Find WellOptimizations belonging to the latest FieldOptimization"""
        latest_opt_statement = select(FieldOptimization.id).order_by(FieldOptimization.execution_date.desc()).limit(1)
        latest_opt_id = self.session.exec(latest_opt_statement).first()
        
        if not latest_opt_id:
            return []
            
        statement = select(WellOptimization).where(WellOptimization.field_optimization_id == latest_opt_id)
        if limit:
            statement = statement.limit(limit)
        return list(self.session.exec(statement).all())