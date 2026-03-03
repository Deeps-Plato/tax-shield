import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_search(client: AsyncClient, test_user, sample_item):
    resp = await client.post("/api/search", json={
        "query": "home office",
    }, headers=test_user["headers"])
    assert resp.status_code == 200
    data = resp.json()
    assert data["query"] == "home office"
    assert data["total"] >= 1
    assert len(data["items"]) >= 1


@pytest.mark.asyncio
async def test_search_no_results(client: AsyncClient, test_user, sample_item):
    resp = await client.post("/api/search", json={
        "query": "xyznonexistent123",
    }, headers=test_user["headers"])
    assert resp.status_code == 200
    assert resp.json()["total"] == 0


@pytest.mark.asyncio
async def test_search_with_category_filter(
    client: AsyncClient, test_user, sample_item, sample_category
):
    resp = await client.post("/api/search", json={
        "query": "home",
        "category_id": sample_category.id,
    }, headers=test_user["headers"])
    assert resp.status_code == 200
    data = resp.json()
    assert all(i["category_id"] == sample_category.id for i in data["items"])
