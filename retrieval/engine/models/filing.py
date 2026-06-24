from datetime import date

from pydantic import BaseModel


class Filing(BaseModel):
    cik: str
    company_name: str
    form_type: str
    filing_date: date
    accession_number: str
