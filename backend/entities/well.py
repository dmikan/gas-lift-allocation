from typing import Optional
from dataclasses import dataclass   
from datetime import datetime

@dataclass
class Well:
    """Class representing well-specific optimization results"""
    id: int = None
    wellbore: str = ""
    afe_id: int = 0
    pms_id: int = 0
    rig_id: int = 0
    field_id: int = 0 
    is_offshore: bool = None   
    subsidiary_id: int = 0 
    op_location_id: int = 0


    @classmethod
    def from_dict(cls, data: dict) -> 'Well':
        """Create object from dictionary"""
        if not data:
            return None
                    
        data = {k.lower(): v for k, v in data.items()} 
        return cls(
            id=data.get('id'),
            wellbore=data.get('name', ''),
            afe_id=data.get('AFE_ID', 0),
            pms_id=data.get('PMS_ID', 0),
            rig_id=data.get('RIG_ID', 0),
            field_id=data.get('field_id', 0),
            is_offshore=data.get('is_offshore'),
            subsidiary_id=data.get('subsidiary_id', 0),
            op_location_id=data.get('op_location_id', 0)
        )
       