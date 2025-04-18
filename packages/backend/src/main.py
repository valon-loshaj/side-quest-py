"""
This is the main file for the Side Quest FastAPI application.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import the centralized settings
from src.side_quest_py.api.config import settings
from src.side_quest_py.api.routes.auth_routes import router as auth_router

# Create FastAPI app instance
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)


# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to Side Quest API"}


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "app": {"env": settings.FASTAPI_ENV, "version": settings.APP_VERSION}}


# Import and include routers
app.include_router(auth_router)
# from src.side_quest_py.api.routes import adventurer_router, quest_router, etc.
# app.include_router(adventurer_router)
# app.include_router(quest_router)
# ...

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
