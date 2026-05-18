from pathlib import Path
class StateKeys:
    SESSION_KEY_GLOBAL = "global_optimization_results"
    SESSION_KEY_CONSTR = "constrained_optimization_results"
    SESSION_KEY_WELL = "well_results"
    SESSION_KEY_LAST_OPTIMIZATION_TAB = "_last_optimization_tab"
    SESSION_KEY_UPLOADED_FILE = "uploaded_file"
    SESSION_KEY_TEMP_PATH = "temp_path"
    SESSION_KEY_DATA_LOAD_MODE = "data_load_mode"
    SESSION_KEY_INFO_DF = "information_about_field_and_wells"
    SESSION_KEY_WCT_DF = "water_cut_threshold"
    SESSION_KEY_PROD_DF = "production_data"
    SESSION_KEY_FINAL_DF = "final_dataframe_to_be_saved"
    SESSION_KEY_DATA_SAVED = "data_saved_successfully"