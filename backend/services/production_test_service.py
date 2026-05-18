from backend.repositories.production_test_repository import ProductionTestRepository
from backend.entities.database import SnowflakeDB
from backend.entities.production_test import ProductionTest
from app.utils.state_keys import StateKeys #HACK: to be replaced with POST request from API.
from backend.services.data_loader_service import DataLoader
import streamlit as st #HACK: to be removed, this service should not have any dependency with Streamlit. The data loading should be done in a controller, and the results passed to this service as parameters.

class ProductionTestService:
    def __init__(self):
        temp_path = st.session_state.get(StateKeys.SESSION_KEY_TEMP_PATH)
        self.repository = ProductionTestRepository(db=SnowflakeDB())
        self.well_names = DataLoader(temp_path).get_well_names()
        
    def get_all_production_tests(self) -> list[ProductionTest]:
        """Get all production tests"""
        return self.repository.fetch_all(well_names=self.well_names)


    def get_last_production_test(self) -> list[ProductionTest]:
        """Get the last production test for a given well"""
        return self.repository.fetch_last_test(well_names=self.well_names)