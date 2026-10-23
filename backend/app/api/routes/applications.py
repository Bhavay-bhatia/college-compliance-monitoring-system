from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user, require_role
from app.models.user import User, UserRole
from app.models.institution import Institution
from app.models.application import Application, ApplicationRevision, ApplicationStatus
from app.models.compliance import ComplianceRun, ComplianceResult, Deficiency
from app.models.base import utc_now
from app.schemas.application import (
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationReview,
    ApplicationListItem,
    ApplicationDetailOut,
    ApplicationRevisionOut
)
from app.schemas.compliance import InstitutionInputSnapshot
from app.services.rule_engine import AICTERuleEngine

router = APIRouter(prefix="/applications", tags=["Institutional Applications & Revisions"])
rule_engine = AICTERuleEngine()

def calculate_snapshot_diff(old_snap: Dict[str, Any], new_snap: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate key-level diff between two snapshots."""
    diff = {}
    all_keys = set(old_snap.keys()).union(set(new_snap.keys()))
    for k in all_keys:
        v_old = old_snap.get(k)
        v_new = new_snap.get(k)
        if v_old != v_new:
            diff[k] = {"before": v_old, "after": v_new}
    return diff

def serialize_application_summary(app: Application) -> ApplicationListItem:
    return ApplicationListItem(
        id=app.id,
        institution_id=app.institution_id,
        institution_name=app.institution.name if app.institution else None,
        institution_code=app.institution.institution_code if app.institution else None,
        application_type=app.application_type,
        programme=app.programme,
        academic_year=app.academic_year,
        declared_student_intake=app.declared_student_intake,
        status=app.status,
        current_version=app.current_version,
        compliance_status=app.compliance_status,
        submitted_at=app.submitted_at,
        approved_at=app.approved_at,
        created_at=app.created_at,
        updated_at=app.updated_at
    )

@router.get("/", response_model=List[ApplicationListItem], summary="List Applications (Role Filtered)")
def list_applications(
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns list of applications.
    - College Admin: Only sees applications belonging to their institution.
    - Scrutiny Officer / Admin: Sees applications across all institutions.
    """
    query = db.query(Application)

    if current_user.role == UserRole.COLLEGE_ADMIN:
        if not current_user.institution_id:
            return []
        query = query.filter(Application.institution_id == current_user.institution_id)

    if status_filter:
        query = query.filter(Application.status == status_filter)

    applications = query.order_by(Application.created_at.desc()).all()
    return [serialize_application_summary(app) for app in applications]

@router.post("/", response_model=ApplicationDetailOut, status_code=status.HTTP_201_CREATED, summary="Create Draft Application (College Admin)")
def create_application(
    app_in: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.COLLEGE_ADMIN]))
):
    if not current_user.institution_id:
        raise HTTPException(status_code=400, detail="User is not affiliated with any institution")

    # Initial snapshot enrichment
    payload = app_in.payload_snapshot.copy()
    if current_user.institution:
        payload["institution_code"] = current_user.institution.institution_code
    payload["academic_year"] = app_in.academic_year
    payload["programme"] = app_in.programme
    payload["total_sanctioned_intake"] = app_in.declared_student_intake

    new_app = Application(
        institution_id=current_user.institution_id,
        application_type=app_in.application_type,
        programme=app_in.programme,
        academic_year=app_in.academic_year,
        declared_student_intake=app_in.declared_student_intake,
        status=ApplicationStatus.DRAFT,
        current_version=1,
        payload_snapshot=payload
    )
    db.add(new_app)
    db.commit()
    db.refresh(new_app)

    # Create Initial Revision Record
    initial_rev = ApplicationRevision(
        application_id=new_app.id,
        revision_number=1,
        author_id=current_user.id,
        change_summary="Initial Application Draft Created",
        snapshot_data=payload,
        changed_fields={}
    )
    db.add(initial_rev)
    db.commit()

    return get_application_detail(new_app.id, db, current_user)

@router.get("/{application_id}", response_model=ApplicationDetailOut, summary="Get Application Details & Revision History")
def get_application_detail(
    application_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    app = db.query(Application).filter(Application.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    if current_user.role == UserRole.COLLEGE_ADMIN and app.institution_id != current_user.institution_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this application")

    revisions_out = [
        ApplicationRevisionOut(
            id=r.id,
            revision_number=r.revision_number,
            author_id=r.author_id,
            change_summary=r.change_summary,
            changed_fields=r.changed_fields or {},
            compliance_summary=r.compliance_summary,
            created_at=r.created_at
        ) for r in app.revisions
    ]

    # Fetch latest deficiencies
    latest_deficiencies = []
    defs = db.query(Deficiency).filter(Deficiency.application_id == app.id).all()
    for d in defs:
        latest_deficiencies.append({
            "id": d.id,
            "field_key": d.field_key,
            "description": d.description,
            "severity": d.severity,
            "status": d.status,
            "first_seen_at": d.first_seen_at.isoformat() if d.first_seen_at else None
        })

    # Latest compliance run summary
    latest_run = db.query(ComplianceRun).filter(ComplianceRun.application_id == app.id).order_by(ComplianceRun.evaluated_at.desc()).first()
    eval_summary = None
    if latest_run:
        eval_summary = {
            "run_id": latest_run.id,
            "overall_status": latest_run.overall_status,
            "evaluated_at": latest_run.evaluated_at.isoformat(),
            "results_count": len(latest_run.results)
        }

    return ApplicationDetailOut(
        id=app.id,
        institution_id=app.institution_id,
        institution_name=app.institution.name if app.institution else None,
        institution_code=app.institution.institution_code if app.institution else None,
        application_type=app.application_type,
        programme=app.programme,
        academic_year=app.academic_year,
        declared_student_intake=app.declared_student_intake,
        status=app.status,
        current_version=app.current_version,
        compliance_status=app.compliance_status,
        payload_snapshot=app.payload_snapshot,
        officer_remarks=app.officer_remarks,
        assigned_officer_id=app.assigned_officer_id,
        submitted_at=app.submitted_at,
        approved_at=app.approved_at,
        created_at=app.created_at,
        updated_at=app.updated_at,
        revisions=revisions_out,
        latest_evaluation=eval_summary,
        deficiencies=latest_deficiencies
    )

@router.post("/{application_id}/submit", response_model=ApplicationDetailOut, summary="Submit Application for Official Compliance Evaluation")
def submit_application(
    application_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.COLLEGE_ADMIN]))
):
    app = db.query(Application).filter(Application.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    if app.institution_id != current_user.institution_id:
        raise HTTPException(status_code=403, detail="Not authorized to submit this application")

    # Parse and run deterministic AICTE Rule Engine
    try:
        snapshot_obj = InstitutionInputSnapshot(**app.payload_snapshot)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid application snapshot data: {str(e)}")

    eval_result = rule_engine.evaluate_all(snapshot_obj)

    # Persist Compliance Run and Results
    comp_run = ComplianceRun(
        application_id=app.id,
        evaluated_at=utc_now(),
        evaluation_period=app.academic_year,
        input_snapshot=app.payload_snapshot,
        overall_status=eval_result.overall_status,
        created_by=current_user.email
    )
    db.add(comp_run)
    db.commit()
    db.refresh(comp_run)

    # Clear previous deficiencies for this application before inserting fresh run
    db.query(Deficiency).filter(Deficiency.application_id == app.id).delete()

    for item in eval_result.results:
        c_res = ComplianceResult(
            compliance_run_id=comp_run.id,
            rule_key=item.rule_key,
            status=item.status,
            severity=item.severity,
            required_value=item.required_value,
            actual_value=item.actual_value,
            shortfall=item.shortfall,
            explanation=item.explanation,
            evidence_refs=item.evidence_refs
        )
        db.add(c_res)
        db.commit()
        db.refresh(c_res)

        if item.status in ["DEFICIENT", "NEEDS_REVIEW"]:
            # Record Deficiencies
            def_record = Deficiency(
                application_id=app.id,
                compliance_result_id=c_res.id,
                field_key=item.rule_key,
                description=item.explanation,
                severity=item.severity,
                status="OPEN"
            )
            db.add(def_record)

    # Determine status
    if eval_result.overall_status == "COMPLIANT":
        app.status = ApplicationStatus.SUBMITTED
    else:
        app.status = ApplicationStatus.DEFICIENCY_ISSUED

    app.compliance_status = eval_result.overall_status
    app.submitted_at = utc_now()

    # Update latest revision compliance summary
    latest_rev = db.query(ApplicationRevision).filter(
        ApplicationRevision.application_id == app.id
    ).order_by(ApplicationRevision.revision_number.desc()).first()
    if latest_rev:
        latest_rev.compliance_summary = {
            "overall_status": eval_result.overall_status,
            "total_rules": eval_result.total_rules_evaluated,
            "compliant": eval_result.compliant_rules_count,
            "deficient": eval_result.deficient_rules_count
        }

    db.commit()
    return get_application_detail(app.id, db, current_user)

@router.post("/{application_id}/rectify", response_model=ApplicationDetailOut, summary="Submit Rectification / Revision (College Admin)")
def rectify_application(
    application_id: str,
    update_in: ApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.COLLEGE_ADMIN]))
):
    app = db.query(Application).filter(Application.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    if app.institution_id != current_user.institution_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this application")

    if app.status not in [ApplicationStatus.DEFICIENCY_ISSUED, ApplicationStatus.DRAFT]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot submit revision while application is in '{app.status}' status."
        )

    old_snapshot = app.payload_snapshot or {}
    new_snapshot = update_in.payload_snapshot

    # Compute key diff
    diff = calculate_snapshot_diff(old_snapshot, new_snapshot)

    # Increment revision version
    next_version = app.current_version + 1
    app.current_version = next_version
    app.payload_snapshot = new_snapshot
    app.status = ApplicationStatus.RECTIFIED

    # Re-evaluate compliance automatically on the revised snapshot
    try:
        snapshot_obj = InstitutionInputSnapshot(**new_snapshot)
        eval_result = rule_engine.evaluate_all(snapshot_obj)
        compliance_summary = {
            "overall_status": eval_result.overall_status,
            "total_rules": eval_result.total_rules_evaluated,
            "compliant": eval_result.compliant_rules_count,
            "deficient": eval_result.deficient_rules_count
        }
        app.compliance_status = eval_result.overall_status
        if eval_result.overall_status == "COMPLIANT":
            app.status = ApplicationStatus.UNDER_REVIEW
        else:
            app.status = ApplicationStatus.DEFICIENCY_ISSUED
    except Exception as e:
        compliance_summary = {"error": str(e)}

    # Create new immutable revision audit record
    revision = ApplicationRevision(
        application_id=app.id,
        revision_number=next_version,
        author_id=current_user.id,
        change_summary=update_in.change_summary,
        snapshot_data=new_snapshot,
        changed_fields=diff,
        compliance_summary=compliance_summary
    )
    db.add(revision)
    db.commit()

    return get_application_detail(app.id, db, current_user)

@router.post("/{application_id}/review", response_model=ApplicationDetailOut, summary="Scrutiny Officer Review & Decision")
def review_application(
    application_id: str,
    review_in: ApplicationReview,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.SCRUTINY_OFFICER, UserRole.SUPER_ADMIN]))
):
    app = db.query(Application).filter(Application.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    action = review_in.action.upper()
    app.assigned_officer_id = current_user.id
    app.officer_remarks = review_in.remarks

    if action == "APPROVE":
        if app.compliance_status != "COMPLIANT":
            raise HTTPException(
                status_code=400,
                detail="Cannot approve application while compliance status is DEFICIENT."
            )
        app.status = ApplicationStatus.APPROVED
        app.approved_at = utc_now()
    elif action == "REJECT":
        app.status = ApplicationStatus.REJECTED
    elif action == "ISSUE_DEFICIENCY":
        app.status = ApplicationStatus.DEFICIENCY_ISSUED
    else:
        raise HTTPException(status_code=400, detail="Invalid action. Allowed: APPROVE, REJECT, ISSUE_DEFICIENCY")

    db.commit()
    return get_application_detail(app.id, db, current_user)
