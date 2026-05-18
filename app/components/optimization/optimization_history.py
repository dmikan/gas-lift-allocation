import streamlit as st
import pandas as pd
from backend.entities.database import SnowflakeDB
from backend.services.field_optimization_service import FieldOptimizationService
from backend.services.well_optimization_service import WellOptimizationService
from app.components.optimization.display_constrained_results import DisplayConstrainedResults
from backend.entities.field_optimization import FieldOptimization
from backend.repositories.field_optimization_repository import FieldOptimizationRepository
from backend.repositories.well_optimization_repository import WellOptimizationRepository
from backend.entities.well_optimization import WellOptimization
from typing import Optional


class OptimizationHistoryComponent:
    def __init__(self, db: SnowflakeDB):
        self.db = db
        self.display_constrained_results = None
        self.field_optimizations = None
        self.wells_optimizations = None

    def show(self):
        st.subheader("History of optimizations")
        try:
            field_optimization_repository = FieldOptimizationRepository(self.db)
            field_optimization_service = FieldOptimizationService(field_optimization_repository)
            self.field_optimizations: list[FieldOptimization] = field_optimization_service.list_field_optimizations()
            self._show_field_optimizations_table()
            self._show_wells_optimizations_table()
        finally:
            print("History of optimizations shown successfully.")


    def _show_field_optimizations_table(self):
        history_field_optimizations_data: list[dict] = [{
            "ID": opt.id,
            "Date": opt.execution_date.strftime("%Y-%m-%d %H:%M:%S"),
            "Field": opt.field_name,
            "Total Production (bbl)": opt.total_production,
            "Total QGL (Mscf)": opt.total_gas_injection,
            "QGL Limit": opt.gas_injection_limit,
            "(USD/bbl)": opt.oil_price,
            "(USD/Mscf)": opt.gas_price
        } for opt in self.field_optimizations]

        df_history_field_optimizations = pd.DataFrame(data=history_field_optimizations_data)

        st.dataframe(
            df_history_field_optimizations.style.format({
                "Total Production (bbl)": "{:.2f}",
                "Total QGL (Mscf)": "{:.2f}",
                "QGL Limit": "{:.2f}",
                "(USD/bbl)": "{:.2f}",
                "(USD/Mscf)": "{:.2f}"
            }),
            use_container_width=True,
            height=300
        )


    def _show_wells_optimizations_table(self):
        selected_id = st.selectbox(
            "Select an optimization to view details",
            options=[opt.id for opt in self.field_optimizations],
            format_func=lambda x: f"optimization ID: {x} - {next((opt.field_name for opt in self.field_optimizations if opt.id == x), '')}"
        )

        if selected_id:
            well_optimization_repository = WellOptimizationRepository(self.db)
            well_optimization_service = WellOptimizationService(well_optimization_repository)
            selected_optimization: FieldOptimization = next((opt for opt in self.field_optimizations if opt.id == selected_id), None)
            self.wells_optimizations: list[WellOptimization] = well_optimization_service.get_well_optimizations_by_optimization(selected_id)
            
            
            if selected_optimization:
                st.subheader(f"Detailed Results for Field {selected_optimization.field_name}")

                self.display_constrained_results = DisplayConstrainedResults(selected_optimization, self.wells_optimizations)
                self.display_constrained_results._show_optimization_well_results_table()
                st.warning("The behavior graphs are not available in the history yet...")
                
                csv = pd.DataFrame([{
                    "Well": well.well_number,
                    "Name": well.well_name,
                    "Production (bbl)": well.optimal_production,
                    "QGL (Mscf)": well.optimal_gas_injection
                } for well in self.wells_optimizations]).to_csv(index=False).encode('utf-8')
                
                st.download_button(
                    label="Download results as CSV",
                    data=csv,
                    file_name=f"optimization_results_{selected_optimization.id}.csv",
                    mime='text/csv'
                )