# Progress Log

> Update this file at the end of every work session.
> AI assistants: read this right after `CLAUDE.md`.

## Current status
- **Current day / sprint:** Day 2 — ingestion
- **Last updated:** 2026-11-20

## Session log

### 2026-11-19
- **Done:** Planned the project; agreed on dataset, stack, rules (`CLAUDE.md`).
- **Next:** Create the repo, set up uv, build the folder structure, explore the API by hand, write `docs/data_profile.md`.
- **Blockers / questions:** —
- **New concepts learned:** —

### 2026-11-19 (session 2)
- **Done:** Set up repo, uv environment, folder structure, rules files. First PR reviewed and merged.
- **Next:** Part B: app token, explore data with SoQL, write docs/data_profile.md.
- **Blockers / questions:** —
- **New concepts learned:** PATH, uv, virtual environment, pyproject.toml, uv.lock, src layout, .gitignore/.gitkeep, Markdown, PR review, local vs remote.

### 2026-11-20
- **Done:** Got API app token (stored in .env). Profiled the source with SoQL: row counts, grain, pay basis, leave status, negative pay, missing boroughs. Wrote docs/data_profile.md.
- **Next:** Day 2: ingest.py, API → raw Parquet by fiscal year (pagination, logging, retries, idempotent).
- **Blockers / questions:** —
- **New concepts learned:** data profiling, grain, SoQL, reconciliation, share vs rate, systematic vs random missingness, PII hashing.

<!-- Copy this block for each new session:
### YYYY-MM-DD
- **Done:**
- **Next:**
- **Blockers / questions:**
- **New concepts learned:**
-->

## Parking Lot (ideas for after the MVP — do not build now)
- Docker image for the full pipeline
- Streamlit or Power BI dashboard on top of the marts
- Natural-language Q&A over the marts using the Claude API
- Fix the Olist repo (UTF-16 requirements.txt, leaked local paths, rename the repo)
