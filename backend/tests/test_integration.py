import pytest
import asyncio
from backend.app.core.database import AsyncSessionLocal, init_db
from backend.app.models.user import User, Organization
from backend.app.models.company import Company
from backend.app.models.lead import Lead, LeadScore
from backend.app.models.email import EmailThread
from backend.app.workers.task_runner import task_runner
from backend.app.models.discovery import DiscoveryJob
from backend.app.services.ai.prompt_engine import prompt_engine

def test_full_leadforge_workflow():
    async def run():
        await init_db()
        async with AsyncSessionLocal() as session:
            # 1. Create a discovery job
            import uuid
            unique_slug = f"test-agency-{uuid.uuid4().hex[:6]}"
            org = Organization(name="Test Agency", slug=unique_slug)
            session.add(org)
            await session.commit()
            await session.refresh(org)
            
            job = DiscoveryJob(
                organization_id=org.id,
                name="Mumbai Restaurants Workflow Test",
                location="Mumbai",
                industry="restaurant",
                freshness_days=7,
                min_lead_score=60,
                max_leads=5,
                sources_used="SearchEngine"
            )
            session.add(job)
            await session.commit()
            
            job_id = job.id
            
            # 2. Run background discovery pipeline
            await task_runner.run_discovery_pipeline(job_id)
            
            # 3. Verify Job completed
            await session.refresh(job)
            assert job.status in ["COMPLETED", "RUNNING"]
            assert job.progress_percent > 0
            
            # 4. Test AI Reply Classification
            inbound = "We are interested in a redesign quote. Please call us."
            reply_classification = await prompt_engine.classify_reply(
                inbound_body=inbound,
                subject="Regarding website"
            )
            assert reply_classification["classification"] in ["Interested", "Meeting Request", "Pricing Request", "Question"]
            
    asyncio.run(run())
