import sys
import os
sys.path.insert(0, os.path.abspath("."))
import asyncio
import logging
from sqlalchemy import text
from backend.app.core.database import AsyncSessionLocal, init_db, Base, engine

logging.basicConfig(level=logging.INFO, format="%(message)s")

async def reset_lead_data():
    await init_db()
    async with engine.begin() as conn:
        print("Safely resetting lead, company, website, audit, contact, provenance and job records...")
        tables_to_clear = [
            "field_provenance",
            "service_need_evidence",
            "lead_opportunities",
            "lead_scores",
            "lead_activities",
            "lead_notes",
            "leads",
            "email_verifications",
            "contacts",
            "website_audits",
            "websites",
            "lead_sources",
            "companies",
            "discovery_jobs"
        ]
        for t in tables_to_clear:
            try:
                await conn.execute(text(f"DROP TABLE IF EXISTS {t}"))
            except Exception as e:
                print(f"Note dropping {t}: {e}")
        
        # Recreate tables with newest schema definitions
        await conn.run_sync(Base.metadata.create_all)
        print("Lead, website, contact, and audit tables recreated with latest truth schema.")

if __name__ == "__main__":
    asyncio.run(reset_lead_data())
