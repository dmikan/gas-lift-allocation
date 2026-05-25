"""
Optimization Entity
"""
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class FieldOptimization(SQLModel, table=True):
    """Class representing optimization results stored in DB"""
    __tablename__ = "field_optimizations"

    id: Optional[int] = Field(default=None, primary_key=True)
    execution_date: datetime = Field(default_factory=datetime.now)
    total_production: float = Field(default=0.0)  # Barrels of oil per day (BOPD)
    total_gas_injection: float = Field(default=0.0)  # Total gas injection (MSCF/D)
    gas_injection_limit: float = Field(default=0.0)  # Gas injection limit (MSCF/D)
    oil_price: float = Field(default=0.0)  # Oil price per barrel (USD)
    gas_price: float = Field(default=0.0)  # Gas price per unit (USD)
    field_name: str = Field(default="")  # Plant/field name

    def to_dict(self) -> dict:
        """Convert object to dictionary for database operations"""
        return {
            "id": self.id,
            "execution_date": self.execution_date,
            "total_production": self.total_production,
            "total_gas_injection": self.total_gas_injection,
            "gas_injection_limit": self.gas_injection_limit,
            "oil_price": self.oil_price,
            "gas_price": self.gas_price,
            "field_name": self.field_name
        }

    @classmethod
    def from_dict(cls, data: dict) -> Optional['FieldOptimization']:
        """Create object from dictionary"""
        if not data:
            return None
                 
        data = {k.lower(): v for k, v in data.items()} 
        
        exec_date = data.get('execution_date', datetime.now())
        if isinstance(exec_date, str):
            try:
                exec_date = datetime.strptime(exec_date, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                try:
                    exec_date = datetime.fromisoformat(exec_date)
                except ValueError:
                    exec_date = datetime.now()

        return cls(
            id=data.get('id'),
            execution_date=exec_date,
            total_production=data.get('total_production', 0.0),
            total_gas_injection=data.get('total_gas_injection', 0.0),
            gas_injection_limit=data.get('gas_injection_limit', 0.0),
            oil_price=data.get('oil_price', 0.0),
            gas_price=data.get('gas_price', 0.0),
            field_name=data.get('field_name', '')
        )