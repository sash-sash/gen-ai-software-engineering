"""In-memory ticket storage with thread-safe access."""

from __future__ import annotations

from threading import Lock
from uuid import UUID

from .models import Ticket, TicketUpdate, utc_now

_lock = Lock()
_tickets: dict[UUID, Ticket] = {}


def create(ticket: Ticket) -> Ticket:
    with _lock:
        _tickets[ticket.id] = ticket
        return ticket


def get(ticket_id: UUID) -> Ticket | None:
    with _lock:
        return _tickets.get(ticket_id)


def list_all(
    *,
    category: str | None = None,
    priority: str | None = None,
    status: str | None = None,
    customer_id: str | None = None,
) -> list[Ticket]:
    with _lock:
        items = list(_tickets.values())

    if category:
        items = [t for t in items if t.category.value == category]
    if priority:
        items = [t for t in items if t.priority.value == priority]
    if status:
        items = [t for t in items if t.status.value == status]
    if customer_id:
        items = [t for t in items if t.customer_id == customer_id]
    return sorted(items, key=lambda t: t.created_at, reverse=True)


def update(ticket_id: UUID, changes: TicketUpdate) -> Ticket | None:
    with _lock:
        existing = _tickets.get(ticket_id)
        if existing is None:
            return None

        data = existing.model_dump()
        patch = changes.model_dump(exclude_unset=True)
        manual_category = "category" in patch
        manual_priority = "priority" in patch
        data.update(patch)
        data["updated_at"] = utc_now()

        if changes.status is not None and changes.status.value in ("resolved", "closed"):
            data["resolved_at"] = utc_now()
        if manual_category or manual_priority:
            data["classification_reasoning"] = "manual override"

        updated = Ticket(**data)
        _tickets[ticket_id] = updated
        return updated


def replace(ticket: Ticket) -> Ticket:
    with _lock:
        ticket = ticket.model_copy(update={"updated_at": utc_now()})
        _tickets[ticket.id] = ticket
        return ticket


def delete(ticket_id: UUID) -> bool:
    with _lock:
        if ticket_id not in _tickets:
            return False
        del _tickets[ticket_id]
        return True


def clear() -> None:
    with _lock:
        _tickets.clear()
