"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.places import router as places_router
from app.api.projects import router as projects_router
from app.config import settings
from app.database import create_tables
from app.exceptions import register_exception_handlers

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler — runs on startup and shutdown."""
    logger.info("Starting Travel Planner API...")
    create_tables()
    logger.info("Database tables created/verified.")
    yield
    logger.info("Shutting down Travel Planner API...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "A management application that helps travellers plan trips and collect "
        "desired places to visit. Uses the Art Institute of Chicago API as a "
        "source for places (artworks)."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
register_exception_handlers(app)

# Include routers
app.include_router(projects_router)
app.include_router(places_router)


@app.get("/", tags=["Health"])
def root():
    """Health check endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "healthy",
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "database": "connected",
        "artic_api": settings.ARTIC_API_BASE_URL,
    }
