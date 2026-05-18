from typing import Optional
from dataclasses import dataclass   
from datetime import datetime

@dataclass
class ProductionTest:
    """Class representing well-specific tests"""
    id: int = None
    wellbore_ci_id: str = ""
    wellbore_ci_name: str = ""
    subsidiary_id: int = 0
    subsidiary_name: str = ""
    test_date: Optional[datetime] = None
    location_id: int = 0
    location_name: str = ""
    bsw: float = 0.0
    q_gl: int = 0
    q_oil: int = 0
    q_gas: int = 0
    q_water: int = 0 
    q_liquid: int = 0   
    whp: int = 0 


    @classmethod
    def from_dict(cls, data: dict) -> 'ProductionTest':
        """Create object from dictionary"""
        if not data:
            return None
                    
        data = {k.lower(): v for k, v in data.items()} 
        return cls(
            wellbore_ci_id=data.get('wellbore_ci_id'),
            wellbore_ci_name=data.get('wellbore_ci_name', ''),
            subsidiary_id=data.get('subsidiary_id', 0),
            subsidiary_name=data.get('subsidiary_name', ''),
            test_date=data.get('test_date'),
            location_id=data.get('location_id', 0),
            location_name=data.get('location_name', ''),
            bsw=data.get('bsw', 0.0),
            q_gl=data.get('q_gl', 0),
            q_oil=data.get('q_oil', 0),
            q_gas=data.get('q_gas', 0),
            q_water=data.get('q_water', 0),
            q_liquid=data.get('q_liquid', 0),
            whp=data.get('whp', 0)
        )
        