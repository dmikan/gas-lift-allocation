from backend.repositories.production_test_repository import ProductionTestRepository
from backend.entities.database import SnowflakeDB
from backend.entities.well import Well
from backend.repositories.well_repository import WellRepository


class WellService:
    def __init__(self):
        self.repository = WellRepository(db=SnowflakeDB())

    def get_all_wells(self) -> list[str]:
        """Get all wells names"""
        wellbore_names = [well.wellbore for well in self.repository.fetch_all()]
        return wellbore_names