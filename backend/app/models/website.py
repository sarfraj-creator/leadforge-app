import datetime
from typing import Optional, List
from sqlalchemy import String, Integer, DateTime, Boolean, ForeignKey, Text, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.core.database import Base

class Website(Base):
    __tablename__ = "websites"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    domain: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    canonical_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Detailed Verification Flags
    website_url_discovered: Mapped[bool] = mapped_column(Boolean, default=True)
    website_reachable: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    website_official_verified: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    
    # Granular Status: URL_DISCOVERED | REACHABLE | OFFICIAL_MATCH | OFFICIAL_VERIFIED | UNVERIFIED | PARKED | BROKEN
    website_verification_status: Mapped[str] = mapped_column(String(50), default="UNVERIFIED", index=True)
    verification_score: Mapped[int] = mapped_column(Integer, default=0) # 0-100
    verification_reasons_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True) # JSON list
    
    # Status: NO_WEBSITE | WEBSITE_FOUND | WEBSITE_UNREACHABLE | WEBSITE_REDIRECT | WEBSITE_BLOCKED | UNKNOWN
    status: Mapped[str] = mapped_column(String(50), default="WEBSITE_FOUND", index=True)
    http_status: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ssl_valid: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    redirect_target: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Change Detection Hashes
    html_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    content_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    website_changed: Mapped[bool] = mapped_column(Boolean, default=False)
    
    last_crawled_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, nullable=True, index=True)
    last_audited_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, nullable=True, index=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), onupdate=lambda: datetime.datetime.now(datetime.timezone.utc))
    
    company: Mapped["Company"] = relationship("Company", back_populates="website_obj")
    pages: Mapped[List["WebsitePage"]] = relationship("WebsitePage", back_populates="website", cascade="all, delete-orphan")
    audits: Mapped[List["WebsiteAudit"]] = relationship("WebsiteAudit", back_populates="website", cascade="all, delete-orphan")

class WebsitePage(Base):
    __tablename__ = "website_pages"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    website_id: Mapped[int] = mapped_column(ForeignKey("websites.id", ondelete="CASCADE"), nullable=False, index=True)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    meta_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    h1_tags: Mapped[Optional[str]] = mapped_column(Text, nullable=True) # JSON list
    visible_text_snippet: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    load_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    page_size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status_code: Mapped[int] = mapped_column(Integer, default=200)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    
    website: Mapped["Website"] = relationship("Website", back_populates="pages")

class WebsiteAudit(Base):
    __tablename__ = "website_audits"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    website_id: Mapped[int] = mapped_column(ForeignKey("websites.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Audit Status: AUDIT_COMPLETE | AUDIT_INCOMPLETE | AUDIT_FAILED
    audit_status: Mapped[str] = mapped_column(String(50), default="AUDIT_INCOMPLETE", index=True)
    
    # Deterministic Scores (0-100)
    overall_score: Mapped[int] = mapped_column(Integer, default=0)
    performance_score: Mapped[int] = mapped_column(Integer, default=0)
    mobile_score: Mapped[int] = mapped_column(Integer, default=0)
    seo_score: Mapped[int] = mapped_column(Integer, default=0)
    accessibility_score: Mapped[int] = mapped_column(Integer, default=0)
    security_score: Mapped[int] = mapped_column(Integer, default=0)
    ux_score: Mapped[int] = mapped_column(Integer, default=0)
    conversion_score: Mapped[int] = mapped_column(Integer, default=0)
    
    # Summary of findings
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    audit_engine_version: Mapped[str] = mapped_column(String(50), default="LeadForge-Audit-2.0")
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), index=True)
    
    website: Mapped["Website"] = relationship("Website", back_populates="audits")
    metrics: Mapped[List["WebsiteAuditMetric"]] = relationship("WebsiteAuditMetric", back_populates="audit", cascade="all, delete-orphan")
    issues: Mapped[List["WebsiteIssue"]] = relationship("WebsiteIssue", back_populates="audit", cascade="all, delete-orphan")
    technologies: Mapped[List["WebsiteTechnology"]] = relationship("WebsiteTechnology", back_populates="audit", cascade="all, delete-orphan")

class WebsiteAuditMetric(Base):
    __tablename__ = "website_audit_metrics"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    audit_id: Mapped[int] = mapped_column(ForeignKey("website_audits.id", ondelete="CASCADE"), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(50), index=True) # performance, mobile, seo, etc.
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[str] = mapped_column(String(255), nullable=False)
    unit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    audit: Mapped["WebsiteAudit"] = relationship("WebsiteAudit", back_populates="metrics")

class WebsiteIssue(Base):
    __tablename__ = "website_issues"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    audit_id: Mapped[int] = mapped_column(ForeignKey("website_audits.id", ondelete="CASCADE"), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(50), index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    severity: Mapped[str] = mapped_column(String(50), default="medium") # critical, high, medium, low
    evidence: Mapped[str] = mapped_column(Text, nullable=False)
    recommendation: Mapped[str] = mapped_column(Text, nullable=False)
    
    audit: Mapped["WebsiteAudit"] = relationship("WebsiteAudit", back_populates="issues")

class WebsiteTechnology(Base):
    __tablename__ = "website_technologies"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    audit_id: Mapped[int] = mapped_column(ForeignKey("website_audits.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(100), default="CMS") # CMS, Framework, Analytics, Ecommerce
    version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    detected_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    
    audit: Mapped["WebsiteAudit"] = relationship("WebsiteAudit", back_populates="technologies")
