from __future__ import annotations


def normalize_id(s: str | None) -> str:
    if s is None:
        return ""
    cleaned = "".join(ch for ch in str(s).upper().strip() if ch.isalnum())
    return cleaned


def confusion_fold(s: str) -> str:
    mapping = str.maketrans({
        "O": "0",
        "I": "1",
        "L": "1",
        "S": "5",
        "B": "8",
        "Z": "2",
        "Q": "0",
    })
    return normalize_id(s).translate(mapping)
