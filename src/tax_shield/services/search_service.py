from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from tax_shield.models.db_models import Item, SearchHistory


async def search_items(
    db: AsyncSession,
    user_id: UUID,
    query: str,
    category_id: int | None = None,
    deduction_type: str | None = None,
    limit: int = 20,
) -> tuple[list[Item], int]:
    # PostgreSQL full-text search with ts_rank
    ts_query = func.plainto_tsquery("english", query)
    ts_vector = func.to_tsvector("english", func.concat(Item.name, " ", Item.description))
    rank = func.ts_rank(ts_vector, ts_query)

    # Also do ILIKE fallback for short/exact queries
    like_pattern = f"%{query}%"

    q = select(Item).where(
        Item.is_active.is_(True),
        (ts_vector.op("@@")(ts_query)) | (Item.name.ilike(like_pattern)),
    )

    if category_id:
        q = q.where(Item.category_id == category_id)
    if deduction_type:
        q = q.where(Item.deduction_type == deduction_type)

    q = q.order_by(rank.desc()).limit(limit)

    result = await db.execute(q)
    items = list(result.scalars().all())

    # Count total matches
    count_q = (
        select(func.count())
        .select_from(Item)
        .where(
            Item.is_active.is_(True),
            (ts_vector.op("@@")(ts_query)) | (Item.name.ilike(like_pattern)),
        )
    )
    if category_id:
        count_q = count_q.where(Item.category_id == category_id)
    if deduction_type:
        count_q = count_q.where(Item.deduction_type == deduction_type)

    total = (await db.execute(count_q)).scalar() or 0

    # Log search history
    history = SearchHistory(
        user_id=user_id,
        query=query,
        result_item_ids=[i.id for i in items],
    )
    db.add(history)
    await db.commit()

    return items, total
