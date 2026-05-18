from typing import List, Optional
from backend.entities.field_optimization import FieldOptimization
from backend.repositories.field_optimization_repository import FieldOptimizationRepository

class FieldOptimizationService:
    def __init__(self, field_optimization_repository: FieldOptimizationRepository):
        self.field_optimization_repository = field_optimization_repository

    def create_field_optimization(self, total_production: float, total_gas_injection: float, gas_injection_limit: float, oil_price: float, gas_price: float, field_name: str) -> int:
        try:
            opt = FieldOptimization() 
            opt.total_production = float(total_production)
            opt.total_gas_injection = float(total_gas_injection)
            opt.gas_injection_limit = float(gas_injection_limit)
            opt.oil_price = float(oil_price)
            opt.gas_price = float(gas_price)
            opt.field_name = field_name
            return self.field_optimization_repository.save(opt)
        except Exception as e:
            raise ValueError(f"Error creating field optimization: {str(e)}")


    def get_latest_field_optimization(self) -> Optional[FieldOptimization]:
        return self.field_optimization_repository.find_latest()


    def list_field_optimizations(self, limit: int = 10) -> List[FieldOptimization]:
        return self.field_optimization_repository.find_all(limit=limit)


    