from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from backend.app.core.database import get_db
from backend.app.services.ai.huggingface import HuggingFaceProvider
from backend.app.services.discovery.registry import source_registry

router = APIRouter(tags=["Health"])

@router.get("/health")
@router.get("/api/health")
async def health_check():
    return {
        "status": "HEALTHY",
        "service": "LeadForge API Engine",
        "version": "1.0.0"
    }

@router.get("/health/dependencies")
async def health_dependencies(db: AsyncSession = Depends(get_db)):
    # 1. Database Check
    db_status = "HEALTHY"
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"ERROR: {str(e)}"

    # 2. AI Provider Check
    ai_status = "HEALTHY"
    try:
        provider = HuggingFaceProvider()
        ai_health = await provider.health_check()
        ai_status = ai_health.get("status", "CONNECTED")
    except Exception as e:
        ai_status = f"ERROR: {str(e)}"

    # 3. Lead Sources Check
    sources_health = await source_registry.check_all_health()

    return {
        "overall_status": "HEALTHY" if db_status == "HEALTHY" else "DEGRADED",
        "database": db_status,
        "ai_provider": ai_status,
        "sources": sources_health
    }
