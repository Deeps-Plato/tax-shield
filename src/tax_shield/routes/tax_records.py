from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tax_shield.database import get_db
from tax_shield.dependencies import get_current_user
from tax_shield.models.api_models import TaxRecordCreate, TaxRecordOut
from tax_shield.models.db_models import TaxRecord, User
from tax_shield.services.tax_form_service import compute_form_data

router = APIRouter(prefix="/api/tax-records", tags=["tax-records"])


@router.get("", response_model=list[TaxRecordOut])
async def list_tax_records(
    tax_year: int | None = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[TaxRecord]:
    q = select(TaxRecord).where(TaxRecord.user_id == user.id)
    if tax_year:
        q = q.where(TaxRecord.tax_year == tax_year)
    q = q.order_by(TaxRecord.generated_at.desc())
    result = await db.execute(q)
    return list(result.scalars().all())


@router.post("", response_model=TaxRecordOut, status_code=status.HTTP_201_CREATED)
async def create_tax_record(
    body: TaxRecordCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TaxRecord:
    data = await compute_form_data(db, user, body.form_type, body.tax_year)

    record = TaxRecord(
        user_id=user.id,
        tax_year=body.tax_year,
        filing_type=body.filing_type,
        form_type=body.form_type,
        data=data,
        status="draft",
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


@router.get("/{record_id}", response_model=TaxRecordOut)
async def get_tax_record(
    record_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TaxRecord:
    result = await db.execute(
        select(TaxRecord).where(TaxRecord.id == record_id, TaxRecord.user_id == user.id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Tax record not found")
    return record
