from typing import Optional
from sqlmodel import SQLModel

class Well(SQLModel):
    """Class representing well-specific optimization results"""
    id: Optional[int] = None
    wellbore: str = ""
    afe_id: int = 0
    pms_id: int = 0
    rig_id: int = 0
    field_id: int = 0 
    is_offshore: Optional[bool] = None   
    subsidiary_id: int = 0 
    op_location_id: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> Optional['Well']:
        """Create object from dictionary"""
        if not data:
            return None
                    
        d = {k.lower(): v for k, v in data.items()} 
        return cls(
            id=d.get('id'),
            wellbore=d.get('name') or d.get('wellbore') or '',
            afe_id=d.get('afe_id', 0),
            pms_id=d.get('pms_id', 0),
            rig_id=d.get('rig_id', 0),
            field_id=d.get('field_id', 0),
            is_offshore=d.get('is_offshore'),
            subsidiary_id=d.get('subsidiary_id', 0),
            op_location_id=d.get('op_location_id', 0)
        )