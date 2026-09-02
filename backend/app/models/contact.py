import datetime
from typing import Optional, List
from sqlalchemy import String, Integer, DateTime, Boolean, ForeignKey, Text, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.core.database import Base

class Contact(Base):
    __tablename__ = "contacts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    
    first_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), index=True, nullable=True)
    job_title: Mapped[Optional[str]] = mapped_column(String(255), index=True, nullable=True)
    is_decision_maker: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    
    email: Mapped[Optional[str]] = mapped_column(String(255), index=True, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    normalized_phone_e164: Mapped[Optional[str]] = mapped_column(String(50), index=True, nullable=True)
    phone_validation_status: Mapped[str] = mapped_column(String(50), default="UNVERIFIED") # VALID_E164, LOCAL_FORMAT, INVALID, UNVERIFIED
    
    linkedin_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Provenance
    source: Mapped[str] = mapped_column(String(100), default="Official Website")
    source_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    
    # Verification Status: SYNTAX_VALID_ONLY | DOMAIN_MAIL_ENABLED | MAILBOX_VERIFIED | INVALID | UNKNOWN
    email_status: Mapped[str] = mapped_column(String(50), default="UNKNOWN", index=True)
    syntax_valid: Mapped[bool] = mapped_column(Boolean, default=False)
    domain_valid: Mapped[bool] = mapped_column(Boolean, default=False)
    mx_valid: Mapped[bool] = mapped_column(Boolean, default=False)
    mailbox_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    email_verified_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, nullable=True)
    
    # Freshness
    observed_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    contact_checked_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), onupdate=lambda: datetime.datetime.now(datetime.timezone.utc))
    
    company: Mapped["Company"] = relationship("Company", back_populates="contacts")
    verifications: Mapped[List["EmailVerificationRecord"]] = relationship("EmailVerificationRecord", back_populates="contact", cascade="all, delete-orphan")

class EmailVerificationRecord(Base):
    __tablename__ = "email_verifications"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    contact_id: Mapped[int] = mapped_column(ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False) # SYNTAX_VALID_ONLY, DOMAIN_MAIL_ENABLED, MAILBOX_VERIFIED, INVALID, UNKNOWN
    provider: Mapped[str] = mapped_column(String(50), default="LeadForge-Validator")
    reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    verified_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    
    contact: Mapped["Contact"] = relationship("Contact", back_populates="verifications")
