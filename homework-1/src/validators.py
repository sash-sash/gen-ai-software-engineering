"""Validation helpers that produce structured error responses."""

from __future__ import annotations

import re
from typing import Any

from pydantic import ValidationError

from .models import TransactionCreate

ACCOUNT_PATTERN = re.compile(r"^ACC-[A-Z0-9]{5}$")


def parse_transaction(data: dict[str, Any]) -> tuple[TransactionCreate | None, list[dict]]:
    """
    Validate raw dict against TransactionCreate.
    Returns (model, []) on success or (None, [error_detail, ...]) on failure.
    """
    try:
        tx = TransactionCreate(**data)
        return tx, []
    except ValidationError as exc:
        errors = []
        for err in exc.errors():
            field = ".".join(str(loc) for loc in err["loc"]) if err["loc"] else "unknown"
            errors.append({"field": field, "message": err["msg"].replace("Value error, ", "")})
        return None, errors
