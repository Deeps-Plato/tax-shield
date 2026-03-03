import json
import uuid
from pathlib import Path

import anthropic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tax_shield.config import settings
from tax_shield.models.db_models import (
    Category,
    Item,
    QuestionnaireResponse,
    User,
    UserItem,
)

TEMPLATES_PATH = Path(__file__).parent.parent / "seed_data" / "questionnaire_templates.json"
MODEL = "claude-sonnet-4-6"


def _load_templates() -> list[dict]:
    if TEMPLATES_PATH.exists():
        return json.loads(TEMPLATES_PATH.read_text())
    return []


async def start_questionnaire(
    db: AsyncSession, user: User, tax_year: int
) -> dict:
    session_id = str(uuid.uuid4())

    # Get user's existing items to skip already-claimed areas
    existing = await db.execute(
        select(UserItem.item_id).where(
            UserItem.user_id == user.id, UserItem.tax_year == tax_year
        )
    )
    existing_item_ids = {row[0] for row in existing.all()}

    templates = _load_templates()
    if not templates:
        # Fallback first question
        return {
            "session_id": session_id,
            "question_key": "filing_status",
            "question": "What is your primary filing status for this tax year?",
            "options": [
                "Single / Self-Employed",
                "Married Filing Jointly",
                "S-Corporation Owner",
                "Partnership / LLC Member",
                "W-2 Employee",
            ],
            "discovered_items": [],
            "is_final": False,
        }

    first = templates[0]
    return {
        "session_id": session_id,
        "question_key": first["key"],
        "question": first["question"],
        "options": first.get("options"),
        "discovered_items": [],
        "is_final": False,
    }


async def answer_question(
    db: AsyncSession, user: User, answer: "QuestionnaireAnswer"  # noqa: F821
) -> dict:
    from tax_shield.models.api_models import QuestionnaireAnswer

    # Save response
    discovered_items: list[dict] = []
    templates = _load_templates()

    # Find current template
    current = None
    next_template = None
    for i, t in enumerate(templates):
        if t["key"] == answer.question_key:
            current = t
            # Check for follow-up based on response
            follow_up_key = t.get("follow_ups", {}).get(answer.response)
            if follow_up_key:
                next_template = next((tt for tt in templates if tt["key"] == follow_up_key), None)
            elif i + 1 < len(templates):
                next_template = templates[i + 1]
            break

    # Discover items based on the answer
    if current and current.get("discovered_category"):
        cat_name = current["discovered_category"]
        cat_result = await db.execute(
            select(Category).where(Category.name == cat_name)
        )
        cat = cat_result.scalar_one_or_none()
        if cat and answer.response.lower().startswith("yes"):
            items_result = await db.execute(
                select(Item).where(Item.category_id == cat.id, Item.is_active.is_(True)).limit(5)
            )
            found_items = items_result.scalars().all()
            discovered_items = [
                {"id": i.id, "name": i.name, "description": i.description}
                for i in found_items
            ]

    # Save response to DB
    qr = QuestionnaireResponse(
        user_id=user.id,
        session_id=answer.session_id,
        question_key=answer.question_key,
        response=answer.response,
        discovered_items=[d["id"] for d in discovered_items],
        tax_year=2025,
    )
    db.add(qr)
    await db.commit()

    # If no more templates, use AI to generate a follow-up
    if not next_template:
        return await _ai_follow_up(db, user, answer)

    return {
        "session_id": answer.session_id,
        "question_key": next_template["key"],
        "question": next_template["question"],
        "options": next_template.get("options"),
        "discovered_items": discovered_items,
        "is_final": False,
    }


async def _ai_follow_up(
    db: AsyncSession, user: User, last_answer: "QuestionnaireAnswer"  # noqa: F821
) -> dict:
    # Get previous responses in this session
    prev = await db.execute(
        select(QuestionnaireResponse).where(
            QuestionnaireResponse.user_id == user.id,
            QuestionnaireResponse.session_id == last_answer.session_id,
        )
    )
    responses = prev.scalars().all()
    history = "\n".join(f"Q: {r.question_key} → A: {r.response}" for r in responses)

    prompt = f"""Based on this taxpayer's questionnaire responses, generate ONE more targeted question
to discover additional tax deductions or credits they may be missing.

Previous responses:
{history}

Return JSON with keys: question (string), options (list of 3-4 strings), question_key (short snake_case identifier).
If no more questions are useful, return {{"is_final": true, "summary": "brief summary of discoveries"}}.
Return ONLY valid JSON, no markdown."""

    try:
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        response = client.messages.create(
            model=MODEL,
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )
        result = json.loads(response.content[0].text)

        if result.get("is_final"):
            return {
                "session_id": last_answer.session_id,
                "question_key": "final",
                "question": result.get("summary", "Questionnaire complete!"),
                "options": None,
                "discovered_items": [],
                "is_final": True,
            }

        return {
            "session_id": last_answer.session_id,
            "question_key": result.get("question_key", "ai_followup"),
            "question": result["question"],
            "options": result.get("options"),
            "discovered_items": [],
            "is_final": False,
        }
    except Exception:
        return {
            "session_id": last_answer.session_id,
            "question_key": "final",
            "question": "Questionnaire complete! Review your discovered items above.",
            "options": None,
            "discovered_items": [],
            "is_final": True,
        }
