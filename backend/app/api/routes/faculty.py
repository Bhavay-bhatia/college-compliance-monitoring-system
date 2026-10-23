import hashlib
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.api.deps import get_db
from app.models.institution import Institution
from app.models.faculty import FacultyMember

router = APIRouter(prefix="/faculty", tags=["Faculty Registry & Cross-College Overlap Detection"])

def hash_id(val: str) -> str:
    return hashlib.sha256(val.strip().upper().encode()).hexdigest()

SAMPLE_FACULTY_ROSTER = [
    # Compliant regular faculty in College A
    {"name": "Dr. Rameshwar Nath", "role": "PROFESSOR", "dept": "Computer Science & Engg", "pan": "ABCDE1234F", "aadhaar": "981273618291", "salary": 185000.0, "inst_code": "1-109283741"},
    {"name": "Dr. Ananya Mukherjee", "role": "ASSOCIATE_PROFESSOR", "dept": "Electronics & Comm", "pan": "BNMPK9912A", "aadhaar": "449102938172", "salary": 145000.0, "inst_code": "1-109283741"},
    {"name": "Prof. Harish Chander", "role": "ASSISTANT_PROFESSOR", "dept": "Mechanical Engg", "pan": "CCKPT4412Z", "aadhaar": "119283746501", "salary": 85000.0, "inst_code": "1-109283741"},
    
    # Legit faculty in College B
    {"name": "Dr. Meenakshi Sundaram", "role": "PROFESSOR", "dept": "Information Tech", "pan": "MSUND8812L", "aadhaar": "667182930192", "salary": 190000.0, "inst_code": "1-209182744"},
    {"name": "Prof. Vikas Kashyap", "role": "ASSISTANT_PROFESSOR", "dept": "Civil Engg", "pan": "VKASH7712M", "aadhaar": "881920394857", "salary": 82000.0, "inst_code": "1-209182744"},

    # --- FRAUDULENT OVERLAP (GHOST FACULTY SHOWN IN BOTH COLLEGES SIMULTANEOUSLY!) ---
    {"name": "Dr. Suresh Chandra Gupta", "role": "PROFESSOR", "dept": "Computer Science", "pan": "SCGUP9021K", "aadhaar": "551928374619", "salary": 175000.0, "inst_code": "1-109283741"},
    {"name": "Dr. S. C. Gupta", "role": "PROFESSOR", "dept": "Artificial Intelligence", "pan": "SCGUP9021K", "aadhaar": "551928374619", "salary": 160000.0, "inst_code": "1-209182744"},

    {"name": "Dr. Pooja Agarwal", "role": "ASSOCIATE_PROFESSOR", "dept": "Data Science", "pan": "PAGAR5541Q", "aadhaar": "771829384756", "salary": 135000.0, "inst_code": "1-109283741"},
    {"name": "Dr. Pooja Agarwal", "role": "ASSOCIATE_PROFESSOR", "dept": "Information Technology", "pan": "PAGAR5541Q", "aadhaar": "771829384756", "salary": 140000.0, "inst_code": "1-209182744"},
]

@router.post("/seed-demo", summary="Seed Cross-College Faculty Records for Demonstration")
def seed_demo_faculty(db: Session = Depends(get_db)):
    """Seeds multi-college faculty registries with deliberate cross-institutional dual-employment conflicts."""
    # Ensure two institutions exist
    inst1 = db.query(Institution).filter(Institution.institution_code == "1-109283741").first()
    if not inst1:
        inst1 = Institution(name="Delhi Institute of Technology & Science", institution_code="1-109283741", region="NORTH")
        db.add(inst1)

    inst2 = db.query(Institution).filter(Institution.institution_code == "1-209182744").first()
    if not inst2:
        inst2 = Institution(name="National Academy of Engineering & Research", institution_code="1-209182744", region="WEST")
        db.add(inst2)

    db.commit()
    db.refresh(inst1)
    db.refresh(inst2)

    inst_map = {"1-109283741": inst1.id, "1-209182744": inst2.id}

    # Clear and re-populate
    db.query(FacultyMember).delete()
    db.commit()

    for item in SAMPLE_FACULTY_ROSTER:
        fm = FacultyMember(
            institution_id=inst_map[item["inst_code"]],
            full_name=item["name"],
            designation=item["role"],
            department=item["dept"],
            pan_hash=hash_id(item["pan"]),
            aadhaar_hash=hash_id(item["aadhaar"]),
            monthly_salary=item["salary"],
            phd_awarded=True,
            bank_account_verified=True,
            is_active=True
        )
        db.add(fm)

    db.commit()
    total = db.query(FacultyMember).count()
    return {"message": "Faculty demo roster initialized successfully", "total_faculty_seeded": total}

@router.get("/overlap-audit", summary="National Cross-College Faculty Overlap & Ghost Teacher Audit")
def run_overlap_audit(db: Session = Depends(get_db)):
    """
    Executes national deduplication cross-matching across all institutions.
    Flags individuals drawing concurrent salaries or claiming full-time faculty slots across multiple colleges.
    """
    # Auto-seed if empty
    if db.query(FacultyMember).count() == 0:
        seed_demo_faculty(db)

    # Find PAN hashes that appear in > 1 institution
    subq = db.query(
        FacultyMember.pan_hash
    ).group_by(FacultyMember.pan_hash).having(func.count(func.distinct(FacultyMember.institution_id)) > 1).all()

    conflicted_hashes = [row[0] for row in subq]

    conflicts = []
    for h in conflicted_hashes:
        records = db.query(FacultyMember).filter(FacultyMember.pan_hash == h).all()
        institutions_involved = []
        total_monthly_fraud = 0.0
        for r in records:
            inst = r.institution
            institutions_involved.append({
                "institution_name": inst.name if inst else "Unknown",
                "institution_code": inst.institution_code if inst else "Unknown",
                "region": inst.region if inst else "Unknown",
                "faculty_name_declared": r.full_name,
                "designation": r.designation,
                "department": r.department,
                "claimed_monthly_salary": r.monthly_salary,
                "joined_date": r.joined_date
            })
            total_monthly_fraud += r.monthly_salary

        conflicts.append({
            "pan_fingerprint": h[:12] + "...",
            "severity": "CRITICAL",
            "fraud_type": "CONCURRENT_REGULAR_EMPLOYMENT_DETECTED",
            "institutions_count": len(institutions_involved),
            "total_monthly_disbursement": total_monthly_fraud,
            "details": institutions_involved,
            "recommended_action": "Issue Immediate Show Cause Notice to both institutions under APH Regulation Section 4.12; debar faculty identifier from National Faculty Registry."
        })

    total_active_faculty = db.query(FacultyMember).count()
    return {
        "status": "COMPLETED",
        "total_active_faculty_audited": total_active_faculty,
        "conflicts_detected_count": len(conflicts),
        "integrity_index": f"{((total_active_faculty - len(conflicts)*2) / total_active_faculty * 100):.1f}%" if total_active_faculty > 0 else "100%",
        "conflicts": conflicts
    }
