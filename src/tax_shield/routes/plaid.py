from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tax_shield.database import get_db
from tax_shield.dependencies import get_current_user
from tax_shield.models.api_models import (
    PlaidConnectionOut,
    PlaidExchangeRequest,
    PlaidLinkTokenResponse,
)
from tax_shield.models.db_models import PlaidConnection, User
from tax_shield.services.plaid_service import (
    create_link_token,
    exchange_public_token,
    sync_transactions,
)

router = APIRouter(prefix="/api/plaid", tags=["plaid"])


@router.post("/link-token", response_model=PlaidLinkTokenResponse)
async def get_link_token(
    user: User = Depends(get_current_user),
) -> dict:
    try:
        token = await create_link_token(user.id)
        return {"link_token": token}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Plaid error: {e}")


@router.post("/exchange", response_model=PlaidConnectionOut)
async def exchange_token(
    body: PlaidExchangeRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PlaidConnection:
    try:
        connection = await exchange_public_token(
            db, user.id, body.public_token, body.institution_name, body.institution_id
        )
        return connection
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Plaid error: {e}")


@router.get("/connections", response_model=list[PlaidConnectionOut])
async def list_connections(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[PlaidConnection]:
    result = await db.execute(
        select(PlaidConnection).where(PlaidConnection.user_id == user.id)
    )
    return list(result.scalars().all())


@router.post("/connections/{connection_id}/sync")
async def sync_connection(
    connection_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    result = await db.execute(
        select(PlaidConnection).where(
            PlaidConnection.id == connection_id, PlaidConnection.user_id == user.id
        )
    )
    connection = result.scalar_one_or_none()
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")

    try:
        imported = await sync_transactions(db, connection)
        return {"imported": imported}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync error: {e}")
