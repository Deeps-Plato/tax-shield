import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tax_shield.models.db_models import Strategy


@pytest.mark.asyncio
async def test_list_strategies(client: AsyncClient, test_user, db: AsyncSession, sample_category):
    strategy = Strategy(
        name="Home Office + Vehicle Combo",
        category_id=sample_category.id,
        description="Combine home office and vehicle deductions for maximum savings.",
        complexity="medium",
        estimated_savings="$2,000-$5,000",
    )
    db.add(strategy)
    await db.commit()

    resp = await client.get("/api/strategies", headers=test_user["headers"])
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_create_strategy_admin(client: AsyncClient, admin_user, sample_category):
    resp = await client.post("/api/strategies", json={
        "name": "Test Strategy",
        "category_id": sample_category.id,
        "description": "A test strategy for testing.",
        "complexity": "low",
    }, headers=admin_user["headers"])
    assert resp.status_code == 201


@pytest.mark.asyncio
async def test_create_strategy_non_admin(client: AsyncClient, test_user, sample_category):
    resp = await client.post("/api/strategies", json={
        "name": "Should Fail",
        "category_id": sample_category.id,
        "description": "Non-admin cannot create.",
    }, headers=test_user["headers"])
    assert resp.status_code == 403
