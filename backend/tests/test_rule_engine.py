import pytest
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

@pytest.fixture
def rule_engine():
    return AICTERuleEngine()

@pytest.fixture
def compliant_snapshot():
    # 240 intake * 4 years = 960 students -> 1:20 requires 48 faculty. Provided: 54 faculty.
    return InstitutionInputSnapshot(
        institution_code="1-AICTE-DELHI-ENG-01",
        academic_year="2026-2027",
        programme="ENGINEERING_AND_TECHNOLOGY",
        level="UG",
        location_type="URBAN",
        total_sanctioned_intake=240,
        course_duration_years=4,
        accredited_status=False,
        faculty=FacultySnapshot(
            total_regular_faculty=54,
            professors=6,
            associate_professors=12,
            assistant_professors=36,
            principal=PrincipalDetails(
                is_appointed=True,
                phd_qualified=True,
                experience_years=20.0
            )
        ),
        infrastructure=InfrastructureSnapshot(
            land_area_acres=3.5,  # Urban requires 2.5
            instructional_area_sqm=5200.0,  # 960 * 5 = 4800 required
            administrative_area_sqm=1200.0,
            amenities_area_sqm=900.0
        ),
        computing=ComputingSnapshot(
            student_terminals=250,  # 960 / 4 = 240 required
            internet_bandwidth_mbps=500.0,  # >600 students requires 500 Mbps
            system_software_count=4,
            application_software_count=25
        ),
        library=LibrarySnapshot(
            total_volumes=12000,
            total_titles=2400,
            national_journals=24,
            international_e_journals=True,
            multimedia_terminals=20
        ),
        safety_and_access=SafetyAndAccessSnapshot(
            fire_noc_valid=True,
            fire_noc_expiry_date="2027-05-30",
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

def test_full_compliance(rule_engine, compliant_snapshot):
    response = rule_engine.evaluate_all(compliant_snapshot)
    assert response.overall_status == "COMPLIANT"
    assert response.total_rules_evaluated == 6
    assert response.compliant_rules_count == 6
    assert response.deficient_rules_count == 0
    assert len(response.deficiencies) == 0

def test_deficiencies_detection(rule_engine, compliant_snapshot):
    # Introduce deliberate non-compliances:
    # 1. Deficient Faculty: Only 35 faculty instead of 48, and no Ph.D. Principal
    compliant_snapshot.faculty.total_regular_faculty = 35
    compliant_snapshot.faculty.principal.phd_qualified = False

    # 2. Deficient Land: 1.8 acres in Urban (requires 2.5)
    compliant_snapshot.infrastructure.land_area_acres = 1.8

    # 3. Deficient Computing: Only 150 PCs instead of 240
    compliant_snapshot.computing.student_terminals = 150

    # 4. Deficient Safety: Expired Fire NOC
    compliant_snapshot.safety_and_access.fire_noc_valid = False

    # 5. Deficient Committees: No ICC External Member
    compliant_snapshot.statutory_committees.icc_external_member = False

    response = rule_engine.evaluate_all(compliant_snapshot)
    assert response.overall_status == "DEFICIENT"
    assert response.deficient_rules_count >= 4
    
    # Check specific rule keys
    failed_keys = {d.rule_key for d in response.deficiencies}
    assert "AICTE_RULE_FSR_01" in failed_keys
    assert "AICTE_RULE_AREA_02" in failed_keys
    assert "AICTE_RULE_COMP_LAB_03" in failed_keys
    assert "AICTE_RULE_SAFETY_05" in failed_keys
    assert "AICTE_RULE_COMM_06" in failed_keys

def test_missing_data_handling(rule_engine):
    # Missing data should not be compliant
    empty_snapshot = InstitutionInputSnapshot(
        institution_code="EMPTY-001",
        total_sanctioned_intake=120
    )
    response = rule_engine.evaluate_all(empty_snapshot)
    assert response.overall_status == "DEFICIENT"
    assert response.deficient_rules_count == 6
