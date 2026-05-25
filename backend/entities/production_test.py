from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel

class ProductionTest(SQLModel):
    """Class representing well-specific tests"""
    id: Optional[int] = None
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
    def from_dict(cls, data: dict) -> Optional['ProductionTest']:
        """Create object from dictionary"""
        if not data:
            return None
                    
        d = {k.lower(): v for k, v in data.items()} 
        
        # Parse date if it is a string
        test_date = d.get('test_date')
        if isinstance(test_date, str):
            try:
                test_date = datetime.strptime(test_date, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                try:
                    test_date = datetime.fromisoformat(test_date)
                except ValueError:
                    pass

        return cls(
            id=d.get('id'),
            wellbore_ci_id=d.get('wellbore_ci_id', ''),
            wellbore_ci_name=d.get('wellbore_ci_name', ''),
            subsidiary_id=d.get('subsidiary_id', 0),
            subsidiary_name=d.get('subsidiary_name', ''),
            test_date=test_date,
            location_id=d.get('location_id', 0),
            location_name=d.get('location_name', ''),
            bsw=d.get('bsw', 0.0),
            q_gl=d.get('q_gl', 0),
            q_oil=d.get('q_oil', 0),
            q_gas=d.get('q_gas', 0),
            q_water=d.get('q_water', 0),
            q_liquid=d.get('q_liquid', 0),
            whp=d.get('whp', 0)
        )