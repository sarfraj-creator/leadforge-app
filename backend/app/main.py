from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.core.database import init_db, AsyncSessionLocal
from backend.app.core.bootstrap import ensure_bootstrap_defaults
from backend.app.api.admin import router as admin_router

# Import API Routers
from backend.app.api.auth import router as auth_router
from backend.app.api.leads import router as leads_router
from backend.app.api.companies import router as companies_router
from backend.app.api.contacts import router as contacts_router
from backend.app.api.discovery import router as discovery_router
from backend.app.api.sources import router as sources_router
from backend.app.api.audits import router as audits_router
from backend.app.api.campaigns import router as campaigns_router
from backend.app.api.emails import router as emails_router
from backend.app.api.inbox import router as inbox_router
from backend.app.api.crm import router as crm_router
from backend.app.api.analytics import router as analytics_router
from backend.app.api.data_quality import router as data_quality_router
from backend.app.api.settings import router as settings_router
from backend.app.api.search import router as search_router
from backend.app.api.health import router as health_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables
    await init_db()
    # Ensure system defaults (Organization, Admin, Stages, Sources) without mock leads
    async with AsyncSessionLocal() as session:
        await ensure_bootstrap_defaults(session)
    yield

app = FastAPI(
    title="LeadForge B2B Intelligence & CRM API",
    description="Production-quality self-hosted B2B lead discovery, enrichment, website intelligence, CRM and outreach engine.",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(health_router)
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(leads_router, prefix=settings.API_V1_STR)
app.include_router(companies_router, prefix=settings.API_V1_STR)
app.include_router(contacts_router, prefix=settings.API_V1_STR)
app.include_router(discovery_router, prefix=settings.API_V1_STR)
app.include_router(sources_router, prefix=settings.API_V1_STR)
app.include_router(audits_router, prefix=settings.API_V1_STR)
app.include_router(campaigns_router, prefix=settings.API_V1_STR)
app.include_router(emails_router, prefix=settings.API_V1_STR)
app.include_router(inbox_router, prefix=settings.API_V1_STR)
app.include_router(crm_router, prefix=settings.API_V1_STR)
app.include_router(analytics_router, prefix=settings.API_V1_STR)
app.include_router(data_quality_router, prefix=settings.API_V1_STR)
app.include_router(settings_router, prefix=settings.API_V1_STR)
app.include_router(search_router, prefix=settings.API_V1_STR)
app.include_router(admin_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {
        "product": "LeadForge",
        "description": "B2B Lead Discovery, Website Intelligence & CRM Platform",
        "docs_url": "/docs",
        "health_url": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
