"""Decision logging for classification events."""

from __future__ import annotations

from datetime import datetime, timezone
from threading import Lock
from uuid import UUID

from .models import Category, Priority

_lock = Lock()
_decisions: list[dict] = []


def log_decision(
    ticket_id: UUID,
    category: Category,
    priority: Priority,
    confidence: float,
    reasoning: str,
    keywords: list[str],
    *,
    manual: bool = False,
) -> None:
    entry = {
        "ticket_id": str(ticket_id),
        "category": category.value,
        "priority": priority.value,
        "confidence": confidence,
        "reasoning": reasoning,
        "keywords": keywords,
        "manual_override": manual,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    with _lock:
        _decisions.append(entry)


def all_decisions() -> list[dict]:
    with _lock:
        return list(_decisions)


def clear_decisions() -> None:
    with _lock:
        _decisions.clear()
