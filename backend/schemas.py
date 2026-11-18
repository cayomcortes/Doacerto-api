from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

from models import BloodType, UserRole, AppointmentStatus


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None
    blood_type: Optional[BloodType] = None


class UserOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    blood_type: Optional[BloodType] = None
    role: UserRole
    last_donation_date: Optional[date] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class AppointmentCreate(BaseModel):
    scheduled_datetime: datetime
    location: str
    notes: Optional[str] = None


class AppointmentOut(BaseModel):
    id: int
    donor_id: int
    scheduled_datetime: datetime
    location: str
    status: AppointmentStatus
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class AppointmentStatusUpdate(BaseModel):
    status: AppointmentStatus


class InventoryOut(BaseModel):
    blood_type: BloodType
    units_available: int
    min_threshold: int

    class Config:
        from_attributes = True


class InventoryUpdate(BaseModel):
    units_available: int
