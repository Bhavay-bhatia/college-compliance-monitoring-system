import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.base import Base, engine
from app.models.user import UserRole

@pytest.fixture(scope="module")
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)

def test_document_ai_pipeline(client):
    # Test valid Fire NOC
    res = client.post("/api/documents/verify", data={"doc_type": "FIRE_NOC", "is_simulated_expired": "false"})
    assert res.status_code == 200
    data = res.json()
    assert data["verification_status"] == "VERIFIED"
    assert data["confidence_score"] >= 0.90
    assert "FIRE" in data["doc_type"]

    # Test expired certificate rejection
    res_exp = client.post("/api/documents/verify", data={"doc_type": "FIRE_NOC", "is_simulated_expired": "true"})
    assert res_exp.status_code == 200
    data_exp = res_exp.json()
    assert data_exp["verification_status"] == "FLAGGED"
    assert data_exp["flag_reason"] is not None

def test_faculty_overlap_and_ghost_teacher_audit(client):
    # Seed faculty and run audit
    res_seed = client.post("/api/faculty/seed-demo")
    assert res_seed.status_code == 200

    res_audit = client.get("/api/faculty/overlap-audit")
    assert res_audit.status_code == 200
    data = res_audit.json()
    assert data["status"] == "COMPLETED"
    assert data["conflicts_detected_count"] >= 2
    assert len(data["conflicts"]) >= 2
    for c in data["conflicts"]:
        assert c["institutions_count"] >= 2
        assert c["severity"] == "CRITICAL"

def test_national_analytics_and_eoa_report(client):
    res_summary = client.get("/api/analytics/national-summary")
    assert res_summary.status_code == 200
    summary = res_summary.json()
    assert summary["total_technical_institutes"] >= 1
    assert len(summary["top_deficiency_breakdown"]) == 6
    assert len(summary["regional_zones"]) == 5
