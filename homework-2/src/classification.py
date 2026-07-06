"""Classification engine: category and priority from ticket text."""

from __future__ import annotations

import re

from .models import Category, ClassificationResult, Priority, Ticket

CATEGORY_RULES: list[tuple[Category, list[str]]] = [
    (Category.ACCOUNT_ACCESS, ["login", "password", "2fa", "can't access", "cant access", "locked out", "sign in"]),
    (Category.BILLING_QUESTION, ["billing", "invoice", "payment", "refund", "charge", "subscription"]),
    (Category.FEATURE_REQUEST, ["feature", "enhancement", "suggestion", "would like", "add support"]),
    (Category.BUG_REPORT, ["bug report", "reproduction steps", "steps to reproduce", "defect"]),
    (Category.TECHNICAL_ISSUE, ["error", "crash", "bug", "exception", "not working", "broken"]),
]

PRIORITY_RULES: list[tuple[Priority, list[str]]] = [
    (Priority.URGENT, ["can't access", "cant access", "critical", "production down", "security"]),
    (Priority.HIGH, ["important", "blocking", "asap", "urgent"]),
    (Priority.LOW, ["minor", "cosmetic", "suggestion"]),
]


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _find_keywords(text: str, keywords: list[str]) -> list[str]:
    found = []
    for keyword in keywords:
        if keyword in text:
            found.append(keyword)
    return found


def classify_text(subject: str, description: str) -> ClassificationResult:
    text = _normalize(f"{subject} {description}")
    keywords_found: list[str] = []

    best_category = Category.OTHER
    best_category_score = 0
    for category, keywords in CATEGORY_RULES:
        matches = _find_keywords(text, keywords)
        if len(matches) > best_category_score:
            best_category_score = len(matches)
            best_category = category
            keywords_found = matches

    if best_category_score == 0:
        best_category = Category.OTHER

    priority = Priority.MEDIUM
    priority_matches: list[str] = []
    for pri, keywords in PRIORITY_RULES:
        matches = _find_keywords(text, keywords)
        if matches:
            priority = pri
            priority_matches = matches
            break

    all_keywords = sorted(set(keywords_found + priority_matches))
    confidence = min(1.0, 0.45 + 0.15 * len(all_keywords))
    if best_category == Category.OTHER:
        confidence = max(0.3, confidence - 0.2)

    reasoning = (
        f"Matched category '{best_category.value}' with {best_category_score} keyword(s); "
        f"priority '{priority.value}' from text analysis."
    )
    return ClassificationResult(
        category=best_category,
        priority=priority,
        confidence=round(confidence, 2),
        reasoning=reasoning,
        keywords_found=all_keywords,
    )


def apply_classification(ticket: Ticket, result: ClassificationResult, *, manual: bool = False) -> Ticket:
    updated = ticket.model_copy(
        update={
            "category": result.category,
            "priority": result.priority,
            "classification_confidence": result.confidence,
            "classification_reasoning": result.reasoning if not manual else "manual override",
        }
    )
    return updated
