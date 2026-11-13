from __future__ import annotations

from datetime import datetime


def generate_tracking_no(application_id: int) -> str:
    year = datetime.utcnow().year
    return f"NCP-KP-{year}-{application_id:06d}"
