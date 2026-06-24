import json
from pathlib import Path
from typing import Optional

from engine.models.filing import Filing

DATA_DIR = Path("data/raw")


def _ensure_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def filing_path(filing: Filing) -> Path:
    return DATA_DIR / filing.cik / filing.accession_number.replace("-", "")


def save_filing(filing: Filing, text: str):
    dir_path = filing_path(filing)
    dir_path.mkdir(parents=True, exist_ok=True)

    meta = filing.model_dump()
    meta["filing_date"] = str(meta["filing_date"])
    with open(dir_path / "metadata.json", "w") as f:
        json.dump(meta, f, indent=2)
    with open(dir_path / "filing.txt", "w") as f:
        f.write(text)


def load_filing(cik: str, accession_no_dashes: str) -> Optional[tuple[Filing, str]]:
    dir_path = DATA_DIR / cik / accession_no_dashes
    if not dir_path.exists():
        return None
    with open(dir_path / "metadata.json") as f:
        meta = json.load(f)
    with open(dir_path / "filing.txt") as f:
        text = f.read()
    return Filing(**meta), text


def list_filings() -> list[Filing]:
    _ensure_dir()
    filings = []
    for cik_dir in DATA_DIR.iterdir():
        if not cik_dir.is_dir():
            continue
        for acc_dir in cik_dir.iterdir():
            meta_path = acc_dir / "metadata.json"
            if meta_path.exists():
                with open(meta_path) as f:
                    filings.append(Filing(**json.load(f)))
    return filings
