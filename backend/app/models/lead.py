import datetime
from typing import Optional, List
from sqlalchemy import String, Integer, DateTime, Boolean, ForeignKey, Text, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.core.database import Base
import backend.app.models.service_need

class Lead(Base):
    __tablename__ = "leads"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    
    # Qualification & Strict 8-Stage Pipeline
    # DISCOVERED | IDENTITY_VERIFIED | WEBSITE_VERIFIED | AUDITED | OPPORTUNITY_DETECTED | CONTACTABLE | QUALIFIED | SALES_READY
    pipeline_stage: Mapped[str] = mapped_column(String(50), default="DISCOVERED", index=True)
    is_qualified: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    is_sales_ready: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    needs_review: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    review_status: Mapped[str] = mapped_column(String(50), default="PENDING", index=True) # PENDING, APPROVED, REJECTED, NEEDS_RECHECK, MARK_DNC
    review_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    review_history_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True) # JSON list of {reviewer, timestamp, old_status, new_status, notes}
    is_do_not_contact: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    
    # CRM Stage (e.g. "New", "Qualified", "Sales Ready", "Contacted", "Follow-up", "Interested", "Meeting", "Proposal", "Won", "Lost", "Do Not Contact")
    stage: Mapped[str] = mapped_column(String(50), default="New", index=True)
    
    # High-level Opportunity summary & recommended services
    primary_opportunity: Mapped[Optional[str]] = mapped_column(String(255), index=True, nullable=True)
    recommended_service: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Data Quality & Freshness
    data_quality_score: Mapped[int] = mapped_column(Integer, default=0, index=True) # 0-100
    data_quality_breakdown_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    freshness_state: Mapped[str] = mapped_column(String(50), default="FRESH", index=True) # FRESH | RECENT | STALE | EXPIRED
    
    # Assignment
    assigned_to_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), index=True)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), onupdate=lambda: datetime.datetime.now(datetime.timezone.utc))
    
    company: Mapped["Company"] = relationship("Company", back_populates="lead")
    score: Mapped[Optional["LeadScore"]] = relationship("LeadScore", back_populates="lead", uselist=False, cascade="all, delete-orphan")
    opportunities: Mapped[List["LeadOpportunity"]] = relationship("LeadOpportunity", back_populates="lead", cascade="all, delete-orphan")
    service_needs: Mapped[List["ServiceNeedEvidence"]] = relationship("ServiceNeedEvidence", back_populates="lead", cascade="all, delete-orphan")
    stage_histories: Mapped[List["StageHistory"]] = relationship("StageHistory", back_populates="lead", cascade="all, delete-orphan")
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="lead", cascade="all, delete-orphan")
    notes: Mapped[List["Note"]] = relationship("Note", back_populates="lead", cascade="all, delete-orphan")
    campaign_leads: Mapped[List["CampaignLead"]] = relationship("CampaignLead", back_populates="lead", cascade="all, delete-orphan")
    email_threads: Mapped[List["EmailThread"]] = relationship("EmailThread", back_populates="lead", cascade="all, delete-orphan")

class LeadScore(Base):
    __tablename__ = "lead_scores"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    lead_id: Mapped[int] = mapped_column(ForeignKey("leads.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    
    total_score: Mapped[int] = mapped_column(Integer, default=0, index=True) # 0-100
    category: Mapped[str] = mapped_column(String(50), default="LOW", index=True) # HOT (80-100), HIGH (65-79), MEDIUM (50-64), LOW (0-49)
    
    # Decoupled 5-Part Lead Scores (0-100)
    data_confidence_score: Mapped[int] = mapped_column(Integer, default=0)
    business_fit_score: Mapped[int] = mapped_column(Integer, default=0)
    opportunity_score: Mapped[int] = mapped_column(Integer, default=0)
    intent_score: Mapped[int] = mapped_column(Integer, default=0)
    buying_intent: Mapped[str] = mapped_column(String(50), default="UNKNOWN") # HIGH | MEDIUM | LOW | UNKNOWN
    contactability_score: Mapped[int] = mapped_column(Integer, default=0)
    
    # Component point contributions
    rules_applied: Mapped[Optional[str]] = mapped_column(Text, nullable=True) # JSON array of {dimension, rule, points, evidence}
    explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True) # Factual "Why is this a good lead?"
    
    calculated_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    
    lead: Mapped["Lead"] = relationship("Lead", back_populates="score")

class LeadOpportunity(Base):
    __tablename__ = "lead_opportunities"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    lead_id: Mapped[int] = mapped_column(ForeignKey("leads.id", ondelete="CASCADE"), nullable=False, index=True)
    
    opportunity_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    observed_evidence: Mapped[str] = mapped_column(Text, nullable=False)
    inferred_benefit: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    detected_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), nullable=True)
    
    lead: Mapped["Lead"] = relationship("Lead", back_populates="opportunities")
