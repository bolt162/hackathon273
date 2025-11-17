"""
Diagnostics and RAG endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import Optional
from datetime import datetime, timezone
import logging
from pydantic import BaseModel

from app.services.rag_service import rag_service

logger = logging.getLogger(__name__)
router = APIRouter()


class QueryRequest(BaseModel):
    question: str
    context: Optional[dict] = None


@router.post("/query")
async def query_llm(request: QueryRequest):
    """Query using LLM with RAG context"""
    try:
        answer = rag_service.query_with_llm(request.question, request.context)

        return {
            "question": request.question,
            "answer": answer,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/logs/errors/{error_code}")
async def get_frequent_ips(error_code: int, top_n: int = 10):
    """Get most frequent IPs generating a specific error code"""
    try:
        results = rag_service.get_frequent_ips_by_error(error_code, top_n)

        return {
            "error_code": error_code,
            "top_ips": results,
            "count": len(results),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        logger.error(f"Error analyzing logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/logs/stats")
async def get_log_statistics():
    """Get overall log statistics"""
    try:
        stats = rag_service.get_error_statistics()

        return {
            "statistics": stats,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/logs/summary")
async def get_diagnostics_summary():
    """Get diagnostics summary"""
    try:
        summary = rag_service.get_diagnostics_summary()

        return {
            "summary": summary,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/logs/search")
async def search_logs(query: str, limit: int = 50):
    """Search logs by keyword"""
    try:
        results = rag_service.search_logs(query, limit)

        return {
            "query": query,
            "results": results,
            "count": len(results),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        logger.error(f"Error searching logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))
