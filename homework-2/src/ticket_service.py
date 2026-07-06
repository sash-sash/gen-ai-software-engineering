"""Ticket creation and auto-classification helpers."""

from __future__ import annotations

from uuid import UUID

from .classification import apply_classification, classify_text
from .decision_log import log_decision
from .models import Category, ClassificationResult, Priority, Ticket, TicketCreate, build_ticket
from . import storage


def create_ticket(payload: TicketCreate) -> Ticket:
    category = payload.category or Category.OTHER
    priority = payload.priority or Priority.MEDIUM
    confidence: float | None = None
    reasoning: str | None = None
    keywords: list[str] = []

    should_classify = payload.auto_classify or payload.category is None or payload.priority is None
    if should_classify:
        result = classify_text(payload.subject, payload.description)
        if payload.category is None:
            category = result.category
        if payload.priority is None:
            priority = result.priority
        confidence = result.confidence
        reasoning = result.reasoning
        keywords = result.keywords_found

    ticket = build_ticket(
        payload,
        category=category,
        priority=priority,
        confidence=confidence,
        reasoning=reasoning,
    )
    created = storage.create(ticket)

    if should_classify:
        log_decision(
            created.id,
            category,
            priority,
            confidence or 0.0,
            reasoning or "",
            keywords,
        )
    return created


def auto_classify_ticket(ticket_id: UUID) -> tuple[Ticket, ClassificationResult]:
    ticket = storage.get(ticket_id)
    if ticket is None:
        raise LookupError("Ticket not found")

    result = classify_text(ticket.subject, ticket.description)
    updated = apply_classification(ticket, result)
    saved = storage.replace(updated)
    log_decision(
        saved.id,
        result.category,
        result.priority,
        result.confidence,
        result.reasoning,
        result.keywords_found,
    )
    return saved, result
