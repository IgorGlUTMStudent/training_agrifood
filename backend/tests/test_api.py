from fastapi.testclient import TestClient

from app.main import app
from app.services.demo_assessment import SIMULATION_NOTICE

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "smart-harvest",
        "analytics": "not_configured",
    }


def test_demo_assessment_is_explicitly_synthetic_and_insufficient() -> None:
    response = client.get("/api/v1/demo/assessment")

    assert response.status_code == 200
    payload = response.json()
    assert set(payload) == {
        "batch_id",
        "status",
        "risk",
        "deterioration_horizon",
        "factors",
        "recommendation",
        "reliability",
        "provenance",
    }
    assert set(payload["reliability"]) == {
        "level",
        "confidence_score",
        "reason_codes",
        "missing_requirements",
    }
    assert set(payload["provenance"]) == {
        "contract_version",
        "engine_tier",
        "engine_version",
        "generated_at",
        "source_dataset_id",
        "simulation",
        "notice",
    }
    assert payload["status"] == "insufficient_data"
    assert payload["risk"] is None
    assert payload["deterioration_horizon"] is None
    assert payload["recommendation"] is None
    assert payload["provenance"]["simulation"] is True
    assert payload["provenance"]["notice"] == SIMULATION_NOTICE
