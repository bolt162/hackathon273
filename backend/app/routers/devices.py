"""
Device management endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Optional
from datetime import datetime, timezone
import paho.mqtt.client as mqtt
import logging

from app.config import settings
from app.services.redis_service import redis_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/active")
async def get_active_devices():
    """Get count of active devices"""
    count = redis_service.get_state("stats:active_devices") or 0

    # Get devices by site
    devices_by_site = {}
    for i in range(1, 11):
        site_key = f"stats:site_{i}_devices"
        devices_by_site[f"site_{i}"] = redis_service.get_state(site_key) or 0

    return {
        "total_active_devices": count,
        "devices_by_site": devices_by_site,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/status/{device_id}")
async def get_device_status(device_id: str):
    """Get status of a specific device"""
    device_data = redis_service.get_state(f"device:{device_id}")

    if not device_data:
        raise HTTPException(status_code=404, detail="Device not found")

    return device_data


@router.get("/alerts")
async def get_device_alerts():
    """Get devices in alert state"""
    # This would query Redis for devices with status.state = "ALERT"
    # For demo purposes, return simulated data

    alerts = []
    alert_keys = redis_service.list_keys("device:*:alert")

    for key in alert_keys[:10]:  # Limit to 10
        alert_data = redis_service.get_state(key)
        if alert_data:
            alerts.append(alert_data)

    return {
        "alert_count": len(alert_keys),
        "alerts": alerts,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/metrics/site/{site_id}")
async def get_site_metrics(site_id: str):
    """Get aggregated metrics for a site"""
    site_data = redis_service.get_hash(f"site:{site_id}:metrics")

    if not site_data:
        # Return default data
        return {
            "site_id": site_id,
            "device_count": 0,
            "alert_count": 0,
            "average_health": 0,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    return site_data
