# API Reference — Customer Support Ticket API

Base URL: `http://127.0.0.1:8000`

## Data Model

### Ticket

| Field | Type | Notes |
|-------|------|-------|
| id | UUID | Auto-generated |
| customer_id | string | Required |
| customer_email | email | Validated |
| customer_name | string | Required |
| subject | string | 1–200 chars |
| description | string | 10–2000 chars |
| category | enum | See categories below |
| priority | enum | urgent, high, medium, low |
| status | enum | new, in_progress, waiting_customer, resolved, closed |
| classification_confidence | float | 0–1, nullable |
| metadata | object | source, browser, device_type |

## Endpoints

### POST /tickets

Create a ticket. Returns **201**.

```bash
curl -X POST http://127.0.0.1:8000/tickets \
  -H "Content-Type: application/json" \
  -d '{"customer_id":"c1","customer_email":"user@example.com","customer_name":"Alice","subject":"Login issue","description":"I cannot login because password reset fails.","auto_classify":true}'
```

### POST /tickets/import

Bulk import. Form fields: `format` (csv|json|xml), `file` (upload).

```bash
curl -X POST http://127.0.0.1:8000/tickets/import \
  -F "format=csv" \
  -F "file=@sample_tickets.csv"
```

Response (**201** or **207**):

```json
{
  "total_records": 50,
  "successful": 48,
  "failed": 2,
  "failures": [{"row": 3, "error": "validation error..."}],
  "ticket_ids": ["..."]
}
```

### GET /tickets

List tickets. Query params: `category`, `priority`, `status`, `customer_id`.

```bash
curl "http://127.0.0.1:8000/tickets?category=billing_question&priority=high"
```

### GET /tickets/{id}

Returns **200** or **404**.

### PUT /tickets/{id}

Partial update. Manual category/priority changes are treated as override.

### DELETE /tickets/{id}

Returns **204** or **404**.

### POST /tickets/{id}/auto-classify

Returns ticket + classification block:

```json
{
  "ticket": { "...": "..." },
  "classification": {
    "category": "account_access",
    "priority": "urgent",
    "confidence": 0.75,
    "reasoning": "...",
    "keywords_found": ["login", "password"]
  }
}
```

### GET /classification/decisions

Audit log of classification events.

## Error Format

Validation errors (**422**):

```json
{
  "detail": [
    {"loc": ["body", "description"], "msg": "String should have at least 10 characters", "type": "string_too_short"}
  ]
}
```

Business errors (**400**, **404**):

```json
{"detail": "Ticket not found"}
```

## Enums

**category**: account_access, technical_issue, billing_question, feature_request, bug_report, other

**priority**: urgent, high, medium, low

**status**: new, in_progress, waiting_customer, resolved, closed
