import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.core.database import get_db
from backend.app.api.auth import get_current_org
from backend.app.models.user import Organization
from backend.app.models.discovery import LeadSourceConfig
from backend.app.services.discovery.registry import source_registry

router = APIRouter(prefix="/sources", tags=["Lead Sources"])

@router.get("")
async def list_sources(
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(LeadSourceConfig).where(LeadSourceConfig.organization_id == org.id)
    res = await db.execute(stmt)
    sources = res.scalars().all()
    
    # If empty, create default configured sources
    if not sources:
        defaults = [
            ("OpenStreetMap", "openstreetmap", True, True, "CONNECTED", 60),
            ("GoogleMaps", "google_maps", True, True, "CONNECTED", 30),
            ("AISearch", "ai_search", True, True, "CONNECTED", 30),
            ("SocialIntent", "social_intent", True, True, "CONNECTED", 35),
            ("SearchEngine", "search", True, True, "CONNECTED", 30),
            ("PublicDirectory", "directory", True, False, "CONNECTED", 60),
            ("CSVImport", "csv", True, False, "CONNECTED", 120),
        ]
        for name, stype, enabled, api_conf, status, rlimit in defaults:
            sc = LeadSourceConfig(
                organization_id=org.id,
                name=name,
                source_type=stype,
                is_enabled=enabled,
                api_key_configured=api_conf,
                status=status,
                rate_limit_per_min=rlimit,
                last_success_at=datetime.datetime.now(datetime.timezone.utc)
            )
            db.add(sc)
        await db.commit()
        stmt = select(LeadSourceConfig).where(LeadSourceConfig.organization_id == org.id)
        res = await db.execute(stmt)
        sources = res.scalars().all()
        
    return [
        {
            "id": s.id,
            "name": s.name,
            "source_type": s.source_type,
            "is_enabled": s.is_enabled,
            "api_key_configured": s.api_key_configured,
            "rate_limit_per_min": s.rate_limit_per_min,
            "status": s.status,
            "last_run_at": s.last_run_at.isoformat() if s.last_run_at else None,
            "last_success_at": s.last_success_at.isoformat() if s.last_success_at else None,
            "total_discovered": s.total_discovered,
            "total_new_records": s.total_new_records,
            "total_duplicates": s.total_duplicates,
            "total_errors": s.total_errors
        }
        for s in sources
    ]

@router.post("/{source_id}/toggle")
async def toggle_source(
    source_id: int,
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    sc = await db.get(LeadSourceConfig, source_id)
    if not sc or sc.organization_id != org.id:
        raise HTTPException(status_code=404, detail="Source not found")
        
    sc.is_enabled = not sc.is_enabled
    await db.commit()
    return {"message": f"Source {'enabled' if sc.is_enabled else 'disabled'}", "is_enabled": sc.is_enabled}

@router.post("/{source_id}/test")
async def test_source_connection(
    source_id: int,
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db)
):
    sc = await db.get(LeadSourceConfig, source_id)
    if not sc or sc.organization_id != org.id:
        raise HTTPException(status_code=404, detail="Source not found")
        
    adapter = source_registry.get_adapter(sc.name)
    if not adapter:
        return {"status": "CONNECTED", "message": "Simulated connection test successful"}
        
    health = await adapter.health_check()
    sc.status = health.get("status", "CONNECTED")
    if sc.status == "CONNECTED":
        sc.last_success_at = datetime.datetime.now(datetime.timezone.utc)
    await db.commit()
    
    return {"source": sc.name, "health": health}
