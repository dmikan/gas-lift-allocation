from backend.services.field_optimization_service import FieldOptimizationService
from backend.services.well_optimization_service import WellOptimizationService
from backend.entities.field_optimization import FieldOptimization
from backend.database import SnowflakeDB
from backend.repositories.field_optimization_repository import FieldOptimizationRepository
from backend.repositories.well_optimization_repository import WellOptimizationRepository
#Orchestration pattern
class SavingOrchestrationService:
    def __init__(self, db: SnowflakeDB):
        self.db = db
    """Orchestrates the saving of complete optimization results"""

    def save_constrained_optimization_results(self, data: dict) -> int:
        """Saves complete optimization results including wells"""

        # in case of not having access to snowflake directly create the tables from the service
        #Optimization.create_table(self.db)
        #WellResult.create_table(self.db)


        field_optimization_repository = FieldOptimizationRepository(self.db)
        well_optimization_repository = WellOptimizationRepository(self.db)
        field_optimization_service = FieldOptimizationService(field_optimization_repository)
        well_optimization_service = WellOptimizationService(well_optimization_repository)

        # Create the optimization record passing the complete dictionary
        opt_id = field_optimization_service.create_field_optimization(
            total_production=data["total_prod"],
            total_gas_injection=data["total_qgl"],
            gas_injection_limit=data.get("qgl_limit", 1000),
            oil_price=data.get("oil_price", 0.0),
            gas_price=data.get("gas_price", 0.0),
            field_name=str(data["info"][0])
        )

        # Create well results passing also the same dictionary
        for well in data["wells_data"]:
            well_optimization_service.create_well_optimization(
                optimization_id=opt_id,
                well_number=well["well_number"], 
                well_name=well["well_name"], 
                optimal_production=well["optimal_production"], 
                optimal_gas_injection=well["optimal_gas_injection"]
        )

        return opt_id


    def save_global_optimization_results(self, data: dict) -> int:
        """Saves complete optimization results including wells"""
        pass