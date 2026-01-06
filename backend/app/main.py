"""Bo_Check FastAPI Application Entry Point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.api.routes import cities, movies, theaters, shows, stats


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup - try to init database, but continue if it fails (demo mode)
    try:
        await init_db()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Database initialization skipped (demo mode): {e}")
    yield
    # Shutdown
    pass


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    🎬 **Bo_Check API** - Movie Booking Statistics for India
    
    Get real-time movie booking stats including:
    - 🎥 Movie listings by city
    - 🎭 Theater information
    - 🕐 Show timings
    - 💺 Seat availability
    - 💰 Ticket prices
    - 📊 Analytics and trends
    
    **Supported Cities:** Mumbai, Delhi, Bangalore, Hyderabad, Chennai, Kolkata, Pune, Ahmedabad
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(cities.router, prefix=settings.api_v1_prefix)
app.include_router(movies.router, prefix=settings.api_v1_prefix)
app.include_router(theaters.router, prefix=settings.api_v1_prefix)
app.include_router(shows.router, prefix=settings.api_v1_prefix)
app.include_router(stats.router, prefix=settings.api_v1_prefix)


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "database": "connected",  # TODO: Add actual DB check
        "cache": "connected",  # TODO: Add actual Redis check
    }
