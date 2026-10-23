from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, description="Password min 6 characters")
    full_name: str = Field(..., min_length=2)
    role: str = Field(default="COLLEGE_ADMIN", description="COLLEGE_ADMIN, SCRUTINY_OFFICER, or SUPER_ADMIN")
    institution_id: Optional[str] = None
    # Optional institution details to auto-provision institution during college admin signup
    institution_code: Optional[str] = None
    institution_name: Optional[str] = None
    institution_region: Optional[str] = "NORTH"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    role: str
    institution_id: Optional[str] = None
    institution_name: Optional[str] = None
    institution_code: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
