from __future__ import annotations

import random
from datetime import datetime

from sqlmodel import Session, select

from .constants import DISTRICTS, MAKE_MODELS, Role
from .models import Application, User
from .services.analysis import analyze
from .services.tracking import generate_tracking_no


def seed_demo_data(session: Session) -> None:
    existing_application = session.exec(select(Application)).first()
    if existing_application is not None:
        return

    existing_usernames = {u.username for u in session.exec(select(User)).all()}
    users = []
    for username, full_name, role in [
        ("citizen1", "Citizen One", Role.citizen),
        ("citizen2", "Citizen Two", Role.citizen),
        ("officer1", "Officer One", Role.officer),
        ("admin1", "Admin One", Role.admin),
    ]:
        if username not in existing_usernames:
            users.append(User(username=username, password="demo123", full_name=full_name, role=role))
    if users:
        session.add_all(users)
        session.commit()

    rng = random.Random(42)
    status_cycle = [
        "SUBMITTED",
        "SUBMITTED",
        "SUBMITTED",
        "UNDER_REVIEW",
        "UNDER_REVIEW",
        "INFO_REQUESTED",
        "PROFILE_VERIFIED",
        "CLOSED_INCOMPLETE",
    ]
    generated_apps = []

    for idx in range(1, 241):
        district = DISTRICTS[(idx - 1) % len(DISTRICTS)]
        make = list(MAKE_MODELS.keys())[(idx - 1) % len(MAKE_MODELS)]
        model = MAKE_MODELS[make][(idx - 1) % len(MAKE_MODELS[make])]
        year = 2011 + ((idx * 3) % 10)
        status = status_cycle[(idx - 1) % len(status_cycle)]
        owner_index = (idx % 5) + 1
        citizen_id = 1 if idx % 2 == 0 else 2
        chassis = f"NZE141-{1000000 + idx:07d}"
        engine = f"1NZ-A{100000 + idx:06d}"
        owner_name = f"Owner {owner_index}"
        owner_cnic = f"99999-{1000000 + idx:07d}-{idx % 10}"
        app = Application(
            tracking_no=generate_tracking_no(idx),
            citizen_id=citizen_id,
            status=status,
            district=district,
            make=make,
            model=model,
            year=year,
            color=rng.choice(["White", "Black", "Silver", "Red", "Blue"]),
            chassis_no=chassis,
            engine_no=engine,
            chassis_norm=chassis.upper().replace("-", ""),
            engine_norm=engine.upper().replace("-", ""),
            owner_name=owner_name,
            owner_cnic=owner_cnic,
            owner_phone=f"03{rng.randint(100000000, 999999999) % 10000000000:011d}",
            risk_level="none",
            is_synthetic=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        generated_apps.append(app)

    session.add_all(generated_apps)
    session.commit()

    for app in generated_apps:
        session.refresh(app)
        analyze(session, app.id)

    print(f"Seeded {len(generated_apps)} applications.")
