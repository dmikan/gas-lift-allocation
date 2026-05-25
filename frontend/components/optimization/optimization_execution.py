import streamlit as st
from frontend.utils.api_client import APIClient
from frontend.components.optimization.display_global_results import DisplayGlobalResults
from frontend.components.optimization.display_constrained_results import DisplayConstrainedResults
from frontend.utils.state_keys import StateKeys

class OptimizationExecutionComponent:
    def __init__(self, db=None):
        # We accept db for signature compatibility, but communicate exclusively via APIClient
        self.api_client = APIClient()

    def run_global_optimization(self, loaded_data, global_settings, message_outside=False):
        q_gl_list, q_fluid_list, wct_list, list_info = loaded_data

        if not q_gl_list:
            st.warning("No valid data loaded to execute global optimization.")
            return

        just_calculated = False
        if st.button("Execute Global Optimization", type="primary", use_container_width=True):
            with st.spinner("Executing Global Optimization in backend..."):
                try:
                    optimization_results = self.api_client.run_global_optimization(
                        q_gl_list=q_gl_list,
                        q_fluid_list=q_fluid_list,
                        wct_list=wct_list,
                        list_info=list_info,
                        settings=global_settings
                    )

                    st.session_state[StateKeys.SESSION_KEY_GLOBAL] = optimization_results
                    st.session_state[StateKeys.SESSION_KEY_LAST_OPTIMIZATION_TAB] = "global"
                    just_calculated = True
                    if not message_outside:
                        self.optimization_completed_message(flag="global")
                        display_global_results = DisplayGlobalResults(optimization_results, list_info)
                        display_global_results.show()

                except Exception as e:
                    st.error(f"❌ Error during global optimization: {str(e)}")

        if not just_calculated and StateKeys.SESSION_KEY_GLOBAL in st.session_state:
            optimization_results = st.session_state[StateKeys.SESSION_KEY_GLOBAL]
            if not message_outside:
                self.optimization_completed_message(flag="global")
                display_global_results = DisplayGlobalResults(optimization_results, list_info)
                display_global_results.show()

    def run_constrained_optimization(self, loaded_data, constrained_settings, message_outside=False):
        q_gl_list, q_fluid_list, wct_list, list_info = loaded_data

        if not q_gl_list:
            st.warning("There are no valid data loaded to execute the constrained optimization.")
            return

        just_calculated = False
        if st.button("Execute Constrained Optimization", type="primary", use_container_width=True):
            with st.spinner("Executing Constrained Optimization in backend..."):
                try:
                    optimization_results, well_results = self.api_client.run_constrained_optimization(
                        q_gl_list=q_gl_list,
                        q_fluid_list=q_fluid_list,
                        wct_list=wct_list,
                        list_info=list_info,
                        settings=constrained_settings
                    )

                    st.session_state[StateKeys.SESSION_KEY_CONSTR] = optimization_results
                    st.session_state[StateKeys.SESSION_KEY_WELL] = well_results
                    st.session_state[StateKeys.SESSION_KEY_LAST_OPTIMIZATION_TAB] = "constrained"

                    just_calculated = True
                    if not message_outside:
                        self.optimization_completed_message(flag="constrained")
                        display_constrained_results = DisplayConstrainedResults(optimization_results, well_results)
                        display_constrained_results.show()

                except Exception as e:
                    st.error(f"❌ Error during constrained optimization: {str(e)}")

        if not just_calculated and StateKeys.SESSION_KEY_CONSTR in st.session_state and StateKeys.SESSION_KEY_WELL in st.session_state:
            optimization_results = st.session_state[StateKeys.SESSION_KEY_CONSTR]
            well_results = st.session_state[StateKeys.SESSION_KEY_WELL]
            if not message_outside:
                self.optimization_completed_message(flag="constrained")
                display_constrained_results = DisplayConstrainedResults(optimization_results, well_results)
                display_constrained_results.show()

    def optimization_completed_message(self, flag):
        if flag == "constrained":
            st.markdown(f"""
                <div class="save-banner-ok">
                    <span style="font-size:24px;">🚀</span>
                    <div>
                        <strong>Constrained optimization completed!</strong>
                    <div class="banner-path">The results are ready for analysis.</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        elif flag == "global":
            st.markdown(f"""
                <div class="save-banner-ok">
                    <span style="font-size:24px;">🚀</span>
                    <div>
                        <strong>Global optimization completed!</strong>
                    <div class="banner-path">Total qgl has stabilized. The results are ready for analysis.</div>
                </div>
            </div>
        """, unsafe_allow_html=True)