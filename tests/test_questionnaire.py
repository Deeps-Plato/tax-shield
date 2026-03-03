import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_questionnaire_flow(client: AsyncClient, test_user, sample_category, sample_item):
    # Start
    start_resp = await client.post(
        "/api/analysis/questionnaire/start",
        json={
            "tax_year": 2025,
        },
        headers=test_user["headers"],
    )
    assert start_resp.status_code == 200
    q = start_resp.json()
    assert q["is_final"] is False
    assert q["session_id"]

    # Answer (this should work with or without templates)
    answer_resp = await client.post(
        "/api/analysis/questionnaire/answer",
        json={
            "session_id": q["session_id"],
            "question_key": q["question_key"],
            "response": q.get("options", ["Yes"])[0] if q.get("options") else "Yes",
        },
        headers=test_user["headers"],
    )
    assert answer_resp.status_code == 200
    next_q = answer_resp.json()
    assert "question" in next_q
    assert "session_id" in next_q
