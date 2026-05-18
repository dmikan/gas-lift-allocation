import streamlit as st
import pandas as pd
from backend.entities.database import SnowflakeDB
from app.components.utils.plotter import Plotter
from app.styles.custom_styles import inject_global_css
from backend.entities.production_test import ProductionTest
from backend.entities.well_optimization import WellOptimization
from backend.services.production_test_service import ProductionTestService

class DisplayConstrainedResults:
    def __init__(self, optimization_results: dict, 
                        well_results: list[WellOptimization]):
        self.plotter = None
        self.optimization_results: dict = optimization_results
        self.well_results: list[WellOptimization] = well_results
        
    '''
    Method to display the optimization results.
    This method is responsible for displaying the optimization results, including summary metrics and well curves.
    '''
    def show(self):
        inject_global_css()
        st.markdown("---")
        self.show_summary_metrics()
        st.markdown("---")
        self.show_production_curves()
        st.markdown("---")
        self.show_detailed_results_by_well()

    def show_summary_metrics(self):
        inject_global_css()
        #st.markdown("#### Summary Metrics")
        self._show_summary_metrics()

    def show_production_curves(self):
        #st.markdown("#### Production Curves")
        self._plot_well_curves()

    def show_detailed_results_by_well(self):
        #PENDING: The three lines below should be implemented in a controller, not here. This component should only be responsible for displaying the results, not fetching data from the database. 
        self._show_optimization_well_results_table()
        production_test_service = ProductionTestService()
        well_tests: list[ProductionTest] = production_test_service.get_last_production_test()
        self._show_well_test_table(well_tests)

    '''
    Method to display the summary metrics of the optimization.
    This method is responsible for displaying the summary metrics of the optimization, including total production, total QGL used, and the configured QGL limit.
    It displays the metrics in columns for better visualization.
    '''
    
    def _show_summary_metrics(self):
        summary = self.optimization_results['summary']
        used_percentage = (summary['total_qgl'] / summary['qgl_limit']) * 100

        html = f"""
        <div class="metric-cards-two-cols">
            <div class="metric-cards-vertical">
                <div class="metric-card">
                    <div class="metric-title">Total Production</div>
                    <div class="metric-value">{summary['total_production']:.2f} <span class="metric-unit">bbl</span></div>
                </div>
                <!-- <div class="metric-card">
                    <div class="metric-title">Total QGL Used</div>
                    <div class="metric-value">{summary['total_qgl']:.2f} <span class="metric-unit">Mscf</span></div>
                    <div class="status-tag">{used_percentage:.1f}% of the limit</div>
                </div> -->
            </div>
            <div class="metric-cards-vertical">
                <div class="metric-card">
                    <div class="metric-title">Configured QGL Limit</div>
                    <div class="metric-value">{summary['qgl_limit']:.2f} <span class="metric-unit">Mscf</span></div>
                </div>
            </div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)




    def _plot_well_curves(self):
        if not self.optimization_results.get('plot_data') or not self.well_results:
            st.warning("No data available to plot")
            return
        self.plotter = Plotter(self.optimization_results)
        fig_prod = self.plotter.create_well_curves(self.well_results)
        st.plotly_chart(fig_prod, use_container_width=True)




    def _show_optimization_well_results_table(self):
        if not self.well_results:
            st.warning("No well data available to display")
            return
        try:
            well_data = [{
                "Well identifier": getattr(result, 'well_name', 'N/A'),
                "Gas lift rate (mscfd)": getattr(result, 'optimal_gas_injection', 0),
                "Oil rate (bopd)": getattr(result, 'optimal_production', 0)
            } for result in self.well_results]

            df = pd.DataFrame(well_data)
            if "Well identifier" not in df.columns:
                df = df.rename(columns={"well_name": "Well identifier"})
            # Header row "Optimal values" above all column names (full row span)
            df.columns = pd.MultiIndex.from_tuples([
                ("Optimal values", "Well identifier"),
                ("Optimal values", "Gas lift rate (mscfd)"),
                ("Optimal values", "Oil rate (bopd)")
            ])
            st.dataframe(
                df.style.format({
                    ("Optimal values", "Gas lift rate (mscfd)"): "{:.0f}",
                    ("Optimal values", "Oil rate (bopd)"): "{:.0f}"
                }),
                hide_index=True,
            )

        except Exception as e:
            st.error(f"Error displaying results: {str(e)}")
            st.write("Data received:", self.well_results)


    def _show_well_test_table(self, well_tests: list[ProductionTest]):
            if not well_tests:
                st.warning("No well test data available to display")
                return
            try:
                well_test_data = [{
                    "Well": getattr(test, 'wellbore_ci_name', 'N/A'),
                    "Test Date": getattr(test, 'test_date', 'N/A'),
                    "Gas lift rate (mscfd)": getattr(test, 'q_gl', 0),
                    "Oil rate (bopd)": getattr(test, 'q_oil', 0), 
                    "Total_fluid_rate (bfpd)": getattr(test, 'q_liquid', 0)
                } for test in well_tests]

                df = pd.DataFrame(well_test_data)
                
                df.columns = pd.MultiIndex.from_tuples([
                    ("Test values", "Well"),
                    ("Test values", "Test Date"),
                    ("Test values", "Gas lift rate (mscfd)"),
                    ("Test values", "Oil rate (bopd)"),
                    ("Test values", "Total fluid rate (bfpd)")
                ])
                st.dataframe(
                    df.style.format({
                        ("Test values", "Gas lift rate (mscfd)"): "{:.0f}",
                        ("Test values", "Oil rate (bopd)"): "{:.0f}",
                        ("Test values", "Total fluid rate (bfpd)"): "{:.0f}",
                                        }),
                    hide_index=True,
                )

            except Exception as e:
                st.error(f"Error displaying results: {str(e)}")
                st.write("Data received:", well_tests)