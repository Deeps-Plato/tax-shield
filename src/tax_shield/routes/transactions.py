import csv
import io
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tax_shield.database import get_db
from tax_shield.dependencies import get_current_user
from tax_shield.models.api_models import CSVUploadResult, TransactionOut, TransactionUpdate
from tax_shield.models.db_models import Transaction, User

router = APIRouter(prefix="/api/transactions", tags=["transactions"])


@router.get("", response_model=list[TransactionOut])
async def list_transactions(
    tax_year: int | None = None,
    is_deductible: bool | None = None,
    tax_category_id: int | None = None,
    source: str | None = None,
    limit: int = Query(default=50, le=500),
    offset: int = 0,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[Transaction]:
    q = select(Transaction).where(Transaction.user_id == user.id)
    if tax_year:
        q = q.where(Transaction.tax_year == tax_year)
    if is_deductible is not None:
        q = q.where(Transaction.is_deductible == is_deductible)
    if tax_category_id:
        q = q.where(Transaction.tax_category_id == tax_category_id)
    if source:
        q = q.where(Transaction.source == source)
    q = q.order_by(Transaction.date.desc()).limit(limit).offset(offset)
    result = await db.execute(q)
    return list(result.scalars().all())


@router.patch("/{transaction_id}", response_model=TransactionOut)
async def update_transaction(
    transaction_id: int,
    body: TransactionUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Transaction:
    result = await db.execute(
        select(Transaction).where(Transaction.id == transaction_id, Transaction.user_id == user.id)
    )
    txn = result.scalar_one_or_none()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(txn, field, value)
    await db.commit()
    await db.refresh(txn)
    return txn


@router.post("/upload-csv", response_model=CSVUploadResult)
async def upload_csv(
    file: UploadFile,
    tax_year: int = Query(default=2025),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    content = await file.read()
    text = content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))

    imported = 0
    skipped = 0
    errors: list[str] = []

    for i, row in enumerate(reader, start=2):
        try:
            date_str = row.get("Date") or row.get("date") or row.get("Transaction Date") or ""
            desc = (
                row.get("Description")
                or row.get("description")
                or row.get("Memo")
                or row.get("memo")
                or ""
            )
            amount_str = (
                row.get("Amount")
                or row.get("amount")
                or row.get("Debit")
                or row.get("debit")
                or "0"
            )
            merchant = row.get("Merchant") or row.get("merchant") or row.get("Name") or None

            if not date_str or not desc:
                skipped += 1
                continue

            # Try common date formats
            parsed_date = None
            for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%m-%d-%Y", "%m/%d/%y", "%d/%m/%Y"):
                try:
                    parsed_date = datetime.strptime(date_str.strip(), fmt)
                    break
                except ValueError:
                    continue

            if not parsed_date:
                errors.append(f"Row {i}: Could not parse date '{date_str}'")
                continue

            amount = float(amount_str.replace(",", "").replace("$", "").strip())

            txn = Transaction(
                user_id=user.id,
                date=parsed_date,
                description=desc.strip(),
                amount=abs(amount),
                merchant=merchant.strip() if merchant else None,
                source="csv",
                tax_year=tax_year,
            )
            db.add(txn)
            imported += 1

        except Exception as e:
            errors.append(f"Row {i}: {e}")

    await db.commit()
    return {"imported": imported, "skipped": skipped, "errors": errors[:20]}
