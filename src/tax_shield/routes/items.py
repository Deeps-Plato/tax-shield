from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from tax_shield.database import get_db
from tax_shield.dependencies import get_current_user, require_admin
from tax_shield.models.api_models import ItemCreate, ItemOut, ItemUpdate
from tax_shield.models.db_models import Item, User

router = APIRouter(prefix="/api/items", tags=["items"])


@router.get("", response_model=list[ItemOut])
async def list_items(
    category_id: int | None = None,
    deduction_type: str | None = None,
    tax_year: int | None = None,
    limit: int = Query(default=50, le=200),
    offset: int = 0,
    _user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[Item]:
    q = select(Item).where(Item.is_active.is_(True))
    if category_id:
        q = q.where(Item.category_id == category_id)
    if deduction_type:
        q = q.where(Item.deduction_type == deduction_type)
    if tax_year:
        q = q.where(Item.tax_year == tax_year)
    q = q.order_by(Item.name).limit(limit).offset(offset)
    result = await db.execute(q)
    return list(result.scalars().all())


@router.get("/{item_id}", response_model=ItemOut)
async def get_item(
    item_id: int,
    _user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Item:
    result = await db.execute(select(Item).where(Item.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.post("", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
async def create_item(
    body: ItemCreate,
    _user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> Item:
    item = Item(**body.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.patch("/{item_id}", response_model=ItemOut)
async def update_item(
    item_id: int,
    body: ItemUpdate,
    _user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> Item:
    result = await db.execute(select(Item).where(Item.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: int,
    _user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> None:
    result = await db.execute(select(Item).where(Item.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item.is_active = False
    await db.commit()
