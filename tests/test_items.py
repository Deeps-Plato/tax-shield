import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_items(client: AsyncClient, test_user, sample_item):
    resp = await client.get("/api/items", headers=test_user["headers"])
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) >= 1
    assert items[0]["name"] == "Home Office Deduction (Simplified)"


@pytest.mark.asyncio
async def test_get_item(client: AsyncClient, test_user, sample_item):
    resp = await client.get(f"/api/items/{sample_item.id}", headers=test_user["headers"])
    assert resp.status_code == 200
    assert resp.json()["name"] == sample_item.name


@pytest.mark.asyncio
async def test_get_item_not_found(client: AsyncClient, test_user):
    resp = await client.get("/api/items/9999", headers=test_user["headers"])
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_create_item_admin(client: AsyncClient, admin_user, sample_category):
    resp = await client.post(
        "/api/items",
        json={
            "name": "Laptop",
            "description": "Business laptop purchase",
            "category_id": sample_category.id,
            "deduction_type": "deduction",
            "max_amount": 2500,
        },
        headers=admin_user["headers"],
    )
    assert resp.status_code == 201
    assert resp.json()["name"] == "Laptop"


@pytest.mark.asyncio
async def test_create_item_non_admin(client: AsyncClient, test_user, sample_category):
    resp = await client.post(
        "/api/items",
        json={
            "name": "Should Fail",
            "description": "Non-admin cannot create",
            "category_id": sample_category.id,
            "deduction_type": "deduction",
        },
        headers=test_user["headers"],
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_update_item(client: AsyncClient, admin_user, sample_item):
    resp = await client.patch(
        f"/api/items/{sample_item.id}",
        json={
            "max_amount": 2000,
        },
        headers=admin_user["headers"],
    )
    assert resp.status_code == 200
    assert resp.json()["max_amount"] == 2000


@pytest.mark.asyncio
async def test_delete_item(client: AsyncClient, admin_user, sample_item):
    resp = await client.delete(f"/api/items/{sample_item.id}", headers=admin_user["headers"])
    assert resp.status_code == 204

    # Should still exist but inactive
    resp = await client.get(f"/api/items/{sample_item.id}", headers=admin_user["headers"])
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False


@pytest.mark.asyncio
async def test_filter_by_category(client: AsyncClient, test_user, sample_item, sample_category):
    resp = await client.get(
        f"/api/items?category_id={sample_category.id}", headers=test_user["headers"]
    )
    assert resp.status_code == 200
    items = resp.json()
    assert all(i["category_id"] == sample_category.id for i in items)
