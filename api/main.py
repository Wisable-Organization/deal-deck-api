import os
import traceback
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from api.routes import router
from api.routes.auth import router as auth_router


def create_app() -> FastAPI:
    app = FastAPI(title="DealDash API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception handlers - print stack traces for all errors
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handle HTTP exceptions and print stack trace"""
        print(f"\n{'='*80}")
        print(f"HTTPException occurred: {exc.status_code} - {exc.detail}")
        print(f"Request: {request.method} {request.url}")
        print(f"{'='*80}")
        traceback.print_exc()
        print(f"{'='*80}\n")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle all unhandled exceptions and print stack trace"""
        print(f"\n{'='*80}")
        print(f"Unhandled exception occurred: {type(exc).__name__}")
        print(f"Request: {request.method} {request.url}")
        print(f"{'='*80}")
        traceback.print_exc()
        print(f"{'='*80}\n")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )

    # Include auth routes first
    app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
    
    # Include API routes
    app.include_router(router, prefix="/api")

    return app


app = create_app()


