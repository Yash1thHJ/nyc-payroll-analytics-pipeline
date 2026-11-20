"""Download NYC payroll data from the Socrata API and save it as raw Parquet."""

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