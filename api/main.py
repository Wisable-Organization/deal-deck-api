import os
import httpx
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from .routes import router
from .routes.auth import router as auth_router


def create_app() -> FastAPI:
    app = FastAPI(title="DealDash API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include auth routes first
    app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
    
    # Include API routes
    app.include_router(router, prefix="/api")

    return app


app = create_app()


