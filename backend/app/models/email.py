import datetime
from typing import Optional, List
from sqlalchemy import String, Integer, DateTime, Boolean, ForeignKey, Text, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.core.database import Base

class EmailThread(Base):
    __tablename__ = "email_threads"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    lead_id: Mapped[Optional[int]] = mapped_column(ForeignKey("leads.id", ondelete="SET NULL"), nullable=True, index=True)
    
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    recipient_email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    last_message_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), index=True)
    
    # Thread Status: ACTIVE | REPLIED | CLOSED | ARCHIVED
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE", index=True)
    
    # AI Classification of latest reply:
    # "Interested", "Question", "Not Interested", "Wrong Person", "Out of Office", "Unsubscribe", "Meeting Request", "Pricing Request", "None"
    reply_classification: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    reply_sentiment_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    lead: Mapped[Optional["Lead"]] = relationship("Lead", back_populates="email_threads")
    messages: Mapped[List["EmailMessage"]] = relationship("EmailMessage", back_populates="thread", cascade="all, delete-orphan", order_by="EmailMessage.created_at")

class EmailMessage(Base):
    __tablename__ = "email_messages"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    thread_id: Mapped[int] = mapped_column(ForeignKey("email_threads.id", ondelete="CASCADE"), nullable=False, index=True)
    
    message_id_header: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    direction: Mapped[str] = mapped_column(String(20), default="OUTBOUND") # OUTBOUND | INBOUND
    from_email: Mapped[str] = mapped_column(String(255), nullable=False)
    to_email: Mapped[str] = mapped_column(String(255), nullable=False)
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    body_html: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    body_text: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Delivery Status: DRAFT | SCHEDULED | SENT | DELIVERED | OPENED | CLICKED | BOUNCED | FAILED
    status: Mapped[str] = mapped_column(String(50), default="SENT", index=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    sent_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), index=True)
    
    thread: Mapped["EmailThread"] = relationship("EmailThread", back_populates="messages")
    events: Mapped[List["EmailEvent"]] = relationship("EmailEvent", back_populates="message", cascade="all, delete-orphan")

class EmailEvent(Base):
    __tablename__ = "email_events"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    message_id: Mapped[int] = mapped_column(ForeignKey("email_messages.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False) # sent, opened, clicked, bounced, replied, unsubscribed
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    occurred_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    
    message: Mapped["EmailMessage"] = relationship("EmailMessage", back_populates="events")

class UnsubscribeRecord(Base):
    __tablename__ = "unsubscribe_records"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    unsubscribed_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
