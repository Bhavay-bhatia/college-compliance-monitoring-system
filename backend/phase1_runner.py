"""
AICTE SETU — Phase 1 Verification & Output Runner
Validates Authentication, Role-Based Access Control (RBAC),
Institutional Application Lifecycle, and Revision Audit Tracking.
"""

import sys
import os
import json
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from app.main import app
from app.models.base import Base, engine
from app.models.user import UserRole

def print_banner(text: str):
    print("\n" + "=" * 80)
    print(f" {text}")
    print("=" * 80)

def run_phase_1_demo():
    print_banner("AICTE SETU — PHASE 1 ARCHITECTURE & LIFECYCLE VERIFICATION")
    print("Core Capabilities: Authentication, Multi-Role RBAC, Application Lifecycle & Revision Auditing")

    # 1. Clean Database initialization
    print("\n[*] Initializing database schema...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("    -> Database schema initialized cleanly.")

    with TestClient(app) as client:
        # ---------------------------------------------------------------------
        # STEP 1: User Registration & JWT Issuance (RBAC Setup)
        # ---------------------------------------------------------------------
        print_banner("STEP 1: USER REGISTRATION & JWT AUTHENTICATION")
        
        # 1a. College Admin
        college_payload = {
            "email": "admin@delhi-tech.edu.in",
            "password": "SecureCollegePass123!",
            "full_name": "Prof. Amit Verma",
            "role": UserRole.COLLEGE_ADMIN,
            "institution_code": "1-109283741",
            "institution_name": "Delhi Institute of Technology & Science",
            "institution_region": "NORTH"
        }
        res_col = client.post("/api/auth/register", json=college_payload)
        assert res_col.status_code == 201, res_col.text
        col_data = res_col.json()
        col_token = col_data["access_token"]
        col_headers = {"Authorization": f"Bearer {col_token}"}
        print(f"[+] Registered College Admin:")
        print(f"    - Name:        {col_data['user']['full_name']}")
        print(f"    - Role:        {col_data['user']['role']}")
        print(f"    - Institution: {col_data['user']['institution_name']} ({col_data['user']['institution_code']})")
        print(f"    - JWT Token:   {col_token[:24]}...")

        # 1b. AICTE Scrutiny Officer
        officer_payload = {
            "email": "scrutiny.officer@aicte.gov.in",
            "password": "GovScrutinySecure987!",
            "full_name": "Dr. Sunita Deshmukh",
            "role": UserRole.SCRUTINY_OFFICER
        }
        res_off = client.post("/api/auth/register", json=officer_payload)
        assert res_off.status_code == 201, res_off.text
        off_data = res_off.json()
        off_token = off_data["access_token"]
        off_headers = {"Authorization": f"Bearer {off_token}"}
        print(f"\n[+] Registered AICTE Scrutiny Officer:")
        print(f"    - Name:      {off_data['user']['full_name']}")
        print(f"    - Role:      {off_data['user']['role']}")
        print(f"    - JWT Token: {off_token[:24]}...")

        # ---------------------------------------------------------------------
        # STEP 2: College Admin creates Application Draft (Revision 1)
        # ---------------------------------------------------------------------
        print_banner("STEP 2: APPLICATION CREATION (REVISION 1 DRAFT)")

        draft_snapshot = {
            "institution_code": "1-109283741",
            "academic_year": "2026-2027",
            "programme": "ENGINEERING_AND_TECHNOLOGY",
            "level": "UG",
            "location_type": "URBAN",
            "total_sanctioned_intake": 240,
            "course_duration_years": 4,
            "accredited_status": False,
            "faculty": {
                "total_regular_faculty": 36,  # Deficient: 960 students at 1:20 requires 48
                "professors": 3,
                "associate_professors": 6,
                "assistant_professors": 27,
                "principal": {"is_appointed": True, "phd_qualified": True, "experience_years": 16.0}
            },
            "infrastructure": {
                "land_area_acres": 3.0,
                "instructional_area_sqm": 5000.0,
                "administrative_area_sqm": 1200.0,
                "amenities_area_sqm": 850.0
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

        app_req = {
            "application_type": "EXTENSION_OF_APPROVAL",
            "programme": "ENGINEERING_AND_TECHNOLOGY",
            "academic_year": "2026-2027",
            "declared_student_intake": 240,
            "payload_snapshot": draft_snapshot
        }
        res_create = client.post("/api/applications/", json=app_req, headers=col_headers)
        assert res_create.status_code == 201, res_create.text
        app_data = res_create.json()
        app_id = app_data["id"]
        print(f"[+] Application Created Successfully:")
        print(f"    - Application ID:  {app_id}")
        print(f"    - Type:            {app_data['application_type']}")
        print(f"    - Status:          {app_data['status']}")
        print(f"    - Current Version: v{app_data['current_version']}")

        # ---------------------------------------------------------------------
        # STEP 3: Submit Application & Automated Evaluation
        # ---------------------------------------------------------------------
        print_banner("STEP 3: SUBMISSION & DETERMINISTIC COMPLIANCE EVALUATION")
        res_sub = client.post(f"/api/applications/{app_id}/submit", headers=col_headers)
        assert res_sub.status_code == 200, res_sub.text
        sub_data = res_sub.json()
        print(f"[+] Evaluation Result Triggered on Submission:")
        print(f"    - Status:            {sub_data['status']}")
        print(f"    - Compliance Status: {sub_data['compliance_status']}")
        print(f"    - Open Deficiencies: {len(sub_data['deficiencies'])}")
        for i, d in enumerate(sub_data['deficiencies'], 1):
            print(f"      {i}. [{d['severity']}] {d['field_key']}: {d['description']}")

        # ---------------------------------------------------------------------
        # STEP 4: RBAC Guard Verification
        # ---------------------------------------------------------------------
        print_banner("STEP 4: RBAC SECURITY ENFORCEMENT CHECK")
        res_unauth = client.post(
            f"/api/applications/{app_id}/review",
            json={"action": "APPROVE", "remarks": "Unauthorized self-approval attempt"},
            headers=col_headers
        )
        print(f"[*] Testing College Admin attempting Officer action:")
        print(f"    - HTTP Response Code: {res_unauth.status_code} (Expected: 403 Forbidden)")
        print(f"    - Error Detail:       {res_unauth.json()['detail']}")
        assert res_unauth.status_code == 403

        # ---------------------------------------------------------------------
        # STEP 5: College Admin Submits Rectification (Revision 2)
        # ---------------------------------------------------------------------
        print_banner("STEP 5: DEFICIENCY RECTIFICATION & REVISION 2 GENERATION")
        rectified_snap = dict(draft_snapshot)
        rectified_snap["faculty"] = {
            "total_regular_faculty": 52,  # Rectified: Now complies with 48 required
            "professors": 6,
            "associate_professors": 12,
            "assistant_professors": 34,
            "principal": {"is_appointed": True, "phd_qualified": True, "experience_years": 16.0}
        }

        rectify_req = {
            "change_summary": "Recruited 16 additional faculty members and restored cadre balance to 1:2:6",
            "payload_snapshot": rectified_snap
        }
        res_rec = client.post(f"/api/applications/{app_id}/rectify", json=rectify_req, headers=col_headers)
        assert res_rec.status_code == 200, res_rec.text
        rec_data = res_rec.json()
        print(f"[+] Revision 2 Created & Auto-Reevaluated:")
        print(f"    - New Version:       v{rec_data['current_version']}")
        print(f"    - New Status:        {rec_data['status']}")
        print(f"    - Compliance Status: {rec_data['compliance_status']}")
        print(f"    - Total Revisions:   {len(rec_data['revisions'])}")
        print(f"    - Audited Diff:      {list(rec_data['revisions'][-1]['changed_fields'].keys())}")

        # ---------------------------------------------------------------------
        # STEP 6: Scrutiny Officer Reviews & Grants Approval
        # ---------------------------------------------------------------------
        print_banner("STEP 6: AICTE SCRUTINY OFFICER AUDIT & APPROVAL")
        review_req = {
            "action": "APPROVE",
            "remarks": "Verified newly joined faculty via salary vouchers and Aadhaar-linked records. All 6 statutory rules satisfied."
        }
        res_rev = client.post(f"/api/applications/{app_id}/review", json=review_req, headers=off_headers)
        assert res_rev.status_code == 200, res_rev.text
        final_app = res_rev.json()
        print(f"[+] Final Approval Processed by Scrutiny Officer:")
        print(f"    - Status:          {final_app['status']}")
        print(f"    - Approved At:     {final_app['approved_at']}")
        print(f"    - Officer Remarks: {final_app['officer_remarks']}")
        print(f"    - Review History:")
        for r in final_app["revisions"]:
            print(f"      • Revision v{r['revision_number']} ({r['created_at'][:19]}): {r['change_summary']}")

    print_banner("PHASE 1 VERIFICATION COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    run_phase_1_demo()
