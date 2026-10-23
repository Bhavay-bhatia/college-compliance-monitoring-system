"""
AICTE SETU — Phase 0 Verification & Output Runner
Evaluates sample technical institution applications against the 6 Core AICTE Rules.
"""

import sys
import os
import json
from pathlib import Path

# Add backend directory to Python sys.path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from app.models.base import Base, engine
from app.services.rule_engine import AICTERuleEngine
from app.schemas.compliance import (
    InstitutionInputSnapshot,
    FacultySnapshot,
    PrincipalDetails,
    InfrastructureSnapshot,
    ComputingSnapshot,
    LibrarySnapshot,
    SafetyAndAccessSnapshot,
    StatutoryCommitteesSnapshot
)

def run_phase_0_demo():
    print("=" * 80)
    print(" AICTE SETU — PHASE 0 ARCHITECTURE & 6 CORE RULES VERIFICATION")
    print("=" * 80)

    # 1. Initialize DB Tables
    print("\n[*] Initializing relational schema (SQLite / PostgreSQL models)...")
    Base.metadata.create_all(bind=engine)
    print("    -> Database schema initialized successfully.")

    # 2. Instantiate Rule Engine
    engine_instance = AICTERuleEngine()
    print(f"[*] AICTE Rule Engine loaded (Engine Version: {engine_instance.RULE_VERSION})")

    # -------------------------------------------------------------------------
    # TEST CASE 1: Compliant Institution
    # -------------------------------------------------------------------------
    compliant_input = InstitutionInputSnapshot(
        institution_code="AICTE-DEMO-EXCELLENCE-TECH",
        academic_year="2026-2027",
        programme="ENGINEERING_AND_TECHNOLOGY",
        level="UG",
        location_type="URBAN",
        total_sanctioned_intake=240,
        course_duration_years=4,
        accredited_status=False,
        faculty=FacultySnapshot(
            total_regular_faculty=52,
            professors=6,
            associate_professors=12,
            assistant_professors=34,
            principal=PrincipalDetails(
                is_appointed=True,
                phd_qualified=True,
                experience_years=19.5
            )
        ),
        infrastructure=InfrastructureSnapshot(
            land_area_acres=3.2,
            instructional_area_sqm=5100.0,
            administrative_area_sqm=1250.0,
            amenities_area_sqm=920.0
        ),
        computing=ComputingSnapshot(
            student_terminals=255,
            internet_bandwidth_mbps=500.0,
            system_software_count=5,
            application_software_count=28
        ),
        library=LibrarySnapshot(
            total_volumes=12800,
            total_titles=2300,
            national_journals=24,
            international_e_journals=True,
            multimedia_terminals=18
        ),
        safety_and_access=SafetyAndAccessSnapshot(
            fire_noc_valid=True,
            fire_noc_expiry_date="2027-04-30",
            structural_stability_certified=True,
            potable_water_certified=True,
            barrier_free_ramps=True,
            braille_enabled_lift=True,
            disabled_friendly_toilets=True
        ),
        statutory_committees=StatutoryCommitteesSnapshot(
            anti_ragging_committee=True,
            anti_ragging_squad=True,
            internal_complaints_committee_icc=True,
            icc_external_member=True,
            student_grievance_redressal_committee=True,
            ombudsman_appointed=True,
            sc_st_committee=True
        )
    )

    print("\n" + "-" * 80)
    print(" [CASE 1] EVALUATING FULLY COMPLIANT INSTITUTION (AICTE-DEMO-EXCELLENCE-TECH)")
    print("-" * 80)
    res_compliant = engine_instance.evaluate_all(compliant_input)

    print(f"Overall Status: {res_compliant.overall_status}")
    print(f"Total Rules Checked: {res_compliant.total_rules_evaluated}")
    print(f"Passed: {res_compliant.compliant_rules_count} | Deficient: {res_compliant.deficient_rules_count}")
    print("\nRule By Rule Breakdown:")
    for idx, r in enumerate(res_compliant.results, start=1):
        print(f"  {idx}. [{r.status}] {r.rule_key} ({r.severity})")
        print(f"     -> {r.explanation}")

    # -------------------------------------------------------------------------
    # TEST CASE 2: Deficient Institution (Simulating Real-World Gaps)
    # -------------------------------------------------------------------------
    deficient_input = InstitutionInputSnapshot(
        institution_code="AICTE-DEMO-DEFICIENT-INST",
        academic_year="2026-2027",
        programme="ENGINEERING_AND_TECHNOLOGY",
        level="UG",
        location_type="URBAN",
        total_sanctioned_intake=240,
        course_duration_years=4,
        accredited_status=False,
        faculty=FacultySnapshot(
            total_regular_faculty=36,       # Shortfall: 48 required (short by 12)
            professors=2,                   # Shortfall: 6 required
            associate_professors=4,         # Shortfall: 11 required
            assistant_professors=30,
            principal=PrincipalDetails(
                is_appointed=False,         # DEFICIENT: No regular Principal
                phd_qualified=False,
                experience_years=0.0
            )
        ),
        infrastructure=InfrastructureSnapshot(
            land_area_acres=1.8,            # Shortfall: 2.5 required in Urban
            instructional_area_sqm=3800.0,  # Shortfall: 4800 required
            administrative_area_sqm=700.0,
            amenities_area_sqm=500.0
        ),
        computing=ComputingSnapshot(
            student_terminals=140,          # Shortfall: 240 required (1:4 ratio)
            internet_bandwidth_mbps=100.0,  # Shortfall: 500 Mbps required
            system_software_count=2,
            application_software_count=12
        ),
        library=LibrarySnapshot(
            total_volumes=6000,             # Deficient: 8000 required
            total_titles=900,
            national_journals=8,
            international_e_journals=False, # DEFICIENT: No e-journal consortium
            multimedia_terminals=5
        ),
        safety_and_access=SafetyAndAccessSnapshot(
            fire_noc_valid=False,           # DEFICIENT: Fire NOC Expired
            fire_noc_expiry_date="2025-12-31",
            structural_stability_certified=False,
            potable_water_certified=True,
            barrier_free_ramps=False,       # DEFICIENT: No Divyangjan ramps
            braille_enabled_lift=False,
            disabled_friendly_toilets=False
        ),
        statutory_committees=StatutoryCommitteesSnapshot(
            anti_ragging_committee=True,
            anti_ragging_squad=False,       # DEFICIENT: Missing Anti-Ragging squad
            internal_complaints_committee_icc=True,
            icc_external_member=False,      # DEFICIENT: Missing external member in ICC
            student_grievance_redressal_committee=True,
            ombudsman_appointed=False,      # DEFICIENT: Missing Ombudsman
            sc_st_committee=False
        )
    )

    print("\n" + "-" * 80)
    print(" [CASE 2] EVALUATING DEFICIENT INSTITUTION (AICTE-DEMO-DEFICIENT-INST)")
    print("-" * 80)
    res_deficient = engine_instance.evaluate_all(deficient_input)

    print(f"Overall Status: \033[91m{res_deficient.overall_status}\033[0m")
    print(f"Total Rules Checked: {res_deficient.total_rules_evaluated}")
    print(f"Compliant: {res_deficient.compliant_rules_count} | Deficient: {res_deficient.deficient_rules_count}")
    
    print("\n--- DEFICIENCY MATRIX ---")
    for idx, d in enumerate(res_deficient.deficiencies, start=1):
        print(f"  [{idx}] Rule: {d.rule_key} | Severity: {d.severity}")
        print(f"      Deficiency: {d.description}")
        print(f"      Action:     {d.recommended_action}")

    # Output Sample JSON response
    output_sample = {
        "institution_code": res_deficient.institution_code,
        "academic_year": res_deficient.academic_year,
        "overall_status": res_deficient.overall_status,
        "compliant_count": res_deficient.compliant_rules_count,
        "deficient_count": res_deficient.deficient_rules_count,
        "deficiencies_sample": [d.model_dump() for d in res_deficient.deficiencies[:3]],
        "sample_rule_result": res_deficient.results[0].model_dump()
    }

    print("\n" + "-" * 80)
    print(" SAMPLE JSON API OUTPUT FROM /api/compliance/check")
    print("-" * 80)
    print(json.dumps(output_sample, indent=2))
    print("\n" + "=" * 80)
    print(" PHASE 0 ENGINE VERIFICATION COMPLETED SUCCESSFULLY!")
    print("=" * 80)

if __name__ == "__main__":
    run_phase_0_demo()
