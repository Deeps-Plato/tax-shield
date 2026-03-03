"""Auto-classify transactions into tax categories using rules + AI fallback."""

import json
from uuid import UUID

import anthropic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tax_shield.config import settings
from tax_shield.models.db_models import Category, Transaction

# Rules-based classification: merchant/description patterns → category name
MERCHANT_RULES: dict[str, str] = {
    "office depot": "Office Supplies",
    "staples": "Office Supplies",
    "amazon": "Equipment & Technology",
    "best buy": "Equipment & Technology",
    "adobe": "Equipment & Technology",
    "microsoft": "Equipment & Technology",
    "google ads": "Marketing & Advertising",
    "facebook ads": "Marketing & Advertising",
    "mailchimp": "Marketing & Advertising",
    "squarespace": "Marketing & Advertising",
    "godaddy": "Marketing & Advertising",
    "uber": "Vehicle & Transportation",
    "lyft": "Vehicle & Transportation",
    "shell": "Vehicle & Transportation",
    "chevron": "Vehicle & Transportation",
    "bp": "Vehicle & Transportation",
    "exxon": "Vehicle & Transportation",
    "delta": "Travel & Meals",
    "united airlines": "Travel & Meals",
    "american airlines": "Travel & Meals",
    "southwest": "Travel & Meals",
    "marriott": "Travel & Meals",
    "hilton": "Travel & Meals",
    "hyatt": "Travel & Meals",
    "airbnb": "Travel & Meals",
    "doordash": "Travel & Meals",
    "grubhub": "Travel & Meals",
    "intuit": "Professional Services",
    "turbotax": "Professional Services",
    "quickbooks": "Professional Services",
    "legalzoom": "Professional Services",
    "wework": "Rent & Utilities",
    "regus": "Rent & Utilities",
    "comcast": "Rent & Utilities",
    "at&t": "Rent & Utilities",
    "verizon": "Rent & Utilities",
    "blue cross": "Insurance",
    "aetna": "Insurance",
    "united health": "Insurance",
    "cigna": "Insurance",
    "state farm": "Insurance",
    "coursera": "Education & Training",
    "udemy": "Education & Training",
    "linkedin learning": "Education & Training",
}


async def classify_transaction(
    db: AsyncSession, transaction: Transaction
) -> int | None:
    """Classify a single transaction. Returns category_id or None."""
    # First: rules-based matching
    desc_lower = (transaction.description or "").lower()
    merchant_lower = (transaction.merchant or "").lower()

    for pattern, cat_name in MERCHANT_RULES.items():
        if pattern in desc_lower or pattern in merchant_lower:
            result = await db.execute(
                select(Category.id).where(Category.name == cat_name)
            )
            cat_id = result.scalar_one_or_none()
            if cat_id:
                return cat_id

    return None


async def classify_batch_with_ai(
    db: AsyncSession, transactions: list[Transaction]
) -> dict[int, int | None]:
    """Use AI to classify ambiguous transactions. Returns {txn_id: category_id}."""
    cats = (await db.execute(select(Category))).scalars().all()
    cat_names = {c.id: c.name for c in cats}
    cat_lookup = {c.name.lower(): c.id for c in cats}

    txn_descs = "\n".join(
        f"{t.id}: {t.description} | {t.merchant or 'N/A'} | ${t.amount}"
        for t in transactions[:50]  # Limit batch size
    )

    prompt = f"""Classify these transactions into tax deduction categories.

Categories: {', '.join(cat_names.values())}

Transactions:
{txn_descs}

Return JSON object mapping transaction ID to category name. Use null if not deductible.
Example: {{"1": "Office Supplies", "2": null, "3": "Travel & Meals"}}
Return ONLY valid JSON."""

    try:
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}],
        )
        classifications = json.loads(response.content[0].text)

        result: dict[int, int | None] = {}
        for txn_id_str, cat_name in classifications.items():
            txn_id = int(txn_id_str)
            if cat_name and cat_name.lower() in cat_lookup:
                result[txn_id] = cat_lookup[cat_name.lower()]
            else:
                result[txn_id] = None
        return result

    except Exception:
        return {}
