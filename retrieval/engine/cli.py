from datetime import date, datetime, timedelta
from typing import Optional

import typer

from engine.fetching.browse import browse_current, browse_since, download_filing_text
from engine.store.storage import save_filing, list_filings
from engine.utils.timestamps import is_valid_timestamp, FORMATS

app = typer.Typer()


def _parse_timestamp(ts: str) -> date:
    if ts == "now":
        return date.today()
    for fmt in [f for f in FORMATS if f != "now"]:
        try:
            dt = datetime.strptime(ts, fmt)
            return dt.date()
        except ValueError:
            pass
    raise typer.BadParameter(f"Invalid timestamp format. Use one of: {FORMATS}")


@app.command()
def ingest(
    from_time: Optional[str] = typer.Argument(None, help="Start date (default: yesterday)"),
    to_time: Optional[str] = typer.Argument(None, help="End date (default: today)"),
):
    if from_time and not is_valid_timestamp(from_time):
        typer.echo(f"Invalid from_time. Valid formats: {FORMATS}")
        raise typer.Exit(code=1)
    if to_time and not is_valid_timestamp(to_time):
        typer.echo(f"Invalid to_time. Valid formats: {FORMATS}")
        raise typer.Exit(code=1)

    if from_time and to_time:
        from_date = _parse_timestamp(from_time)
        to_date = _parse_timestamp(to_time)
        typer.echo(f"Browsing filings {from_date} → {to_date} ...")
        filings = browse_since(from_date, to_date)
    else:
        typer.echo("Fetching latest batch of filings ...")
        filings = browse_current()

    if not filings:
        typer.echo("No filings found.")
        raise typer.Exit(code=0)

    typer.echo(f"Found {len(filings)} filings. Downloading ...")

    ok = 0
    fail = 0
    for f in filings:
        try:
            typer.echo(f"  [{f.form_type:>8}] {f.company_name} ({f.filing_date}) ... ", nl=False)
            text = download_filing_text(f)
            save_filing(f, text)
            typer.echo("OK")
            ok += 1
        except Exception as e:
            typer.echo(f"FAIL — {e}")
            fail += 1

    typer.echo(f"\nDone. {ok} saved, {fail} failed.")


@app.command()
def count(name: str = "", formal: bool = False):
    all_filings = list_filings()
    typer.echo(f"Total filings stored: {len(all_filings)}")
    if name:
        matching = [f for f in all_filings if name.lower() in f.company_name.lower()]
        typer.echo(f"Matching '{name}': {len(matching)}")
        if formal:
            for f in matching:
                typer.echo(f"  {f.filing_date} {f.form_type} {f.company_name} ({f.cik})")


if __name__ == "__main__":
    app()
