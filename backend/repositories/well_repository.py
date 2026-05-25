from backend.database import SnowflakeDB
from backend.entities.well import Well

class WellRepository:
    def __init__(self, db: SnowflakeDB):
        self.db = db

    def fetch_all(self) -> list[Well]:
        """Fetch wells from the database"""
        query = """
        WITH latest_tests AS (

            SELECT *
            FROM PROD.ANALYTICS_D_PRODUCTION.PRODUCTION__TESTS
            QUALIFY ROW_NUMBER() OVER (
                PARTITION BY wellbore_ci_name 
                ORDER BY test_date DESC
            ) = 1
        )
        SELECT 
            ci.id,
            ci.name,
            ci.AFE_ID,
            ci.PMS_ID,
            ci.RIG_ID,
            ci.field_id,
            ci.is_offshore,
            ci.subsidiary_id,
            ci.op_location_id,
            lt.activation_type_name
        FROM raw.agg__operationreference_v02.common_identity ci
        LEFT JOIN latest_tests lt
            ON ci.name = lt.wellbore_ci_name
        WHERE ci.common_identity_type_id = '1' AND lt.activation_type_name = 'AGL';
        """
        results: list[dict] = self.db.execute_query_raw(query)
        return [Well.from_dict(row) for row in results]


if __name__ == "__main__":
    db = SnowflakeDB()
    repo = WellRepository(db)
    wells = repo.fetch_all()
    print(wells)
