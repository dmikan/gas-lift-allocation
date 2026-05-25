import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from frontend.pages.optimization_page import OptimizationPage
from frontend.pages.other_services_page import OtherServicesPage
from frontend.pages.historical_data_page import HistoricalPage
from frontend.styles.custom_styles import inject_global_css

def main():
    # Configuration
    inject_global_css()
    st.set_page_config(page_title="Gas Lift Allocation Optimizer", layout="wide")
    st.title("🛢️ Gas Lift Allocation Optimizer")

    # --- Tabs ---
    tabs = st.sidebar.radio(
        "Select an option", 
        ["Optimization", "Historical Data" ,"Other services"]
    )

    if tabs == "Optimization":
        page = OptimizationPage()
        page.show()
    elif tabs == "Historical Data":
        page = HistoricalPage()
        page.show()   
    elif tabs == "Other services":
        page = OtherServicesPage()
        page.show()

if __name__ == "__main__":
    main()