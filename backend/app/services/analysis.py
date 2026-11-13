from __future__ import annotations

from sqlmodel import Session, select

from ..constants import AlertState, Severity
from ..models import Alert, Application
from .anomalies import (
    check_cnic_format,
    check_id_format,
    check_make_model_conflict,
    check_missing_required,
    check_no_document,
    check_no_photo,
    check_ocr_mismatch,
    check_owner_multi_vehicle,
    check_year_implausible,
)
from .duplicates import find_duplicates


def analyze(session: Session, application_id: int) -> None:
    app = session.get(Application, application_id)
    if app is None:
        return

    session.query(Alert).filter(Alert.application_id == app.id, Alert.source == 'system', Alert.state == 'open').delete()

    alerts = []
    alerts.extend(find_duplicates(session, app))
    for check in [
        check_missing_required,
        check_no_document,
        check_no_photo,
        check_year_implausible,
        check_id_format,
        check_cnic_format,
        check_owner_multi_vehicle,
        check_make_model_conflict,
        check_ocr_mismatch,
    ]:
        result = check(session, app) if check in {check_no_document, check_no_photo, check_owner_multi_vehicle, check_ocr_mismatch} else check(app)
        if result:
            alerts.append({
                'type': result['type'],
                'severity': result['severity'],
                'message': result['message'],
                'related_application_id': None,
                'score': None,
            })

    for alert_data in alerts:
        existing = session.query(Alert).filter(
            Alert.application_id == app.id,
            Alert.type == alert_data['type'],
            Alert.related_application_id == alert_data.get('related_application_id'),
            Alert.state != 'open'
        ).first()
        if existing:
            continue
        alert = Alert(
            application_id=app.id,
            type=alert_data['type'],
            severity=alert_data['severity'],
            message=alert_data['message'],
            related_application_id=alert_data.get('related_application_id'),
            score=alert_data.get('score'),
            state=AlertState.open,
            source='system',
        )
        session.add(alert)

    open_alerts = session.query(Alert).filter(Alert.application_id == app.id, Alert.state == 'open').all()
    if open_alerts:
        app.risk_level = max((a.severity.value for a in open_alerts), key=lambda s: ['low', 'medium', 'high'].index(s))
    else:
        app.risk_level = 'none'
    session.commit()
