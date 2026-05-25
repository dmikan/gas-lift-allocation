import streamlit as st
from pathlib import Path
import os
from app.components.file_upload.manual_input_component import ManualInputComponent
from app.components.file_upload.csv_input_component import CSVInputComponent
from app.components.file_upload.proper_input_component import ProperInputComponent
from app.utils.state_keys import StateKeys

class FileUploadComponent:


    def show(self):
        """Show the file upload component."""
        self._init_session_state()
        tmp_dir: Path = self._get_tmp_dir()
        tab1, tab2, _ = self._choose_data_loading_method()

        with tab1:
            manual_input = ManualInputComponent(tmp_dir)
            manual_input.load()
        with tab2:
            csv_input = CSVInputComponent(tmp_dir)
            csv_input.load()
        #with tab3:
            #proper_input = ProperInputComponent(tmp_dir)
            #proper_input.load()



    def _init_session_state(self):
        """Initialize session state variables."""
        if StateKeys.SESSION_KEY_UPLOADED_FILE not in st.session_state:
            st.session_state[StateKeys.SESSION_KEY_UPLOADED_FILE] = None
        if StateKeys.SESSION_KEY_TEMP_PATH not in st.session_state:
            st.session_state[StateKeys.SESSION_KEY_TEMP_PATH] = None
        if StateKeys.SESSION_KEY_DATA_LOAD_MODE not in st.session_state:
            st.session_state[StateKeys.SESSION_KEY_DATA_LOAD_MODE] = None



    def _get_tmp_dir(self) -> Path:
        """Get the temporary directory for storing uploaded files."""
        is_snowflake = os.path.exists("/home/udf")
        if is_snowflake:
            return Path("/tmp")
        else:
            project_root = Path(__file__).parent.parent.parent.parent
            local_path = project_root / "tmp"
            local_path.mkdir(parents=True, exist_ok=True)
            return local_path


    
    def _choose_data_loading_method(self):
        """Choose the data loading method."""
        tab1, tab2, tab3 = st.tabs([
            "Manual input",
            "Upload csv file",
            "Generate from Prosper"
        ])
        return tab1, tab2, tab3