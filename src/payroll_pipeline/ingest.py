"""Download NYC payroll data from the Socrata API and save it as raw Parquet."""

from collections.abc import Iterator
from pathlib import Path  # NEW

import pyarrow as pa  # NEW
import pyarrow.parquet as pq  # NEW
import requests

from payroll_pipeline import config

# NEW: the 17 columns we expect from the source, in a fixed order
RAW_COLUMNS = [
    "fiscal_year",
    "payroll_number",
    "agency_name",
    "last_name",
    "first_name",
    "mid_init",
    "agency_start_date",
    "work_location_borough",
    "title_description",
    "leave_status_as_of_june_30",
    "base_salary",
    "pay_basis",
    "regular_hours",
    "regular_gross_paid",
    "ot_hours",
    "total_ot_paid",
    "total_other_pay",
]

# NEW: raw layer keeps every column as text, exactly as the API sends it
RAW_SCHEMA = pa.schema([(name, pa.string()) for name in RAW_COLUMNS])


def fetch_page(fiscal_year: int, offset: int, limit: int = config.PAGE_SIZE) -> list[dict]:
    """Fetch one page of payroll rows for a fiscal year.

    Args:
        fiscal_year: The fiscal year to download, e.g. 2025.
        offset: How many rows to skip (0 for the first page).
        limit: Maximum number of rows to return.

    Returns:
        A list of rows, where each row is a dict of column name -> value.
    """
    params = {
        "$where": f"fiscal_year={fiscal_year}",
        "$order": ":id",
        "$limit": limit,
        "$offset": offset,
    }
    headers = {"X-App-Token": config.SOCRATA_APP_TOKEN} if config.SOCRATA_APP_TOKEN else {}

    response = requests.get(
        config.API_URL,
        params=params,
        headers=headers,
        timeout=config.REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()


def iter_pages(fiscal_year: int, page_size: int = config.PAGE_SIZE) -> Iterator[list[dict]]:
    """Yield pages of payroll rows for one fiscal year until all rows are fetched.

    Pages are yielded one at a time, so the whole year never has to sit in
    memory as Python dicts.

    Args:
        fiscal_year: The fiscal year to download, e.g. 2025.
        page_size: Number of rows to request per page.

    Yields:
        One page of rows (a list of dicts) per API request.
    """
    offset = 0
    while True:
        page = fetch_page(fiscal_year, offset, page_size)
        if not page:  # empty page: nothing left
            break
        yield page
        if len(page) < page_size:  # short page: this was the last one
            break
        offset += page_size


# NEW
def page_to_table(page: list[dict]) -> pa.Table:
    """Convert one page of API rows into an Arrow table with the raw schema.

    Every column is kept as text. Fields missing from a row become nulls.
    """
    columns = {name: [row.get(name) for row in page] for name in RAW_COLUMNS}
    return pa.table(columns, schema=RAW_SCHEMA)


# NEW
def raw_path(fiscal_year: int) -> Path:
    """Return the raw Parquet file path for a fiscal year."""
    return config.RAW_DIR / "payroll" / f"fiscal_year={fiscal_year}" / "data.parquet"


# NEW
def ingest_year(fiscal_year: int, page_size: int = config.PAGE_SIZE) -> Path:
    """Download one fiscal year and save it as a raw Parquet file.

    Returns:
        The path of the saved file.
    """
    tables = [page_to_table(page) for page in iter_pages(fiscal_year, page_size)]
    table = pa.concat_tables(tables)

    path = raw_path(fiscal_year)
    path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(table, path)
    return path