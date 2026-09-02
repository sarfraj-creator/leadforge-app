import datetime
from typing import Optional, List
from sqlalchemy import String, Integer, DateTime, Boolean, ForeignKey, Text, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.core.database import Base

class Campaign(Base):
    __tablename__ = "campaigns"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Status: DRAFT | SCHEDULED | RUNNING | PAUSED | COMPLETED | ARCHIVED
    status: Mapped[str] = mapped_column(String(50), default="DRAFT", index=True)
    
    # Sending Controls
    daily_limit: Mapped[int] = mapped_column(Integer, default=50)
    hourly_limit: Mapped[int] = mapped_column(Integer, default=10)
    timezone: Mapped[str] = mapped_column(String(100), default="UTC")
    sending_window_start: Mapped[str] = mapped_column(String(10), default="09:00")
    sending_window_end: Mapped[str] = mapped_column(String(10), default="17:00")
    
    # Approval Mode: MANUAL (Review AI email before sending) | AUTOMATIC
    approval_mode: Mapped[str] = mapped_column(String(50), default="MANUAL")
    
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), onupdate=lambda: datetime.datetime.now(datetime.timezone.utc))
    
    # Relationships
    leads: Mapped[List["CampaignLead"]] = relationship("CampaignLead", back_populates="campaign", cascade="all, delete-orphan")
    sequence_steps: Mapped[List["SequenceStep"]] = relationship("SequenceStep", back_populates="campaign", cascade="all, delete-orphan", order_by="SequenceStep.step_number")

class SequenceStep(Base):
    __tablename__ = "sequence_steps"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True)
    
    step_number: Mapped[int] = mapped_column(Integer, default=1) # 1, 2, 3...
    delay_days: Mapped[int] = mapped_column(Integer, default=0) # 0 for first email, 3 for follow up 1, 7 for follow up 2...
    subject_template: Mapped[str] = mapped_column(String(500), nullable=False)
    body_template: Mapped[str] = mapped_column(Text, nullable=False)
    use_ai_personalization: Mapped[bool] = mapped_column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    campaign: Mapped["Campaign"] = relationship("Campaign", back_populates="sequence_steps")

class CampaignLead(Base):
    __tablename__ = "campaign_leads"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True)
    lead_id: Mapped[int] = mapped_column(ForeignKey("leads.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Status: QUEUED | APPROVED | SENDING | IN_SEQUENCE | REPLIED | BOUNCED | UNSUBSCRIBED | COMPLETED | PAUSED
    status: Mapped[str] = mapped_column(String(50), default="QUEUED", index=True)
    current_step: Mapped[int] = mapped_column(Integer, default=0)
    next_step_due_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, nullable=True, index=True)
    
    # Generated customized email subject & body for current step
    customized_subject: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    customized_body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_approved_by_user: Mapped[bool] = mapped_column(Boolean, default=False)
    
    enrolled_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    completed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, nullable=True)
    
    campaign: Mapped["Campaign"] = relationship("Campaign", back_populates="leads")
    lead: Mapped["Lead"] = relationship("Lead", back_populates="campaign_leads")
