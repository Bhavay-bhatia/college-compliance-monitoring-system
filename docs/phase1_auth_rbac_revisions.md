# AICTE SETU — Phase 1: Authentication, RBAC & Application Revision Tracking

**Document Version:** 1.0  
**Phase:** Phase 1  
**Regulatory Baseline:** AICTE Approval Process Regulations  
**Components:** User Management, JWT Authentication, Multi-Role Access Control (RBAC), Application State Machine, Immutable Revision Auditing  

---

## 1. Overview & Objectives

In **Phase 0**, the core deterministic 6-rule compliance engine was built to mathematically evaluate snapshots and output deficiency statements.

**Phase 1** introduces the operational multi-tenant workflow layer that wraps the rule engine:
1. **Multi-Role Authentication & Access Control:**
   - **`COLLEGE_ADMIN`**: Institutional representative permitted to create draft applications, submit applications for official review, view institutional deficiencies, and submit rectifications.
   - **`SCRUTINY_OFFICER`**: AICTE / Regional Directorate official permitted to review applications across colleges, audit historical revisions, issue deficiency notices, and formally approve/reject applications.
   - **`SUPER_ADMIN`**: System & AICTE HQ administrative oversight.
2. **Deterministic State Machine & Lifecycle:**
   - `DRAFT` ➔ `SUBMITTED` ➔ `UNDER_REVIEW` ➔ `DEFICIENCY_ISSUED` ➔ `RECTIFIED` ➔ `APPROVED` / `REJECTED`.
3. **Immutable Revision Tracking & Audit Trail:**
   - Every submission and rectification automatically produces a new version (`v1`, `v2`, `v3`...).
   - Each revision captures an immutable copy of the snapshot, the author ID, the timestamp, the human reason for change, the auto-computed field-level diff, and the engine evaluation summary.

---

## 2. RBAC Permission Matrix

| Operation | Endpoint | College Admin | Scrutiny Officer | Super Admin |
|---|---|:---:|:---:|:---:|
| **Register / Login** | `POST /api/auth/register`, `/login` | ✅ | ✅ | ✅ |
| **View Self Profile** | `GET /api/auth/me` | ✅ | ✅ | ✅ |
| **List Applications** | `GET /api/applications/` | Own College Only | All Colleges | All Colleges |
| **Create Application Draft** | `POST /api/applications/` | ✅ | ❌ | ❌ |
| **Submit Application (v1)** | `POST /api/applications/{id}/submit` | ✅ | ❌ | ❌ |
| **Rectify Deficiencies (v2+)** | `POST /api/applications/{id}/rectify` | ✅ | ❌ | ❌ |
| **Audit Application Revisions**| `GET /api/applications/{id}` | Own College Only | ✅ | ✅ |
| **Officer Review & Decision** | `POST /api/applications/{id}/review` | ❌ | ✅ | ✅ |

---

## 3. Data Schema & Models

```
┌─────────────────┐       1:N       ┌─────────────────────┐
│   Institution   ├────────────────►│        User         │
└────────┬────────┘                 └──────────┬──────────┘
         │                                     │
         │ 1:N                                 │ 1:N
         ▼                                     ▼
┌─────────────────┐       1:N       ┌─────────────────────┐
│   Application   ├────────────────►│ ApplicationRevision │
└────────┬────────┘                 └─────────────────────┘
         │
         │ 1:N
         ▼
┌─────────────────┐       1:N       ┌─────────────────────┐
│  ComplianceRun  ├────────────────►│  ComplianceResult   │
└─────────────────┘                 └──────────┬──────────┘
                                               │ 1:N
                                               ▼
                                    ┌─────────────────────┐
                                    │     Deficiency      │
                                    └─────────────────────┘
```

### 3.1 User Model (`users`)
- `id`: UUID (Primary Key)
- `email`: Indexed Unique Email
- `hashed_password`: Bcrypt encrypted password
- `full_name`: Official's or Admin's Name
- `role`: `COLLEGE_ADMIN` | `SCRUTINY_OFFICER` | `SUPER_ADMIN`
- `institution_id`: Foreign Key (`institutions.id`, optional for officers)
- `is_active`: Boolean flag

### 3.2 Application Revision Model (`application_revisions`)
- `id`: UUID (Primary Key)
- `application_id`: Foreign Key (`applications.id`)
- `revision_number`: Sequential integer (`1, 2, 3...`)
- `author_id`: Foreign Key (`users.id`)
- `change_summary`: Text description of changes made
- `snapshot_data`: JSONB representation of the complete institutional snapshot
- `changed_fields`: JSONB containing before/after diff for modified fields
- `compliance_summary`: JSONB containing evaluation verdict and metric totals
- `created_at`: UTC timestamp

---

## 4. API Endpoints

### 4.1 Auth Endpoints
- `POST /api/auth/register`:
  Registers a new user. For `COLLEGE_ADMIN`, auto-provisions or links an institution code.
- `POST /api/auth/login`:
  Authenticates with email and password, returning a signed JWT Bearer Token.
- `GET /api/auth/me`:
  Returns the authenticated user's credentials and institution affiliation.

### 4.2 Application Endpoints
- `GET /api/applications/`:
  Lists applications (filtered by college affiliation for College Admins).
- `POST /api/applications/`:
  Creates an initial draft application and stages Revision 1.
- `POST /api/applications/{id}/submit`:
  College Admin submits draft. Engine runs automated evaluation and flags open deficiencies.
- `POST /api/applications/{id}/rectify`:
  College Admin rectifies shortfalls, generates Revision 2+, calculates snapshot diff, and re-triggers compliance evaluation.
- `POST /api/applications/{id}/review`:
  Scrutiny Officer review (`APPROVE`, `REJECT`, `ISSUE_DEFICIENCY`) with official remarks.

---

## 5. Verification & Testing

### 1. Run the Automated Phase 1 CLI Demo
```bash
python run_phase1.py
```
This script exercises the full end-to-end lifecycle:
1. College Admin and Scrutiny Officer registration & JWT issuance.
2. Draft Application creation (Revision 1 with deliberate deficiency).
3. Submission and automated deficiency detection.
4. RBAC security check preventing unauthorized approval.
5. Deficiency rectification and Revision 2 generation with automated field diff.
6. Scrutiny Officer review and final approval.

### 2. Run Test Suite
```bash
cd backend
pytest -v
```
All unit tests in [`tests/test_rule_engine.py`](file:///c:/Users/bhava/OneDrive/styxx07/SIH/college-compliance-monitoring-system/backend/tests/test_rule_engine.py) and [`tests/test_phase1_auth_revisions.py`](file:///c:/Users/bhava/OneDrive/styxx07/SIH/college-compliance-monitoring-system/backend/tests/test_phase1_auth_revisions.py) run and pass in ~3 seconds.
