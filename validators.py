from __future__ import annotations
from datetime import date
from pathlib import Path
from config import ALLOWED_IMAGE_TYPES, MAX_IMAGE_BYTES

def validate_password(password: str) -> str | None:
    if len(password) < 10: return "Use at least 10 characters."
    if not any(c.isalpha() for c in password) or not any(c.isdigit() for c in password): return "Include at least one letter and one number."
    return None

def validate_item(data: dict) -> str | None:
    for key, label in (("item_name", "Item name"), ("category", "Category"), ("description", "Description"), ("location", "Location"), ("event_date", "Date")):
        if not str(data.get(key, "")).strip(): return f"{label} is required."
    try: date.fromisoformat(data["event_date"])
    except (ValueError, TypeError): return "Enter the date as YYYY-MM-DD."
    if len(data["item_name"]) > 100 or len(data["description"]) > 1200: return "Some text is longer than the allowed limit."
    if data.get("contact") and len(data["contact"]) > 120: return "Contact details are too long."
    return None

def validate_image(path: str | Path | None) -> str | None:
    if not path: return None
    p = Path(path)
    if p.suffix.lower() not in ALLOWED_IMAGE_TYPES: return "Choose a PNG, JPG, or WEBP image."
    try:
        if p.stat().st_size > MAX_IMAGE_BYTES: return "Images must be 5 MB or smaller."
        with p.open("rb") as f:
            sig = f.read(12)
        valid = sig.startswith(b"\x89PNG\r\n\x1a\n") or sig.startswith(b"\xff\xd8\xff") or (sig[:4] == b"RIFF" and sig[8:12] == b"WEBP")
        if not valid: return "The selected file is not a valid supported image."
    except OSError: return "The selected image could not be read."
    return None
