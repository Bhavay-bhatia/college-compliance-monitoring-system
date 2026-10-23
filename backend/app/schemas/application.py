from datetime import datetime
from typing import Optional, Any, List, Dict
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.compliance import InstitutionInputSnapshot, ComplianceEvaluationResponse, DeficiencyItem

class ApplicationCreate(BaseModel):
    application_type: str = Field(default="EXTENSION_OF_APPROVAL", description="EXTENSION_OF_APPROVAL, NEW, INTAKE_EXPANSION")
    programme: str = Field(default="ENGINEERING_AND_TECHNOLOGY")
    academic_year: str = Field(default="2026-2027")
    declared_student_intake: int = Field(default=240, gt=0)
    payload_snapshot: Dict[str, Any] = Field(default_factory=dict, description="Initial institutional data snapshot")

class ApplicationUpdate(BaseModel):
    change_summary: str = Field(default="Updated institutional details", description="Reason for update or rectification")
    payload_snapshot: Dict[str, Any] = Field(..., description="Updated institutional data snapshot")

class ApplicationReview(BaseModel):
    action: str = Field(..., description="APPROVE, REJECT, or ISSUE_DEFICIENCY")
    remarks: str = Field(..., min_length=3, description="Officer review findings and notes")

class ApplicationRevisionOut(BaseModel):
    id: str
    revision_number: int
    author_id: Optional[str] = None
    change_summary: str
    changed_fields: Dict[str, Any] = Field(default_factory=dict)
    compliance_summary: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ApplicationListItem(BaseModel):
    id: str
    institution_id: str
    institution_name: Optional[str] = None
    institution_code: Optional[str] = None
    application_type: str
    programme: str
    academic_year: str
    declared_student_intake: int
    status: str
    current_version: int
    compliance_status: Optional[str] = None
    submitted_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ApplicationDetailOut(ApplicationListItem):
    payload_snapshot: Dict[str, Any]
    officer_remarks: Optional[str] = None
    assigned_officer_id: Optional[str] = None
    revisions: List[ApplicationRevisionOut] = Field(default_factory=list)
    latest_evaluation: Optional[Dict[str, Any]] = None
    deficiencies: List[Dict[str, Any]] = Field(default_factory=list)
