import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship

from database import Base


class BloodType(str, enum.Enum):
    A_POS = "A+"
    A_NEG = "A-"
    B_POS = "B+"
    B_NEG = "B-"
    AB_POS = "AB+"
    AB_NEG = "AB-"
    O_POS = "O+"
    O_NEG = "O-"


class UserRole(str, enum.Enum):
    DONOR = "donor"
    ADMIN = "admin"


class AppointmentStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELED = "canceled"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    blood_type = Column(Enum(BloodType), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.DONOR)
    phone = Column(String, nullable=True)
    last_donation_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    appointments = relationship("Appointment", back_populates="donor")


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    donor_id = Column(Integer, ForeignKey("users.id"))
    scheduled_datetime = Column(DateTime, nullable=False)
    location = Column(String, nullable=False)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.SCHEDULED)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    donor = relationship("User", back_populates="appointments")


class InventoryItem(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    blood_type = Column(Enum(BloodType), unique=True, nullable=False)
    units_available = Column(Integer, default=0)
    min_threshold = Column(Integer, default=10)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
