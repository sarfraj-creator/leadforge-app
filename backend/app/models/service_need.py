import datetime
from typing import Optional, List
from sqlalchemy import String, Integer, DateTime, Boolean, ForeignKey, Text, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.core.database import Base

class ServiceNeedEvidence(Base):
    """
    Stores verifiable evidence for 9 core agency services:
    WEB_DESIGN, WEB_DEVELOPMENT, UI_UX, SEO, PERFORMANCE,
    ECOMMERCE, CONVERSION, ACCESSIBILITY, MAINTENANCE.
    """
    __tablename__ = "service_need_evidence"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    lead_id: Mapped[int] = mapped_column(ForeignKey("leads.id", ondelete="CASCADE"), nullable=False, index=True)
    
    service_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True) # WEB_DESIGN, WEB_DEVELOPMENT, UI_UX, SEO, PERFORMANCE, ECOMMERCE, CONVERSION, ACCESSIBILITY, MAINTENANCE
    need_score: Mapped[int] = mapped_column(Integer, default=0) # 0-100 observable need
    
    # Traceable Observations
    evidence_json: Mapped[str] = mapped_column(Text, nullable=False) # JSON array of concrete measured defects/reasons
    source_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    
    observed_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    
    lead: Mapped["Lead"] = relationship("Lead", back_populates="service_needs")
