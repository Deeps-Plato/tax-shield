from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tax_shield.database import get_db
from tax_shield.dependencies import get_current_user
from tax_shield.models.api_models import (
    QuestionnaireAnswer,
    QuestionnaireQuestion,
    QuestionnaireStart,
    SynergyRequest,
    SynergyResponse,
)
from tax_shield.models.db_models import Item, User
from tax_shield.services.analysis_service import run_synergy_analysis
from tax_shield.services.questionnaire_service import answer_question, start_questionnaire

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.post("/synergy", response_model=SynergyResponse)
async def synergy_analysis(
    body: SynergyRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    if len(body.item_ids) < 2:
        raise HTTPException(status_code=400, detail="Select at least 2 items for analysis")

    # Fetch items
    result = await db.execute(select(Item).where(Item.id.in_(body.item_ids)))
    items = list(result.scalars().all())
    if len(items) < 2:
        raise HTTPException(status_code=404, detail="Some items not found")

    analysis, cached = await run_synergy_analysis(db, user.id, items)
    return {"analysis": analysis, "item_ids": body.item_ids, "cached": cached}


@router.post("/questionnaire/start", response_model=QuestionnaireQuestion)
async def questionnaire_start(
    body: QuestionnaireStart,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await start_questionnaire(db, user, body.tax_year)


@router.post("/questionnaire/answer", response_model=QuestionnaireQuestion)
async def questionnaire_answer(
    body: QuestionnaireAnswer,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await answer_question(db, user, body)
