import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.base import Base, engine, SessionLocal
from app.models.user import UserRole

@pytest.fixture(scope="module")
def client():
    # Setup test database tables cleanly
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)

def test_phase1_full_workflow(client):
    # -------------------------------------------------------------------------
    # 1. Register College Admin
    # -------------------------------------------------------------------------
    college_signup = {
        "email": "admin@apextech.edu.in",
        "password": "CollegePassword123!",
        "full_name": "Prof. R. K. Sharma",
        "role": UserRole.COLLEGE_ADMIN,
        "institution_code": "1-109283741",
        "institution_name": "Apex Institute of Technology",
        "institution_region": "NORTH"
    }
    res = client.post("/api/auth/register", json=college_signup)
    assert res.status_code == 201, res.text
    college_data = res.json()
    college_token = college_data["access_token"]
    college_headers = {"Authorization": f"Bearer {college_token}"}
    assert college_data["user"]["role"] == UserRole.COLLEGE_ADMIN

    # -------------------------------------------------------------------------
    # 2. Register Scrutiny Officer
    # -------------------------------------------------------------------------
    officer_signup = {
        "email": "officer.verma@aicte-india.org",
        "password": "OfficerPassword123!",
        "full_name": "Dr. S. K. Verma",
        "role": UserRole.SCRUTINY_OFFICER
    }
    res = client.post("/api/auth/register", json=officer_signup)
    assert res.status_code == 201, res.text
    officer_data = res.json()
    officer_token = officer_data["access_token"]
    officer_headers = {"Authorization": f"Bearer {officer_token}"}
    assert officer_data["user"]["role"] == UserRole.SCRUTINY_OFFICER

    # -------------------------------------------------------------------------
    # 3. College Admin creates Application Draft (Version 1, with a deliberate deficiency)
    # -------------------------------------------------------------------------
    initial_snapshot = {
        "institution_code": "1-109283741",
        "academic_year": "2026-2027",
        "programme": "ENGINEERING_AND_TECHNOLOGY",
        "level": "UG",
        "location_type": "URBAN",
        "total_sanctioned_intake": 240,
        "course_duration_years": 4,
        "accredited_status": False,
        "faculty": {
            "total_regular_faculty": 32,  # Deficient: 960 students at 1:20 requires 48
            "professors": 3,
            "associate_professors": 5,
            "assistant_professors": 24,
            "principal": { "is_appointed": True, "phd_qualified": True, "experience_years": 15.0 }
        },
        "infrastructure": {
            "land_area_acres": 3.0,
            "instructional_area_sqm": 5000.0,
            "administrative_area_sqm": 1200.0,
            "amenities_area_sqm": 800.0
        },
        "computing": {
            "student_terminals": 250,
            "internet_bandwidth_mbps": 500.0,
            "system_software_count": 4,
            "application_software_count": 22
        },
        "library": {
            "total_volumes": 12000,
            "total_titles": 2200,
            "national_journals": 24,
            "international_e_journals": True,
            "multimedia_terminals": 15
        },
        "safety_and_access": {
            "fire_noc_valid": True,
            "fire_noc_expiry_date": "2027-01-01",
            "structural_stability_certified": True,
            "potable_water_certified": True,
            "barrier_free_ramps": True,
            "braille_enabled_lift": True,
            "disabled_friendly_toilets": True
        },
        "statutory_committees": {
            "anti_ragging_committee": True,
            "anti_ragging_squad": True,
            "internal_complaints_committee_icc": True,
            "icc_external_member": True,
            "student_grievance_redressal_committee": True,
            "ombudsman_appointed": True,
            "sc_st_committee": True
        }
    }

    app_payload = {
        "application_type": "EXTENSION_OF_APPROVAL",
        "programme": "ENGINEERING_AND_TECHNOLOGY",
        "academic_year": "2026-2027",
        "declared_student_intake": 240,
        "payload_snapshot": initial_snapshot
    }

    res = client.post("/api/applications/", json=app_payload, headers=college_headers)
    assert res.status_code == 201, res.text
    created_app = res.json()
    app_id = created_app["id"]
    assert created_app["status"] == "DRAFT"
    assert created_app["current_version"] == 1
    assert len(created_app["revisions"]) == 1

    # -------------------------------------------------------------------------
    # 4. College Admin submits application -> Triggers compliance engine
    # -------------------------------------------------------------------------
    res = client.post(f"/api/applications/{app_id}/submit", headers=college_headers)
    assert res.status_code == 200, res.text
    submitted_app = res.json()
    assert submitted_app["status"] == "DEFICIENCY_ISSUED"
    assert submitted_app["compliance_status"] == "DEFICIENT"
    assert len(submitted_app["deficiencies"]) > 0

    # -------------------------------------------------------------------------
    # 5. RBAC Check: College Admin cannot approve their own application
    # -------------------------------------------------------------------------
    res = client.post(
        f"/api/applications/{app_id}/review",
        json={"action": "APPROVE", "remarks": "Trying to self-approve"},
        headers=college_headers
    )
    assert res.status_code == 403

    # -------------------------------------------------------------------------
    # 6. Rectification & Revision 2: College Admin resolves the faculty shortfall
    # -------------------------------------------------------------------------
    rectified_snapshot = dict(initial_snapshot)
    rectified_snapshot["faculty"] = {
        "total_regular_faculty": 50,  # Now compliant (>= 48)
        "professors": 6,
        "associate_professors": 12,
        "assistant_professors": 32,
        "principal": { "is_appointed": True, "phd_qualified": True, "experience_years": 15.0 }
    }

    rectify_payload = {
        "change_summary": "Recruited 18 additional regular faculty and balanced cadre ratio",
        "payload_snapshot": rectified_snapshot
    }

    res = client.post(f"/api/applications/{app_id}/rectify", json=rectify_payload, headers=college_headers)
    assert res.status_code == 200, res.text
    rectified_app = res.json()
    assert rectified_app["current_version"] == 2
    assert rectified_app["compliance_status"] == "COMPLIANT"
    assert rectified_app["status"] == "UNDER_REVIEW"
    assert len(rectified_app["revisions"]) == 2
    assert "faculty" in rectified_app["revisions"][-1]["changed_fields"]

    # -------------------------------------------------------------------------
    # 7. Scrutiny Officer views list and reviews revised application -> APPROVED
    # -------------------------------------------------------------------------
    res = client.get("/api/applications/", headers=officer_headers)
    assert res.status_code == 200
    apps_list = res.json()
    assert any(a["id"] == app_id for a in apps_list)

    review_payload = {
        "action": "APPROVE",
        "remarks": "Verified faculty appointment letters and cadre ratio. All 6 core compliance rules satisfied."
    }
    res = client.post(f"/api/applications/{app_id}/review", json=review_payload, headers=officer_headers)
    assert res.status_code == 200, res.text
    approved_app = res.json()
    assert approved_app["status"] == "APPROVED"
    assert approved_app["approved_at"] is not None
    assert approved_app["officer_remarks"] == review_payload["remarks"]
