from __future__ import annotations

from enum import Enum


class Role(str, Enum):
    citizen = "citizen"
    officer = "officer"
    admin = "admin"


class Status(str, Enum):
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    INFO_REQUESTED = "INFO_REQUESTED"
    PROFILE_VERIFIED = "PROFILE_VERIFIED"
    CLOSED_INCOMPLETE = "CLOSED_INCOMPLETE"


class AlertType(str, Enum):
    DUPLICATE_EXACT = "DUPLICATE_EXACT"
    DUPLICATE_NEAR = "DUPLICATE_NEAR"
    MISSING_REQUIRED = "MISSING_REQUIRED"
    NO_DOCUMENT = "NO_DOCUMENT"
    NO_PHOTO = "NO_PHOTO"
    YEAR_IMPLAUSIBLE = "YEAR_IMPLAUSIBLE"
    ID_FORMAT_ODD = "ID_FORMAT_ODD"
    CNIC_FORMAT = "CNIC_FORMAT"
    OWNER_MULTI_VEHICLE = "OWNER_MULTI_VEHICLE"
    OCR_MISMATCH = "OCR_MISMATCH"
    MAKE_MODEL_CONFLICT = "MAKE_MODEL_CONFLICT"


class Severity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class AlertState(str, Enum):
    open = "open"
    dismissed = "dismissed"
    confirmed = "confirmed"


class DocKind(str, Enum):
    registration_doc = "registration_doc"
    photo = "photo"


DISTRICTS = [
    "Peshawar",
    "Mardan",
    "Swat",
    "Abbottabad",
    "Kohat",
    "Bannu",
    "Dera Ismail Khan",
    "Swabi",
    "Charsadda",
    "Nowshera",
    "Mansehra",
    "Malakand",
    "Buner",
    "Dir Lower",
    "Chitral",
    "Haripur",
]

MAKE_MODELS = {
    "Toyota": ["Corolla", "Land Cruiser", "Prado", "Vitz", "Aqua", "Hilux", "Passo"],
    "Honda": ["Civic", "Vezel", "Fit", "City", "N-Box"],
    "Suzuki": ["Alto", "Wagon R", "Swift", "Every", "Jimny"],
    "Nissan": ["Dayz", "Note", "X-Trail", "Sunny"],
    "Daihatsu": ["Mira", "Move", "Tanto", "Cast"],
}

MODEL_MIN_YEAR = {"Aqua": 2011, "Vezel": 2013, "N-Box": 2011, "Dayz": 2013}

DEMO_IDS = {
    "doc_clean": "DOC-CLEAN-001",
    "doc_exact_dup": "DOC-EXACT-DUP-001",
    "doc_near_dup": "DOC-NEAR-DUP-001",
    "doc_mismatch": "DOC-MISMATCH-001",
    "doc_noisy": "DOC-NOISY-001",
    "photo_vehicle": "PHOTO-VEHICLE-001",
}
