"""
User activity endpoints
"""
from fastapi import APIRouter
from typing import List, Dict
from datetime import datetime, timezone
import logging

from app.config import settings
from app.services.redis_service import redis_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/active")
async def get_active_users():
    """Get active users count and details"""
    count = redis_service.get_state("stats:active_users") or 0
    connections = redis_service.get_state("stats:active_connections") or 0

    # Get latest user activity from Redis
    user_activity = redis_service.get_state("latest:user_activity")

    if not user_activity:
        user_activity = {
            "active_users": count,
            "active_connections": connections,
            "server_cpu_pct": 0,
            "server_memory_gb": 0,
            "average_latency_ms": 0
        }

    return {
        "metrics": user_activity,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/activity")
async def get_user_activity():
    """Get detailed user activity"""
    activity = redis_service.get_state("latest:user_activity_full")

    if not activity:
        return {
            "message": "No user activity data available",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    return activity


@router.get("/connections")
async def get_active_connections():
    """Get active backend connections"""
    connections = redis_service.get_state("stats:active_connections") or 0

    return {
        "active_connections": connections,
        "region": settings.REGION,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
