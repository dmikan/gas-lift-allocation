import streamlit as st
from frontend.components.historical_data.historical_data_component import HistoricalDataComponents

class HistoricalPage:
    def show(self):
        st.subheader("Historical Data")
        
        components = HistoricalDataComponents()
        
        # Show graphs in tabs
        tab1, tab2 = st.tabs(["Gas-Liquid Ratio", "Variable Importance"])
        
        with tab1:
            components.render_scatter_plot()
        
        with tab2:
            components.render_mutual_info_heatmap()