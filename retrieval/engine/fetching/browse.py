import re
import time
from datetime import date, datetime
from typing import Optional

import requests
from bs4 import BeautifulSoup, Tag

from engine.models.filing import Filing

SEC_BROWSE_URL = "https://www.sec.gov/cgi-bin/browse-edgar"
SEC_ARCHIVES_URL = "https://www.sec.gov/Archives"
USER_AGENT = "Martin Darazs martin.protostar@gmail.com"
RATE_LIMIT_S = 0.15


def _headers() -> dict:
    return {
        "User-Agent": USER_AGENT,
        "Accept-Encoding": "gzip, deflate",
    }


def _rate_limit():
    time.sleep(RATE_LIMIT_S)


def _date_to_sec(d: date) -> str:
    return d.strftime("%m/%d/%Y")


def _request_page(params: dict) -> str:
    response = requests.get(SEC_BROWSE_URL, params=params, headers=_headers())
    response.raise_for_status()
    _rate_limit()
    return response.text


def _get_filings_table(html: str) -> Optional[Tag]:
    soup = BeautifulSoup(html, "html.parser")
    tables = soup.find_all("table")
    if len(tables) > 6:
        return tables[6]
    for table in tables:
        if table.find("th") and "Filing Date" in table.get_text():
            return table
    return None


_CIK_RE = re.compile(r"\((\d+)\)")


def _parse_cik(text: str) -> Optional[str]:
    m = _CIK_RE.search(text)
    return m.group(1) if m else None


def _extract_accno_from_link(cell: Tag) -> Optional[str]:
    for link in cell.find_all("a"):
        href = link.get("href", "")
        m = re.search(r'/edgar/data/\d+/\d+/([\d-]+)\.txt', href)
        if m:
            return m.group(1)
    return None


def _find_date_col(header_cells: list[Tag]) -> int:
    for i, c in enumerate(header_cells):
        if "Filing Date" in c.get_text():
            return i
    return -1


def _parse_page(html: str) -> list[Filing]:
    table = _get_filings_table(html)
    if not table:
        return []

    rows = table.find_all("tr")
    filings: list[Filing] = []
    pending_cik: Optional[str] = None
    pending_company: Optional[str] = None
    date_col = -1

    for row in rows:
        cells = row.find_all(["td", "th"])
        if not cells:
            continue

        # Header row — identify Filing Date column index
        if cells[0].name == "th":
            date_col = _find_date_col(cells)
            continue

        ncells = len(cells)

        # Filer row — 3 cells with same content containing CIK
        if ncells == 3:
            text = cells[0].get_text(strip=True)
            cik = _parse_cik(text)
            if cik:
                company = re.sub(r"\s*\(\d+\).*", "", text).strip()
                pending_cik = cik
                pending_company = company
            continue

        # Data row — 5 or 6 cells with filing info
        if ncells in (5, 6) and pending_cik is not None and date_col >= 0:
            form_type = cells[0].get_text(strip=True)

            date_text = cells[date_col].get_text(strip=True) if date_col < ncells else ""
            try:
                filing_date = datetime.strptime(date_text, "%Y-%m-%d").date()
            except ValueError:
                pending_cik = None
                pending_company = None
                continue

            accession_number = _extract_accno_from_link(cells[1])
            if not accession_number:
                pending_cik = None
                pending_company = None
                continue

            filings.append(Filing(
                cik=pending_cik,
                company_name=pending_company or "",
                form_type=form_type,
                filing_date=filing_date,
                accession_number=accession_number,
            ))
            pending_cik = None
            pending_company = None

    return filings


def browse_current() -> list[Filing]:
    return _parse_page(_request_page({
        "company": "",
        "CIK": "",
        "type": "",
        "owner": "include",
        "count": "100",
        "action": "getcurrent",
    }))


def browse_since(from_date: date, to_date: Optional[date] = None) -> list[Filing]:
    if to_date is None:
        to_date = date.today()

    all_filings: list[Filing] = []
    start = 0
    count = 100

    while True:
        params = {
            "company": "",
            "CIK": "",
            "type": "",
            "owner": "include",
            "count": str(count),
            "start": str(start),
            "action": "getcurrent",
            "datea": _date_to_sec(from_date),
            "dateb": _date_to_sec(to_date),
        }
        filings = _parse_page(_request_page(params))
        if not filings:
            break
        all_filings.extend(filings)
        if len(filings) < count:
            break
        start += count

    return all_filings


def download_filing_text(filing: Filing) -> str:
    cik_clean = filing.cik.lstrip("0") or filing.cik
    acc_no_dashes = filing.accession_number.replace("-", "")
    url = f"{SEC_ARCHIVES_URL}/edgar/data/{cik_clean}/{acc_no_dashes}/{filing.accession_number}.txt"
    response = requests.get(url, headers=_headers())
    response.raise_for_status()
    _rate_limit()
    return response.text


# Legacy entrypoint — kept for compatibility.
def request_edgar_api():
    return _request_page({
        "company": "",
        "CIK": "",
        "type": "",
        "owner": "include",
        "count": "100",
        "action": "getcurrent",
    })
