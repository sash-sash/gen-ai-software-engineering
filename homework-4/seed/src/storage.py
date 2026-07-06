"""In-memory history store plus on-disk receipt files."""

import os

RECEIPTS_DIR = os.path.join(os.path.dirname(__file__), "receipts")

_history: list[dict] = []
_next_id: int = 1


def _ensure_dir() -> None:
    os.makedirs(RECEIPTS_DIR, exist_ok=True)


def add(result: dict) -> dict:
    """Store a calculation in history and write a receipt file for it."""
    global _next_id
    _ensure_dir()

    record = {"id": _next_id, **result}
    _history.append(record)

    receipt_path = os.path.join(RECEIPTS_DIR, f"{_next_id}.txt")
    with open(receipt_path, "w", encoding="utf-8") as f:
        f.write(_format_receipt(record))

    _next_id += 1
    return record


def all() -> list[dict]:
    return list(_history)


def get(item_id: int) -> dict | None:
    for record in _history:
        if record["id"] == item_id:
            return record
    return None


def clear() -> None:
    _history.clear()


def read_receipt(name: str) -> str:
    """Read a receipt file by name from the receipts directory."""
    path = os.path.join(RECEIPTS_DIR, name)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _format_receipt(record: dict) -> str:
    return (
        f"Receipt #{record['id']}\n"
        f"Amount:     {record['amount']}\n"
        f"Tip ({record['tip_percent']}%): {record['tip']}\n"
        f"Total:      {record['total']}\n"
        f"People:     {record['people']}\n"
        f"Per person: {record['per_person']}\n"
    )
