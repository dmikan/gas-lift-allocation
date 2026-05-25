from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.controllers.well_controller import router as well_router
from backend.controllers.optimization_controller import router as optimization_router
from backend.controllers.data_controller import router as data_router
from backend.database import init_db

app = FastAPI(
    title="Gas Lift Allocation Optimizer API",
    description="Backend API for curve fitting, constrained, and global optimizations of Gas Lift production.",
    version="1.0.0"
)

# Configure CORS so Streamlit can make requests safely
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for local development
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Register controllers/routers
app.include_router(well_router, prefix="/api")
app.include_router(optimization_router, prefix="/api")
app.include_router(data_router, prefix="/api")

@app.on_event("startup")
def on_startup():
    """Ensure database schema is created and initialized upon application launch."""
    print("Initializing SQLModel database schema...")
    try:
        init_db()
        print("Database schema successfully synchronized.")
    except Exception as e:
        print(f"Error initializing database: {e}")

@app.get("/")
def read_root():
    return {"status": "online", "service": "Gas Lift Allocation Optimizer API"}
