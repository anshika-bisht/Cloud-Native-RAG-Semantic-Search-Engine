from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logger import logger
from app.api.dependencies import get_vector_store
from app.api.middleware.logging import PerformanceLoggingMiddleware

# Import routers
from app.api.routes import upload, query, documents, sessions, system

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Cloud-Native RAG API...")
    # Initialize Vector Store Collection
    vector_store = get_vector_store()
    try:
        await vector_store.create_collection()
        logger.info("Vector Store initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize Vector Store: {e}")
        
    yield
    
    logger.info("Shutting down RAG API...")

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="Production-Grade Cloud-Native RAG Semantic Search Engine",
        version="2.0.0",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url=f"{settings.API_V1_STR}/docs",
        lifespan=lifespan
    )

    # Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(PerformanceLoggingMiddleware)

    # Include Routers
    app.include_router(upload.router, prefix=settings.API_V1_STR)
    app.include_router(query.router, prefix=settings.API_V1_STR)
    app.include_router(documents.router, prefix=settings.API_V1_STR)
    app.include_router(sessions.router, prefix=settings.API_V1_STR)
    app.include_router(system.router, prefix=settings.API_V1_STR)

    return app

app = create_app()
