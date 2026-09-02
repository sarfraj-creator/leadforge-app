import os
import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text
from backend.app.core.config import settings

logger = logging.getLogger("leadforge.database")

# Configure SQLite or PostgreSQL async engine
is_sqlite = settings.DATABASE_URL.startswith("sqlite")

engine_kwargs = {}
if not is_sqlite:
    engine_kwargs.update({
        "pool_size": 20,
        "max_overflow": 10,
        "pool_pre_ping": True,
    })

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    **engine_kwargs
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_db():
    # Import all models to ensure metadata registration
    import backend.app.models.user
    import backend.app.models.discovery
    import backend.app.models.company
    import backend.app.models.website
    import backend.app.models.contact
    import backend.app.models.lead
    import backend.app.models.crm
    import backend.app.models.email
    import backend.app.models.provenance
    import backend.app.models.service_need

    async with engine.begin() as conn:
        # Create all tables if they don't exist
        await conn.run_sync(Base.metadata.create_all)

        # Idempotent SQLite column migrations for new hardened fields
        if is_sqlite:
            columns_to_ensure = [
                # discovery_jobs
                ("discovery_jobs", "websites_reachable_count", "INTEGER DEFAULT 0"),
                ("discovery_jobs", "websites_verified_count", "INTEGER DEFAULT 0"),
                ("discovery_jobs", "audits_incomplete_count", "INTEGER DEFAULT 0"),
                ("discovery_jobs", "sales_ready_count", "INTEGER DEFAULT 0"),
                
                # companies
                ("companies", "normalized_phone_e164", "VARCHAR(50)"),
                ("companies", "phone_validation_status", "VARCHAR(50) DEFAULT 'UNVERIFIED'"),
                ("companies", "identity_verification_status", "VARCHAR(50) DEFAULT 'UNVERIFIED'"),
                ("companies", "identity_signals_json", "TEXT"),
                ("companies", "has_conflicts", "BOOLEAN DEFAULT 0"),
                ("companies", "conflict_count", "INTEGER DEFAULT 0"),
                ("companies", "operating_status", "VARCHAR(50) DEFAULT 'UNKNOWN'"),
                ("companies", "operating_status_evidence_json", "TEXT"),
                ("companies", "discovered_industry", "VARCHAR(100)"),
                ("companies", "verified_industry", "VARCHAR(100)"),
                ("companies", "company_observed_at", "DATETIME"),
                ("companies", "website_observed_at", "DATETIME"),
                ("companies", "phone_observed_at", "DATETIME"),
                ("companies", "email_observed_at", "DATETIME"),

                # discovery_jobs
                ("discovery_jobs", "rejection_reasons_json", "TEXT"),
                ("discovery_jobs", "geographic_coverage_json", "TEXT"),

                # websites
                ("websites", "website_url_discovered", "BOOLEAN DEFAULT 1"),
                ("websites", "website_reachable", "BOOLEAN DEFAULT 0"),
                ("websites", "website_official_verified", "BOOLEAN DEFAULT 0"),
                ("websites", "website_verification_status", "VARCHAR(50) DEFAULT 'UNVERIFIED'"),
                ("websites", "verification_score", "INTEGER DEFAULT 0"),
                ("websites", "verification_reasons_json", "TEXT"),

                # website_audits
                ("website_audits", "audit_status", "VARCHAR(50) DEFAULT 'AUDIT_COMPLETE'"),

                # contacts
                ("contacts", "normalized_phone_e164", "VARCHAR(50)"),
                ("contacts", "phone_validation_status", "VARCHAR(50) DEFAULT 'UNVERIFIED'"),
                ("contacts", "source_url", "VARCHAR(1000)"),
                ("contacts", "syntax_valid", "BOOLEAN DEFAULT 0"),
                ("contacts", "domain_valid", "BOOLEAN DEFAULT 0"),
                ("contacts", "mx_valid", "BOOLEAN DEFAULT 0"),
                ("contacts", "mailbox_verified", "BOOLEAN DEFAULT 0"),
                ("contacts", "observed_at", "DATETIME"),

                # leads
                ("leads", "pipeline_stage", "VARCHAR(50) DEFAULT 'DISCOVERED'"),
                ("leads", "is_qualified", "BOOLEAN DEFAULT 0"),
                ("leads", "is_sales_ready", "BOOLEAN DEFAULT 0"),
                ("leads", "review_status", "VARCHAR(50) DEFAULT 'PENDING'"),
                ("leads", "review_notes", "TEXT"),
                ("leads", "review_history_json", "TEXT"),
                ("leads", "data_quality_score", "INTEGER DEFAULT 0"),
                ("leads", "data_quality_breakdown_json", "TEXT"),

                # lead_scores
                ("lead_scores", "data_confidence_score", "INTEGER DEFAULT 0"),
                ("lead_scores", "business_fit_score", "INTEGER DEFAULT 0"),
                ("lead_scores", "opportunity_score", "INTEGER DEFAULT 0"),
                ("lead_scores", "intent_score", "INTEGER DEFAULT 0"),
                ("lead_scores", "buying_intent", "VARCHAR(50) DEFAULT 'UNKNOWN'"),
                ("lead_scores", "contactability_score", "INTEGER DEFAULT 0"),

                # lead_source_records
                ("lead_source_records", "source_record_id", "VARCHAR(255)"),
                ("lead_source_records", "discovered_at", "DATETIME"),

                # lead_opportunities
                ("lead_opportunities", "created_at", "DATETIME"),
                ("lead_opportunities", "inferred_benefit", "TEXT"),
            ]
            for table, col, col_type in columns_to_ensure:
                try:
                    await conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}"))
                except Exception:
                    # Column already exists
                    pass
