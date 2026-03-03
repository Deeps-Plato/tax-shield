from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from tax_shield.database import get_db
from tax_shield.dependencies import get_current_user
from tax_shield.models.api_models import UserItemCreate, UserItemOut, UserItemUpdate
from tax_shield.models.db_models import User, UserItem

router = APIRouter(prefix="/api/user-items", tags=["user-items"])


@router.get("", response_model=list[UserItemOut])
async def list_user_items(
    tax_year: int | None = None,
    claimed: bool | None = None,
    limit: int = Query(default=50, le=200),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[UserItem]:
    q = (
        select(UserItem)
        .options(selectinload(UserItem.item))
        .where(UserItem.user_id == user.id)
    )
    if tax_year:
        q = q.where(UserItem.tax_year == tax_year)
    if claimed is not None:
        q = q.where(UserItem.claimed == claimed)
    q = q.order_by(UserItem.created_at.desc()).limit(limit)
    result = await db.execute(q)
    return list(result.scalars().all())


@router.post("", response_model=UserItemOut, status_code=status.HTTP_201_CREATED)
async def save_item(
    body: UserItemCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserItem:
    # Check for duplicate
    existing = await db.execute(
        select(UserItem).where(
            UserItem.user_id == user.id,
            UserItem.item_id == body.item_id,
            UserItem.tax_year == body.tax_year,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Item already saved for this tax year")

    user_item = UserItem(user_id=user.id, **body.model_dump())
    db.add(user_item)
    await db.commit()
    await db.refresh(user_item)
    return user_item


@router.patch("/{user_item_id}", response_model=UserItemOut)
async def update_user_item(
    user_item_id: int,
    body: UserItemUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserItem:
    result = await db.execute(
        select(UserItem).where(UserItem.id == user_item_id, UserItem.user_id == user.id)
    )
    user_item = result.scalar_one_or_none()
    if not user_item:
        raise HTTPException(status_code=404, detail="Saved item not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(user_item, field, value)
    await db.commit()
    await db.refresh(user_item)
    return user_item


@router.delete("/{user_item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_user_item(
    user_item_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    result = await db.execute(
        select(UserItem).where(UserItem.id == user_item_id, UserItem.user_id == user.id)
    )
    user_item = result.scalar_one_or_none()
    if not user_item:
        raise HTTPException(status_code=404, detail="Saved item not found")
    await db.delete(user_item)
    await db.commit()
