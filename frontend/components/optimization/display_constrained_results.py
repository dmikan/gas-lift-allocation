import streamlit as st
import pandas as pd
from frontend.components.utils.plotter import Plotter
from frontend.styles.custom_styles import inject_global_css
from frontend.utils.models import ProductionTest, WellOptimization
from frontend.utils.api_client import APIClient

class DisplayConstrainedResults:
    def __init__(self, optimization_results: dict, 
                        well_results: list[WellOptimization]):
        self.plotter = None
        self.optimization_results: dict = optimization_results
        self.well_results: list[WellOptimization] = well_results
        self.api_client = APIClient()
        

    def show_detailed_results_by_well(self):
        '''
        Method to display the production data and optimization results for each well.
        This method retrieves the latest well test data for the wells involved in the optimization and displays it.
        '''    
        well_names = [getattr(result, 'well_name', '') for result in self.well_results if getattr(result, 'well_name', '')]
        if well_names:
            well_tests = self.api_client.get_latest_well_tests(well_names)
            self._show_optimization_and_well_tests_table(well_tests)

    
    def show_summary_metrics(self):
        '''
        Method to display the summary metrics of the optimization.
        This method is responsible for displaying the summary metrics of the optimization, including total production, total QGL used, and the configured QGL limit.
        It displays the metrics in columns for better visualization.
        '''
        summary = self.optimization_results['summary']

        # First row
        c1, c2 = st.columns(2)
        with c1:
            st.metric(label="Total Production", 
                      value=f"{summary['total_production']:.0f} bopd")
        with c2:
            st.metric(label="QGL Input", 
                      value=f"{summary['qgl_limit']:.0f} mscfd")

        # Second row: calculate marginal productivity (oil / gas ratio)
        well_names = [getattr(result, 'well_name', '') for result in self.well_results if getattr(result, 'well_name', '')]
        if well_names:
            try:
                well_tests = self.api_client.get_latest_well_tests(well_names)
                if well_tests:
                    # Baseline marginal productivity (Last Tests)
                    total_test_oil = sum(getattr(test, 'q_oil', 0) for test in well_tests)
                    total_test_qgl = sum(getattr(test, 'q_gl', 0) for test in well_tests)
                    baseline_ratio = (total_test_oil / total_test_qgl) if total_test_qgl > 0 else 0

                    # Optimized marginal productivity
                    optimized_oil = summary['total_production']
                    optimized_qgl = summary['total_qgl']
                    optimized_ratio = (optimized_oil / optimized_qgl) if optimized_qgl > 0 else 0

                    # Delta percentage calculation
                    if baseline_ratio > 0:
                        percentage_gain = ((optimized_ratio - baseline_ratio) / baseline_ratio) * 100
                        delta_str = f"{percentage_gain:+.1f}% efficiency"
                    else:
                        delta_str = None

                    c3, c4 = st.columns(2)
                    with c3:
                        st.metric(
                            label="Baseline Marginal Productivity",
                            value=f"{baseline_ratio:.2f} bopd/mscfd"
                        )
                    with c4:
                        st.metric(
                            label="Optimized Marginal Productivity",
                            value=f"{optimized_ratio:.2f} bopd/mscfd",
                            delta=delta_str
                        )
            except Exception as e:
                st.caption(f"Could not calculate marginal productivity baseline: {e}")


    def show_production_curves(self):
        if not self.optimization_results.get('plot_data') or not self.well_results:
            st.warning("No data available to plot")
            return
        self.plotter = Plotter(self.optimization_results)
        fig_prod = self.plotter.create_well_curves(self.well_results)
        st.plotly_chart(fig_prod, use_container_width=True)


    def _show_optimization_and_well_tests_table(self, well_tests: list[ProductionTest]):
        if not well_tests:
            st.warning("No well test data available to display")
            return
        if not self.well_results:
            st.warning("No well data available to display")
            return
        try:
            well_test_data = [{
                "Well": getattr(test, 'wellbore_ci_name', 'N/A'),
                "Test Date": getattr(test, 'test_date', 'N/A'),
                "Gas lift rate (mscfd)": getattr(test, 'q_gl', 0),
                "Oil rate (bopd)": getattr(test, 'q_oil', 0), 
                "Total_fluid_rate (bfpd)": getattr(test, 'q_liquid', 0)
            } for test in well_tests]

            well_optimisation_results = [{
                "Well": getattr(result, 'well_name', 'N/A'),
                "Gas lift rate (mscfd)": getattr(result, 'optimal_gas_injection', 0),
                "Oil rate (bopd)": getattr(result, 'optimal_production', 0)
            } for result in self.well_results]

            df_well_tests = pd.DataFrame(well_test_data)
            df_well_optimisation = pd.DataFrame(well_optimisation_results)

            df_merged = pd.merge(df_well_tests, df_well_optimisation, on="Well", how="outer")
            
            columns_multi = [
                ("", "Well"),
                ("Test values", "Test Date"),
                ("Test values", "Gas lift rate (mscfd)"),
                ("Test values", "Oil rate (bopd)"),
                ("Test values", "Total fluid rate (bfpd)"),
                ("Optimal values", "Gas lift rate (mscfd)"),
                ("Optimal values", "Oil rate (bopd)")
            ]
            
            df_merged.columns = pd.MultiIndex.from_tuples(columns_multi)

            totals = {col: "" for col in df_merged.columns}
            totals[("", "Well")] = "Total"

            numeric_cols = columns_multi[2:]
            for col in numeric_cols:
                totals[col] = df_merged[col].sum()
            
            df_totals = pd.DataFrame([totals])
            df_final = pd.concat([df_merged, df_totals], ignore_index=True)
            
            st.dataframe(
                df_final.style.format({
                    ("Test values", "Test Date"): lambda x: str(x)[:10] if pd.notnull(x) else "", # modify
                    ("Test values", "Gas lift rate (mscfd)"): "{:.0f}",
                    ("Test values", "Oil rate (bopd)"): "{:.0f}",
                    ("Test values", "Total fluid rate (bfpd)"): "{:.0f}",
                    ("Optimal values", "Gas lift rate (mscfd)"): "{:.0f}",
                    ("Optimal values", "Oil rate (bopd)"): "{:.0f}"
                                    }).set_properties(
                    subset=pd.IndexSlice[df_final.index[-1], :],
                    **{'font-weight': 'bold', 'background-color': '#1a1c24'}  
                ),
                hide_index=True,            
                )

        except Exception as e:
            st.error(f"Error displaying results: {str(e)}")
            st.write("Data received:", well_tests)
            st.write("Data received:", self.well_results)