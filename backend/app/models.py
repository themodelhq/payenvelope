"""SQLAlchemy ORM models for PayEnvelope."""

from datetime import datetime
import uuid

from sqlalchemy import (
    Column, String, Float, Integer, Boolean, DateTime, ForeignKey, Text, JSON
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


def gen_uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=gen_uuid)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=True)  # nullable to allow OAuth-only accounts
    full_name = Column(String, nullable=True)
    country = Column(String, default="NG")
    currency = Column(String, default="NGN")
    auth_provider = Column(String, default="password")  # password | google | microsoft | apple | magic_link
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    payslips = relationship("Payslip", back_populates="user", cascade="all, delete-orphan")
    envelopes = relationship("Envelope", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    rules = relationship("EnvelopeRule", back_populates="user", cascade="all, delete-orphan")
    goals = relationship("SavingsGoal", back_populates="user", cascade="all, delete-orphan")
    bills = relationship("Bill", back_populates="user", cascade="all, delete-orphan")


class Employer(Base):
    __tablename__ = "employers"

    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String, nullable=False)
    country = Column(String, default="NG")


class Payslip(Base):
    __tablename__ = "payslips"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    employer_name = Column(String, nullable=True)
    payroll_month = Column(Integer, nullable=True)
    payroll_year = Column(Integer, nullable=True)

    basic_salary = Column(Float, default=0.0)
    housing_allowance = Column(Float, default=0.0)
    transport_allowance = Column(Float, default=0.0)
    utility_allowance = Column(Float, default=0.0)
    medical_allowance = Column(Float, default=0.0)
    meal_allowance = Column(Float, default=0.0)
    bonus = Column(Float, default=0.0)
    commission = Column(Float, default=0.0)

    tax = Column(Float, default=0.0)
    pension = Column(Float, default=0.0)
    nhf = Column(Float, default=0.0)
    other_deductions = Column(Float, default=0.0)

    gross_salary = Column(Float, default=0.0)
    net_salary = Column(Float, default=0.0)

    currency = Column(String, default="NGN")
    country = Column(String, default="NG")
    validation_status = Column(String, default="INCOMPLETE")
    extraction_notes = Column(JSON, default=list)

    source_type = Column(String, default="paste")  # pdf | image | paste | camera
    raw_text_hash = Column(String, nullable=True)  # store a hash, never the raw text, once processed
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="payslips")


class EnvelopeRule(Base):
    __tablename__ = "envelope_rules"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    envelope_name = Column(String, nullable=False)
    allocation_type = Column(String, nullable=False)  # PERCENTAGE | FIXED | REMAINDER
    value = Column(Float, default=0.0)
    color = Column(String, default="#6366F1")
    priority = Column(Integer, default=99)
    active = Column(Boolean, default=True)

    user = relationship("User", back_populates="rules")


class Envelope(Base):
    __tablename__ = "envelopes"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    balance = Column(Float, default=0.0)
    allocated = Column(Float, default=0.0)
    color = Column(String, default="#6366F1")
    priority = Column(Integer, default=99)
    locked = Column(Boolean, default=False)
    archived = Column(Boolean, default=False)
    recurring = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="envelopes")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    envelope_id = Column(String, ForeignKey("envelopes.id"), nullable=True)
    type = Column(String, nullable=False)  # expense | income | transfer | refund
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=True)
    merchant = Column(String, nullable=True)
    note = Column(Text, nullable=True)
    receipt_url = Column(String, nullable=True)
    occurred_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="transactions")


class SavingsGoal(Base):
    __tablename__ = "savings_goals"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    target_amount = Column(Float, nullable=False)
    current_amount = Column(Float, default=0.0)
    target_date = Column(DateTime, nullable=True)
    envelope_id = Column(String, ForeignKey("envelopes.id"), nullable=True)

    user = relationship("User", back_populates="goals")


class Bill(Base):
    __tablename__ = "bills"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    due_day_of_month = Column(Integer, nullable=False)
    envelope_id = Column(String, ForeignKey("envelopes.id"), nullable=True)
    recurring = Column(Boolean, default=True)
    paid_this_cycle = Column(Boolean, default=False)

    user = relationship("User", back_populates="bills")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    body = Column(String, nullable=False)
    kind = Column(String, default="reminder")  # reminder | alert | system
    read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    plan = Column(String, default="free")  # free | premium | business
    status = Column(String, default="active")
    renews_at = Column(DateTime, nullable=True)
    provider = Column(String, nullable=True)  # paystack | flutterwave | stripe


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
