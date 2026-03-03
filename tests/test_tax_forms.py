import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_tax_record(client: AsyncClient, test_user):
    resp = await client.post(
        "/api/tax-records",
        json={
            "tax_year": 2025,
            "filing_type": "self_employed",
            "form_type": "schedule_c",
        },
        headers=test_user["headers"],
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["form_type"] == "schedule_c"
    assert data["status"] == "draft"
    assert "data" in data


@pytest.mark.asyncio
async def test_list_tax_records(client: AsyncClient, test_user):
    resp = await client.get("/api/tax-records", headers=test_user["headers"])
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_download_pdf(client: AsyncClient, test_user):
    # First create a record
    create_resp = await client.post(
        "/api/tax-records",
        json={
            "tax_year": 2025,
            "filing_type": "individual",
            "form_type": "1040",
        },
        headers=test_user["headers"],
    )
    record_id = create_resp.json()["id"]

    # Download PDF
    resp = await client.get(f"/api/tax-forms/{record_id}/pdf", headers=test_user["headers"])
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert len(resp.content) > 100  # Should have some PDF content
