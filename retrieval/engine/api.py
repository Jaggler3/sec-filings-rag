from datetime import date
from typing import Optional

from fastapi import FastAPI, Query
from pydantic import BaseModel

from engine.fetching.browse import browse_current, browse_since, download_filing_text
from engine.store.storage import save_filing, list_filings

app = FastAPI()


class QueryBody(BaseModel):
    text: str


class IngestResponse(BaseModel):
    total: int
    saved: int
    failed: int


class FilingOut(BaseModel):
    cik: str
    company_name: str
    form_type: str
    filing_date: date
    accession_number: str


@app.post("/query")
def perform_query(body: QueryBody):
    return {"text": "your query was " + body.text}


@app.post("/ingest")
def trigger_ingest(
    from_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    to_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
):
    if from_date and to_date:
        filings = browse_since(date.fromisoformat(from_date), date.fromisoformat(to_date))
    else:
        filings = browse_current()

    saved = 0
    failed = 0
    for f in filings:
        try:
            text = download_filing_text(f)
            save_filing(f, text)
            saved += 1
        except Exception:
            failed += 1

    return IngestResponse(total=len(filings), saved=saved, failed=failed)


@app.get("/filings")
def get_filings():
    return [FilingOut(**f.model_dump()) for f in list_filings()]
