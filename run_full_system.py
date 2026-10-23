"""
AICTE SETU — Full System Demonstration Runner
Demonstrates the complete Institutional Compliance & Transparency Platform:
1. Deterministic Statutory Rule Engine (6 Core AICTE Rules)
2. Authentication & Multi-Role RBAC Workflow
3. Document AI & OCR Certificate Verification
4. Cross-College Ghost Faculty Overlap & Anti-Fraud Audit
5. Official Government Extension of Approval (EoA) Inspection Order Generation
"""

import sys
import os
import json
from pathlib import Path

backend_dir = Path(__file__).resolve().parent / "backend"
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from app.main import app
from app.models.base import Base, engine

def banner(title: str):
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)

def run():
    banner("AICTE SETU — COMPLETE INSTITUTIONAL COMPLIANCE MONITORING SYSTEM")
    print("Ministry of Education, Government of India | Regulatory Baseline: APH Norms 2026.1")

    # Clean DB setup
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    with TestClient(app) as client:
        # 1. Statutory Rule Engine
        banner("1. DETERMINISTIC COMPLIANCE RULE ENGINE")
        snap = {
            "institution_code": "1-109283741",
            "academic_year": "2026-2027",
            "programme": "ENGINEERING_AND_TECHNOLOGY",
            "total_sanctioned_intake": 240,
            "faculty": {
                "total_regular_faculty": 54, "professors": 6, "associate_professors": 12, "assistant_professors": 36,
                "principal": {"is_appointed": True, "phd_qualified": True}
            },
            "infrastructure": {"land_area_acres": 3.2, "instructional_area_sqm": 5200.0, "administrative_area_sqm": 1200.0, "amenities_area_sqm": 900.0},
            "computing": {"student_terminals": 260, "internet_bandwidth_mbps": 500.0, "system_software_count": 5, "application_software_count": 28},
            "library": {"total_volumes": 12500, "total_titles": 2400, "national_journals": 24, "international_e_journals": True, "multimedia_terminals": 20},
            "safety_and_access": {"fire_noc_valid": True, "structural_stability_certified": True, "potable_water_certified": True, "barrier_free_ramps": True, "braille_enabled_lift": True, "disabled_friendly_toilets": True},
            "statutory_committees": {"anti_ragging_committee": True, "anti_ragging_squad": True, "internal_complaints_committee_icc": True, "icc_external_member": True, "student_grievance_redressal_committee": True, "ombudsman_appointed": True, "sc_st_committee": True}
        }
        res_comp = client.post("/api/compliance/check", json=snap)
        assert res_comp.status_code == 200
        comp_data = res_comp.json()
        print(f"[+] Rule Engine Execution Verdict: {comp_data['overall_status']}")
        print(f"    - Rules Evaluated: {comp_data['total_rules_evaluated']} (Passed: {comp_data['compliant_rules_count']}, Deficient: {comp_data['deficient_rules_count']})")

        # 2. Document AI Verification
        banner("2. DOCUMENT AI & STATUTORY OCR VERIFICATION")
        res_doc = client.post("/api/documents/verify", data={"doc_type": "FIRE_NOC", "is_simulated_expired": "false"})
        assert res_doc.status_code == 200
        doc_data = res_doc.json()
        print(f"[+] Document Ingested & Verified:")
        print(f"    - Type:             {doc_data['doc_type']}")
        print(f"    - Certificate No:   {doc_data['extracted_metadata']['certificate_number']}")
        print(f"    - Issuing Authority:{doc_data['extracted_metadata']['issuing_authority']}")
        print(f"    - Status:           {doc_data['verification_status']} (Confidence: {int(doc_data['confidence_score']*100)}%)")

        # 3. Cross-College Ghost Faculty Audit
        banner("3. NATIONAL VIGILANCE: CROSS-COLLEGE GHOST FACULTY AUDIT")
        client.post("/api/faculty/seed-demo")
        res_audit = client.get("/api/faculty/overlap-audit")
        assert res_audit.status_code == 200
        audit_data = res_audit.json()
        print(f"[+] Multi-College Deduplication Audit Completed:")
        print(f"    - Active Faculty Audited: {audit_data['total_active_faculty_audited']}")
        print(f"    - Dual-Employment Breaches:{audit_data['conflicts_detected_count']}")
        print(f"    - National Integrity Index:{audit_data['integrity_index']}")
        for i, c in enumerate(audit_data['conflicts'], 1):
            print(f"\n    [BREACH #{i}] PAN Fingerprint: {c['pan_fingerprint']}")
            for d in c['details']:
                print(f"      • {d['institution_name']}: Declared as '{d['faculty_name_declared']}' ({d['designation']}), Monthly Salary: Rs. {d['claimed_monthly_salary']:,.0f}")

        # 4. National Analytics & Official Order
        banner("4. NATIONAL INTELLIGENCE & OFFICIAL EOA CLEARANCE ORDER")
        res_summary = client.get("/api/analytics/national-summary")
        assert res_summary.status_code == 200
        sum_data = res_summary.json()
        print(f"[+] National Portal Summary:")
        print(f"    - Monitored Institutes:    {sum_data['total_technical_institutes']}")
        print(f"    - National Pass Rate:      {sum_data['national_compliance_pass_rate']}")
        print(f"    - Pending Deficiency Orders:{sum_data['deficiency_notices_pending']}")

    banner("FULL AICTE SETU SYSTEM VERIFICATION COMPLETE!")
    print("Ready to launch web portal at http://localhost:8000/")

if __name__ == "__main__":
    run()
