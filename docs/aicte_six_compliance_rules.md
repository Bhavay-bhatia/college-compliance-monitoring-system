# AICTE SETU — Core 6 Statutory Compliance Rules Specification

**Document Version:** 1.0  
**Regulatory Baseline:** AICTE Approval Process Handbook (APH)  
**System:** AICTE SETU (Self-Evaluation & Transparency Unit)  
**Target:** Automated, Deterministic Institutional Compliance & Deficiency Evaluation Engine  

---

## Executive Summary

Under the AICTE Approval Process regulations, technical institutions (Engineering & Technology, Management, MCA, Pharmacy, Architecture, Planning) must satisfy mandatory statutory norms to obtain initial approval, annual Extension of Approval (EoA), or intake expansion. 

AICTE SETU implements a **deterministic, versioned Rule Engine** that assesses institutional applications against these norms. Each rule processes a verified snapshot of institutional data, detects discrepancies, calculates exact shortfalls, and outputs structured deficiency statements backed by evidence citations.

This document formally defines the **6 Core Compliance Rules** that form the baseline of the Phase 0 Rule Engine.

---

## 1. Rule Matrix Summary

| # | Rule Key | Rule Name | Regulatory Standard | Severity | Primary Parameters |
|---|----------|-----------|---------------------|----------|-------------------|
| **1** | `AICTE_RULE_FSR_01` | Faculty-to-Student Ratio & Cadre Distribution | APH Norms (1:20 UG Engg, 1:15 PG/Accredited, 1:2:6 Cadre) | **CRITICAL** | Total Approved Intake, Regular Faculty Count, Cadre Breakdown, Qualified Principal |
| **2** | `AICTE_RULE_AREA_02` | Instructional & Built-Up Area Norms | Carpet area per division/student (Classrooms, Labs, Workshops) | **HIGH** | Land Area (acres), Instructional Carpet Area (sq.m), Admin & Amenities Area |
| **3** | `AICTE_RULE_COMP_LAB_03` | Student-to-Computer Ratio & Computing Infrastructure | 1:4 Student-Computer Ratio (Engg), Min Bandwidth & Licences | **HIGH** | Dedicated Student Terminals, Legal Software Bundles, Internet Bandwidth (Mbps) |
| **4** | `AICTE_RULE_LIB_04` | Library Resources, Titles & Consortium Subscriptions | Min Volumes & Titles per Programme + National/International Journals | **MEDIUM** | Book Volumes, Book Titles, Journal Subscriptions (Print + e-Journals), Digital Terminals |
| **5** | `AICTE_RULE_SAFETY_05` | Statutory Safety & Divyangjan Barrier-Free Access | Fire Safety NOC, Structural Stability, Barrier-Free Inclusivity | **CRITICAL** | Valid Fire NOC, Municipal Occupancy, Ramps/Lifts, Disabled-Friendly Toilets |
| **6** | `AICTE_RULE_COMM_06` | Statutory Oversight & Redressal Committees | Supreme Court & UGC/AICTE Mandated Committees | **CRITICAL** | Anti-Ragging Committee/Squad, ICC (POSH), SGRC & Ombudsman, SC/ST Committee |

---

## 2. Detailed Rule Specifications

```
                              ┌──────────────────────────────────┐
                              │     AICTE SETU RULE ENGINE       │
                              └─────────────────┬────────────────┘
                                                │
       ┌──────────────────┬─────────────────────┼────────────────────┬──────────────────┐
       ▼                  ▼                     ▼                    ▼                  ▼
┌─────────────┐    ┌─────────────┐       ┌─────────────┐      ┌─────────────┐    ┌─────────────┐
│ 01. FSR &   │    │ 02. Land &  │       │ 03. Comp &  │      │ 04. Library │    │ 05. Safety  │ (and 06. Committees)
│ Cadre Ratio │    │ Built Area  │       │ Lab Facility│      │ Resources   │    │ & Divyangjan│
└─────────────┘    └─────────────┘       └─────────────┘      └─────────────┘    └─────────────┘
```

---

### Rule 1: Faculty-to-Student Ratio (FSR) & Cadre Distribution
- **Rule Key:** `AICTE_RULE_FSR_01`
- **Rule Version:** `2026.1`
- **Statutory Authority:** AICTE APH Appendix 7 & Gazette Regulations on Faculty Norms.
- **Severity:** `CRITICAL` (Deficiency directly restricts EoA or enforces intake reduction).

#### 1. Description
Every institution must maintain adequate full-time regular faculty members based on sanctioned student enrollment, along with a balanced academic cadre ratio and a designated full-time qualified Principal/Director.

#### 2. Evaluation Logic & Mathematical Formulas
1. **Total Effective Student Strength ($S$):**
   $$S = \sum (\text{Sanctioned Intake per Year} \times \text{Duration of Programme in Years})$$
2. **Required Faculty ($F_{\text{req}}$):**
   $$F_{\text{req}} = \lceil \frac{S}{\text{Prescribed Ratio}} \rceil$$
   *(Standard ratio: 1:20 for Undergraduate Engineering & Technology; 1:15 for PG / Autonomous / Accredited).*
3. **Cadre Distribution Norms ($1 : 2 : 6$):**
   - **Professors ($P_{\text{req}}$):** $\lceil \frac{F_{\text{req}}}{9} \times 1 \rceil$
   - **Associate Professors ($AP_{\text{req}}$):** $\lceil \frac{F_{\text{req}}}{9} \times 2 \rceil$
   - **Assistant Professors ($Lect_{\text{req}}$):** $F_{\text{req}} - (P_{\text{req}} + AP_{\text{req}})$
4. **Mandatory Principal:**
   - Principal must be appointed, Ph.D. qualified, and active.

#### 3. Decision Matrix
- **COMPLIANT:** $F_{\text{actual}} \ge F_{\text{req}}$ AND Cadre shortfalls $\le 20\%$ AND Qualified Principal present.
- **DEFICIENT:** $F_{\text{actual}} < F_{\text{req}}$ OR Principal missing/unqualified.
- **NEEDS_REVIEW:** Document extraction pending or faculty overlap detected across institutions.

---

### Rule 2: Land & Instructional / Administrative Built-Up Area
- **Rule Key:** `AICTE_RULE_AREA_02`
- **Rule Version:** `2026.1`
- **Statutory Authority:** AICTE APH Appendix 4 (Norms for Land and Built-Up Area).
- **Severity:** `HIGH`

#### 1. Description
Institutions must possess contiguous land (free from encumbrances) and sufficient built-up carpet area for instructional activities, laboratories, workshops, administration, and amenities.

#### 2. Evaluation Logic & Mathematical Formulas
1. **Minimum Land Area Requirement:**
   - **Mega / Metro City:** $\ge 1.5$ to $2.5$ contiguous acres.
   - **Urban Area:** $\ge 2.5$ contiguous acres.
   - **Rural Area:** $\ge 7.5$ contiguous acres.
2. **Instructional Area Requirement ($A_{\text{inst}}$):**
   - Classrooms: Minimum 66 sq.m per room; 0.75 classrooms per division.
   - Tutorial Rooms: Minimum 33 sq.m per room.
   - Laboratories / Workshops: Minimum 66 sq.m for general labs; 200 sq.m for central workshop.
   - Total instructional area must meet or exceed $\text{Total Divisions} \times \text{Prescribed Area Threshold}$.
3. **Administrative & Amenities Area:**
   - Principal's Cabin ($\ge 30$ sq.m), Board Room, Faculty Cabins, Central Exam Cell, Boys/Girls Common Rooms, First Aid Room.

#### 3. Shortfall Calculation
$$\text{Area Shortfall} = \max(0, A_{\text{required}} - A_{\text{actual}})$$

---

### Rule 3: Student-to-Computer Ratio & Laboratory Computing Infrastructure
- **Rule Key:** `AICTE_RULE_COMP_LAB_03`
- **Rule Version:** `2026.1`
- **Statutory Authority:** AICTE APH Appendix 5 (Norms for Books, Library, Computers & Software).
- **Severity:** `HIGH`

#### 1. Description
Institutions must provide modern computing infrastructure with genuine software licenses, structured networking, and high-speed dedicated internet bandwidth to support technical coursework.

#### 2. Evaluation Logic & Mathematical Formulas
1. **Student-to-Computer Ratio (SCR):**
   - Minimum 1 operational desktop/laptop for every 4 enrolled technical students ($1:4$ ratio).
   - Maximum allowable deficit: $0\%$.
2. **Dedicated Internet Bandwidth ($BW$):**
   - For total enrollment up to 300: $\ge 100\text{ Mbps}$ dedicated line.
   - For enrollment between 301 and 600: $\ge 300\text{ Mbps}$.
   - For enrollment $> 600$: $\ge 500\text{ Mbps}$ to $1\text{ Gbps}$.
3. **Legal Software Suites:**
   - Minimum 3 System Software titles (licensed OS / enterprise Linux).
   - Minimum 20 Application Software packages relevant to curriculum.

#### 3. Decision Matrix
- **COMPLIANT:** Computer count $\ge \lceil S / 4 \rceil$ AND Bandwidth $\ge BW_{\text{req}}$ AND Software licenses confirmed.
- **DEFICIENT:** Computer shortfalls $> 0$ OR Bandwidth $< BW_{\text{req}}$.

---

### Rule 4: Library Resources, Titles & Consortium Subscriptions
- **Rule Key:** `AICTE_RULE_LIB_04`
- **Rule Version:** `2026.1`
- **Statutory Authority:** AICTE APH Appendix 5.
- **Severity:** `MEDIUM`

#### 1. Description
The Central Library must maintain a growing collection of titles and volumes of reference textbooks, indexed national print journals, subscribed international e-journals (e.g., IEEE, Elsevier, Springer), and multimedia terminals.

#### 2. Evaluation Logic & Mathematical Formulas
1. **Book Titles ($T_{\text{req}}$) & Volumes ($V_{\text{req}}$):**
   - Minimum Titles: $\ge 100$ titles per division of intake.
   - Minimum Volumes: $\ge 500$ volumes per division of intake.
   - Annual addition requirement: Minimum 50 titles and 250 volumes added annually.
2. **Journal Subscriptions ($J_{\text{req}}$):**
   - Minimum 6 to 12 national print journals per branch.
   - Subscriptions to recognized digital e-journals consortium (DELNET, IEEE Xplore, ScienceDirect).
3. **Digital Library Terminals:**
   - Minimum 10 to 20 dedicated multimedia workstations connected to institutional intranet.

---

### Rule 5: Statutory Safety & Divyangjan Barrier-Free Accessibility
- **Rule Key:** `AICTE_RULE_SAFETY_05`
- **Rule Version:** `2026.1`
- **Statutory Authority:** Rights of Persons with Disabilities (RPwD) Act 2016, National Building Code (NBC), and State Fire Safety Directives.
- **Severity:** `CRITICAL`

#### 1. Description
Zero-tolerance verification of building safety, structural stability, fire hazard mitigation, safe potable drinking water, and unconditional physical accessibility for Divyangjan (differently-abled students/staff).

#### 2. Evaluation Checklist & Criteria
1. **Fire Safety Certificate (NOC):**
   - Must be valid, issued by the competent State Fire Services Authority, and cover all active academic blocks. Expired certificate results in immediate deficiency.
2. **Structural Stability Certificate:**
   - Issued by a government-approved certified structural engineer, valid for the campus buildings.
3. **Barrier-Free Divyangjan Infrastructure:**
   - Standard ramps with handrails (slope $\le 1:12$) at every academic entry point.
   - Operational elevator / lift with audio announcements and Braille keypads.
   - At least 1 dedicated accessible toilet on each academic floor.
4. **Potable Drinking Water & Sanitation:**
   - Valid water potability lab test certificate issued within the past 12 months.
   - Separate washroom blocks for male, female, and transgender students/staff.

---

### Rule 6: Mandatory Statutory Committees & Redressal Mechanisms
- **Rule Key:** `AICTE_RULE_COMM_06`
- **Rule Version:** `2026.1`
- **Statutory Authority:** Supreme Court Directives, UGC Regulations 2009, POSH Act 2013, AICTE (Establishment of Mechanism for Grievance Redressal) Regulations.
- **Severity:** `CRITICAL`

#### 1. Description
Institutions must formally notify, constitute, and operate 4 statutory oversight committees with active memberships, regular meetings, and public grievance portals.

#### 2. Statutory Committees Evaluated
1. **Anti-Ragging Committee (ARC) & Squad:**
   - Formed under AICTE Anti-Ragging Regulations.
   - Must include Representatives of Civil/Police Administration, Local Media, NGO, Faculty, Parents, and Freshers.
   - Emergency contact numbers & 24x7 helpline displayed on institutional website and notice boards.
2. **Internal Complaints Committee (ICC) / POSH:**
   - Formed pursuant to the Sexual Harassment of Women at Workplace (Prevention, Prohibition and Redressal) Act, 2013.
   - Presiding Officer must be a senior female faculty member ($\ge 50\%$ female representation overall).
   - At least one external member from an NGO or legal association committed to women's causes.
3. **Student Grievance Redressal Committee (SGRC) & Ombudsman:**
   - SGRC constituted with Principal as Chairperson and representative student member.
   - Formal appointment and notification of University/AICTE Ombudsman.
4. **Committee for SC/ST (Prevention of Atrocities):**
   - Formed as per Scheduled Castes and Scheduled Tribes (Prevention of Atrocities) Act.

#### 3. Decision Matrix
- **COMPLIANT:** All 4 committees formally notified with approved minutes and external representation.
- **DEFICIENT:** Any committee missing, lapsed, or lacking mandatory external/female representation.

---

## 3. Data Schema & Rule Engine I/O Contract

### 3.1 Input Snapshot Schema (`JSONB`)

```json
{
  "institution_code": "1-109283741",
  "academic_year": "2026-2027",
  "programme": "ENGINEERING_AND_TECHNOLOGY",
  "level": "UG",
  "location_type": "URBAN",
  "total_sanctioned_intake": 240,
  "course_duration_years": 4,
  "faculty": {
    "total_regular_faculty": 52,
    "professors": 6,
    "associate_professors": 12,
    "assistant_professors": 34,
    "principal": {
      "is_appointed": true,
      "phd_qualified": true,
      "experience_years": 18
    }
  },
  "infrastructure": {
    "land_area_acres": 3.2,
    "instructional_area_sqm": 7800.0,
    "administrative_area_sqm": 1200.0,
    "amenities_area_sqm": 950.0
  },
  "computing": {
    "student_terminals": 260,
    "internet_bandwidth_mbps": 500,
    "system_software_count": 5,
    "application_software_count": 28
  },
  "library": {
    "total_volumes": 12500,
    "total_titles": 2200,
    "national_journals": 18,
    "international_e_journals": true,
    "multimedia_terminals": 15
  },
  "safety_and_access": {
    "fire_noc_valid": true,
    "fire_noc_expiry_date": "2027-04-15",
    "structural_stability_certified": true,
    "potable_water_certified": true,
    "barrier_free_ramps": true,
    "braille_enabled_lift": true,
    "disabled_friendly_toilets": true
  },
  "statutory_committees": {
    "anti_ragging_committee": true,
    "anti_ragging_squad": true,
    "internal_complaints_committee_icc": true,
    "icc_external_member": true,
    "student_grievance_redressal_committee": true,
    "ombudsman_appointed": true,
    "sc_st_committee": true
  }
}
```

### 3.2 Output Result Item Schema (`JSONB`)

```json
{
  "rule_key": "AICTE_RULE_FSR_01",
  "rule_version": "2026.1",
  "status": "COMPLIANT",
  "severity": "CRITICAL",
  "required_value": {
    "minimum_faculty": 48,
    "cadre_professors": 6,
    "cadre_associate_professors": 11,
    "principal_required": true
  },
  "actual_value": {
    "total_faculty": 52,
    "professors": 6,
    "associate_professors": 12,
    "has_qualified_principal": true
  },
  "shortfall": {
    "faculty_shortfall": 0,
    "professor_shortfall": 0,
    "associate_prof_shortfall": 0
  },
  "explanation": "Faculty strength of 52 exceeds the minimum required 48 (1:20 ratio for 960 total students). Cadre balance and qualified principal are satisfied.",
  "evidence_refs": ["DOC-FAC-ROSTER-2026", "DOC-PRIN-PHD-DEGREE"],
  "evaluated_at": "2026-10-23T12:00:00Z"
}
```

---

## 4. Lifecycle & Versioning Strategy

1. **Immutable Rule Versions:** When AICTE amends the Approval Process Handbook, a new `rule_version` record is staged in `DRAFT` status and reviewed by Rule Admins.
2. **Effective Dating:** Evaluations load the rule version whose `effective_from <= evaluated_at < effective_to`.
3. **No Retrospective Penalties:** Historical compliance audits use the version in effect during that academic cycle.
4. **Deterministic Calculation:** No arbitrary Python `eval()` or unconstrained LLM heuristics are allowed in compliance verdict calculations.
