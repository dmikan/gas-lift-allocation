from typing import List, Optional
from backend.entities.field_optimization import FieldOptimization
from backend.entities.well_optimization import WellOptimization
from backend.repositories.field_optimization_repository import FieldOptimizationRepository
from backend.repositories.well_optimization_repository import WellOptimizationRepository

class OptimizationService:
    def __init__(self, field_repo: FieldOptimizationRepository, well_repo: WellOptimizationRepository):
        self.field_repo = field_repo
        self.well_repo = well_repo

    def create_field_optimization(self, total_production: float, total_gas_injection: float, gas_injection_limit: float, oil_price: float, gas_price: float, field_name: str) -> int:
        try:
            opt = FieldOptimization() 
            opt.total_production = float(total_production)
            opt.total_gas_injection = float(total_gas_injection)
            opt.gas_injection_limit = float(gas_injection_limit)
            opt.oil_price = float(oil_price)
            opt.gas_price = float(gas_price)
            opt.field_name = field_name
            return self.field_repo.save(opt)
        except Exception as e:
            raise ValueError(f"Error creating field optimization: {str(e)}")

    def get_latest_field_optimization(self) -> Optional[FieldOptimization]:
        return self.field_repo.find_latest()

    def list_field_optimizations(self, limit: int = 10) -> List[FieldOptimization]:
        return self.field_repo.find_all(limit=limit)

    def create_well_optimization(self, optimization_id: int, well_number: int, well_name: str, optimal_production: float, optimal_gas_injection: float) -> bool:
        try:
            well_optimization = WellOptimization()
            well_optimization.optimization_id = float(optimization_id)
            well_optimization.well_number = float(well_number)
            well_optimization.well_name = well_name
            well_optimization.optimal_production = float(optimal_production)
            well_optimization.optimal_gas_injection = float(optimal_gas_injection)
            self.well_repo.save(well_optimization)  
            return True
        except Exception as e:
            raise ValueError(f"Error creating well optimization: {str(e)}")

    def get_latest_well_optimizations(self) -> List[WellOptimization]:
        return self.well_repo.find_latest()
          
    def get_well_optimizations_by_optimization(self, optimization_id: int) -> List[WellOptimization]:
        return self.well_repo.find_by_optimization_id(optimization_id)
