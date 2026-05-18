from backend.entities.field_optimization import FieldOptimization
from backend.entities.database import SnowflakeDB
from typing import Optional, List
from datetime import datetime
    
class FieldOptimizationRepository:
    def __init__(self, db: SnowflakeDB):
        self.db = db

    def save(self, opt: FieldOptimization) -> int:
        id_query = "SELECT field_optimizations_id_seq.NEXTVAL"
        new_id = self.db.execute_query(id_query)[0]['NEXTVAL'] 
        query = """
                INSERT INTO field_optimizations (
                    id, execution_date, total_production, total_gas_injection, gas_injection_limit,
                    oil_price, gas_price, field_name
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
        params = (
            new_id,
            datetime.now(),
            opt.total_production,
            opt.total_gas_injection,
            opt.gas_injection_limit,
            opt.oil_price,
            opt.gas_price,
            opt.field_name
        )
        self.db.execute_query(query, params)
        return new_id

        

    def find_latest(self) -> Optional[FieldOptimization]:
        query = """
                SELECT * FROM field_optimizations 
                ORDER BY execution_date DESC 
                LIMIT 1
            """
        result = self.db.execute_query(query)
        return FieldOptimization.from_dict(result[0]) if result else None



    def find_all(self, limit: int = None) -> List[FieldOptimization]:
        query = """
                SELECT * FROM field_optimizations 
                ORDER BY execution_date DESC
            """
        if limit is not None:
            query += f" LIMIT {limit}"     
        results = self.db.execute_query(query)
        return [FieldOptimization.from_dict(row) for row in results]