import hashlib
import json
from app.models.sheet import SheetRow


def dataset_hash(rows: list[SheetRow]) -> str:
    """Hash canonical row data, including row numbers and empty cells."""
    payload = [row.model_dump() for row in rows]
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()
