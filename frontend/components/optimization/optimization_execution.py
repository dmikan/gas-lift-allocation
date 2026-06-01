import streamlit as st
from frontend.utils.api_client import APIClient
from frontend.utils.state_keys import StateKeys

class OptimizationExecutionComponent:
    def __init__(self, db=None):
        # We accept db for signature compatibility, but communicate exclusively via APIClient
        self.api_client = APIClient()

    def run_global_optimization(self, loaded_data, global_settings):
        q_gl_list, q_fluid_list, wct_list, list_info = loaded_data

        if not q_gl_list:
            st.warning("No valid data loaded to execute global optimization.")
            return

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
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Error during global optimization: {str(e)}")

    def run_constrained_optimization(self, loaded_data, constrained_settings):
        q_gl_list, q_fluid_list, wct_list, list_info = loaded_data

        if not q_gl_list:
            st.warning("There are no valid data loaded to execute the constrained optimization.")
            return

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
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Error during constrained optimization: {str(e)}")

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