from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from tax_shield.database import get_db
from tax_shield.dependencies import require_admin
from tax_shield.models.api_models import UserOut
from tax_shield.models.db_models import Category, Item, Strategy, User, UserItem
from tax_shield.services.seed_service import seed_all

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/seed", status_code=status.HTTP_200_OK)
async def seed_data(
    force: bool = False,
    _user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict:
    counts = await seed_all(db, force=force)
    return {"message": "Seed data loaded", "counts": counts}


@router.get("/stats")
async def stats(
    _user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict:
    users = (await db.execute(select(func.count()).select_from(User))).scalar() or 0
    items = (await db.execute(select(func.count()).select_from(Item))).scalar() or 0
    categories = (await db.execute(select(func.count()).select_from(Category))).scalar() or 0
    strategies = (await db.execute(select(func.count()).select_from(Strategy))).scalar() or 0
    saved = (await db.execute(select(func.count()).select_from(UserItem))).scalar() or 0

    return {
        "users": users,
        "items": items,
        "categories": categories,
        "strategies": strategies,
        "saved_items": saved,
    }


@router.get("/users", response_model=list[UserOut])
async def list_users(
    _user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> list[User]:
    result = await db.execute(select(User).order_by(User.created_at))
    return list(result.scalars().all())


@router.patch("/users/{user_id}/toggle-active")
async def toggle_user_active(
    user_id: str,
    _user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict:
    from uuid import UUID

    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    target.is_active = not target.is_active
    await db.commit()
    return {"id": str(target.id), "is_active": target.is_active}
