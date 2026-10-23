# AICTE SETU — Institutional Compliance & Approval Portal

> **Self-Evaluation & Transparency Unit (SETU)**  
> *Ministry of Education, Government of India | Regulatory Baseline: AICTE Approval Process Handbook (APH) Norms 2026.1*

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.14-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![Pydantic](https://img.shields.io/badge/Pydantic-V2-E92063.svg)](https://docs.pydantic.dev/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-red.svg)](https://www.sqlalchemy.org/)
[![Tests](https://img.shields.io/badge/Tests-7%2F7%20Pytest%20Passing-success.svg)](https://docs.pytest.org/)

---

## 🏛️ Executive Summary

**AICTE SETU** is a national-scale institutional compliance monitoring and governance platform built for the **Smart India Hackathon (SIH)**. Under the statutory mandates of the All India Council for Technical Education (AICTE), colleges must satisfy strict statutory infrastructure, faculty cadre, computing, safety, and oversight committee norms to obtain annual **Extension of Approval (EoA)** or intake expansion.

SETU replaces subjective inspection with an end-to-end, automated digital platform featuring:
1. **Deterministic Statutory Rule Engine:** Mathematical evaluation of college applications against the 6 core AICTE statutory rules with exact shortfall formulas and corrective actions.
2. **Multi-Role RBAC Governance:** Separation of concerns between **College Admins** (who lodge applications & rectify deficits), **Scrutiny Officers** (who review & issue decisions), and **National Directorate** (system oversight).
3. **Application Lifecycle & Revision Diff Tracking:** Immutable version tracking (`v1`, `v2`, `v3`...) with automated before/after field diff auditing.
4. **Document AI & OCR Verification:** Automated SHA-256 fingerprinting, certificate number parsing, expiry detection, and fraud rejection for statutory certificates (Fire NOC, Land Deeds, Structural Stability).
5. **Cross-College Ghost Faculty Overlap Detection:** National deduplication engine using hashed Aadhaar & PAN fingerprints to detect dual-employment fraud where faculty claim concurrent full-time salaries across institutions.
6. **Government Dark-Theme Web Portal:** Official Ministry of Education / AICTE dark interface with multi-role switcher, live national analytics, interactive self-check workbench, and printable Gazette EoA orders.

---

## 📜 The 6 Core AICTE Statutory Rules

| # | Rule Key | Rule Name | Prescribed Regulatory Standard | Severity |
|---|---|---|---|---|
| **1** | `AICTE_RULE_FSR_01` | **Faculty-to-Student Ratio & Cadre** | **1:20** UG Engineering (**1:15** PG/Accredited); Cadre ratio **1:2:6** (Prof : Assoc Prof : Asst Prof); Ph.D. qualified regular Principal. | `CRITICAL` |
| **2** | `AICTE_RULE_AREA_02` | **Land & Built-Up Area Norms** | Land Area (Urban $\ge 2.5$ acres, Rural $\ge 7.5$ acres, Metro $\ge 1.5$ acres); Instructional carpet area $\ge 5.0\text{ m}^2/\text{student}$. | `HIGH` |
| **3** | `AICTE_RULE_COMP_LAB_03` | **Computing Infra & Bandwidth** | **1:4** Student-to-Computer ratio; dedicated leased line bandwidth ($100-500\text{ Mbps}$); licensed software suites. | `HIGH` |
| **4** | `AICTE_RULE_LIB_04` | **Library Resources & Consortium** | Min $\ge 100$ titles & $\ge 500$ volumes per division; national print journals & international digital e-journal consortium. | `MEDIUM` |
| **5** | `AICTE_RULE_SAFETY_05` | **Safety & Divyangjan Barrier-Free** | Valid State Fire Services NOC; structural stability certificate; RPwD Act compliant ramps ($\le 1:12$ slope), lift, & accessible washrooms. | `CRITICAL` |
| **6** | `AICTE_RULE_COMM_06` | **Mandatory Statutory Committees** | Anti-Ragging Committee & Squad; ICC/POSH with external member; SGRC & university-notified Ombudsman; SC/ST Committee. | `CRITICAL` |

---

## 🚀 Quickstart & Verification

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Full End-to-End System Demonstration
```bash
python run_full_system.py
```
*Executes the complete system journey in the terminal: runs the rule engine, performs Document AI certificate verification, triggers cross-college ghost faculty deduplication, and generates national intelligence metrics.*

### 3. Run Pytest Suite
```bash
cd backend
pytest -v
```
*All 7 unit and integration test suites pass in ~3 seconds.*

### 4. Launch the Government Dark-Themed Web Portal
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```
- **Web Portal:** Open [http://localhost:8000/](http://localhost:8000/)
- **Swagger API Docs:** Open [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🎨 Web Portal Features (Government Dark Theme)

- **Official Masthead & National Tricolor Accent:** Authoritative Ministry of Education & AICTE branding with emblem shield, Ashoka chakra blue/gold highlights, and sleek dark slate glassmorphism.
- **Interactive Multi-Role Switcher:** Switch live between:
  - 🏛️ **National Directorate (HQ)**: High-level KPI cards, pass rates, and regional compliance distribution.
  - 🏫 **College Admin Portal**: Interactive parameter sliders, instant 6-rule compliance audit, and shortfall cards.
  - 🔍 **Scrutiny Officer Cell**: Application review queue, immutable revision timeline (`v1`, `v2`), and audit diffs.
  - 🤖 **Document AI Chamber**: OCR parsing of Fire NOCs, structural stability reports, and expired document rejection.
  - 🕵️ **Vigilance Unit**: Cross-college faculty deduplication table identifying ghost professors drawing multiple salaries.
  - 📜 **Official Gazette Order**: Printable Extension of Approval (EoA) clearance letter with digital seal.

---

## 📂 Architecture & Directory Structure

```text
college-compliance-monitoring-system/
├── docs/
│   ├── aicte_six_compliance_rules.md    # Detailed regulatory formulas for the 6 rules
│   └── phase1_auth_rbac_revisions.md    # Multi-role RBAC & revision audit specs
├── backend/
│   ├── pytest.ini                       # Test configuration
│   ├── phase0_runner.py                 # Phase 0 Rule Engine CLI runner
│   ├── phase1_runner.py                 # Phase 1 RBAC & Revision CLI runner
│   ├── tests/
│   │   ├── test_rule_engine.py          # Rule engine mathematical tests
│   │   ├── test_phase1_auth_revisions.py# Auth, RBAC & Revision tests
│   │   └── test_complete_system.py      # Document AI, Faculty Fraud & Analytics tests
│   └── app/
│       ├── main.py                      # FastAPI App registering all routes & static UI
│       ├── core/
│       │   ├── config.py                # Environment configurations
│       │   └── security.py              # Bcrypt & PyJWT token utilities
│       ├── models/                      # SQLAlchemy 2.0 Relational Models
│       │   ├── base.py                  # Database engine & base
│       │   ├── user.py                  # User & UserRole models
│       │   ├── institution.py           # Institution profiles
│       │   ├── application.py           # Applications & ApplicationRevision audit
│       │   ├── rule.py                  # Versioned Rules & Parameters
│       │   ├── compliance.py            # ComplianceRun, Results, Deficiencies
│       │   ├── document.py              # DocumentVerification model (Document AI)
│       │   └── faculty.py               # FacultyMember model (Cross-College Overlap)
│       ├── schemas/                     # Pydantic V2 validation schemas
│       ├── services/
│       │   └── rule_engine.py           # Deterministic 6-Rule Evaluator Engine
│       ├── api/
│       │   ├── deps.py                  # RBAC security dependency guards
│       │   └── routes/
│       │       ├── auth.py              # /api/auth/register, /login, /me
│       │       ├── applications.py      # /api/applications/ CRUD, submit, rectify, review
│       │       ├── compliance.py        # /api/compliance/rules & /check endpoints
│       │       ├── documents.py         # /api/documents/verify (OCR extraction)
│       │       ├── faculty.py           # /api/faculty/overlap-audit (Ghost teacher audit)
│       │       └── analytics.py         # /api/analytics/national-summary & reports
│       └── static/
│           └── index.html               # Government Dark Theme Compliance Workbench
├── run_phase0.py                        # Top-level Phase 0 runner
├── run_phase1.py                        # Top-level Phase 1 runner
├── run_full_system.py                   # Top-level Full System runner
├── requirements.txt                     # Python dependencies
└── readme.md                            # Comprehensive project documentation
```
