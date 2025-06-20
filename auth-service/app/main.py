from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import asyncio
from app.configs.config import settings
from app.configs.database import create_db_and_tables, test_connection
from app.routes import users, auth, verify

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("Starting application...")
    try:
        # Test database connection and create tables
        await asyncio.get_event_loop().run_in_executor(None, create_db_and_tables)
        print("Application startup complete")
    except Exception as e:
        print(f"Startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    print("Shutting down application...")

# Create FastAPI app with lifespan
app = FastAPI(
    title="Your API",
    description="API with proper database connection handling",
    version="1.0.0",
    lifespan=lifespan
)

# Include routers
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(verify.router)

@app.get("/")
async def root():
    return {"message": "Server running successfully", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Health check endpoint for Docker/deployment"""
    try:
        await asyncio.get_event_loop().run_in_executor(None, test_connection)
        return {
            "status": "healthy",
            "database": "connected",
            "environment": settings.ENVIRONMENT
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service unavailable: {str(e)}"
        )

@app.get("/config")
async def get_config():
    """Debug endpoint to check configuration (remove in production)"""
    return {
        "database_url_configured": bool(settings.DATABASE_URL),
        "jwt_secret_configured": bool(settings.JWT_SECRET),
        "environment": settings.ENVIRONMENT,
        "database_host": settings.DATABASE_URL.split("@")[1].split(":")[0] if settings.DATABASE_URL else "not configured"
    }