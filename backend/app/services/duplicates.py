from __future__ import annotations

from rapidfuzz import fuzz
from sqlmodel import Session

from ..constants import AlertType, Severity
from ..models import Alert, Application
from ..services.normalize import confusion_fold, normalize_id


def find_duplicates(session: Session, app: Application) -> list[dict]:
    alerts: list[dict] = []
    for other in session.query(Application).filter(Application.id != app.id, Application.status != 'CLOSED_INCOMPLETE').all():
        for field_name in ('chassis_no', 'engine_no'):
            a = getattr(app, field_name)
            b = getattr(other, field_name)
            if not a or not b:
                continue
            a_norm = normalize_id(a)
            b_norm = normalize_id(b)
            if a_norm and b_norm and a_norm == b_norm:
                alerts.append({
                    'type': AlertType.DUPLICATE_EXACT,
                    'severity': Severity.high,
                    'message': f"{field_name.replace('_no', '').title()} {a} is a duplicate of application {other.tracking_no}.",
                    'related_application_id': other.id,
                    'score': 100.0,
                })
                continue
            if not a_norm or not b_norm:
                continue
            score = fuzz.ratio(confusion_fold(a_norm), confusion_fold(b_norm))
            if score >= 90 and abs(len(a_norm) - len(b_norm)) <= 2:
                severity = Severity.high if score >= 95 else Severity.medium
                alerts.append({
                    'type': AlertType.DUPLICATE_NEAR,
                    'severity': severity,
                    'message': f"{field_name.replace('_no', '').title()} {a} is a near match (score {score}) to application {other.tracking_no}.",
                    'related_application_id': other.id,
                    'score': float(score),
                })
    return alerts
