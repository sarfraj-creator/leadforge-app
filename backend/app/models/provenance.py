import datetime
from typing import Optional, List
from sqlalchemy import String, Integer, DateTime, Boolean, ForeignKey, Text, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.core.database import Base

class FieldProvenanceRecord(Base):
    """
    Field-level provenance model: Tracks exact source, URL, record ID,
    observed timestamp, verification method, verification status, and
    confidence score for every individual lead property.
    """
    __tablename__ = "field_provenance_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Entity reference
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True) # company, contact, website, intent, audit, opportunity
    entity_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    
    # Field Details
    field_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True) # business_name, phone, email, website, contact_name, job_title, etc.
    value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Source Provenance
    source_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True) # OPENSTREETMAP, OFFICIAL_WEBSITE, REGISTRY, DNS, LIVE_PROBE
    source_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    source_record_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Timestamps & Freshness
    observed_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), index=True)
    freshness_state: Mapped[str] = mapped_column(String(50), default="FRESH") # FRESH, RECENT, STALE, EXPIRED, UNKNOWN
    
    # Verification & Quality
    verification_method: Mapped[str] = mapped_column(String(100), default="SOURCE_PROVIDED") # DNS_MX, LIVE_HTTP_PROBE, BRAND_TOKEN_MATCH, OSM_TAG, E164_ITU
    verification_status: Mapped[str] = mapped_column(String(50), default="UNVERIFIED") # VERIFIED, SYNTAX_VALID_ONLY, DOMAIN_MAIL_ENABLED, MAILBOX_VERIFIED, UNVERIFIED, CONFLICT_DETECTED, INVALID, UNKNOWN
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0)
    
    # Contradiction Tracking
    is_conflicting: Mapped[bool] = mapped_column(Boolean, default=False)
    conflict_details_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True) # JSON array of competing source values
    
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
