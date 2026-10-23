# AICTE SETU — Institutional Compliance Monitoring System

> **Self-Evaluation & Transparency Unit (SETU)**  
> *A modular, transparent, and deterministic compliance engine for AICTE Approval Process verification.*

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.14-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![Pydantic](https://img.shields.io/badge/Pydantic-V2-E92063.svg)](https://docs.pydantic.dev/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-red.svg)](https://www.sqlalchemy.org/)
[![Tests](https://img.shields.io/badge/Tests-Pytest%20Passing-success.svg)](https://docs.pytest.org/)

---

## 🏛️ Overview

**AICTE SETU** is an institutional compliance monitoring platform built for the **Smart India Hackathon (SIH)**. Under the All India Council for Technical Education (AICTE) regulations, technical colleges must satisfy strict statutory infrastructure, faculty, and academic norms for annual **Extension of Approval (EoA)** or intake expansion.

SETU replaces subjective manual scrutiny with a **deterministic, versioned Rule Engine** that:
1. Ingests institution-declared data and document-extracted snapshots.
2. Validates metrics mathematically against versioned regulatory thresholds.
3. Generates an instant, explainable **Deficiency Matrix** with exact shortfall quantities and corrective recommendations.

---

## 📜 The 6 Core AICTE Compliance Rules

Phase 0 implements and validates the **6 canonical statutory compliance rules** specified in the AICTE Approval Process Handbook (APH):

| # | Rule Key | Rule Name | Prescribed Regulatory Standard | Severity |
|---|---|---|---|---|
| **1** | `AICTE_RULE_FSR_01` | **Faculty-to-Student Ratio & Cadre** | **1:20** UG Engineering (**1:15** PG/Accredited); Cadre ratio **1:2:6** (Prof : Assoc Prof : Asst Prof); Ph.D. qualified regular Principal. | `CRITICAL` |
| **2** | `AICTE_RULE_AREA_02` | **Land & Built-Up Area Norms** | Land Area (Urban $\ge 2.5$ acres, Rural $\ge 7.5$ acres, Metro $\ge 1.5$ acres); Instructional carpet area $\ge 5.0\text{ m}^2/\text{student}$. | `HIGH` |
| **3** | `AICTE_RULE_COMP_LAB_03` | **Computing Infra & Bandwidth** | **1:4** Student-to-Computer ratio; dedicated leased line bandwidth ($100-500\text{ Mbps}$); licensed software suites. | `HIGH` |
| **4** | `AICTE_RULE_LIB_04` | **Library Resources & Consortium** | Min $\ge 100$ titles & $\ge 500$ volumes per division; national print journals & international digital e-journal consortium. | `MEDIUM` |
| **5** | `AICTE_RULE_SAFETY_05` | **Safety & Divyangjan Barrier-Free** | Valid State Fire Services NOC; structural stability certificate; RPwD Act compliant ramps ($\le 1:12$ slope), lift, & accessible washrooms. | `CRITICAL` |
| **6** | `AICTE_RULE_COMM_06` | **Mandatory Statutory Committees** | Anti-Ragging Committee & Squad; ICC/POSH with external member; SGRC & university-notified Ombudsman; SC/ST Committee. | `CRITICAL` |

📖 **Detailed Rule Specifications:** See [`docs/aicte_six_compliance_rules.md`](docs/aicte_six_compliance_rules.md) for formulas, parameters, and evidence requirements.

---

## 🏗️ Architecture & Module Structure

SETU is built as a **clean modular monolith**:

```text
college-compliance-monitoring-system/
├── docs/
│   └── aicte_six_compliance_rules.md    # Formal regulatory specifications for the 6 rules
├── backend/
│   ├── pytest.ini                       # Test configuration
│   ├── phase0_runner.py                 # Automated verification CLI runner
│   └── app/
│       ├── main.py                      # FastAPI App with CORS, Health & Dashboard routes
│       ├── core/
│       │   └── config.py                # App configuration & environment settings
│       ├── models/                      # SQLAlchemy 2.0 Relational Models
│       │   ├── base.py                  # Base, DB Engine & Session factory
│       │   ├── rule.py                  # Versioned Rules & Parameters
│       │   ├── institution.py           # Institution profiles
│       │   ├── application.py           # Applications & revisions
│       │   └── compliance.py            # ComplianceRun, Results, Deficiencies
│       ├── schemas/
│       │   └── compliance.py            # Pydantic V2 snapshot & result contracts
│       ├── services/
│       │   └── rule_engine.py           # Deterministic 6-Rule Evaluator Engine
│       ├── api/
│       │   ├── deps.py                  # DB dependency injection
│       │   └── routes/
│       │       └── compliance.py        # /api/compliance/rules & /check endpoints
│       └── static/
│           └── index.html               # Interactive dark-mode compliance workbench
├── run_phase0.py                        # Top-level runner shortcut
├── requirements.txt                     # Python dependencies
└── readme.md                            # Project documentation
```

---

## 🚀 Quickstart Guide

### 1. Installation
Clone the repository and install dependencies:
```bash
git clone https://github.com/Bhavay-bhatia/college-compliance-monitoring-system.git
cd college-compliance-monitoring-system
pip install -r requirements.txt
```

### 2. Run the Phase 0 Verification Runner
Run the automated test runner to evaluate sample compliant and deficient colleges:
```bash
python run_phase0.py
```

### 3. Run Unit Tests
Execute the pytest suite covering the deterministic engine:
```bash
cd backend
pytest -v
```

### 4. Start the Local Server & Interactive Dashboard
Launch the FastAPI server:
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```
- **Interactive UI Dashboard:** Open [http://localhost:8000/](http://localhost:8000/)
- **Swagger / OpenAPI Documentation:** Open [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📡 API Contract (Phase 0)

### 1. Health Check
`GET /api/health`
```json
{
  "status": "healthy",
  "service": "AICTE SETU Core API",
  "phase": "Phase 0 (Baseline Scaffolding & 6 Core Rules Engine)",
  "version": "1.0.0"
}
```

### 2. List the 6 Rules
`GET /api/compliance/rules`
Returns active regulatory metadata, severity levels, and APH references for the 6 core rules.

### 3. Run Self-Check Evaluation
`POST /api/compliance/check`

**Input Payload (`JSON`):**
```json
{
  "institution_code": "1-109283741",
  "academic_year": "2026-2027",
  "programme": "ENGINEERING_AND_TECHNOLOGY",
  "total_sanctioned_intake": 240,
  "course_duration_years": 4,
  "faculty": {
    "total_regular_faculty": 52,
    "professors": 6,
    "associate_professors": 12,
    "assistant_professors": 34,
    "principal": { "is_appointed": true, "phd_qualified": true }
  },
  "infrastructure": { "land_area_acres": 3.2, "instructional_area_sqm": 5100.0 },
  "computing": { "student_terminals": 255, "internet_bandwidth_mbps": 500.0 },
  "library": { "total_volumes": 12800, "total_titles": 2300, "international_e_journals": true },
  "safety_and_access": { "fire_noc_valid": true, "barrier_free_ramps": true },
  "statutory_committees": { "anti_ragging_committee": true, "internal_complaints_committee_icc": true }
}
```

**Response Output (`JSON`):**
```json
{
  "institution_code": "1-109283741",
  "overall_status": "COMPLIANT",
  "total_rules_evaluated": 6,
  "compliant_rules_count": 6,
  "deficient_rules_count": 0,
  "results": [ ... ],
  "deficiencies": [ ]
}
```

---

## 🛠️ Next Steps (Roadmap)
- **Phase 1:** Authentication, RBAC (College Admin vs Scrutiny Officer), and Revision Tracking.
- **Phase 2:** Document AI & OCR Pipeline (PaddleOCR parsing of Land Deeds, Fire NOCs, and Faculty Rosters).
- **Phase 3:** Compliance Drift Monitoring and Cross-College Faculty Overlap Detection.
