from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.user import User, UserRole
from app.models.institution import Institution
from app.schemas.user import UserRegister, UserLogin, UserOut, Token

router = APIRouter(prefix="/auth", tags=["Authentication & RBAC"])

def serialize_user(user: User) -> UserOut:
    return UserOut(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        institution_id=user.institution_id,
        institution_name=user.institution.name if user.institution else None,
        institution_code=user.institution.institution_code if user.institution else None,
        is_active=user.is_active,
        created_at=user.created_at
    )

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED, summary="Register User (College Admin / Scrutiny Officer)")
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    # Check if email is already taken
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    institution_id = user_in.institution_id

    # If College Admin, ensure institution is associated
    if user_in.role == UserRole.COLLEGE_ADMIN:
        if not institution_id:
            # Auto-provision or link institution by code
            code = user_in.institution_code or f"INST-{user_in.email.split('@')[0].upper()}"
            name = user_in.institution_name or f"{user_in.full_name}'s Technical Institute"
            
            inst = db.query(Institution).filter(Institution.institution_code == code).first()
            if not inst:
                inst = Institution(
                    name=name,
                    institution_code=code,
                    region=user_in.institution_region or "NORTH"
                )
                db.add(inst)
                db.commit()
                db.refresh(inst)
            institution_id = inst.id

    new_user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role,
        institution_id=institution_id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token({"sub": new_user.id, "role": new_user.role})
    return Token(access_token=token, token_type="bearer", user=serialize_user(new_user))

@router.post("/login", response_model=Token, summary="User Login (JSON Body)")
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user account")

    token = create_access_token({"sub": user.id, "role": user.role})
    return Token(access_token=token, token_type="bearer", user=serialize_user(user))

@router.post("/token", summary="OAuth2 Form Login (For Swagger UI)")
def token_form(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token({"sub": user.id, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserOut, summary="Get Current Authenticated User Profile")
def get_me(current_user: User = Depends(get_current_user)):
    return serialize_user(current_user)
