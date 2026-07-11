"""Pydantic schemas for API request/response validation."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


# ---- Auth ----------------------------------------------------------

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: Optional[str] = None
    country: str = "NG"

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit.")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: str
    email: EmailStr
    full_name: Optional[str]
    country: str
    currency: str

    class Config:
        from_attributes = True


# ---- Payslips --------------------------------------------------------

class PayslipParseRequest(BaseModel):
    raw_text: str = Field(min_length=10, description="Extracted/pasted payslip text")
    country: Optional[str] = None  # ISO code override; auto-detected if omitted


class PayslipOut(BaseModel):
    id: str
    employer_name: Optional[str]
    payroll_month: Optional[int]
    payroll_year: Optional[int]
    basic_salary: float
    housing_allowance: float
    transport_allowance: float
    utility_allowance: float
    medical_allowance: float
    meal_allowance: float
    bonus: float
    commission: float
    tax: float
    pension: float
    nhf: float
    other_deductions: float
    gross_salary: float
    net_salary: float
    currency: str
    country: str
    validation_status: str
    extraction_notes: list[str]

    class Config:
        from_attributes = True


# ---- Envelopes & rules ----------------------------------------------

class EnvelopeRuleIn(BaseModel):
    envelope_name: str
    allocation_type: str  # PERCENTAGE | FIXED | REMAINDER
    value: float = 0.0
    color: str = "#6366F1"
    priority: int = 99


class EnvelopeOut(BaseModel):
    id: str
    name: str
    balance: float
    allocated: float
    color: str
    priority: int
    locked: bool
    archived: bool
    recurring: bool

    class Config:
        from_attributes = True


class EnvelopeCreate(BaseModel):
    name: str
    color: str = "#6366F1"
    priority: int = 99


class EnvelopeRename(BaseModel):
    new_name: str


class EnvelopeTransfer(BaseModel):
    from_envelope_id: str
    to_envelope_id: str
    amount: float = Field(gt=0)


class EnvelopeMerge(BaseModel):
    source_envelope_id: str
    target_envelope_id: str


class EnvelopeSplit(BaseModel):
    source_envelope_id: str
    new_name: str
    fraction: float = Field(gt=0, lt=1)


# ---- Transactions ------------------------------------------------------

class TransactionCreate(BaseModel):
    envelope_id: Optional[str] = None
    type: str  # expense | income | transfer | refund
    amount: float = Field(gt=0)
    category: Optional[str] = None
    merchant: Optional[str] = None
    note: Optional[str] = None
    occurred_at: Optional[datetime] = None


class TransactionOut(BaseModel):
    id: str
    envelope_id: Optional[str]
    type: str
    amount: float
    category: Optional[str]
    merchant: Optional[str]
    note: Optional[str]
    occurred_at: datetime

    class Config:
        from_attributes = True
