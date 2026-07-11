import hashlib

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas, auth, parser
from ..database import get_db

router = APIRouter(prefix="/payslips", tags=["payslips"])


@router.post("/parse", response_model=schemas.PayslipOut)
def parse_and_save(
    payload: schemas.PayslipParseRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    country_enum = parser.Country(payload.country) if payload.country else None
    parsed = parser.parse_payslip(payload.raw_text, country=country_enum)

    record = models.Payslip(
        user_id=current_user.id,
        employer_name=parsed.employer,
        payroll_month=parsed.payroll_month,
        payroll_year=parsed.payroll_year,
        basic_salary=parsed.basic_salary,
        housing_allowance=parsed.housing_allowance,
        transport_allowance=parsed.transport_allowance,
        utility_allowance=parsed.utility_allowance,
        medical_allowance=parsed.medical_allowance,
        meal_allowance=parsed.meal_allowance,
        bonus=parsed.bonus,
        commission=parsed.commission,
        tax=parsed.tax,
        pension=parsed.pension,
        nhf=parsed.nhf,
        other_deductions=parsed.other_deductions,
        gross_salary=parsed.gross_salary,
        net_salary=parsed.net_salary,
        currency=parsed.currency,
        country=parsed.country,
        validation_status=parsed.validation_status.value,
        extraction_notes=parsed.extraction_notes,
        # Store only a hash of the raw text, never the raw text itself,
        # once it has been parsed — matches the brief's "purge raw document" intent.
        raw_text_hash=hashlib.sha256(payload.raw_text.encode()).hexdigest(),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/", response_model=list[schemas.PayslipOut])
def list_payslips(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    return (
        db.query(models.Payslip)
        .filter(models.Payslip.user_id == current_user.id)
        .order_by(models.Payslip.created_at.desc())
        .all()
    )
