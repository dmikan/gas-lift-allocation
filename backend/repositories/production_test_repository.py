from backend.entities.production_test import ProductionTest
from backend.database import SnowflakeDB


class ProductionTestRepository:
    def __init__(self, db: SnowflakeDB):
        self.db = db

    def fetch_all(self, well_names: list[str]) -> list[ProductionTest]:
        """Fetch all production tests from the database"""
        wells_names_str = ", ".join(f"'{name}'" for name in well_names)  # Format for SQL IN clause
        query = f"""
        SELECT 
            wellbore_ci_id, 
            wellbore_ci_name, 
            subsidiary_id, 
            subsidiary_name, 
            test_date, location_id, 
            location_name, 
            bsw, 
            q_gl,
            q_oil, 
            q_gas, 
            q_water,
            q_liquid, 
            whp 
        FROM prod.analytics_d_production.production__tests
        WHERE name IN ({wells_names_str});
        """
        results = self.db.execute_query_prod(query,)
        return [ProductionTest.from_dict(row) for row in results]

    def fetch_last_test(self, well_names: list[str]) -> list[ProductionTest]:
        """Fetch the last production test for a given well"""
        wells_names_str = ", ".join(f"'{name}'" for name in well_names)  # Format for SQL IN clause
        query = f"""
        SELECT *
        FROM (
            SELECT 
                wellbore_ci_id,
                wellbore_ci_name,
                subsidiary_id,
                subsidiary_name,
                test_date,
                location_id,
                location_name,
                bsw,
                q_gl,
                q_oil,
                q_gas,
                q_water,
                q_liquid,
                whp,
                ROW_NUMBER() OVER (
                    PARTITION BY wellbore_ci_name 
                    ORDER BY test_date DESC
                ) AS rn
        FROM prod.analytics_d_production.production__tests
        WHERE wellbore_ci_name IN ({wells_names_str})
        )
        WHERE rn = 1;
        """
        results = self.db.execute_query_prod(query,)
        return [ProductionTest.from_dict(row) for row in results]

