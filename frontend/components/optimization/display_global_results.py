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

    def _get_baseline_and_opt_metrics(self):
        baseline_qgl = None
        baseline_prod = None
        oil_opt_at_baseline = None
        
        if self.loaded_data is not None:
            try:
                q_gl_list, q_fluid_list, wct_list, well_names = self.loaded_data
                if well_names:
                    well_tests = self.api_client.get_latest_well_tests(well_names)
                    if well_tests:
                        baseline_qgl = sum(getattr(test, 'q_gl', 0) for test in well_tests)
                        baseline_prod = sum(getattr(test, 'q_oil', 0) for test in well_tests)
                        
                        cache_key = f"oil_opt_at_{baseline_qgl:.2f}"
                        if cache_key in st.session_state:
                            oil_opt_at_baseline = st.session_state[cache_key]
                        else:
                            constr_results, _ = self.api_client.run_constrained_optimization(
                                q_gl_list=q_gl_list,
                                q_fluid_list=q_fluid_list,
                                wct_list=wct_list,
                                list_info=self.list_info,
                                settings={
                                    "qgl_limit_constrained": baseline_qgl,
                                    "qgl_min_constrained": 0.0,
                                    "p_qoil_constrained": 0.0,
                                    "p_qgl_constrained": 0.0
                                }
                            )
                            oil_opt_at_baseline = constr_results['summary']['total_production']
                            st.session_state[cache_key] = oil_opt_at_baseline
                            st.session_state["oil_opt_at_baseline"] = oil_opt_at_baseline
                            st.session_state["baseline_qgl"] = baseline_qgl
                            st.session_state["baseline_prod"] = baseline_prod
            except Exception:
                pass
        return baseline_qgl, baseline_prod, oil_opt_at_baseline

    def show_summary_metrics(self):
        self._show_summary_metrics()

    def show_global_curve(self):
        baseline_qgl, baseline_prod, oil_opt_at_baseline = self._get_baseline_and_opt_metrics()

        self.plotter = Plotter(self.optimization_results)
        fig = self.plotter.create_global_curve(
            baseline_qgl=baseline_qgl,
            baseline_production=baseline_prod,
            oil_opt_at_baseline=oil_opt_at_baseline
        )
        st.plotly_chart(fig, use_container_width=True)

    def _show_summary_metrics(self):
        summary: list = self.optimization_results['summary']

        st.metric(label="Total Production", 
                  value=f"{summary['total_production']:.0f} bopd")
        st.metric(label="Total QGL Used", 
                  value=f"{summary['total_qgl']:.0f} mscfd")

        baseline_qgl, baseline_prod, oil_opt_at_baseline = self._get_baseline_and_opt_metrics()

        if baseline_prod is not None and oil_opt_at_baseline is not None:
            diff_bopd = oil_opt_at_baseline - baseline_prod
            diff_pct = (diff_bopd / baseline_prod * 100) if baseline_prod > 0 else 0.0
            
            st.metric(
                label="Opt. Gain at Baseline QGL",
                value=f"{diff_bopd:+.0f} bopd",
                delta=f"{diff_pct:+.1f}% vs baseline"
            )
            st.metric(
                label="Fixed QGL Baseline",
                value=f"{baseline_qgl:.0f} mscfd"
            )

        # Calculate incremental production compared to latest tests of wells
        if baseline_prod is not None:
            try:
                optimized_oil = summary['total_production']
                incremental_prod = optimized_oil - baseline_prod
                if baseline_prod > 0:
                    percentage_gain = (incremental_prod / baseline_prod) * 100
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