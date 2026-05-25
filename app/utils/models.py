from datetime import datetime
from typing import Optional, Dict, Any

class WellOptimization:
    """Frontend-side model representing well-specific optimization results"""
    
    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.field_optimization_id = kwargs.get("field_optimization_id") or kwargs.get("optimization_id")
        self.well_number = kwargs.get("well_number", 0)
        self.well_name = kwargs.get("well_name", "")
        self.optimal_production = kwargs.get("optimal_production", 0.0)
        self.optimal_gas_injection = kwargs.get("optimal_gas_injection", 0.0)

    @property
    def optimization_id(self) -> Optional[int]:
        return self.field_optimization_id

    @optimization_id.setter
    def optimization_id(self, value: Optional[int]):
        self.field_optimization_id = value

    @classmethod
    def from_dict(cls, data: dict) -> 'WellOptimization':
        if not data:
            return None
        return cls(**{k.lower(): v for k, v in data.items()})

    def to_dict(self) -> dict:
        return {
            "optimization_id": self.field_optimization_id,
            "well_number": self.well_number,
            "well_name": self.well_name,
            "optimal_production": self.optimal_production,
            "optimal_gas_injection": self.optimal_gas_injection
        }


class FieldOptimization:
    """Frontend-side model representing field-wide optimization results"""
    
    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.execution_date = kwargs.get("execution_date")
        self.total_production = kwargs.get("total_production", 0.0)
        self.total_gas_injection = kwargs.get("total_gas_injection", 0.0)
        self.gas_injection_limit = kwargs.get("gas_injection_limit", 0.0)
        self.oil_price = kwargs.get("oil_price", 0.0)
        self.gas_price = kwargs.get("gas_price", 0.0)
        self.field_name = kwargs.get("field_name", "")

    @classmethod
    def from_dict(cls, data: dict) -> 'FieldOptimization':
        if not data:
            return None
        data = {k.lower(): v for k, v in data.items()}
        exec_date = data.get('execution_date')
        if isinstance(exec_date, str):
            try:
                exec_date = datetime.strptime(exec_date, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                try:
                    exec_date = datetime.fromisoformat(exec_date)
                except ValueError:
                    exec_date = datetime.now()
        else:
            exec_date = exec_date or datetime.now()
        data['execution_date'] = exec_date
        return cls(**data)

    def to_dict(self) -> dict:
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


class ProductionTest:
    """Frontend-side model representing well production tests"""
    
    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.wellbore_ci_id = kwargs.get("wellbore_ci_id", "")
        self.wellbore_ci_name = kwargs.get("wellbore_ci_name", "")
        self.subsidiary_id = kwargs.get("subsidiary_id", 0)
        self.subsidiary_name = kwargs.get("subsidiary_name", "")
        self.test_date = kwargs.get("test_date")
        self.location_id = kwargs.get("location_id", 0)
        self.location_name = kwargs.get("location_name", "")
        self.bsw = kwargs.get("bsw", 0.0)
        self.q_gl = kwargs.get("q_gl", 0)
        self.q_oil = kwargs.get("q_oil", 0)
        self.q_gas = kwargs.get("q_gas", 0)
        self.q_water = kwargs.get("q_water", 0)
        self.q_liquid = kwargs.get("q_liquid", 0)
        self.whp = kwargs.get("whp", 0)

    @classmethod
    def from_dict(cls, data: dict) -> 'ProductionTest':
        if not data:
            return None
        return cls(**{k.lower(): v for k, v in data.items()})
