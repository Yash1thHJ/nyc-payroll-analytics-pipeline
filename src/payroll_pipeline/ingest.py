"""Download NYC payroll data from the Socrata API and save it as raw Parquet."""

from collections.abc import Iterator
import requests

from payroll_pipeline import config


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