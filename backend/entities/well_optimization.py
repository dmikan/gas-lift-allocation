"""
Well Result Entity

"""
from dataclasses import dataclass

@dataclass
class WellOptimization:
    """Class representing well-specific optimization results"""
    id: int = None
    optimization_id: int = None
    well_number: int = 0  # Well identifier number
    well_name: str = ""  # Well name/tag
    optimal_production: float = 0.0  # Optimal oil production (BOPD)
    optimal_gas_injection: float = 0.0  # Optimal gas injection (MSCF/D)

    @property
    def table_name(self) -> str:
        return "well_optimizations"

    def to_dict(self) -> dict:
        """Convert object to dictionary for database operations"""
        return {
            "optimization_id": self.optimization_id,
            "well_number": self.well_number,
            "well_name": self.well_name,
            "optimal_production": self.optimal_production,
            "optimal_gas_injection": self.optimal_gas_injection
        }

    @classmethod
    def create_table(cls, db):
        """Create table and sequence for this entity"""
        queries = [
            "CREATE SEQUENCE IF NOT EXISTS well_results_id_seq START WITH 1 INCREMENT BY 1",
            """
            CREATE TABLE IF NOT EXISTS well_results (
                id INTEGER PRIMARY KEY DEFAULT well_results_id_seq.NEXTVAL,
                optimization_id INTEGER REFERENCES optimizations(id),
                well_number INTEGER,
                well_name VARCHAR(100),
                optimal_production FLOAT,
                optimal_gas_injection FLOAT
            )
            """
        ]
        for query in queries:
            db.execute(query)        

    @classmethod
    def from_dict(cls, data: dict) -> 'WellOptimization':
        """Create object from dictionary"""
        data = {k.lower(): v for k, v in data.items()}  
        return cls(
            id=data.get('id'),
            optimization_id=data.get('optimization_id'),
            well_number=data.get('well_number', 0),
            well_name=data.get('well_name', ''),
            optimal_production=data.get('optimal_production', 0.0),
            optimal_gas_injection=data.get('optimal_gas_injection', 0.0)
        )