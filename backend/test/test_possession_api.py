from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_create_possession_summary():
    response = client.post(
        "/api/v1/possessions/summary",
        json={
            "possession_id": "poss_001",
            "team": "team_a",
            "start_time": 5.0,
            "end_time": 15.0,
            "duration_seconds": 10.0,
            "result": "missed_shot",
            "pass_count": 3,
            "manually_segmented": True,
            "spacing": {
                "average_spacing_feet": 14.8,
                "minimum_spacing_feet": 11.2,
                "maximum_spacing_feet": 18.4,
                "spacing_sample_count": 20,
            },
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "summary" in data
    assert "positive" in data
    assert "improvement" in data
    assert "evidence_keys" in data