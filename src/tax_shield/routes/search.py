from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from tax_shield.database import get_db
from tax_shield.dependencies import get_current_user
from tax_shield.models.api_models import SearchRequest, SearchResult
from tax_shield.models.db_models import User
from tax_shield.services.search_service import search_items

router = APIRouter(prefix="/api/search", tags=["search"])


@router.post("", response_model=SearchResult)
async def search(
    body: SearchRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    items, total = await search_items(
        db,
        user_id=user.id,
        query=body.query,
        category_id=body.category_id,
        deduction_type=body.deduction_type,
        limit=body.limit,
    )
    return {"items": items, "total": total, "query": body.query}
