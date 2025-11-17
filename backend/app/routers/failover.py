"""
Failover simulation and management endpoints
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
import time
import logging

from app.config import settings
from app.services.redis_service import redis_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/simulate")
async def simulate_failover():
    """Simulate a failover event"""
    try:
        start_time = time.time()

        # Mark current region as failing over
        redis_service.set_state(f"{settings.REGION}:status", "failover_in_progress")

        # Determine target region
        target_region = "region2" if settings.REGION == "region1" else "region1"

        # Sync state to target region (in real scenario, this would replicate data)
        active_users = redis_service.get_state("stats:active_users")
        active_devices = redis_service.get_state("stats:active_devices")

        # Simulate state replication
        redis_service.set_state(f"{target_region}:failover_state", {
            "active_users": active_users,
            "active_devices": active_devices,
            "source_region": settings.REGION,
            "failover_time": datetime.now(timezone.utc).isoformat()
        })

        # Mark failover complete
        redis_service.set_state(f"{settings.REGION}:status", "failed_over")
        redis_service.set_state(f"{target_region}:status", "active")

        end_time = time.time()
        failover_latency = end_time - start_time

        return {
            "status": "success",
            "source_region": settings.REGION,
            "target_region": target_region,
            "failover_latency_seconds": round(failover_latency, 6),
            "message": f"Failover completed from {settings.REGION} to {target_region}",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        logger.error(f"Failover simulation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_failover_status():
    """Get failover status"""
    try:
        status = redis_service.get_state(f"{settings.REGION}:status")
        failover_state = redis_service.get_state(f"{settings.REGION}:failover_state")

        return {
            "region": settings.REGION,
            "status": status or "active",
            "failover_state": failover_state,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        logger.error(f"Error getting failover status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/restore")
async def restore_region():
    """Restore region to active status"""
    try:
        redis_service.set_state(f"{settings.REGION}:status", "active")

        return {
            "status": "success",
            "region": settings.REGION,
            "message": f"{settings.REGION} restored to active status",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        logger.error(f"Error restoring region: {e}")
        raise HTTPException(status_code=500, detail=str(e))
