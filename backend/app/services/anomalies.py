from __future__ import annotations

import re
from datetime import datetime

from rapidfuzz import fuzz
from sqlmodel import Session

from ..constants import AlertType, MAKE_MODELS, MODEL_MIN_YEAR, Severity
from ..models import Alert, Application, Document
from ..services.normalize import normalize_id


def check_missing_required(app: Application) -> dict | None:
    required = [app.chassis_no, app.engine_no, app.make, app.model, app.year, app.owner_name, app.owner_cnic, app.district]
    if any(v in (None, '', 0) for v in required):
        return {'type': AlertType.MISSING_REQUIRED, 'severity': Severity.high, 'message': 'One or more required fields are missing.'}
    return None


def check_no_document(session: Session, app: Application) -> dict | None:
    has_doc = session.query(Document).filter(Document.application_id == app.id, Document.kind == 'registration_doc').first() is not None
    if not has_doc:
        return {'type': AlertType.NO_DOCUMENT, 'severity': Severity.medium, 'message': 'No registration document is attached.'}
    return None


def check_no_photo(session: Session, app: Application) -> dict | None:
    has_photo = session.query(Document).filter(Document.application_id == app.id, Document.kind == 'photo').first() is not None
    if not has_photo:
        return {'type': AlertType.NO_PHOTO, 'severity': Severity.low, 'message': 'No photo is attached.'}
    return None


def check_year_implausible(app: Application) -> dict | None:
    if app.year is None or app.year < 1980 or app.year > datetime.utcnow().year:
        return {'type': AlertType.YEAR_IMPLAUSIBLE, 'severity': Severity.medium, 'message': f'Year {app.year} is implausible.'}
    return None


def check_id_format(app: Application) -> dict | None:
    chassis = normalize_id(app.chassis_no)
    engine = normalize_id(app.engine_no)
    if len(chassis) < 6 or len(chassis) > 20 or not any(ch.isdigit() for ch in chassis):
        return {'type': AlertType.ID_FORMAT_ODD, 'severity': Severity.medium, 'message': 'Chassis number format is unusual.'}
    if len(engine) < 4 or len(engine) > 20 or not any(ch.isdigit() for ch in engine):
        return {'type': AlertType.ID_FORMAT_ODD, 'severity': Severity.medium, 'message': 'Engine number format is unusual.'}
    return None


def check_cnic_format(app: Application) -> dict | None:
    if app.owner_cnic is None:
        return None
    if not re.match(r'^\d{5}-\d{7}-\d$', app.owner_cnic):
        return {'type': AlertType.CNIC_FORMAT, 'severity': Severity.medium, 'message': 'Owner CNIC format is invalid.'}
    return None


def check_owner_multi_vehicle(session: Session, app: Application) -> dict | None:
    if not app.owner_cnic:
        return None
    count = session.query(Application).filter(Application.owner_cnic == app.owner_cnic).count()
    if count >= 3:
        return {'type': AlertType.OWNER_MULTI_VEHICLE, 'severity': Severity.medium, 'message': 'This owner appears on multiple vehicles.'}
    return None


def check_make_model_conflict(app: Application) -> dict | None:
    if not app.make or not app.model:
        return None
    models = MAKE_MODELS.get(app.make, [])
    if app.model not in models:
        return {'type': AlertType.MAKE_MODEL_CONFLICT, 'severity': Severity.medium, 'message': 'Make/model conflict.'}
    if app.year is not None:
        min_year = MODEL_MIN_YEAR.get(app.model)
        if min_year is not None and app.year < min_year:
            return {'type': AlertType.MAKE_MODEL_CONFLICT, 'severity': Severity.medium, 'message': 'Model year is below the minimum allowed.'}
    return None


def check_ocr_mismatch(session: Session, app: Application) -> dict | None:
    doc = session.query(Document).filter(Document.application_id == app.id, Document.kind == 'registration_doc').first()
    if doc is None or doc.ocr_confidence is None or doc.ocr_confidence < 0.5:
        return None
    typed_chassis = normalize_id(app.chassis_no)
    ocr_chassis = normalize_id(doc.ocr_chassis)
    typed_engine = normalize_id(app.engine_no)
    ocr_engine = normalize_id(doc.ocr_engine)
    if typed_chassis and ocr_chassis and fuzz.ratio(typed_chassis, ocr_chassis) < 90:
        severity = Severity.high if fuzz.ratio(typed_chassis, ocr_chassis) < 80 else Severity.low
        return {'type': AlertType.OCR_MISMATCH, 'severity': severity, 'message': 'OCR chassis does not match typed chassis.'}
    if typed_engine and ocr_engine and fuzz.ratio(typed_engine, ocr_engine) < 90:
        severity = Severity.high if fuzz.ratio(typed_engine, ocr_engine) < 80 else Severity.low
        return {'type': AlertType.OCR_MISMATCH, 'severity': severity, 'message': 'OCR engine does not match typed engine.'}
    return None
