"""
FastAPI Backend for Enterprise SRE System
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import asyncio
from datetime import datetime, timezone

from app.config import settings
from app.services.redis_service import redis_service
from app.services.embedding_service import embedding_service
from app.services.rag_service import rag_service
from app.routers import devices, users, images, diagnostics, failover

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management for the application"""
    logger.info(f"Starting backend for {settings.REGION}")

    # Initialize embeddings on startup
    try:
        logger.info("Initializing image embeddings...")
        count = embedding_service.initialize_embeddings(settings.DATA_PATH)
        logger.info(f"Initialized {count} embeddings")
    except Exception as e:
        logger.error(f"Error initializing embeddings: {e}")

    # Set initial state in Redis
    redis_service.set_state(f"{settings.REGION}:status", "active")
    redis_service.set_state(f"{settings.REGION}:version", settings.APP_VERSION)
    redis_service.set_state(f"{settings.REGION}:startup_time", datetime.now(timezone.utc).isoformat())

    yield

    # Cleanup on shutdown
    logger.info(f"Shutting down {settings.REGION}")
    redis_service.set_state(f"{settings.REGION}:status", "inactive")


app = FastAPI(
    title="Enterprise SRE AI System",
    description="Tier-0 Enterprise Reliability System with 99.99999% availability",
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(devices.router, prefix="/api/devices", tags=["Devices"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(images.router, prefix="/api/images", tags=["Images"])
app.include_router(diagnostics.router, prefix="/api/diagnostics", tags=["Diagnostics"])
app.include_router(failover.router, prefix="/api/failover", tags=["Failover"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Enterprise SRE AI System",
        "region": settings.REGION,
        "version": settings.APP_VERSION,
        "status": "operational",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    redis_healthy = redis_service.health_check()

    return {
        "status": "healthy" if redis_healthy else "degraded",
        "region": settings.REGION,
        "version": settings.APP_VERSION,
        "redis": "connected" if redis_healthy else "disconnected",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/fastapi/{region}/getappversion")
async def get_app_version(region: str):
    """Get application version for a region"""
    if region != settings.REGION:
        # Try to get from Redis in case of cross-region query
        version = redis_service.get_state(f"{region}:version")
        if version:
            return {"version": version, "region": region}
        raise HTTPException(status_code=404, detail=f"Region {region} not found")

    return {
        "version": settings.APP_VERSION,
        "region": settings.REGION
    }


@app.get("/api/status")
async def get_status():
    """Get system status"""
    status = redis_service.get_state(f"{settings.REGION}:status")
    startup_time = redis_service.get_state(f"{settings.REGION}:startup_time")

    # Get counts from Redis
    active_devices = redis_service.get_state("stats:active_devices") or 0
    active_users = redis_service.get_state("stats:active_users") or 0

    return {
        "region": settings.REGION,
        "status": status or "active",
        "version": settings.APP_VERSION,
        "startup_time": startup_time,
        "active_devices": active_devices,
        "active_users": active_users,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.post("/api/simulate/high-traffic")
async def simulate_high_traffic(background_tasks: BackgroundTasks):
    """Simulate high traffic scenario"""
    logger.info(f"Simulating high traffic on {settings.REGION}")

    # Increment traffic counter
    count = redis_service.increment(f"{settings.REGION}:traffic_simulation_count")

    return {
        "status": "simulating",
        "region": settings.REGION,
        "simulation_count": count,
        "message": "High traffic simulation initiated",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/api/metrics")
async def get_metrics():
    """Get system metrics"""
    metrics = {
        "region": settings.REGION,
        "active_devices": redis_service.get_state("stats:active_devices") or 0,
        "active_users": redis_service.get_state("stats:active_users") or 0,
        "total_requests": redis_service.get_state(f"{settings.REGION}:total_requests") or 0,
        "error_count": redis_service.get_state(f"{settings.REGION}:error_count") or 0,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    return metrics


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
