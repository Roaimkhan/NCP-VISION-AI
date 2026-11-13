from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, or_, select

from ..auth import require_role
from ..db import get_session
from ..models import Alert, Application, AuditLog, User

router = APIRouter(prefix="/api")


class ActionPayload(BaseModel):
    action: str
    note: str | None = None


class ResolvePayload(BaseModel):
    resolution: str
    note: str | None = None


def _serialize_application(app: Application) -> dict:
    return {
        "id": app.id,
        "tracking_no": app.tracking_no,
        "status": app.status.value if hasattr(app.status, 'value') else app.status,
        "district": app.district,
        "make": app.make,
        "model": app.model,
        "year": app.year,
        "owner_name": app.owner_name,
        "risk_level": app.risk_level,
        "updated_at": app.updated_at.isoformat() if app.updated_at else None,
    }


@router.get("/officer/applications")
def list_officer_applications(
    status: str | None = None,
    district: str | None = None,
    q: str | None = None,
    min_risk: str | None = None,
    page: int = 1,
    page_size: int = 50,
    user: User = Depends(require_role("officer", "admin")),
    session: Session = Depends(get_session),
):
    stmt = select(Application)
    rows = session.exec(stmt).all()
    if status:
        rows = [r for r in rows if str(r.status).lower() == status.lower()]
    if district:
        rows = [r for r in rows if r.district == district]
    if q:
        qv = q.lower()
        rows = [r for r in rows if qv in (r.tracking_no or '').lower() or qv in (r.chassis_no or '').lower() or qv in (r.engine_no or '').lower() or qv in (r.owner_name or '').lower() or qv in (r.owner_cnic or '').lower()]
    if min_risk:
        rank = {"low": 1, "medium": 2, "high": 3, "none": 0}
        rows = [r for r in rows if rank.get(str(r.risk_level).lower(), 0) >= rank.get(min_risk.lower(), 0)]
    total = len(rows)
    rows = rows[(page - 1) * page_size: page * page_size]
    return {"items": [_serialize_application(r) for r in rows], "total": total}


@router.get("/officer/applications/{application_id}")
def get_application_detail(
    application_id: int,
    user: User = Depends(require_role("officer", "admin")),
    session: Session = Depends(get_session),
):
    app = session.get(Application, application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    alerts = session.exec(select(Alert).where(Alert.application_id == app.id)).all()
    related = []
    for alert in alerts:
        if alert.related_application_id:
            other = session.get(Application, alert.related_application_id)
            if other:
                related.append({"alert_id": alert.id, "tracking_no": other.tracking_no, "status": other.status, "district": other.district, "make": other.make, "model": other.model})
    audit = session.exec(select(AuditLog).where(AuditLog.application_id == app.id)).all()
    return {
        "application": {
            **_serialize_application(app),
            "citizen_id": app.citizen_id,
            "color": app.color,
            "chassis_no": app.chassis_no,
            "engine_no": app.engine_no,
            "owner_cnic": app.owner_cnic,
            "owner_phone": app.owner_phone,
            "info_request_note": app.info_request_note,
            "officer_note": app.officer_note,
        },
        "alerts": [{
            "id": a.id,
            "type": a.type.value if hasattr(a.type, 'value') else a.type,
            "severity": a.severity.value if hasattr(a.severity, 'value') else a.severity,
            "message": a.message,
            "related_application_id": a.related_application_id,
            "state": a.state.value if hasattr(a.state, 'value') else a.state,
            "score": a.score,
        } for a in alerts],
        "related": related,
        "audit": [{"id": a.id, "action": a.action, "actor_username": a.actor_username, "detail": a.detail, "created_at": a.created_at.isoformat()} for a in audit],
    }


@router.post("/officer/applications/{application_id}/action")
def officer_action(
    application_id: int,
    payload: ActionPayload,
    user: User = Depends(require_role("officer", "admin")),
    session: Session = Depends(get_session),
):
    app = session.get(Application, application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    action = payload.action
    if action == "start_review":
        if app.status != "SUBMITTED":
            raise HTTPException(status_code=409, detail="Invalid status transition")
        app.status = "UNDER_REVIEW"
    elif action == "request_info":
        if app.status not in {"SUBMITTED", "UNDER_REVIEW"}:
            raise HTTPException(status_code=409, detail="Invalid status transition")
        if not payload.note:
            raise HTTPException(status_code=409, detail="Note is required")
        app.status = "INFO_REQUESTED"
        app.info_request_note = payload.note
    elif action == "verify":
        if app.status != "UNDER_REVIEW":
            raise HTTPException(status_code=409, detail="Invalid status transition")
        has_high = any(a.state == 'open' and str(a.severity).lower() == 'high' for a in session.exec(select(Alert).where(Alert.application_id == app.id)).all())
        if has_high:
            raise HTTPException(status_code=409, detail="Resolve high-severity alerts first")
        app.status = "PROFILE_VERIFIED"
    elif action == "close_incomplete":
        if app.status in {"PROFILE_VERIFIED", "CLOSED_INCOMPLETE"}:
            raise HTTPException(status_code=409, detail="Invalid status transition")
        if not payload.note:
            raise HTTPException(status_code=409, detail="Note is required")
        app.status = "CLOSED_INCOMPLETE"
        app.officer_note = payload.note
    else:
        raise HTTPException(status_code=400, detail="Unknown action")

    session.add(AuditLog(actor_username=user.username, action=action, application_id=app.id, detail=payload.note or ""))
    session.commit()
    return {"ok": True, "status": app.status}


@router.post("/officer/alerts/{alert_id}/resolve")
def resolve_alert(
    alert_id: int,
    payload: ResolvePayload,
    user: User = Depends(require_role("officer", "admin")),
    session: Session = Depends(get_session),
):
    alert = session.get(Alert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    if payload.resolution not in {"dismissed", "confirmed"}:
        raise HTTPException(status_code=400, detail="Invalid resolution")
    alert.state = payload.resolution
    app = session.get(Application, alert.application_id)
    if app:
        open_alerts = session.exec(select(Alert).where(Alert.application_id == app.id, Alert.state == 'open')).all()
        app.risk_level = 'none' if not open_alerts else max(([a.severity for a in open_alerts]), key=lambda s: ['low', 'medium', 'high'].index(str(s).lower()))
    session.add(AuditLog(actor_username=user.username, action='resolve_alert', application_id=alert.application_id, detail=f"{payload.resolution}: {payload.note or ''}"))
    session.commit()
    return {"ok": True, "risk_level": app.risk_level if app else None}


@router.get("/officer/stats")
def officer_stats(
    user: User = Depends(require_role("officer", "admin")),
    session: Session = Depends(get_session),
):
    rows = session.exec(select(Application)).all()
    by_status = {}
    by_district = {}
    for app in rows:
        by_status[str(app.status)] = by_status.get(str(app.status), 0) + 1
        by_district[app.district] = by_district.get(app.district, 0) + 1
    totals = {
        'total': len(rows),
        'open_alerts': session.exec(select(Alert).where(Alert.state == 'open')).all().__len__(),
        'high_risk': sum(1 for r in rows if str(r.risk_level).lower() == 'high'),
    }
    return {'totals': totals, 'by_status': by_status, 'by_district': [{'district': k, 'total': v} for k, v in by_district.items()]}
