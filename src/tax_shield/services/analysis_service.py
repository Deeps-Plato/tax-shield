import hashlib
import json
from uuid import UUID

import anthropic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tax_shield.config import settings
from tax_shield.models.db_models import Item, SynergyAnalysis

MODEL = "claude-sonnet-4-6"


def _compute_hash(item_ids: list[int]) -> str:
    return hashlib.sha256(json.dumps(sorted(item_ids)).encode()).hexdigest()


async def run_synergy_analysis(
    db: AsyncSession,
    user_id: UUID,
    items: list[Item],
) -> tuple[str, bool]:
    item_ids = [i.id for i in items]
    input_hash = _compute_hash(item_ids)

    # Check cache
    cached = await db.execute(
        select(SynergyAnalysis).where(
            SynergyAnalysis.user_id == user_id,
            SynergyAnalysis.input_hash == input_hash,
        )
    )
    existing = cached.scalar_one_or_none()
    if existing:
        return existing.analysis, True

    # Build prompt
    items_desc = "\n".join(
        f"- {i.name}: {i.description} (type: {i.deduction_type}, "
        f"category: {i.category_id}, max: {i.max_amount})"
        for i in items
    )

    prompt = f"""Analyze these tax deduction/credit items for synergies \
and optimization opportunities.

Items selected:
{items_desc}

Provide:
1. **Overlapping Benefits**: Any items that work together for greater savings
2. **Complementary Strategies**: Additional deductions unlocked by this combination
3. **Timing Optimization**: Best order or timing for claiming these
4. **Entity Structure**: Whether an S-Corp, LLC, or sole prop maximizes these deductions
5. **Risks & Caveats**: IRS scrutiny areas or audit triggers
6. **Estimated Combined Savings**: Rough range of total tax savings

Be specific with dollar amounts where possible. Reference IRS publications and sections.
Format in clean markdown."""

    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    response = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )

    analysis_text = response.content[0].text

    # Cache result
    record = SynergyAnalysis(
        user_id=user_id,
        input_hash=input_hash,
        item_ids=item_ids,
        analysis=analysis_text,
        model_used=MODEL,
    )
    db.add(record)
    await db.commit()

    return analysis_text, False
