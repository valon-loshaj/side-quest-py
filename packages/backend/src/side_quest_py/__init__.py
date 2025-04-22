"""Side Quest Py - A FastAPI-based adventure game backend.

This module serves as the main entry point for the Side Quest Py application.
It initializes the FastAPI application, configures the database, and sets up routes.
"""

import os
from typing import Dict, Any, Optional

import pymysql
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.side_quest_py.api.config import settings
from src.side_quest_py.database import get_db

# Use MySQLdb as driver for pymysql
pymysql.install_as_MySQLdb()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        FastAPI: Configured FastAPI application instance
    """
    # Create FastAPI app using settings from config
    app = FastAPI(title=settings.APP_NAME, description=settings.APP_DESCRIPTION, version=settings.APP_VERSION)

    # Configure CORS from settings
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )

    # Add a simple route to verify the app is working
    @app.get("/hello")
    def hello():
        return {"message": "Hello, Side Quest!"}

    # Add health check endpoint
    @app.get("/health")
    def health_check(db: Session = Depends(get_db)):
        try:
            # Test the database connection
            db.execute(text("SELECT 1"))
            db_status = "connected"
        except SQLAlchemyError as e:
            db_status = f"error: {str(e)}"

        return {
            "status": "healthy" if db_status == "connected" else "unhealthy",
            "db": {
                "status": db_status,
                "uri": settings.DATABASE_URL.split("@")[-1] if settings.DATABASE_URL else "Not configured",
                "env": settings.FASTAPI_ENV,
            },
            "app": {"env": settings.FASTAPI_ENV, "debug": settings.DEBUG},
        }

    from src.side_quest_py.api.routes.adventurer_routes import router as adventurer_router
    from src.side_quest_py.api.routes.auth_routes import router as auth_router
    from src.side_quest_py.api.routes.quests_routes import router as quest_router

    app.include_router(adventurer_router)
    app.include_router(quest_router)
    app.include_router(auth_router)

    return app


app = create_app()
