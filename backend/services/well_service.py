from backend.repositories.well_repository import WellRepository
from backend.repositories.production_test_repository import ProductionTestRepository
from backend.database import SnowflakeDB
from backend.entities.well import Well
from backend.entities.production_test import ProductionTest
from typing import List

class WellService:
    def __init__(self, db: SnowflakeDB = None):
        self.db = db or SnowflakeDB()
        self.well_repo = WellRepository(self.db)
        self.test_repo = ProductionTestRepository(self.db)

    def get_all_wells(self) -> List[str]:
        """Get all active wellbore names"""
        wells = self.well_repo.fetch_all()
        return [well.wellbore for well in wells]

    def get_latest_tests(self, well_names: List[str]) -> List[ProductionTest]:
        """Retrieve the latest production tests for the given wellbore names"""
        return self.test_repo.fetch_last_test(well_names=well_names)

    def get_all_production_tests(self, well_names: List[str]) -> List[ProductionTest]:
        """Retrieve all production tests for the given wellbore names"""
        return self.test_repo.fetch_all(well_names=well_names)