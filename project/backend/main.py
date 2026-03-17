from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from backend.api.routes import router as api_router
from backend.config import settings




def create_app() -> FastAPI:
    """Application factory for FastAPI app."""
    app = FastAPI(title=settings.app_name)

    # CORS for local Streamlit frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=settings.api_prefix)

    @app.get("/")
    def root() -> dict:
        return {"message": "AI Database Generator backend is running."}

    return app


app = create_app()

