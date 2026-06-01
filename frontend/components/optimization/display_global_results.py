import streamlit as st
import pandas as pd
from frontend.components.utils.plotter import Plotter
from frontend.utils.api_client import APIClient

class DisplayGlobalResults:
    def __init__(self, optimization_results: dict, list_info: list, loaded_data: any = None):
        self.plotter = None
        self.optimization_results = optimization_results
        self.list_info = list_info
        self.loaded_data = loaded_data
        self.api_client = APIClient()

    def show_summary_metrics(self):
        self._show_summary_metrics()

    def show_global_curve(self):
        # Calculate baseline points to plot on the curve
        baseline_qgl = None
        baseline_prod = None
        if self.loaded_data is not None:
            try:
                _, _, _, well_names = self.loaded_data
                if well_names:
                    well_tests = self.api_client.get_latest_well_tests(well_names)
                    if well_tests:
                        baseline_qgl = sum(getattr(test, 'q_gl', 0) for test in well_tests)
                        baseline_prod = sum(getattr(test, 'q_oil', 0) for test in well_tests)
            except Exception:
                pass

        self.plotter = Plotter(self.optimization_results)
        fig = self.plotter.create_global_curve(
            baseline_qgl=baseline_qgl,
            baseline_production=baseline_prod
        )
        st.plotly_chart(fig, use_container_width=True)

    def _show_summary_metrics(self):
        summary: list = self.optimization_results['summary']

        st.metric(label="Total Production", 
                  value=f"{summary['total_production']:.0f} bopd")
        st.metric(label="Total QGL Used", 
                  value=f"{summary['total_qgl']:.0f} mscfd")

        # Calculate incremental production compared to latest tests of wells
        if self.loaded_data is not None:
            try:
                _, _, _, well_names = self.loaded_data
                if well_names:
                    well_tests = self.api_client.get_latest_well_tests(well_names)
                    if well_tests:
                        total_test_oil = sum(getattr(test, 'q_oil', 0) for test in well_tests)
                        optimized_oil = summary['total_production']
                        
                        incremental_prod = optimized_oil - total_test_oil
                        if total_test_oil > 0:
                            percentage_gain = (incremental_prod / total_test_oil) * 100
                            delta_str = f"+{percentage_gain:.1f}% vs last tests"
                        else:
                            delta_str = None
                        st.metric(
                            label="Incremental Production",
                            value=f"{incremental_prod:+.0f} bopd",
                            delta=delta_str
                        )
            except Exception as e:
                st.caption(f"Baseline error: {e}")