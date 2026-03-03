from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tax_shield.database import get_db
from tax_shield.dependencies import get_current_user
from tax_shield.models.db_models import TaxRecord, User
from tax_shield.services.tax_form_service import generate_pdf

router = APIRouter(prefix="/api/tax-forms", tags=["tax-forms"])


@router.get("/{record_id}/pdf")
async def download_form_pdf(
    record_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    result = await db.execute(
        select(TaxRecord).where(TaxRecord.id == record_id, TaxRecord.user_id == user.id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Tax record not found")

    pdf_bytes = generate_pdf(record)
    filename = f"{record.form_type}_{record.tax_year}_{record.status}.pdf"

    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
