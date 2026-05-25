import streamlit as st
import pandas as pd
from app.utils.api_client import APIClient
from app.components.optimization.display_constrained_results import DisplayConstrainedResults
from app.utils.models import FieldOptimization, WellOptimization

class OptimizationHistoryComponent:
    def __init__(self, db=None):
        # Signature compatibility, but using backend REST API exclusively
        self.api_client = APIClient()
        self.display_constrained_results = None
        self.field_optimizations = []
        self.wells_optimizations = []

    def show(self):
        st.subheader("History of optimizations")
        try:
            self.field_optimizations = self.api_client.get_optimization_history()
            if not self.field_optimizations:
                st.info("No historical optimizations found.")
                return
            self._show_field_optimizations_table()
            self._show_wells_optimizations_table()
        except Exception as e:
            st.error(f"❌ Error displaying optimization history: {str(e)}")

    def _show_field_optimizations_table(self):
        history_field_optimizations_data: list[dict] = [{
            "ID": opt.id,
            "Date": opt.execution_date.strftime("%Y-%m-%d %H:%M:%S") if hasattr(opt.execution_date, "strftime") else str(opt.execution_date),
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
            selected_optimization: FieldOptimization = next((opt for opt in self.field_optimizations if opt.id == selected_id), None)
            
            # Retrieve well details exclusively from the API
            self.wells_optimizations = self.api_client.get_well_optimization_details(selected_id)
            
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