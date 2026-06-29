"""Bill Splitter REST API (FastAPI).

A tiny service that calculates how to split a bill (with tip) between people
and keeps a history of past calculations.
"""

import hmac
import os

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from . import calculator, storage

app = FastAPI(title="Bill Splitter API", version="1.0.0")

ADMIN_API_KEY = os.environ.get("ADMIN_API_KEY", "")


class SplitRequest(BaseModel):
    amount: float
    tip_percent: float = 0
    people: int = Field(gt=0)


@app.get("/")
def root():
    return {"service": "Bill Splitter API", "docs": "/docs"}


@app.post("/calculate")
def calculate(req: SplitRequest):
    result = calculator.calculate_split(req.amount, req.tip_percent, req.people)
    return storage.add(result)


@app.get("/history")
def history():
    return storage.all()


@app.get("/history/{item_id}")
def history_item(item_id: int):
    record = storage.get(item_id)
    if record is None:
        raise HTTPException(status_code=404, detail="calculation not found")
    return record


@app.delete("/history")
def clear_history(api_key: str = Query(...)):
    if not ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="forbidden")
    if hmac.compare_digest(api_key, ADMIN_API_KEY):
        storage.clear()
        return {"status": "cleared"}
    raise HTTPException(status_code=403, detail="forbidden")


@app.get("/receipt")
def get_receipt(name: str):
    try:
        content = storage.read_receipt(name)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="receipt not found")
    except ValueError:
        raise HTTPException(status_code=400, detail="invalid receipt name")
    return {"name": name, "content": content}
