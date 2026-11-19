# CLAUDE.md — Project Charter & Working Rules
## NYC Payroll Analytics Pipeline

> **Read this file at the start of every session — human or AI.**
> Then read `docs/PROGRESS.md` to see where we left off.
> If anything in a conversation conflicts with this file, this file wins
> until it is changed through the Decision Log (section 12).

---

## 1. Purpose

Build an automated analytics pipeline that downloads NYC Citywide Payroll
data, validates it, transforms it, tests it, analyses it and publishes a
report (with an AI-written summary), on a schedule, without manual steps.

**Career goal:** a portfolio project that shows a recruiter for Data Analyst /
AI Data Analyst roles that Yashwanth can (1) analyse data rigorously and
(2) automate analytics to current industry standards.

**Story with the existing Olist project:**
Olist = careful manual analysis. This project = the same rigour, automated
and reproducible.

---

## 2. Roles

| Who | Role | Responsibilities |
|---|---|---|
| Yashwanth | Developer and project owner | Writes the code, makes final decisions, opens PRs, updates PROGRESS.md |
| Claude (chat) | Team lead and mentor | Plans sprints, teaches concepts, reviews PRs, keeps the project on track |
| Claude Code (VS Code) | Pair programmer | Explains, suggests and debugs code inside the editor, always following this file |

---

## 3. Locked decisions

These change only through the Decision Log (section 12).

| Area | Decision |
|---|---|
| Dataset | NYC Citywide Payroll Data (Fiscal Year), NYC Open Data, dataset id `k397-673e`, ~7.3M rows, updated annually |
| Language | Python 3.12 |
| Environment and dependencies | `uv` + `pyproject.toml` + `uv.lock` |
| Ingestion | Socrata API → raw Parquet files, one fiscal year at a time |
| Raw validation | pandera |
| Warehouse | DuckDB (single local file) |
| Transformations | dbt-core with the dbt-duckdb adapter |
| Data quality | dbt tests + custom reconciliation tests |
| Code quality | ruff, pytest, pre-commit |
| Automation | GitHub Actions (CI on every PR + scheduled pipeline run) |
| Report | Auto-generated HTML report published to GitHub Pages |
| AI layer | Claude API writes the executive summary; code verifies every number against DuckDB |
| Timeline | 10-day MVP (see section 11); polish after MVP |

---

## 4. Teaching rules (how Claude mentors)

1. **Explain theory before practice.** Before using any new concept or tool, Claude gives a short overview:
   - **What** it is, in plain language
   - **Why** teams use it (the problem it solves)
   - **An analogy** from everyday life or from Yashwanth's QA/payroll work
   - **Where** it fits in this project
2. **One new concept at a time.** Don't stack several unfamiliar tools in one step.
3. **Yashwanth asks follow-up questions** whenever needed; Claude answers before moving on.
4. **Concept checks.** After a concept, Claude may ask 1–3 short questions. Wrong answers are expected; they show what to re-teach.
5. **Plain language first.** Use simple words, define jargon the first time it appears, and add new terms to `docs/glossary.md`.
6. **Small, concrete steps.** Every task says exactly what to do, where, and how to check that it worked.

---

## 5. AI-use rules (for every AI assistant on this project)

1. Yashwanth writes or types the code himself. AI may explain, suggest, generate examples, debug and review.
2. **No code gets merged that Yashwanth can't explain line by line.** If he can't, the AI explains it until he can.
3. **No new tools, libraries or services** outside section 3 without Yashwanth's approval and a Decision Log entry.
4. **Never invent facts about the data.** Every claim about rows, values or totals must come from a query or a test output.
5. **Never invent experience** for resumes or the README. Describe only what was actually built.
6. **Secrets never go into code or Git.** API keys and tokens live in `.env` locally and in GitHub Secrets in CI.
7. **Stay in scope.** New ideas go to the Parking Lot in `docs/PROGRESS.md`. Nothing new gets built during the MVP.
8. **When unsure, ask** instead of guessing.

---

## 6. Workflow (how a real team works)

1. **Every task is a GitHub Issue** with a clear goal and a Definition of Done.
2. **One branch per issue:** `day-<n>/<short-name>`, e.g. `day-2/ingestion`.
3. **Small commits in present tense**, e.g. `Add fiscal-year ingestion with pagination`.
4. **Open a Pull Request** that describes what changed, why, and how it was tested.
5. **Claude reviews the PR.** Yashwanth fixes the comments, then merges.
6. **Never commit directly to `main`** once CI is set up (Day 9).
7. **End of session:** update `docs/PROGRESS.md`.

---

## 7. Engineering standards

- **No hard-coded paths.** All paths and settings come from `config.py` or environment variables, so the project runs on any machine.
- **Files are UTF-8.** Dependencies are pinned through `uv.lock`; never use `pip freeze >` in PowerShell.
- **Idempotent steps:** running any step twice gives the same result, with no duplicates.
- **Raw data stays untouched.** All cleaning happens in later layers.
- **Use `logging`, not `print`,** in pipeline code.
- **Small functions** with docstrings and type hints.
- **ruff passes** before every commit (enforced by pre-commit).
- **Every pipeline step has at least one test.**
- **Notebooks are for exploration only.** Pipeline logic lives in `src/payroll_pipeline/`.
- **No large data files in Git.** `data/` is git-ignored.

---

## 8. Data rules

- **Document the grain** (what one row represents) for every table in `docs/data_profile.md` and in dbt docs.
- **Mask personal data.** Employee names are dropped or hashed in the staging layer and never appear in marts, reports or screenshots.
- **Define every metric** in `docs/metrics.md` before it shows up in a report.
- **Reconcile:** totals must match from raw → staging → marts, and a test checks this.
- **Treat exceptions explicitly** (missing, negative or odd values). Don't drop them silently.
- **No causal claims** from descriptive data.
- **Numbers in the README and report come only from pipeline output,** never typed by hand.
- **The AI summary is verified:** every number it states is checked against DuckDB, and the run fails if any number doesn't match.

---

## 9. Honesty rules for portfolio and resume

- Describe the project as a **portfolio project**, not professional experience.
- Keep tools that were learned for this project separate from tools used at work.
- Every resume bullet must be backed by code that exists in the repo.

---

## 10. Definition of Done (for every task)

- [ ] The code works and Yashwanth can explain it
- [ ] Tests are added and passing
- [ ] ruff is clean
- [ ] Docs are updated (README, glossary or metrics, where relevant)
- [ ] The PR is reviewed and merged
- [ ] `docs/PROGRESS.md` is updated

---

## 11. Roadmap (10-day MVP)

| Day | Deliverable | Status |
|---|---|---|
| 1 | Repo, environment and folder structure; first manual look at the data; `docs/data_profile.md` | ☐ |
| 2 | `ingest.py`: API → raw Parquet by fiscal year, with pagination, logging, retries; idempotent | ☐ |
| 3 | pandera raw validation; load raw into DuckDB | ☐ |
| 4 | dbt setup + staging models (types, cleaning, personal-data masking) | ☐ |
| 5 | dbt intermediate + mart models (agency-year, overtime, headcount, pay basis) | ☐ |
| 6 | dbt tests + reconciliation tests | ☐ |
| 7 | Automated HTML report with charts | ☐ |
| 8 | AI summary with the Claude API + number-verification guardrail + anomaly flags | ☐ |
| 9 | GitHub Actions: CI on PRs, scheduled run, publish to GitHub Pages | ☐ |
| 10 | README, architecture diagram, resume bullets, mock interview | ☐ |

Learning new tools may stretch days. Quality comes before speed, but scope does not grow.

### Business questions (MVP)
1. Where is overtime spending concentrated (by agency, title and borough)?
2. Which agencies' overtime is growing fastest year over year?
3. How do headcount and pay basis (annual / hourly / per diem) change over time?
4. How large is the gap between base salary and total gross pay?

---

## 12. Decision Log

| Date | Decision | Reason |
|---|---|---|
| 2026-11-19 | Dataset: NYC Citywide Payroll | Real, large, messy, API-based; links to Yashwanth's payroll data-validation background; doesn't overlap Olist |
| 2026-11-19 | Stack as listed in section 3 | Matches current DA/analytics-engineering job requirements; all free except Claude API |
| 2026-11-19 | Claude API for the AI layer | Real LLM summaries; small pay-as-you-go cost approved |
| 2026-11-19 | 10-day MVP | Yashwanth wants the project portfolio-ready quickly |

---

## 13. Key risks and how we handle them

| Risk | Mitigation |
|---|---|
| API throttling or timeouts | Free app token, pagination, retries with backoff, ingest one year at a time |
| Large data (7.3M rows) | Parquet + DuckDB, no loading everything into pandas at once |
| Personal data in the source | Mask in staging; never shown in outputs |
| Source schema changes | pandera schema fails loudly on the first bad run |
| AI hallucinating numbers | The AI only receives computed metrics; a verification step fails the run on any mismatch |
| AI cost | Small prompts built from summary tables only; a dry-run mode needs no key |
| Leaked secrets | `.env` is git-ignored; GitHub Secrets; pre-commit check |
| Scope creep | Parking Lot; MVP first |
| Losing context between AI sessions | This file + `docs/PROGRESS.md`, read at the start of every session |
