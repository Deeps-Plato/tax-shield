import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tax_shield.models.db_models import Category, Item, Strategy

SEED_DIR = Path(__file__).parent.parent / "seed_data"


async def seed_all(db: AsyncSession) -> dict[str, int]:
    counts: dict[str, int] = {}

    counts["categories"] = await _seed_categories(db)
    counts["items"] = await _seed_items(db)
    counts["strategies"] = await _seed_strategies(db)

    return counts


async def _seed_categories(db: AsyncSession) -> int:
    existing = (await db.execute(select(Category))).scalars().all()
    if existing:
        return 0

    data = json.loads((SEED_DIR / "categories.json").read_text())
    for entry in data:
        db.add(Category(**entry))
    await db.commit()
    return len(data)


async def _seed_items(db: AsyncSession) -> int:
    existing_count = (await db.execute(select(Item.id).limit(1))).scalar_one_or_none()
    if existing_count is not None:
        return 0

    # Build category name→id lookup
    cats = (await db.execute(select(Category))).scalars().all()
    cat_lookup = {c.name: c.id for c in cats}

    data = json.loads((SEED_DIR / "items.json").read_text())
    count = 0
    for entry in data:
        cat_name = entry.pop("category", None)
        if cat_name and cat_name in cat_lookup:
            entry["category_id"] = cat_lookup[cat_name]
        elif cat_name:
            # Try partial match
            for name, cid in cat_lookup.items():
                if cat_name.lower() in name.lower():
                    entry["category_id"] = cid
                    break
            else:
                entry["category_id"] = cat_lookup.get("Miscellaneous", 1)
        else:
            entry["category_id"] = cat_lookup.get("Miscellaneous", 1)

        db.add(Item(**entry))
        count += 1

    await db.commit()
    return count


async def _seed_strategies(db: AsyncSession) -> int:
    existing_count = (await db.execute(select(Strategy.id).limit(1))).scalar_one_or_none()
    if existing_count is not None:
        return 0

    cats = (await db.execute(select(Category))).scalars().all()
    cat_lookup = {c.name: c.id for c in cats}

    # Build item name→id lookup for related_items
    items = (await db.execute(select(Item))).scalars().all()
    item_lookup = {i.name.lower(): i.id for i in items}

    data = json.loads((SEED_DIR / "strategies.json").read_text())
    count = 0
    for entry in data:
        cat_name = entry.pop("category", None)
        if cat_name and cat_name in cat_lookup:
            entry["category_id"] = cat_lookup[cat_name]
        else:
            entry["category_id"] = cat_lookup.get("Miscellaneous", 1)

        # Resolve related_items names to IDs
        related_names = entry.pop("related_items", [])
        related_ids = []
        for name in related_names:
            iid = item_lookup.get(name.lower())
            if iid:
                related_ids.append(iid)
        entry["related_item_ids"] = related_ids

        db.add(Strategy(**entry))
        count += 1

    await db.commit()
    return count
