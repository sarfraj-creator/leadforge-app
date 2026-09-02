from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_db
from backend.app.services.admin.data_reset import reset_demo_and_lead_data

router = APIRouter(prefix="/admin", tags=["Admin & Data Management"])

class ResetDemoRequest(BaseModel):
    confirm: bool

@router.post("/data/reset-demo")
async def reset_demo_data_endpoint(
    req: ResetDemoRequest,
    db: AsyncSession = Depends(get_db)
):
    if not req.confirm:
        raise HTTPException(
            status_code=400,
            detail="Confirmation required. Set 'confirm': true to reset demo and lead data."
        )
    result = await reset_demo_and_lead_data(db)
    return result
