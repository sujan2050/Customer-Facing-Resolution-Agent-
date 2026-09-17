from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    tier = Column(String(20), nullable=False)  # Gold, Silver, Platinum
    pnr = Column(String(20), unique=True, index=True, nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(50), nullable=True)
    travel_history = Column(Text, nullable=True)

    bookings = relationship("Booking", back_populates="customer", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="customer")
    actions = relationship("ActionLedgerEntry", back_populates="customer")

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    pnr = Column(String(20), index=True, nullable=False)
    flight_number = Column(String(20), nullable=False)
    route = Column(String(100), nullable=False)
    flight_date = Column(String(50), nullable=False)  # Wed 23 Sep 2026, etc.
    scheduled_departure = Column(String(20), nullable=False)
    status = Column(String(100), nullable=False)  # Cancelled (operational reasons), Delayed 4h..., etc.
    delay_hours = Column(Integer, default=0)
    new_departure = Column(String(20), nullable=True)
    is_cancelled = Column(Boolean, default=False)
    is_airline_caused = Column(Boolean, default=True)

    customer = relationship("Customer", back_populates="bookings")

class PolicyRule(Base):
    __tablename__ = "policy_rules"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(50), nullable=False)  # cancellation, delay, refund, fare_difference, loyalty
    rule_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    entitlement_summary = Column(Text, nullable=False)
    conditions_json = Column(JSON, nullable=True)

class ActionLedgerEntry(Base):
    __tablename__ = "action_ledger"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String(64), ForeignKey("conversations.id"), nullable=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    action_type = Column(String(50), nullable=False)  # rebooked, voucher_issued, lounge_granted, hotel_arranged, refund_initiated, escalated_to_supervisor
    rule_cited = Column(String(100), nullable=False)
    status = Column(String(30), default="COMPLETED")  # COMPLETED, ESCALATED, BLOCKED
    details_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer", back_populates="actions")
    conversation = relationship("Conversation", back_populates="actions")

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String(64), primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    pnr = Column(String(20), nullable=False)
    status = Column(String(30), default="ACTIVE")  # ACTIVE, ESCALATED, RESOLVED
    escalation_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    customer = relationship("Customer", back_populates="conversations")
    messages = relationship("MessageAudit", back_populates="conversation", cascade="all, delete-orphan")
    actions = relationship("ActionLedgerEntry", back_populates="conversation")

class MessageAudit(Base):
    __tablename__ = "message_audits"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String(64), ForeignKey("conversations.id"), nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    agent_traces_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")
