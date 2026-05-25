from fastapi import APIRouter, UploadFile, File, HTTPException
import tempfile
import os
from backend.services.data_loader_service import DataLoader

router = APIRouter(prefix="/data", tags=["Data"])

@router.post("/load")
def load_data(file: UploadFile = File(...)):
    """Upload a production data CSV and parse it in the backend on the server side."""
    try:
        # Create a temporary file on the server to store uploaded bytes
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
            tmp.write(file.file.read())
            tmp_path = tmp.name
        
        try:
            loader = DataLoader(tmp_path)
            q_gl_list, q_fluid_list, wct_list, list_info = loader.load_data()
            return {
                "q_gl_list": q_gl_list,
                "q_fluid_list": q_fluid_list,
                "wct_list": wct_list,
                "list_info": list_info
            }
        finally:
            # Clean up the temp file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load and parse data in backend: {str(e)}")
