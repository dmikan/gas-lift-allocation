import streamlit as st
from app.components.optimization.display_global_results import DisplayGlobalResults


class OptimizationSettingsComponent:
    def __init__(self):
        self.qgl_min_global = 300
        self.p_qoil_global = 70.0
        self.p_qgl_global = 300.0
        self.qgl_limit_constrained = 1000
        self.qgl_min_constrained = 300
        self.p_qoil_constrained = 70.0
        self.p_qgl_constrained = 300.0

    
    def choose_global_settings(self, use_expander=True, render_button=None):
        '''
        If use_expander=False, only the inputs are rendered (no expander wrapper).
        If render_button is a callable(settings_dict), it is called at the end so the button renders inside the same expander.
        '''
        def _content():
            row1_col1, row1_col2 = st.columns(2)
            with row1_col1:
                self.p_qoil_global = st.number_input(
                    "Oil price (USD/bbl)",
                    min_value=0.1,
                    max_value=None,
                    value=100.0,
                    step=1.0,
                    key="p_qoil_global"
                )

            with row1_col2:
                self.p_qgl_global = st.number_input(
                    "Gas cost (USD/Mscf)",
                    min_value=0.1,
                    max_value=None,
                    value=1.0,
                    step=1.0,
                    key="p_qgl_global"
                )

            row2_col1, row2_col2 = st.columns(2)

            with row2_col1:
                self.qgl_min_global = st.number_input(
                    "Minimum QGL limit (Mscf)",
                    min_value=0.1,
                    max_value=None,
                    value=1.0,
                    step=1.0,
                    key="qgl_min_global"
                )

            settings = dict(
                p_qoil_global=self.p_qoil_global,
                p_qgl_global=self.p_qgl_global,
                qgl_min_global=self.qgl_min_global
            )
            if render_button:
                render_button(settings)
            return settings

        if use_expander:
            with st.expander("Global Optimization Configuration", expanded=True):
                return _content()
        return _content()

    def choose_constrained_settings(self, use_expander=True, render_button=None):
        '''
        If use_expander=False, only the inputs are rendered (no expander wrapper).
        If render_button is a callable(settings_dict), it is called at the end so the button renders inside the same expander.
        '''
        def _content():
            row1_col1, row1_col2 = st.columns(2)

            with row1_col1:
                self.qgl_limit_constrained = st.number_input(
                    "Total QGL limit (Mscf)",
                    min_value=0,
                    max_value=None,
                    value=1000,
                    step=100,
                    key="qgl_limit"
                )

            with row1_col2:
                self.qgl_min_constrained = st.number_input(
                    "Minimum QGL limit (Mscf)",
                    min_value=0.1,
                    max_value=None,
                    value=1.0,
                    step=1.0,
                    key="qgl_min"
                )

            row2_col1, row2_col2 = st.columns(2)

            with row2_col1:
                self.p_qoil_constrained = st.number_input(
                    "Oil price (USD/bbl)",
                    min_value=0.1,
                    max_value=None,
                    value=100.0,
                    step=1.0,
                    key="p_qoil"
                )

            with row2_col2:
                self.p_qgl_constrained = st.number_input(
                    "Gas price (USD/Mscf)",
                    min_value=0.1,
                    max_value=None,
                    value=1.0,
                    step=1.0,
                    key="p_qgl"
                )

            settings = dict(
                qgl_limit_constrained=self.qgl_limit_constrained,
                qgl_min_constrained=self.qgl_min_constrained,
                p_qoil_constrained=self.p_qoil_constrained,
                p_qgl_constrained=self.p_qgl_constrained
            )
            if render_button:
                render_button(settings)
            return settings

        if use_expander:
            with st.expander("Configuration of Optimization", expanded=True):
                return _content()
        return _content()