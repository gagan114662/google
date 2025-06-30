from fastapi import FastAPI
from app.api.main_router import router as health_router # Renamed for clarity
from app.core.config import Base, engine
# from app.api import main_api_router # This will be for versioned API endpoints

# Create database tables
# In a production setup, you'd use Alembic for migrations.
# For now, this is fine for initial development.
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Chimera Core API",
    description="The backend API for Project Chimera, an open-source autonomous agent platform.",
    version="0.1.0"
)

# Include the health check router
app.include_router(health_router)

# Include other routers, e.g., for a versioned API
# app.include_router(main_api_router, prefix="/api/v1")


# Example of how to add event handlers for startup/shutdown
# @app.on_event("startup")
# async def startup_event():
#     # Initialize things like database connections, ML models, etc.
#     print("Chimera Core API starting up...")

# @app.on_event("shutdown")
# async def shutdown_event():
#     # Clean up resources
#     print("Chimera Core API shutting down...")

if __name__ == "__main__":
    import uvicorn
    # This is for local development running this file directly.
    # Typically, you'd run: uvicorn app.main:app --reload
    uvicorn.run(app, host="0.0.0.0", port=8000)
