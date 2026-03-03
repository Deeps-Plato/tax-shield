from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tax_shield.database import get_db
from tax_shield.dependencies import get_current_user, require_admin
from tax_shield.models.api_models import StrategyCreate, StrategyOut
from tax_shield.models.db_models import Strategy, User

router = APIRouter(prefix="/api/strategies", tags=["strategies"])


@router.get("", response_model=list[StrategyOut])
async def list_strategies(
    category_id: int | None = None,
    complexity: str | None = None,
    limit: int = Query(default=50, le=100),
    _user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[Strategy]:
    q = select(Strategy).where(Strategy.is_active.is_(True))
    if category_id:
        q = q.where(Strategy.category_id == category_id)
    if complexity:
        q = q.where(Strategy.complexity == complexity)
    q = q.order_by(Strategy.name).limit(limit)
    result = await db.execute(q)
    return list(result.scalars().all())


@router.get("/{strategy_id}", response_model=StrategyOut)
async def get_strategy(
    strategy_id: int,
    _user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Strategy:
    result = await db.execute(select(Strategy).where(Strategy.id == strategy_id))
    strategy = result.scalar_one_or_none()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return strategy


@router.post("", response_model=StrategyOut, status_code=status.HTTP_201_CREATED)
async def create_strategy(
    body: StrategyCreate,
    _user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> Strategy:
    strategy = Strategy(**body.model_dump())
    db.add(strategy)
    await db.commit()
    await db.refresh(strategy)
    return strategy
