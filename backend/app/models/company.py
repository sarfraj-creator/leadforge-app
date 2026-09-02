import datetime
from typing import Optional, List
from sqlalchemy import String, Integer, DateTime, Boolean, ForeignKey, Text, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.core.database import Base

class Company(Base):
    __tablename__ = "companies"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Normalized fields
    business_name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    legal_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    industry: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Location
    country: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    postal_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Direct communication
    phone: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    normalized_phone_e164: Mapped[Optional[str]] = mapped_column(String(50), index=True, nullable=True)
    phone_validation_status: Mapped[Optional[str]] = mapped_column(String(50), default="UNVERIFIED")
    business_email: Mapped[Optional[str]] = mapped_column(String(255), index=True, nullable=True)
    
    # Website
    website: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    domain: Mapped[Optional[str]] = mapped_column(String(255), index=True, nullable=True)
    
    # Identity Verification
    identity_verification_status: Mapped[str] = mapped_column(String(50), default="UNVERIFIED", index=True) # HIGH, MEDIUM, LOW, UNVERIFIED
    identity_signals_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Operating Status Determination
    operating_status: Mapped[str] = mapped_column(String(50), default="UNKNOWN", index=True) # ACTIVE, PROBABLY_ACTIVE, UNKNOWN, CLOSED, PERMANENTLY_CLOSED
    operating_status_evidence_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True) # JSON array of signals + timestamps
    
    # Industry Specialization Truth
    discovered_industry: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    verified_industry: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    
    # Contradiction Detection
    has_conflicts: Mapped[bool] = mapped_column(Boolean, default=False)
    conflict_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Metadata
    social_links: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string
    employee_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    technologies: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string
    
    # Entity Resolution & Deduplication Key
    dedup_hash: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    
    # Source & Provenance
    source: Mapped[str] = mapped_column(String(100), default="Direct", index=True)
    source_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    
    # Field-level Freshness Timestamps
    company_observed_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    website_observed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, nullable=True)
    phone_observed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, nullable=True)
    email_observed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, nullable=True)
    
    discovered_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), index=True)
    collected_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    last_seen_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    last_checked_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), index=True)
    
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), onupdate=lambda: datetime.datetime.now(datetime.timezone.utc))
    
    # Relationships
    source_records: Mapped[List["LeadSourceRecord"]] = relationship("LeadSourceRecord", back_populates="company", cascade="all, delete-orphan")
    contacts: Mapped[List["Contact"]] = relationship("Contact", back_populates="company", cascade="all, delete-orphan")
    lead: Mapped[Optional["Lead"]] = relationship("Lead", back_populates="company", uselist=False, cascade="all, delete-orphan")
    website_obj: Mapped[Optional["Website"]] = relationship("Website", back_populates="company", uselist=False, cascade="all, delete-orphan")

class LeadSourceRecord(Base):
    """
    Stores multi-source provenance. When multiple sources discover the same business,
    we keep 1 Company and multiple LeadSourceRecords to preserve exact provenance.
    """
    __tablename__ = "lead_source_records"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    source_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    source_record_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    source_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    raw_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON formatted raw payload
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    discovered_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    collected_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    
    company: Mapped["Company"] = relationship("Company", back_populates="source_records")
