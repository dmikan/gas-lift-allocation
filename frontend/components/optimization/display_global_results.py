import streamlit as st
import pandas as pd
from frontend.components.utils.plotter import Plotter

class DisplayGlobalResults:
    def __init__(self, optimization_results: dict, list_info: list):
        self.plotter = None
        self.optimization_results = optimization_results
        self.list_info = list_info

    def show(self):
        st.divider()
        self.show_summary_metrics()
        st.divider()
        self.show_global_curve()

    def show_summary_metrics(self):
        self._show_summary_metrics()

    def show_global_curve(self):
        #field_name = self.list_info[0] if self.list_info else "Unknown Field"
        #st.markdown(f"#### Global optimization curve: {field_name}")
        self.plotter = Plotter(self.optimization_results)
        fig = self.plotter.create_global_curve()
        st.plotly_chart(fig, use_container_width=True)

    def _show_summary_metrics(self):
        summary: list = self.optimization_results['summary']
        used_percentage = (summary['total_qgl'] / summary['qgl_limit']) * 100

        html = f"""
        <div class="metric-cards-vertical">
            <div class="metric-card">
                <div class="metric-title">Total Production</div>
                <div class="metric-value">{summary['total_production']:.2f} <span class="metric-unit">bbl</span></div>
            </div>
            <div class="metric-card">
                <div class="metric-title">Total QGL Used</div>
                <div class="metric-value">{summary['total_qgl']:.2f} <span class="metric-unit">Mscf</span></div>
                <!-- <div class="status-tag">{used_percentage:.1f}% of the limit</div> -->
            </div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)