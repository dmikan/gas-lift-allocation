"""
Well Result Entity
"""
from typing import Optional
from sqlmodel import SQLModel, Field

class WellOptimization(SQLModel, table=True):
    """Class representing well-specific optimization results stored in DB"""
    __tablename__ = "well_optimizations"

    id: Optional[int] = Field(default=None, primary_key=True)
    field_optimization_id: Optional[int] = Field(default=None, foreign_key="field_optimizations.id")
    well_number: int = Field(default=0)  # Well identifier number
    well_name: str = Field(default="")  # Well name/tag
    optimal_production: float = Field(default=0.0)  # Optimal oil production (BOPD)
    optimal_gas_injection: float = Field(default=0.0)  # Optimal gas injection (MSCF/D)

    @property
    def optimization_id(self) -> Optional[int]:
        return self.field_optimization_id

    @optimization_id.setter
    def optimization_id(self, value: Optional[int]):
        self.field_optimization_id = value

    @property
    def table_name(self) -> str:
        return "well_optimizations"

    def to_dict(self) -> dict:
        """Convert object to dictionary for database operations"""
        return {
            "optimization_id": self.field_optimization_id,
            "well_number": self.well_number,
            "well_name": self.well_name,
            "optimal_production": self.optimal_production,
            "optimal_gas_injection": self.optimal_gas_injection
        }

    @classmethod
    def from_dict(cls, data: dict) -> Optional['WellOptimization']:
        """Create object from dictionary"""
        if not data:
            return None
        data = {k.lower(): v for k, v in data.items()}  
        return cls(
            id=data.get('id'),
            field_optimization_id=data.get('field_optimization_id') or data.get('optimization_id'),
            well_number=data.get('well_number', 0),
            well_name=data.get('well_name', ''),
            optimal_production=data.get('optimal_production', 0.0),
            optimal_gas_injection=data.get('optimal_gas_injection', 0.0)
        )