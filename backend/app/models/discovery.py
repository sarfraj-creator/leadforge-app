import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime, Boolean, ForeignKey, Text, Float
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.core.database import Base

class LeadSourceConfig(Base):
    __tablename__ = "lead_sources"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    name: Mapped[str] = mapped_column(String(100), nullable=False) # OpenStreetMap, Search Engine, Directory, CSV, Custom API
    source_type: Mapped[str] = mapped_column(String(50), nullable=False) # openstreetmap | search | directory | csv | custom_api
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    api_key_configured: Mapped[bool] = mapped_column(Boolean, default=False)
    rate_limit_per_min: Mapped[int] = mapped_column(Integer, default=60)
    
    # Health Metrics
    status: Mapped[str] = mapped_column(String(50), default="CONNECTED") # CONNECTED | DEGRADED | ERROR | PAUSED
    last_run_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, nullable=True)
    last_success_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, nullable=True)
    total_discovered: Mapped[int] = mapped_column(Integer, default=0)
    total_new_records: Mapped[int] = mapped_column(Integer, default=0)
    total_duplicates: Mapped[int] = mapped_column(Integer, default=0)
    total_errors: Mapped[int] = mapped_column(Integer, default=0)
    config_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), onupdate=lambda: datetime.datetime.now(datetime.timezone.utc))

class DiscoveryJob(Base):
    __tablename__ = "discovery_jobs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    # Status: QUEUED | RUNNING | PAUSED | COMPLETED | FAILED | CANCELLED
    status: Mapped[str] = mapped_column(String(50), default="QUEUED", index=True)
    
    # Query parameters
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    industry: Mapped[str] = mapped_column(String(255), nullable=False)
    keywords: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    freshness_days: Mapped[int] = mapped_column(Integer, default=7)
    min_lead_score: Mapped[int] = mapped_column(Integer, default=60)
    max_leads: Mapped[int] = mapped_column(Integer, default=50)
    sources_used: Mapped[str] = mapped_column(String(500), default="OpenStreetMap,SearchEngine,Directory")
    
    # Natural Language interpretation if used
    natural_language_query: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    interpreted_criteria_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Real-time backend metrics
    discovered_count: Mapped[int] = mapped_column(Integer, default=0)
    new_businesses_count: Mapped[int] = mapped_column(Integer, default=0)
    duplicates_count: Mapped[int] = mapped_column(Integer, default=0)
    websites_found_count: Mapped[int] = mapped_column(Integer, default=0)
    websites_reachable_count: Mapped[int] = mapped_column(Integer, default=0)
    websites_verified_count: Mapped[int] = mapped_column(Integer, default=0)
    websites_crawled_count: Mapped[int] = mapped_column(Integer, default=0)
    audits_completed_count: Mapped[int] = mapped_column(Integer, default=0)
    audits_incomplete_count: Mapped[int] = mapped_column(Integer, default=0)
    qualified_leads_count: Mapped[int] = mapped_column(Integer, default=0)
    sales_ready_count: Mapped[int] = mapped_column(Integer, default=0)
    contacts_found_count: Mapped[int] = mapped_column(Integer, default=0)
    verified_emails_count: Mapped[int] = mapped_column(Integer, default=0)
    
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    progress_percent: Mapped[int] = mapped_column(Integer, default=0)
    
    # Granular Rejection & Geographic Telemetry
    rejection_reasons_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True) # JSON dict of reasons: count
    geographic_coverage_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True) # JSON list of country/region counts
    
    started_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), index=True)
