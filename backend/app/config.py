from pydantic import BaseModel

DATABASE_URL = "sqlite:///./backend/ncp.db"
JWT_SECRET = "demo-secret"
UPLOAD_DIR = "backend/uploads"
OCR_ENGINE = "stub"


class Settings(BaseModel):
    database_url: str = DATABASE_URL
    jwt_secret: str = JWT_SECRET
    upload_dir: str = UPLOAD_DIR
    ocr_engine: str = OCR_ENGINE
