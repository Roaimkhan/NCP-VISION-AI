from __future__ import annotations

from sqlmodel import Session

from ..models import AuditLog


def log_action(session: Session, actor_username: str, action: str, detail: str, application_id: int | None = None) -> AuditLog:
    row = AuditLog(
        actor_username=actor_username,
        action=action,
        application_id=application_id,
        detail=detail,
    )
    session.add(row)
    session.commit()
    session.refresh(row)
    return row
