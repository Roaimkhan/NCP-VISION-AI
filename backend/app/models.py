from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel

from .constants import AlertState, AlertType, DocKind, Role, Severity, Status


class User(SQLModel, table=True):
    __tablename__ = "user"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password: str
    full_name: str
    role: Role


class Application(SQLModel, table=True):
    __tablename__ = "application"

    id: Optional[int] = Field(default=None, primary_key=True)
    tracking_no: str = Field(index=True, unique=True)
    citizen_id: Optional[int] = Field(default=None, foreign_key="user.id")
    status: Status = Field(default=Status.SUBMITTED)
    district: str
    make: str
    model: str
    year: Optional[int] = None
    color: Optional[str] = None
    chassis_no: Optional[str] = None
    engine_no: Optional[str] = None
    chassis_norm: str = ""
    engine_norm: str = ""
    owner_name: Optional[str] = None
    owner_cnic: Optional[str] = None
    owner_phone: Optional[str] = None
    info_request_note: Optional[str] = None
    officer_note: Optional[str] = None
    risk_level: str = "none"
    is_synthetic: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Document(SQLModel, table=True):
    __tablename__ = "document"

    id: Optional[int] = Field(default=None, primary_key=True)
    application_id: Optional[int] = Field(default=None, foreign_key="application.id")
    kind: DocKind
    filename: str
    path: str
    ocr_text: Optional[str] = None
    ocr_chassis: Optional[str] = None
    ocr_engine: Optional[str] = None
    ocr_confidence: Optional[float] = None


class Alert(SQLModel, table=True):
    __tablename__ = "alert"

    id: Optional[int] = Field(default=None, primary_key=True)
    application_id: int = Field(foreign_key="application.id")
    type: AlertType
    severity: Severity
    message: str
    related_application_id: Optional[int] = Field(default=None, foreign_key="application.id")
    score: Optional[float] = None
    state: AlertState = Field(default=AlertState.open)
    source: str = "system"


class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_log"

    id: Optional[int] = Field(default=None, primary_key=True)
    actor_username: str
    action: str
    application_id: Optional[int] = Field(default=None, foreign_key="application.id")
    detail: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
