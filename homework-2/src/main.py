"""Customer Support Ticket Management API."""

from __future__ import annotations

from uuid import UUID

from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import JSONResponse

from .decision_log import all_decisions
from .import_service import import_file
from .models import ClassificationResult, Ticket, TicketCreate, TicketUpdate
from . import storage
from .ticket_service import auto_classify_ticket, create_ticket

app = FastAPI(title="Customer Support Ticket API", version="1.0.0")


@app.get("/")
def root():
    return {"service": "Customer Support Ticket API", "docs": "/docs"}


@app.post("/tickets", status_code=201, response_model=Ticket)
def create_ticket_endpoint(payload: TicketCreate):
    return create_ticket(payload)


@app.post("/tickets/import")
async def import_tickets(
    file: UploadFile = File(...),
    format: str = Form(...),
):
    try:
        raw = (await file.read()).decode("utf-8")
        summary = import_file(raw, format)
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be UTF-8 encoded text")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Malformed file: {exc}")

    status = 201 if summary.failed == 0 else 207
    return JSONResponse(status_code=status, content=summary.model_dump())


@app.get("/tickets", response_model=list[Ticket])
def list_tickets(
    category: str | None = Query(default=None),
    priority: str | None = Query(default=None),
    status: str | None = Query(default=None),
    customer_id: str | None = Query(default=None),
):
    return storage.list_all(
        category=category,
        priority=priority,
        status=status,
        customer_id=customer_id,
    )


@app.get("/tickets/{ticket_id}", response_model=Ticket)
def get_ticket(ticket_id: UUID):
    ticket = storage.get(ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@app.put("/tickets/{ticket_id}", response_model=Ticket)
def update_ticket(ticket_id: UUID, payload: TicketUpdate):
    updated = storage.update(ticket_id, payload)
    if updated is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return updated


@app.delete("/tickets/{ticket_id}", status_code=204)
def delete_ticket(ticket_id: UUID):
    if not storage.delete(ticket_id):
        raise HTTPException(status_code=404, detail="Ticket not found")


@app.post("/tickets/{ticket_id}/auto-classify")
def classify_ticket(ticket_id: UUID):
    try:
        ticket, result = auto_classify_ticket(ticket_id)
    except LookupError:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return {
        "ticket": ticket,
        "classification": ClassificationResult(
            category=result.category,
            priority=result.priority,
            confidence=result.confidence,
            reasoning=result.reasoning,
            keywords_found=result.keywords_found,
        ),
    }


@app.get("/classification/decisions")
def classification_decisions():
    return {"decisions": all_decisions()}
