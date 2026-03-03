import io

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_upload_csv(client: AsyncClient, test_user):
    csv_content = "Date,Description,Amount,Merchant\n01/15/2025,Office Supplies,45.99,Staples\n01/20/2025,Software License,199.00,Adobe\n"
    files = {"file": ("statement.csv", io.BytesIO(csv_content.encode()), "text/csv")}
    resp = await client.post(
        "/api/transactions/upload-csv?tax_year=2025",
        files=files,
        headers=test_user["headers"],
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["imported"] == 2
    assert data["skipped"] == 0


@pytest.mark.asyncio
async def test_list_transactions(client: AsyncClient, test_user):
    resp = await client.get("/api/transactions", headers=test_user["headers"])
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_upload_invalid_file(client: AsyncClient, test_user):
    files = {"file": ("data.txt", io.BytesIO(b"not csv"), "text/plain")}
    resp = await client.post(
        "/api/transactions/upload-csv",
        files=files,
        headers=test_user["headers"],
    )
    assert resp.status_code == 400
