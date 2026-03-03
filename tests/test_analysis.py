import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_synergy_needs_two_items(client: AsyncClient, test_user):
    resp = await client.post(
        "/api/analysis/synergy",
        json={
            "item_ids": [1],
        },
        headers=test_user["headers"],
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_questionnaire_start(client: AsyncClient, test_user):
    resp = await client.post(
        "/api/analysis/questionnaire/start",
        json={
            "tax_year": 2025,
        },
        headers=test_user["headers"],
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "session_id" in data
    assert "question" in data
    assert data["is_final"] is False
