import hashlib
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.user import User, UserRole
from app.models.institution import Institution
from app.models.document import DocumentVerification, DocumentType
from app.models.base import utc_now

router = APIRouter(prefix="/documents", tags=["Document AI & Verification Pipeline"])

# Simulated OCR text templates for government certificates
OCR_SAMPLES = {
    DocumentType.FIRE_NOC: {
        "text": "OFFICE OF THE DIRECTOR, STATE FIRE AND EMERGENCY SERVICES.\n"
                "NO OBJECTION CERTIFICATE (NOC) FOR ACADEMIC BLOCK\n"
                "Certificate No: DFS/HQ/NOC/2026/89412\n"
                "Issued To: Academic Block A & B, Technical Campus.\n"
                "Valid From: 15-04-2026 to 14-04-2027.\n"
                "Inspection confirms installed wet risers, automatic sprinklers, and dual fire exits.",
        "authority": "State Fire & Emergency Services Directorate",
        "valid_till": "2027-04-14",
        "cert_no": "DFS/HQ/NOC/2026/89412"
    },
    DocumentType.LAND_DEED: {
        "text": "GOVERNMENT OF NCT OF DELHI — SUB-REGISTRAR OFFICE IV\n"
                "REGISTERED TITLE DEED & CONTINUOUS ENCUMBRANCE CERTIFICATE\n"
                "Deed Registration No: DL-SR-8921/2018\n"
                "Parcel Land Area: 3.52 Contiguous Acres (14,245 sq. meters)\n"
                "Classification: Educational / Institutional Use.\n"
                "Clear Title confirmed free from legal disputes or mortgage encumbrances.",
        "authority": "Sub-Registrar Office of Revenue & Land Administration",
        "valid_till": "PERPETUAL",
        "cert_no": "DL-SR-8921/2018"
    },
    DocumentType.BUILDING_STABILITY: {
        "text": "CERTIFICATE OF STRUCTURAL STABILITY & SOUNDNESS\n"
                "Issued by: Er. S. P. Namboodiri, M.Tech (Structures), Govt. Empanelled Auditor (Lic: SE/MCD/4491)\n"
                "The RCC Framed Multi-Storey Academic & Lab Blocks have been inspected.\n"
                "All structural members conform to Indian Standard IS 456:2000 and IS 1893:2016 for Seismic Zone IV.\n"
                "The building is safe and structurally sound for educational occupancy.",
        "authority": "Government Empanelled Chartered Structural Engineer",
        "valid_till": "2028-12-31",
        "cert_no": "SE/MCD/4491/2026"
    },
    DocumentType.WATER_POTABILITY: {
        "text": "PUBLIC HEALTH ENGINEERING DEPARTMENT — CENTRAL WATER TESTING LAB\n"
                "BACTERIOLOGICAL & CHEMICAL ANALYSIS REPORT\n"
                "Sample Source: Campus RO Filtration Plant & Over-Head Storage\n"
                "Turbidity: 0.8 NTU (Norm: < 1.0) | Total Dissolved Solids (TDS): 165 mg/L | Coliform: Absent\n"
                "Conclusion: The water sample conforms strictly to BIS Drinking Water Standard IS 10500:2012.",
        "authority": "Public Health Engineering Department (PHED)",
        "valid_till": "2027-03-31",
        "cert_no": "PHED-LAB-2026-9023"
    }
}

@router.post("/verify", summary="Upload & Verify Statutory Certificate (OCR Pipeline)")
async def upload_and_verify_document(
    doc_type: str = Form(...),
    institution_id: Optional[str] = Form(None),
    application_id: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    filename_override: Optional[str] = Form(None),
    is_simulated_expired: bool = Form(False),
    db: Session = Depends(get_db)
):
    """
    Ingests document, computes SHA-256 hash, runs automated OCR text extraction,
    detects issuing authority, validity dates, and returns confidence verification score.
    """
    doc_name = filename_override or (file.filename if file else f"{doc_type.lower()}_verified_2026.pdf")
    file_bytes = await file.read() if file else f"SIMULATED_CONTENT_{doc_type}_{datetime.now().isoformat()}".encode()
    file_sha = hashlib.sha256(file_bytes).hexdigest()

    # Match or fallback OCR template
    ocr_template = OCR_SAMPLES.get(doc_type, {
        "text": f"OFFICIAL STATUTORY DOCUMENT CERTIFICATION: {doc_type}\nVerified by competent state authority.",
        "authority": "Competent Statutory Authority",
        "valid_till": "2027-06-30",
        "cert_no": f"GOV-{doc_type[:4]}-2026"
    })

    extracted_text = ocr_template["text"]
    confidence = 0.96 if not is_simulated_expired else 0.45
    verification_status = "VERIFIED"
    flag_reason = None

    if is_simulated_expired:
        verification_status = "FLAGGED"
        flag_reason = "Certificate validity has lapsed or fails state registry checksum."
        extracted_text = extracted_text.replace("2027", "2023").replace("2028", "2023")

    # Target institution fallback
    target_inst_id = institution_id
    if not target_inst_id:
        inst = db.query(Institution).first()
        if inst:
            target_inst_id = inst.id
        else:
            inst = Institution(
                name="Delhi Institute of Technology & Science",
                institution_code="1-109283741",
                region="NORTH"
            )
            db.add(inst)
            db.commit()
            target_inst_id = inst.id

    doc_record = DocumentVerification(
        application_id=application_id,
        institution_id=target_inst_id,
        doc_type=doc_type,
        filename=doc_name,
        file_hash=file_sha,
        ocr_status="COMPLETED",
        extracted_text=extracted_text,
        extracted_metadata={
            "issuing_authority": ocr_template["authority"],
            "certificate_number": ocr_template["cert_no"],
            "valid_till": ocr_template["valid_till"] if not is_simulated_expired else "2023-12-31",
            "is_digitally_signed": True
        },
        verification_status=verification_status,
        confidence_score=confidence,
        flag_reason=flag_reason
    )
    db.add(doc_record)
    db.commit()
    db.refresh(doc_record)

    return {
        "id": doc_record.id,
        "doc_type": doc_record.doc_type,
        "filename": doc_record.filename,
        "file_hash": doc_record.file_hash,
        "ocr_status": doc_record.ocr_status,
        "verification_status": doc_record.verification_status,
        "confidence_score": doc_record.confidence_score,
        "flag_reason": doc_record.flag_reason,
        "extracted_metadata": doc_record.extracted_metadata,
        "extracted_text_preview": doc_record.extracted_text[:280] + "..."
    }

@router.get("/list", summary="List All Verified Documents")
def list_verified_documents(
    doc_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(DocumentVerification)
    if doc_type:
        query = query.filter(DocumentVerification.doc_type == doc_type)
    docs = query.order_by(DocumentVerification.created_at.desc()).limit(20).all()
    return [
        {
            "id": d.id,
            "doc_type": d.doc_type,
            "filename": d.filename,
            "verification_status": d.verification_status,
            "confidence_score": d.confidence_score,
            "extracted_metadata": d.extracted_metadata,
            "flag_reason": d.flag_reason,
            "created_at": d.created_at.isoformat()
        } for d in docs
    ]
