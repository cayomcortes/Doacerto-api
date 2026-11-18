from datetime import date
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import models
import schemas
from database import engine, get_db, Base
from auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user,
    get_current_admin,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sistema de Doação de Sangue",
    description=(
        "API para gestão de doadores, agendamento de doações e controle de "
        "estoque de um hemocentro."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def seed_data():
    db = next(get_db())
    try:
        if not db.query(models.InventoryItem).first():
            for bt in models.BloodType:
                db.add(
                    models.InventoryItem(
                        blood_type=bt, units_available=20, min_threshold=10
                    )
                )
        if not db.query(models.User).filter(
            models.User.role == models.UserRole.ADMIN
        ).first():
            admin = models.User(
                full_name="Administrador do Hemocentro",
                email="admin@hemocentro.com",
                hashed_password=get_password_hash("admin123"),
                role=models.UserRole.ADMIN,
            )
            db.add(admin)
        db.commit()
    finally:
        db.close()


@app.get("/")
def root():
    return {"status": "ok", "mensagem": "API do Sistema de Doação de Sangue no ar"}


# ---------------------------------------------------------------------------
# Autenticação
# ---------------------------------------------------------------------------

@app.post("/auth/register", response_model=schemas.UserOut, tags=["Autenticação"])
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")
    new_user = models.User(
        full_name=user.full_name,
        email=user.email,
        hashed_password=get_password_hash(user.password),
        phone=user.phone,
        blood_type=user.blood_type,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/auth/login", response_model=schemas.Token, tags=["Autenticação"])
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="E-mail ou senha inválidos")
    token = create_access_token({"sub": user.email, "role": user.role.value})
    return {"access_token": token, "token_type": "bearer"}


@app.get("/auth/me", response_model=schemas.UserOut, tags=["Autenticação"])
def read_me(current_user: models.User = Depends(get_current_user)):
    return current_user


# ---------------------------------------------------------------------------
# Agendamentos
# ---------------------------------------------------------------------------

@app.post("/appointments", response_model=schemas.AppointmentOut, tags=["Agendamentos"])
def create_appointment(
    appt: schemas.AppointmentCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    new_appt = models.Appointment(
        donor_id=current_user.id,
        scheduled_datetime=appt.scheduled_datetime,
        location=appt.location,
        notes=appt.notes,
    )
    db.add(new_appt)
    db.commit()
    db.refresh(new_appt)
    return new_appt


@app.get("/appointments/me", response_model=List[schemas.AppointmentOut], tags=["Agendamentos"])
def my_appointments(
    current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return (
        db.query(models.Appointment)
        .filter(models.Appointment.donor_id == current_user.id)
        .order_by(models.Appointment.scheduled_datetime.desc())
        .all()
    )


@app.get("/appointments", response_model=List[schemas.AppointmentOut], tags=["Agendamentos"])
def list_appointments(
    status_filter: Optional[models.AppointmentStatus] = None,
    admin: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    query = db.query(models.Appointment)
    if status_filter:
        query = query.filter(models.Appointment.status == status_filter)
    return query.order_by(models.Appointment.scheduled_datetime).all()


@app.patch(
    "/appointments/{appointment_id}/status",
    response_model=schemas.AppointmentOut,
    tags=["Agendamentos"],
)
def update_appointment_status(
    appointment_id: int,
    update: schemas.AppointmentStatusUpdate,
    admin: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    appt = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if not appt:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")

    appt.status = update.status

    # Quando uma doação é concluída, atualiza a data da última doação do
    # doador e soma uma unidade ao estoque do respectivo tipo sanguíneo.
    if update.status == models.AppointmentStatus.COMPLETED:
        donor = db.query(models.User).filter(models.User.id == appt.donor_id).first()
        if donor:
            donor.last_donation_date = date.today()
            if donor.blood_type:
                inv = (
                    db.query(models.InventoryItem)
                    .filter(models.InventoryItem.blood_type == donor.blood_type)
                    .first()
                )
                if inv:
                    inv.units_available += 1

    db.commit()
    db.refresh(appt)
    return appt


# ---------------------------------------------------------------------------
# Estoque
# ---------------------------------------------------------------------------

@app.get("/inventory", response_model=List[schemas.InventoryOut], tags=["Estoque"])
def get_inventory(db: Session = Depends(get_db)):
    return db.query(models.InventoryItem).all()


@app.get("/inventory/low-stock", response_model=List[schemas.InventoryOut], tags=["Estoque"])
def low_stock(admin: models.User = Depends(get_current_admin), db: Session = Depends(get_db)):
    items = db.query(models.InventoryItem).all()
    return [i for i in items if i.units_available < i.min_threshold]


@app.patch("/inventory/{blood_type}", response_model=schemas.InventoryOut, tags=["Estoque"])
def update_inventory(
    blood_type: models.BloodType,
    update: schemas.InventoryUpdate,
    admin: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    item = (
        db.query(models.InventoryItem)
        .filter(models.InventoryItem.blood_type == blood_type)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail="Tipo sanguíneo não encontrado")
    item.units_available = update.units_available
    db.commit()
    db.refresh(item)
    return item
