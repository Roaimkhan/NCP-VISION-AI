from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, SQLModel, select

from .auth import require_role
from .constants import DISTRICTS, MAKE_MODELS, Role
from .db import engine, get_session
from .models import Application, User
from .routers.auth import router as auth_router
from .routers.officer import router as officer_router
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

    status_cycle = ["SUBMITTED", "SUBMITTED", "SUBMITTED", "UNDER_REVIEW", "UNDER_REVIEW", "INFO_REQUESTED", "PROFILE_VERIFIED", "CLOSED_INCOMPLETE"]
    generated_apps = []
    for idx in range(1, 241):
        make = list(MAKE_MODELS.keys())[(idx - 1) % len(MAKE_MODELS)]
        model = MAKE_MODELS[make][(idx - 1) % len(MAKE_MODELS[make])]
        district = DISTRICTS[(idx - 1) % len(DISTRICTS)]
        year = 2011 + ((idx * 3) % 10)
        status = status_cycle[(idx - 1) % len(status_cycle)]
        chassis = f"NZE141-{1000000 + idx:07d}"
        engine = f"1NZ-A{100000 + idx:06d}"
        app = Application(
            tracking_no=generate_tracking_no(idx),
            citizen_id=1 if idx % 2 == 0 else 2,
            status=status,
            district=district,
            make=make,
            model=model,
            year=year,
            color="White",
            chassis_no=chassis,
            engine_no=engine,
            chassis_norm=chassis.replace("-", "").upper(),
            engine_norm=engine.replace("-", "").upper(),
            owner_name=f"Owner {(idx % 5) + 1}",
            owner_cnic=f"99999-{1000000 + idx:07d}-{idx % 10}",
            owner_phone=f"030{idx:08d}",
            risk_level="none",
            is_synthetic=True,
        )
        generated_apps.append(app)
    session.add_all(generated_apps)
    session.commit()
    for app in generated_apps:
        analyze(session, app.id)

app = FastAPI(title="NCP Vision API")
UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

SQLModel.metadata.create_all(engine)
with Session(engine) as session:
    user_exists = session.exec(select(User)).first() is not None
    app_exists = session.exec(select(Application)).first() is not None
    if not user_exists or not app_exists:
        seed_demo_data(session)

app.include_router(auth_router)
app.include_router(officer_router)


@app.get("/api/health")
def health():
    return {"ok": True}


@app.post("/api/applications")
def create_application(payload: dict, user: User = Depends(require_role("citizen")), session: Session = Depends(get_session)):
    app = Application(
        citizen_id=user.id,
        status="SUBMITTED",
        district=str(payload.get("district", "")),
        make=str(payload.get("make", "")),
        model=str(payload.get("model", "")),
        year=int(payload.get("year") or 0) or None,
        color=str(payload.get("color") or ""),
        chassis_no=payload.get("chassis_no"),
        engine_no=payload.get("engine_no"),
        owner_name=payload.get("owner_name"),
        owner_cnic=payload.get("owner_cnic"),
        owner_phone=payload.get("owner_phone"),
        is_synthetic=True,
    )
    session.add(app)
    session.commit()
    session.refresh(app)
    app.tracking_no = generate_tracking_no(app.id)
    session.add(app)
    session.commit()
    analyze(session, app.id)
    return {"id": app.id, "tracking_no": app.tracking_no}


@app.get("/api/track/{tracking_no}")
def public_track(tracking_no: str, session: Session = Depends(get_session)):
    app = session.exec(select(Application).where(Application.tracking_no == tracking_no)).first()
    if not app:
        raise HTTPException(status_code=404, detail="Not found")
    return {
        "tracking_no": app.tracking_no,
        "status": app.status,
        "district": app.district,
        "make": app.make,
        "model": app.model,
        "year": app.year,
        "updated_at": app.updated_at.isoformat(),
        "timeline": [{"status": str(app.status), "at": app.updated_at.isoformat()}],
        "info_request_note": app.info_request_note,
    }


app.mount("/files", StaticFiles(directory=str(UPLOAD_DIR)), name="files")
