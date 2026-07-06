"""Bulk import from CSV, JSON, and XML."""

from __future__ import annotations

import csv
import io
import json
import xml.etree.ElementTree as ET
from typing import Any

from pydantic import ValidationError

from .models import ImportFailure, ImportSummary, ticket_from_dict
from .ticket_service import create_ticket
from . import storage  # noqa: F401 - used in tests via module path


def _row_to_dict(row: dict[str, str]) -> dict[str, Any]:
    metadata = {
        "source": row.get("metadata_source") or "api",
        "browser": row.get("metadata_browser") or "",
        "device_type": row.get("metadata_device_type") or "desktop",
    }
    return {
        "customer_id": row.get("customer_id", ""),
        "customer_email": row.get("customer_email", ""),
        "customer_name": row.get("customer_name", ""),
        "subject": row.get("subject", ""),
        "description": row.get("description", ""),
        "category": row.get("category") or None,
        "priority": row.get("priority") or None,
        "status": row.get("status") or "new",
        "assigned_to": row.get("assigned_to") or None,
        "tags": row.get("tags") or "",
        "metadata": metadata,
        "auto_classify": row.get("auto_classify", "false"),
    }


def parse_csv(content: str) -> list[dict[str, Any]]:
    reader = csv.DictReader(io.StringIO(content))
    if reader.fieldnames is None:
        raise ValueError("CSV file is empty or missing header row")
    return [_row_to_dict(row) for row in reader]


def parse_json(content: str) -> list[dict[str, Any]]:
    data = json.loads(content)
    if isinstance(data, dict) and "tickets" in data:
        records = data["tickets"]
    elif isinstance(data, list):
        records = data
    else:
        raise ValueError("JSON must be an array of tickets or an object with a 'tickets' key")
    if not isinstance(records, list):
        raise ValueError("JSON tickets payload must be a list")
    return records


def parse_xml(content: str) -> list[dict[str, Any]]:
    root = ET.fromstring(content)
    records: list[dict[str, Any]] = []
    for ticket_el in root.findall(".//ticket"):
        metadata_el = ticket_el.find("metadata")
        metadata = {}
        if metadata_el is not None:
            metadata = {
                "source": (metadata_el.findtext("source") or "api").strip(),
                "browser": (metadata_el.findtext("browser") or "").strip(),
                "device_type": (metadata_el.findtext("device_type") or "desktop").strip(),
            }
        tags_el = ticket_el.find("tags")
        tags: list[str] = []
        if tags_el is not None:
            tags = [tag.text.strip() for tag in tags_el.findall("tag") if tag.text]
        records.append(
            {
                "customer_id": (ticket_el.findtext("customer_id") or "").strip(),
                "customer_email": (ticket_el.findtext("customer_email") or "").strip(),
                "customer_name": (ticket_el.findtext("customer_name") or "").strip(),
                "subject": (ticket_el.findtext("subject") or "").strip(),
                "description": (ticket_el.findtext("description") or "").strip(),
                "category": (ticket_el.findtext("category") or "").strip() or None,
                "priority": (ticket_el.findtext("priority") or "").strip() or None,
                "status": (ticket_el.findtext("status") or "new").strip(),
                "assigned_to": (ticket_el.findtext("assigned_to") or "").strip() or None,
                "tags": tags,
                "metadata": metadata,
                "auto_classify": (ticket_el.findtext("auto_classify") or "false").strip(),
            }
        )
    return records


def import_records(records: list[dict[str, Any]]) -> ImportSummary:
    summary = ImportSummary(total_records=len(records), successful=0, failed=0)
    for index, record in enumerate(records, start=1):
        try:
            payload = ticket_from_dict(record)
            ticket = create_ticket(payload)
            summary.successful += 1
            summary.ticket_ids.append(str(ticket.id))
        except (ValidationError, ValueError, KeyError) as exc:
            summary.failed += 1
            summary.failures.append(ImportFailure(row=index, error=str(exc)))
    return summary


def import_file(content: str, file_format: str) -> ImportSummary:
    fmt = file_format.lower().strip()
    if fmt == "csv":
        records = parse_csv(content)
    elif fmt == "json":
        records = parse_json(content)
    elif fmt == "xml":
        records = parse_xml(content)
    else:
        raise ValueError(f"Unsupported format '{file_format}'. Use csv, json, or xml.")
    return import_records(records)
