"""
Image intelligence and semantic search endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict
from datetime import datetime, timezone
import logging
from pydantic import BaseModel

from app.services.embedding_service import embedding_service
from app.services.redis_service import redis_service

logger = logging.getLogger(__name__)
router = APIRouter()


class ImageSearchRequest(BaseModel):
    query: str
    top_k: int = 5


@router.post("/search")
async def search_images(request: ImageSearchRequest):
    """Search for images using natural language query"""
    try:
        results = embedding_service.search_images(request.query, request.top_k)

        return {
            "query": request.query,
            "results": results,
            "count": len(results),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        logger.error(f"Error searching images: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_images():
    """List all processed images"""
    try:
        # Get all embedding keys
        keys = redis_service.list_keys("embedding:*")

        images = []
        for key in keys[:50]:  # Limit to 50
            embedding_data = redis_service.get_embedding(key.replace("embedding:", ""))
            if embedding_data:
                images.append({
                    "key": key.replace("embedding:", ""),
                    "metadata": embedding_data["metadata"]
                })

        return {
            "total": len(keys),
            "images": images,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        logger.error(f"Error listing images: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/site/{site_id}")
async def get_site_images(site_id: str):
    """Get images for a specific site"""
    try:
        # Get all embedding keys for the site
        keys = redis_service.list_keys(f"embedding:{site_id}*")

        images = []
        for key in keys:
            embedding_data = redis_service.get_embedding(key.replace("embedding:", ""))
            if embedding_data:
                images.append({
                    "key": key.replace("embedding:", ""),
                    "metadata": embedding_data["metadata"]
                })

        return {
            "site_id": site_id,
            "count": len(images),
            "images": images,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        logger.error(f"Error getting site images: {e}")
        raise HTTPException(status_code=500, detail=str(e))
