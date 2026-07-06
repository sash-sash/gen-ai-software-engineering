"""Pydantic models and enums for support tickets."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, EmailStr, Field, field_validator


class Category(str, Enum):
    ACCOUNT_ACCESS = "account_access"
    TECHNICAL_ISSUE = "technical_issue"
    BILLING_QUESTION = "billing_question"
    FEATURE_REQUEST = "feature_request"
    BUG_REPORT = "bug_report"
    OTHER = "other"


class Priority(str, Enum):
    URGENT = "urgent"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Status(str, Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    WAITING_CUSTOMER = "waiting_customer"
    RESOLVED = "resolved"
    CLOSED = "closed"


class MetadataSource(str, Enum):
    WEB_FORM = "web_form"
    EMAIL = "email"
    API = "api"
    CHAT = "chat"
    PHONE = "phone"


class DeviceType(str, Enum):
    DESKTOP = "desktop"
    MOBILE = "mobile"
    TABLET = "tablet"


class TicketMetadata(BaseModel):
    source: MetadataSource = MetadataSource.API
    browser: str = ""
    device_type: DeviceType = DeviceType.DESKTOP


class TicketCreate(BaseModel):
    customer_id: str = Field(min_length=1)
    customer_email: EmailStr
    customer_name: str = Field(min_length=1)
    subject: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=10, max_length=2000)
    category: Category | None = None
    priority: Priority | None = None
    status: Status = Status.NEW
    assigned_to: str | None = None
    tags: list[str] = Field(default_factory=list)
    metadata: TicketMetadata = Field(default_factory=TicketMetadata)
    auto_classify: bool = False


class TicketUpdate(BaseModel):
    customer_id: str | None = None
    customer_email: EmailStr | None = None
    customer_name: str | None = None
    subject: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, min_length=10, max_length=2000)
    category: Category | None = None
    priority: Priority | None = None
    status: Status | None = None
    assigned_to: str | None = None
    tags: list[str] | None = None
    metadata: TicketMetadata | None = None


class Ticket(BaseModel):
    id: UUID
    customer_id: str
    customer_email: EmailStr
    customer_name: str
    subject: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=10, max_length=2000)
    category: Category
    priority: Priority
    status: Status
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None = None
    assigned_to: str | None = None
    tags: list[str] = Field(default_factory=list)
    metadata: TicketMetadata = Field(default_factory=TicketMetadata)
    classification_confidence: float | None = None
    classification_reasoning: str | None = None

    @field_validator("subject", "description")
    @classmethod
    def validate_lengths(cls, value: str, info) -> str:
        if info.field_name == "subject" and not (1 <= len(value) <= 200):
            raise ValueError("subject must be 1-200 characters")
        if info.field_name == "description" and not (10 <= len(value) <= 2000):
            raise ValueError("description must be 10-2000 characters")
        return value


class ClassificationResult(BaseModel):
    category: Category
    priority: Priority
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    keywords_found: list[str]


class ImportFailure(BaseModel):
    row: int
    error: str


class ImportSummary(BaseModel):
    total_records: int
    successful: int
    failed: int
    failures: list[ImportFailure] = Field(default_factory=list)
    ticket_ids: list[str] = Field(default_factory=list)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def build_ticket(data: TicketCreate, *, category: Category, priority: Priority,
                 confidence: float | None = None, reasoning: str | None = None) -> Ticket:
    now = utc_now()
    return Ticket(
        id=uuid4(),
        customer_id=data.customer_id,
        customer_email=data.customer_email,
        customer_name=data.customer_name,
        subject=data.subject,
        description=data.description,
        category=category,
        priority=priority,
        status=data.status,
        created_at=now,
        updated_at=now,
        assigned_to=data.assigned_to,
        tags=list(data.tags),
        metadata=data.metadata,
        classification_confidence=confidence,
        classification_reasoning=reasoning,
    )


def ticket_from_dict(raw: dict[str, Any]) -> TicketCreate:
    """Build TicketCreate from a flat dict (import parsers)."""
    metadata_raw = raw.get("metadata") or {}
    if isinstance(metadata_raw, str):
        metadata_raw = {}
    tags = raw.get("tags") or []
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]

    return TicketCreate(
        customer_id=str(raw["customer_id"]),
        customer_email=raw["customer_email"],
        customer_name=str(raw["customer_name"]),
        subject=str(raw["subject"]),
        description=str(raw["description"]),
        category=Category(raw["category"]) if raw.get("category") else None,
        priority=Priority(raw["priority"]) if raw.get("priority") else None,
        status=Status(raw.get("status", Status.NEW.value)),
        assigned_to=raw.get("assigned_to"),
        tags=tags,
        metadata=TicketMetadata(
            source=MetadataSource(metadata_raw.get("source", MetadataSource.API.value)),
            browser=str(metadata_raw.get("browser", "")),
            device_type=DeviceType(metadata_raw.get("device_type", DeviceType.DESKTOP.value)),
        ),
        auto_classify=str(raw.get("auto_classify", "false")).lower() in ("true", "1", "yes"),
    )
