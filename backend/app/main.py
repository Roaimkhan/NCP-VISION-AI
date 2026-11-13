from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="NCP Vision API")
UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


@app.get("/api/health")
def health():
    return {"ok": True}


app.mount("/files", StaticFiles(directory=str(UPLOAD_DIR)), name="files")
