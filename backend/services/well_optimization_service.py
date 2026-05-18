from backend.entities.well_optimization import WellOptimization
from typing import List
from backend.repositories.well_optimization_repository import WellOptimizationRepository

class WellOptimizationService:
    def __init__(self, well_optimization_repository: WellOptimizationRepository):
        self.well_optimization_repository = well_optimization_repository
    
    
    def create_well_optimization(self, optimization_id: int, well_number: int, well_name: str, optimal_production: float, optimal_gas_injection: float) -> bool:
        """Create well optimization in a single transaction"""
        try:
            well_optimization = WellOptimization()
            well_optimization.optimization_id = float(optimization_id)
            well_optimization.well_number = float(well_number)
            well_optimization.well_name = well_name
            well_optimization.optimal_production = float(optimal_production)
            well_optimization.optimal_gas_injection = float(optimal_gas_injection)
            self.well_optimization_repository.save(well_optimization)  
            return True
        except Exception as e:
            raise ValueError(f"Error creating well optimization: {str(e)}")

    def get_latest_well_optimizations(self) -> List[WellOptimization]:
        return self.well_optimization_repository.find_latest()
          
    def get_well_optimizations_by_optimization(self, optimization_id: int) -> List[WellOptimization]:
        return self.well_optimization_repository.find_by_optimization_id(optimization_id)