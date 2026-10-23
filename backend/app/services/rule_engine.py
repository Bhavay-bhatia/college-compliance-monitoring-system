import math
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple
from app.schemas.compliance import (
    InstitutionInputSnapshot,
    ComplianceResultItem,
    DeficiencyItem,
    ComplianceEvaluationResponse
)

class AICTERuleEngine:
    """
    Deterministic AICTE Compliance Rule Engine (Phase 0).
    Evaluates institutional snapshots against the 6 Core APH Statutory Rules.
    Explicitly handles missing data without assuming compliance.
    """

    RULE_VERSION = "2026.1"

    def evaluate_all(self, snapshot: InstitutionInputSnapshot, evaluated_at: str = None) -> ComplianceEvaluationResponse:
        if not evaluated_at:
            evaluated_at = datetime.now(timezone.utc).isoformat()

        results: List[ComplianceResultItem] = []
        deficiencies: List[DeficiencyItem] = []

        # 1. Rule 1: Faculty-to-Student Ratio & Cadre
        r1, d1 = self._evaluate_fsr(snapshot, evaluated_at)
        results.append(r1)
        if d1:
            deficiencies.extend(d1)

        # 2. Rule 2: Land & Built-up Area
        r2, d2 = self._evaluate_area(snapshot, evaluated_at)
        results.append(r2)
        if d2:
            deficiencies.extend(d2)

        # 3. Rule 3: Computer & Computing Infrastructure
        r3, d3 = self._evaluate_computing(snapshot, evaluated_at)
        results.append(r3)
        if d3:
            deficiencies.extend(d3)

        # 4. Rule 4: Library Resources
        r4, d4 = self._evaluate_library(snapshot, evaluated_at)
        results.append(r4)
        if d4:
            deficiencies.extend(d4)

        # 5. Rule 5: Statutory Safety & Divyangjan Barrier-Free
        r5, d5 = self._evaluate_safety(snapshot, evaluated_at)
        results.append(r5)
        if d5:
            deficiencies.extend(d5)

        # 6. Rule 6: Mandatory Statutory Committees
        r6, d6 = self._evaluate_committees(snapshot, evaluated_at)
        results.append(r6)
        if d6:
            deficiencies.extend(d6)

        # Calculate counts and overall status
        compliant_count = sum(1 for r in results if r.status == "COMPLIANT")
        deficient_count = sum(1 for r in results if r.status == "DEFICIENT")
        review_count = sum(1 for r in results if r.status == "NEEDS_REVIEW")

        if deficient_count > 0:
            overall_status = "DEFICIENT"
        elif review_count > 0:
            overall_status = "NEEDS_REVIEW"
        else:
            overall_status = "COMPLIANT"

        return ComplianceEvaluationResponse(
            institution_code=snapshot.institution_code,
            academic_year=snapshot.academic_year,
            evaluated_at=evaluated_at,
            overall_status=overall_status,
            total_rules_evaluated=len(results),
            compliant_rules_count=compliant_count,
            deficient_rules_count=deficient_count,
            review_rules_count=review_count,
            results=results,
            deficiencies=deficiencies
        )

    # -------------------------------------------------------------------------
    # RULE 1: Faculty-to-Student Ratio & Cadre Distribution (AICTE_RULE_FSR_01)
    # -------------------------------------------------------------------------
    def _evaluate_fsr(self, snap: InstitutionInputSnapshot, evaluated_at: str) -> Tuple[ComplianceResultItem, List[DeficiencyItem]]:
        rule_key = "AICTE_RULE_FSR_01"
        severity = "CRITICAL"

        if not snap.faculty:
            return ComplianceResultItem(
                rule_key=rule_key,
                rule_version=self.RULE_VERSION,
                status="DEFICIENT",
                severity=severity,
                required_value={"faculty_data": "Mandatory faculty snapshot"},
                actual_value={"faculty_data": None},
                shortfall={"missing_data": "Faculty records not provided"},
                explanation="No faculty data submitted. Under AICTE rules, missing data is non-compliant.",
                evidence_refs=[],
                evaluated_at=evaluated_at
            ), [
                DeficiencyItem(
                    rule_key=rule_key,
                    field_key="faculty",
                    severity=severity,
                    description="Institutional faculty roster and Principal details are missing.",
                    recommended_action="Submit verified faculty roster and appointment orders."
                )
            ]

        # Calculate student strength
        total_students = snap.total_sanctioned_intake * snap.course_duration_years
        
        # Prescribed ratio: 1:20 for standard UG, 1:15 for accredited/autonomous
        ratio = 15 if snap.accredited_status else 20
        required_faculty = math.ceil(total_students / ratio)

        # Cadre formula: 1:2:6
        req_prof = math.ceil(required_faculty / 9 * 1)
        req_assoc = math.ceil(required_faculty / 9 * 2)
        req_asst = required_faculty - (req_prof + req_assoc)

        actual_total = snap.faculty.total_regular_faculty
        actual_prof = snap.faculty.professors
        actual_assoc = snap.faculty.associate_professors
        actual_asst = snap.faculty.assistant_professors
        has_principal = snap.faculty.principal and snap.faculty.principal.is_appointed and snap.faculty.principal.phd_qualified

        faculty_shortfall = max(0, required_faculty - actual_total)
        prof_shortfall = max(0, req_prof - actual_prof)
        assoc_shortfall = max(0, req_assoc - actual_assoc)

        deficiencies: List[DeficiencyItem] = []
        shortfall_dict = {
            "total_faculty_shortfall": faculty_shortfall,
            "professor_shortfall": prof_shortfall,
            "associate_professor_shortfall": assoc_shortfall,
            "principal_shortfall": 0 if has_principal else 1
        }

        if faculty_shortfall > 0:
            deficiencies.append(DeficiencyItem(
                rule_key=rule_key,
                field_key="faculty.total_regular_faculty",
                severity="CRITICAL",
                description=f"Total regular faculty ({actual_total}) falls short by {faculty_shortfall} of required {required_faculty} for {total_students} students (ratio 1:{ratio}).",
                recommended_action=f"Recruit at least {faculty_shortfall} additional qualified full-time regular faculty."
            ))

        if not has_principal:
            deficiencies.append(DeficiencyItem(
                rule_key=rule_key,
                field_key="faculty.principal",
                severity="CRITICAL",
                description="Institution lacks an approved, full-time Ph.D. qualified Principal/Director.",
                recommended_action="Appoint an AICTE-qualified regular Principal and upload doctorate credentials."
            ))

        status = "COMPLIANT" if (faculty_shortfall == 0 and has_principal) else "DEFICIENT"
        
        explanation = (
            f"FSR ratio 1:{ratio} for {total_students} students requires {required_faculty} regular faculty. "
            f"Current regular faculty: {actual_total}. "
            f"Cadre distribution: {actual_prof} Professors (req: {req_prof}), {actual_assoc} Assoc Profs (req: {req_assoc}). "
            f"Principal verified: {'Yes' if has_principal else 'No (Deficient)'}."
        )

        return ComplianceResultItem(
            rule_key=rule_key,
            rule_version=self.RULE_VERSION,
            status=status,
            severity=severity,
            required_value={
                "effective_students": total_students,
                "prescribed_ratio": f"1:{ratio}",
                "minimum_faculty": required_faculty,
                "required_professors": req_prof,
                "required_associate_professors": req_assoc,
                "required_assistant_professors": req_asst,
                "principal_phd_required": True
            },
            actual_value={
                "total_faculty": actual_total,
                "professors": actual_prof,
                "associate_professors": actual_assoc,
                "assistant_professors": actual_asst,
                "principal_appointed": bool(snap.faculty.principal and snap.faculty.principal.is_appointed),
                "principal_phd": bool(snap.faculty.principal and snap.faculty.principal.phd_qualified)
            },
            shortfall=shortfall_dict,
            explanation=explanation,
            evidence_refs=["DOC-FACULTY-ROSTER", "DOC-PRINCIPAL-APPOINTMENT"],
            evaluated_at=evaluated_at
        ), deficiencies

    # -------------------------------------------------------------------------
    # RULE 2: Land & Built-up Area (AICTE_RULE_AREA_02)
    # -------------------------------------------------------------------------
    def _evaluate_area(self, snap: InstitutionInputSnapshot, evaluated_at: str) -> Tuple[ComplianceResultItem, List[DeficiencyItem]]:
        rule_key = "AICTE_RULE_AREA_02"
        severity = "HIGH"

        if not snap.infrastructure:
            return ComplianceResultItem(
                rule_key=rule_key,
                rule_version=self.RULE_VERSION,
                status="DEFICIENT",
                severity=severity,
                required_value={"infrastructure_data": "Mandatory area snapshot"},
                actual_value={"infrastructure_data": None},
                shortfall={"missing_data": "Infrastructure records not provided"},
                explanation="No infrastructure data provided.",
                evidence_refs=[],
                evaluated_at=evaluated_at
            ), [
                DeficiencyItem(
                    rule_key=rule_key,
                    field_key="infrastructure",
                    severity=severity,
                    description="Infrastructure area records not submitted.",
                    recommended_action="Submit Architect carpet area certificate and registered land deed."
                )
            ]

        # Land requirement based on location: Urban: 2.5 acres, Rural: 7.5 acres, Mega: 1.5 acres
        loc = snap.location_type.upper()
        if loc == "MEGA_METRO":
            min_land_acres = 1.5
        elif loc == "RURAL":
            min_land_acres = 7.5
        else:
            min_land_acres = 2.5

        # Instructional area estimate: approx 5.0 sq.m per student enrolled
        total_students = snap.total_sanctioned_intake * snap.course_duration_years
        min_instructional_sqm = total_students * 5.0
        min_admin_sqm = 1000.0
        min_amenities_sqm = 800.0

        act_land = snap.infrastructure.land_area_acres
        act_inst = snap.infrastructure.instructional_area_sqm
        act_admin = snap.infrastructure.administrative_area_sqm
        act_amen = snap.infrastructure.amenities_area_sqm

        land_shortfall = max(0.0, round(min_land_acres - act_land, 2))
        inst_shortfall = max(0.0, round(min_instructional_sqm - act_inst, 2))
        admin_shortfall = max(0.0, round(min_admin_sqm - act_admin, 2))

        deficiencies: List[DeficiencyItem] = []
        if land_shortfall > 0:
            deficiencies.append(DeficiencyItem(
                rule_key=rule_key,
                field_key="infrastructure.land_area_acres",
                severity="HIGH",
                description=f"Campus land area ({act_land} acres) falls short of mandatory {min_land_acres} acres for {loc} location.",
                recommended_action=f"Provide certified land registration documents showing at least {min_land_acres} contiguous acres."
            ))

        if inst_shortfall > 0:
            deficiencies.append(DeficiencyItem(
                rule_key=rule_key,
                field_key="infrastructure.instructional_area_sqm",
                severity="HIGH",
                description=f"Instructional carpet area ({act_inst} sq.m) is short by {inst_shortfall} sq.m for {total_students} students (req: {min_instructional_sqm} sq.m).",
                recommended_action="Expand instructional area (classrooms, tutorial rooms, laboratories) or reallocate space."
            ))

        status = "COMPLIANT" if (land_shortfall == 0 and inst_shortfall == 0 and admin_shortfall == 0) else "DEFICIENT"
        
        explanation = (
            f"Location {loc} requires {min_land_acres} acres (actual: {act_land} acres). "
            f"Instructional area requires {min_instructional_sqm} sq.m (actual: {act_inst} sq.m). "
            f"Administrative area: {act_admin} sq.m (req: {min_admin_sqm} sq.m)."
        )

        return ComplianceResultItem(
            rule_key=rule_key,
            rule_version=self.RULE_VERSION,
            status=status,
            severity=severity,
            required_value={
                "minimum_land_acres": min_land_acres,
                "minimum_instructional_sqm": min_instructional_sqm,
                "minimum_administrative_sqm": min_admin_sqm,
                "minimum_amenities_sqm": min_amenities_sqm
            },
            actual_value={
                "land_area_acres": act_land,
                "instructional_area_sqm": act_inst,
                "administrative_area_sqm": act_admin,
                "amenities_area_sqm": act_amen
            },
            shortfall={
                "land_acres_shortfall": land_shortfall,
                "instructional_sqm_shortfall": inst_shortfall,
                "administrative_sqm_shortfall": admin_shortfall
            },
            explanation=explanation,
            evidence_refs=["DOC-REGISTERED-DEED", "DOC-APPROVED-BUILDING-PLAN"],
            evaluated_at=evaluated_at
        ), deficiencies

    # -------------------------------------------------------------------------
    # RULE 3: Computer & Computing Infrastructure (AICTE_RULE_COMP_LAB_03)
    # -------------------------------------------------------------------------
    def _evaluate_computing(self, snap: InstitutionInputSnapshot, evaluated_at: str) -> Tuple[ComplianceResultItem, List[DeficiencyItem]]:
        rule_key = "AICTE_RULE_COMP_LAB_03"
        severity = "HIGH"

        if not snap.computing:
            return ComplianceResultItem(
                rule_key=rule_key,
                rule_version=self.RULE_VERSION,
                status="DEFICIENT",
                severity=severity,
                required_value={"computing_data": "Mandatory computing snapshot"},
                actual_value={"computing_data": None},
                shortfall={"missing_data": "Computing records missing"},
                explanation="No computing or bandwidth data provided.",
                evidence_refs=[],
                evaluated_at=evaluated_at
            ), [
                DeficiencyItem(
                    rule_key=rule_key,
                    field_key="computing",
                    severity=severity,
                    description="Computing and internet bandwidth records not provided.",
                    recommended_action="Submit IT inventory register and ISP bandwidth bills."
                )
            ]

        total_students = snap.total_sanctioned_intake * snap.course_duration_years
        
        # Student-to-Computer Ratio: 1:4 for technical
        req_computers = math.ceil(total_students / 4)
        
        # Bandwidth norms: < 300 students: 100 Mbps; 300-600: 300 Mbps; > 600: 500 Mbps
        if total_students <= 300:
            req_bandwidth = 100.0
        elif total_students <= 600:
            req_bandwidth = 300.0
        else:
            req_bandwidth = 500.0

        req_sys_sw = 3
        req_app_sw = 20

        act_computers = snap.computing.student_terminals
        act_bandwidth = snap.computing.internet_bandwidth_mbps
        act_sys_sw = snap.computing.system_software_count
        act_app_sw = snap.computing.application_software_count

        comp_shortfall = max(0, req_computers - act_computers)
        bw_shortfall = max(0.0, round(req_bandwidth - act_bandwidth, 1))
        sys_shortfall = max(0, req_sys_sw - act_sys_sw)
        app_shortfall = max(0, req_app_sw - act_app_sw)

        deficiencies: List[DeficiencyItem] = []
        if comp_shortfall > 0:
            deficiencies.append(DeficiencyItem(
                rule_key=rule_key,
                field_key="computing.student_terminals",
                severity="HIGH",
                description=f"Student computers ({act_computers}) falls short by {comp_shortfall} of required {req_computers} (1:4 ratio for {total_students} students).",
                recommended_action=f"Procure at least {comp_shortfall} additional student desktop terminals."
            ))

        if bw_shortfall > 0:
            deficiencies.append(DeficiencyItem(
                rule_key=rule_key,
                field_key="computing.internet_bandwidth_mbps",
                severity="HIGH",
                description=f"Internet bandwidth ({act_bandwidth} Mbps) is less than required {req_bandwidth} Mbps.",
                recommended_action=f"Upgrade leased line connection to at least {req_bandwidth} Mbps."
            ))

        status = "COMPLIANT" if (comp_shortfall == 0 and bw_shortfall == 0 and sys_shortfall == 0 and app_shortfall == 0) else "DEFICIENT"

        explanation = (
            f"1:4 Student-Computer ratio requires {req_computers} PCs (actual: {act_computers}). "
            f"Internet bandwidth requires {req_bandwidth} Mbps (actual: {act_bandwidth} Mbps). "
            f"Software packages: {act_sys_sw} System (req: {req_sys_sw}), {act_app_sw} Applications (req: {req_app_sw})."
        )

        return ComplianceResultItem(
            rule_key=rule_key,
            rule_version=self.RULE_VERSION,
            status=status,
            severity=severity,
            required_value={
                "required_computers": req_computers,
                "required_bandwidth_mbps": req_bandwidth,
                "required_system_software": req_sys_sw,
                "required_application_software": req_app_sw
            },
            actual_value={
                "student_terminals": act_computers,
                "internet_bandwidth_mbps": act_bandwidth,
                "system_software_count": act_sys_sw,
                "application_software_count": act_app_sw
            },
            shortfall={
                "computers_shortfall": comp_shortfall,
                "bandwidth_shortfall_mbps": bw_shortfall,
                "system_software_shortfall": sys_shortfall,
                "application_software_shortfall": app_shortfall
            },
            explanation=explanation,
            evidence_refs=["DOC-IT-STOCK-REGISTER", "DOC-ISP-BANDWIDTH-BILL"],
            evaluated_at=evaluated_at
        ), deficiencies

    # -------------------------------------------------------------------------
    # RULE 4: Library Resources (AICTE_RULE_LIB_04)
    # -------------------------------------------------------------------------
    def _evaluate_library(self, snap: InstitutionInputSnapshot, evaluated_at: str) -> Tuple[ComplianceResultItem, List[DeficiencyItem]]:
        rule_key = "AICTE_RULE_LIB_04"
        severity = "MEDIUM"

        if not snap.library:
            return ComplianceResultItem(
                rule_key=rule_key,
                rule_version=self.RULE_VERSION,
                status="DEFICIENT",
                severity=severity,
                required_value={"library_data": "Mandatory library snapshot"},
                actual_value={"library_data": None},
                shortfall={"missing_data": "Library data missing"},
                explanation="No library records provided.",
                evidence_refs=[],
                evaluated_at=evaluated_at
            ), [
                DeficiencyItem(
                    rule_key=rule_key,
                    field_key="library",
                    severity=severity,
                    description="Library catalog data and journal subscriptions missing.",
                    recommended_action="Submit Central Library Accession Register and publisher receipts."
                )
            ]

        divisions = math.ceil(snap.total_sanctioned_intake / 60)
        req_titles = divisions * 100 * snap.course_duration_years
        req_volumes = divisions * 500 * snap.course_duration_years
        req_journals = divisions * 6
        req_e_journals = True

        act_vol = snap.library.total_volumes
        act_titles = snap.library.total_titles
        act_journals = snap.library.national_journals
        act_e_journals = snap.library.international_e_journals

        vol_shortfall = max(0, req_volumes - act_vol)
        titles_shortfall = max(0, req_titles - act_titles)
        journal_shortfall = max(0, req_journals - act_journals)

        deficiencies: List[DeficiencyItem] = []
        if vol_shortfall > 0:
            deficiencies.append(DeficiencyItem(
                rule_key=rule_key,
                field_key="library.total_volumes",
                severity="MEDIUM",
                description=f"Library volume count ({act_vol}) is deficient by {vol_shortfall} (required: {req_volumes}).",
                recommended_action=f"Acquire at least {vol_shortfall} volumes across syllabus courses."
            ))

        if not act_e_journals:
            deficiencies.append(DeficiencyItem(
                rule_key=rule_key,
                field_key="library.international_e_journals",
                severity="MEDIUM",
                description="Mandatory subscription to international e-journal consortium (IEEE/ScienceDirect/Springer) is missing.",
                recommended_action="Subscribe to authorized digital e-journals consortium."
            ))

        status = "COMPLIANT" if (vol_shortfall == 0 and titles_shortfall == 0 and journal_shortfall == 0 and act_e_journals) else "DEFICIENT"

        explanation = (
            f"Library requirement for {divisions} divisions ({snap.course_duration_years} yrs): "
            f"Volumes: {act_vol} (req: {req_volumes}), Titles: {act_titles} (req: {req_titles}), "
            f"National Journals: {act_journals} (req: {req_journals}), "
            f"International e-Journals: {'Subscribed' if act_e_journals else 'Missing'}."
        )

        return ComplianceResultItem(
            rule_key=rule_key,
            rule_version=self.RULE_VERSION,
            status=status,
            severity=severity,
            required_value={
                "required_volumes": req_volumes,
                "required_titles": req_titles,
                "required_national_journals": req_journals,
                "international_e_journals_mandatory": req_e_journals
            },
            actual_value={
                "total_volumes": act_vol,
                "total_titles": act_titles,
                "national_journals": act_journals,
                "international_e_journals": act_e_journals
            },
            shortfall={
                "volumes_shortfall": vol_shortfall,
                "titles_shortfall": titles_shortfall,
                "national_journals_shortfall": journal_shortfall,
                "e_journals_missing": not act_e_journals
            },
            explanation=explanation,
            evidence_refs=["DOC-LIBRARY-ACCESSION-REGISTER", "DOC-E-JOURNAL-INVOICE"],
            evaluated_at=evaluated_at
        ), deficiencies

    # -------------------------------------------------------------------------
    # RULE 5: Statutory Safety & Divyangjan Barrier-Free Access (AICTE_RULE_SAFETY_05)
    # -------------------------------------------------------------------------
    def _evaluate_safety(self, snap: InstitutionInputSnapshot, evaluated_at: str) -> Tuple[ComplianceResultItem, List[DeficiencyItem]]:
        rule_key = "AICTE_RULE_SAFETY_05"
        severity = "CRITICAL"

        if not snap.safety_and_access:
            return ComplianceResultItem(
                rule_key=rule_key,
                rule_version=self.RULE_VERSION,
                status="DEFICIENT",
                severity=severity,
                required_value={"safety_data": "Mandatory safety certificates"},
                actual_value={"safety_data": None},
                shortfall={"missing_data": "Safety records missing"},
                explanation="No safety certificates or barrier-free infrastructure records provided.",
                evidence_refs=[],
                evaluated_at=evaluated_at
            ), [
                DeficiencyItem(
                    rule_key=rule_key,
                    field_key="safety_and_access",
                    severity=severity,
                    description="Mandatory Fire Safety NOC and Divyangjan accessibility data missing.",
                    recommended_action="Submit valid Fire Department NOC and accessibility compliance certificate."
                )
            ]

        sa = snap.safety_and_access
        deficiencies: List[DeficiencyItem] = []

        if not sa.fire_noc_valid:
            deficiencies.append(DeficiencyItem(
                rule_key=rule_key,
                field_key="safety_and_access.fire_noc_valid",
                severity="CRITICAL",
                description="Institution lacks a valid Fire Safety Certificate (NOC) issued by competent Fire Services.",
                recommended_action="Obtain and upload renewed Fire Safety Certificate immediately."
            ))

        if not sa.structural_stability_certified:
            deficiencies.append(DeficiencyItem(
                rule_key=rule_key,
                field_key="safety_and_access.structural_stability_certified",
                severity="CRITICAL",
                description="Structural Stability Certificate issued by a certified engineer is missing or unverified.",
                recommended_action="Commission certified structural stability audit."
            ))

        if not sa.barrier_free_ramps or not sa.disabled_friendly_toilets:
            deficiencies.append(DeficiencyItem(
                rule_key=rule_key,
                field_key="safety_and_access.divyangjan_facilities",
                severity="CRITICAL",
                description="Divyangjan barrier-free compliance failed (mandatory ramps <= 1:12 slope and accessible washrooms missing).",
                recommended_action="Construct compliant entrance ramps and accessible toilets pursuant to RPwD Act 2016."
            ))

        status = "COMPLIANT" if len(deficiencies) == 0 else "DEFICIENT"
        
        explanation = (
            f"Fire Safety NOC: {'Valid' if sa.fire_noc_valid else 'EXPIRED/MISSING'}. "
            f"Structural Stability: {'Certified' if sa.structural_stability_certified else 'MISSING'}. "
            f"Potable Water: {'Certified' if sa.potable_water_certified else 'Deficient'}. "
            f"Divyangjan Barrier-Free Ramps: {'Present' if sa.barrier_free_ramps else 'MISSING'}, "
            f"Lift: {'Operational' if sa.braille_enabled_lift else 'No'}, "
            f"Accessible Toilets: {'Available' if sa.disabled_friendly_toilets else 'MISSING'}."
        )

        return ComplianceResultItem(
            rule_key=rule_key,
            rule_version=self.RULE_VERSION,
            status=status,
            severity=severity,
            required_value={
                "fire_noc_valid": True,
                "structural_stability_certified": True,
                "potable_water_certified": True,
                "barrier_free_ramps": True,
                "disabled_friendly_toilets": True
            },
            actual_value={
                "fire_noc_valid": sa.fire_noc_valid,
                "fire_noc_expiry_date": sa.fire_noc_expiry_date,
                "structural_stability_certified": sa.structural_stability_certified,
                "potable_water_certified": sa.potable_water_certified,
                "barrier_free_ramps": sa.barrier_free_ramps,
                "braille_enabled_lift": sa.braille_enabled_lift,
                "disabled_friendly_toilets": sa.disabled_friendly_toilets
            },
            shortfall={
                "fire_safety_violation": not sa.fire_noc_valid,
                "structural_stability_violation": not sa.structural_stability_certified,
                "accessibility_violation": not (sa.barrier_free_ramps and sa.disabled_friendly_toilets)
            },
            explanation=explanation,
            evidence_refs=["DOC-FIRE-SAFETY-NOC", "DOC-STRUCTURAL-STABILITY-CERT", "DOC-WATER-TEST-REPORT"],
            evaluated_at=evaluated_at
        ), deficiencies

    # -------------------------------------------------------------------------
    # RULE 6: Mandatory Statutory Committees (AICTE_RULE_COMM_06)
    # -------------------------------------------------------------------------
    def _evaluate_committees(self, snap: InstitutionInputSnapshot, evaluated_at: str) -> Tuple[ComplianceResultItem, List[DeficiencyItem]]:
        rule_key = "AICTE_RULE_COMM_06"
        severity = "CRITICAL"

        if not snap.statutory_committees:
            return ComplianceResultItem(
                rule_key=rule_key,
                rule_version=self.RULE_VERSION,
                status="DEFICIENT",
                severity=severity,
                required_value={"committee_data": "Mandatory committee constitutions"},
                actual_value={"committee_data": None},
                shortfall={"missing_data": "Committee records missing"},
                explanation="No statutory committee data provided.",
                evidence_refs=[],
                evaluated_at=evaluated_at
            ), [
                DeficiencyItem(
                    rule_key=rule_key,
                    field_key="statutory_committees",
                    severity=severity,
                    description="Mandatory Anti-Ragging, ICC, and SGRC committee records missing.",
                    recommended_action="Submit committee constitution notifications and meeting minutes."
                )
            ]

        sc = snap.statutory_committees
        deficiencies: List[DeficiencyItem] = []

        if not (sc.anti_ragging_committee and sc.anti_ragging_squad):
            deficiencies.append(DeficiencyItem(
                rule_key=rule_key,
                field_key="statutory_committees.anti_ragging",
                severity="CRITICAL",
                description="Anti-Ragging Committee or Anti-Ragging Squad is not properly constituted.",
                recommended_action="Form Anti-Ragging Committee and Squad with external police, media, parent representation."
            ))

        if not (sc.internal_complaints_committee_icc and sc.icc_external_member):
            deficiencies.append(DeficiencyItem(
                rule_key=rule_key,
                field_key="statutory_committees.icc",
                severity="CRITICAL",
                description="Internal Complaints Committee (ICC/POSH) missing or lacks mandatory external NGO representative.",
                recommended_action="Reconstitute ICC with woman Presiding Officer and external NGO member pursuant to POSH Act 2013."
            ))

        if not (sc.student_grievance_redressal_committee and sc.ombudsman_appointed):
            deficiencies.append(DeficiencyItem(
                rule_key=rule_key,
                field_key="statutory_committees.sgrc_ombudsman",
                severity="CRITICAL",
                description="Student Grievance Redressal Committee (SGRC) or notified Ombudsman is missing.",
                recommended_action="Constitute SGRC and notify university-approved Ombudsman."
            ))

        status = "COMPLIANT" if len(deficiencies) == 0 else "DEFICIENT"

        explanation = (
            f"Anti-Ragging Committee/Squad: {'Active' if (sc.anti_ragging_committee and sc.anti_ragging_squad) else 'NON-COMPLIANT'}. "
            f"ICC (POSH) with External Member: {'Active' if (sc.internal_complaints_committee_icc and sc.icc_external_member) else 'NON-COMPLIANT'}. "
            f"SGRC & Ombudsman: {'Active' if (sc.student_grievance_redressal_committee and sc.ombudsman_appointed) else 'NON-COMPLIANT'}. "
            f"SC/ST Committee: {'Constituted' if sc.sc_st_committee else 'Pending'}."
        )

        return ComplianceResultItem(
            rule_key=rule_key,
            rule_version=self.RULE_VERSION,
            status=status,
            severity=severity,
            required_value={
                "anti_ragging_committee": True,
                "anti_ragging_squad": True,
                "internal_complaints_committee_icc": True,
                "icc_external_member": True,
                "student_grievance_redressal_committee": True,
                "ombudsman_appointed": True,
                "sc_st_committee": True
            },
            actual_value={
                "anti_ragging_committee": sc.anti_ragging_committee,
                "anti_ragging_squad": sc.anti_ragging_squad,
                "internal_complaints_committee_icc": sc.internal_complaints_committee_icc,
                "icc_external_member": sc.icc_external_member,
                "student_grievance_redressal_committee": sc.student_grievance_redressal_committee,
                "ombudsman_appointed": sc.ombudsman_appointed,
                "sc_st_committee": sc.sc_st_committee
            },
            shortfall={
                "anti_ragging_deficiency": not (sc.anti_ragging_committee and sc.anti_ragging_squad),
                "icc_deficiency": not (sc.internal_complaints_committee_icc and sc.icc_external_member),
                "sgrc_deficiency": not (sc.student_grievance_redressal_committee and sc.ombudsman_appointed),
                "sc_st_deficiency": not sc.sc_st_committee
            },
            explanation=explanation,
            evidence_refs=["DOC-ANTI-RAGGING-NOTIFICATION", "DOC-ICC-NOTIFICATION", "DOC-OMBUDSMAN-ORDER"],
            evaluated_at=evaluated_at
        ), deficiencies
