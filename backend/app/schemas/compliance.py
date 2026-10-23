from datetime import datetime
from typing import Optional, Any, List, Dict
from pydantic import BaseModel, Field

class PrincipalDetails(BaseModel):
    is_appointed: bool = Field(..., description="Whether a full-time Principal is appointed")
    phd_qualified: bool = Field(..., description="Whether Principal holds a verified Ph.D. degree")
    experience_years: Optional[float] = Field(None, description="Total academic & administrative experience")

class FacultySnapshot(BaseModel):
    total_regular_faculty: int = Field(..., ge=0, description="Total full-time regular faculty on rolls")
    professors: int = Field(0, ge=0)
    associate_professors: int = Field(0, ge=0)
    assistant_professors: int = Field(0, ge=0)
    principal: Optional[PrincipalDetails] = None

class InfrastructureSnapshot(BaseModel):
    land_area_acres: float = Field(..., ge=0.0, description="Contiguous campus land in acres")
    instructional_area_sqm: float = Field(..., ge=0.0, description="Carpet area for classrooms/labs")
    administrative_area_sqm: float = Field(..., ge=0.0)
    amenities_area_sqm: float = Field(..., ge=0.0)

class ComputingSnapshot(BaseModel):
    student_terminals: int = Field(..., ge=0, description="Number of operational PCs for students")
    internet_bandwidth_mbps: float = Field(..., ge=0.0, description="Dedicated leased line bandwidth")
    system_software_count: int = Field(0, ge=0)
    application_software_count: int = Field(0, ge=0)

class LibrarySnapshot(BaseModel):
    total_volumes: int = Field(..., ge=0)
    total_titles: int = Field(..., ge=0)
    national_journals: int = Field(0, ge=0)
    international_e_journals: bool = Field(False)
    multimedia_terminals: int = Field(0, ge=0)

class SafetyAndAccessSnapshot(BaseModel):
    fire_noc_valid: bool = Field(..., description="Valid Fire Safety NOC from Fire Department")
    fire_noc_expiry_date: Optional[str] = None
    structural_stability_certified: bool = Field(..., description="Structural stability certificate")
    potable_water_certified: bool = Field(..., description="Water potability test report")
    barrier_free_ramps: bool = Field(..., description="Ramps with handrails (slope <= 1:12)")
    braille_enabled_lift: bool = Field(..., description="Lifts with Braille and voice announcements")
    disabled_friendly_toilets: bool = Field(..., description="Special toilets for Divyangjan")

class StatutoryCommitteesSnapshot(BaseModel):
    anti_ragging_committee: bool = Field(..., description="Anti-Ragging Committee constituted")
    anti_ragging_squad: bool = Field(..., description="Anti-Ragging Squad operational")
    internal_complaints_committee_icc: bool = Field(..., description="ICC / POSH committee active")
    icc_external_member: bool = Field(..., description="External NGO/legal representative in ICC")
    student_grievance_redressal_committee: bool = Field(..., description="SGRC constituted")
    ombudsman_appointed: bool = Field(..., description="University/AICTE Ombudsman notified")
    sc_st_committee: bool = Field(..., description="SC/ST Prevention of Atrocities Committee")

class InstitutionInputSnapshot(BaseModel):
    institution_code: str
    academic_year: str = "2026-2027"
    programme: str = "ENGINEERING_AND_TECHNOLOGY"  # ENGINEERING_AND_TECHNOLOGY, MANAGEMENT, PHARMACY, etc.
    level: str = "UG"  # UG, PG, DIPLOMA
    location_type: str = "URBAN"  # MEGA_METRO, URBAN, RURAL
    total_sanctioned_intake: int = Field(..., gt=0, description="Annual approved intake per batch")
    course_duration_years: int = Field(4, ge=1, le=5)
    accredited_status: bool = False
    
    # Sub-domain snapshots
    faculty: Optional[FacultySnapshot] = None
    infrastructure: Optional[InfrastructureSnapshot] = None
    computing: Optional[ComputingSnapshot] = None
    library: Optional[LibrarySnapshot] = None
    safety_and_access: Optional[SafetyAndAccessSnapshot] = None
    statutory_committees: Optional[StatutoryCommitteesSnapshot] = None

class ComplianceResultItem(BaseModel):
    rule_key: str
    rule_version: str = "2026.1"
    status: str  # COMPLIANT, DEFICIENT, NEEDS_REVIEW, NOT_APPLICABLE
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    required_value: Optional[Dict[str, Any]] = None
    actual_value: Optional[Dict[str, Any]] = None
    shortfall: Optional[Dict[str, Any]] = None
    explanation: str
    evidence_refs: List[str] = Field(default_factory=list)
    evaluated_at: str

class DeficiencyItem(BaseModel):
    rule_key: str
    field_key: str
    severity: str
    description: str
    recommended_action: str

class ComplianceEvaluationResponse(BaseModel):
    institution_code: str
    academic_year: str
    evaluated_at: str
    overall_status: str  # COMPLIANT, DEFICIENT, NEEDS_REVIEW
    total_rules_evaluated: int
    compliant_rules_count: int
    deficient_rules_count: int
    review_rules_count: int
    results: List[ComplianceResultItem]
    deficiencies: List[DeficiencyItem]
