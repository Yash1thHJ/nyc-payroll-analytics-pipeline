# Glossary

Plain-language definitions of every concept used in this project.
New terms are added here as we meet them.

## Pipeline basics

**Data pipeline**
A series of automatic steps that takes data from a source and turns it into
something useful (tables, reports). Like an assembly line: each station does
one job and passes the result on.

**Ingestion (`ingest.py`)**
"Ingest" means to take in. Ingestion is the first step: downloading data
from the source and saving it. `ingest.py` is simply the Python file that
does this step.

**ETL vs ELT**
- ETL = Extract, Transform, Load: clean the data *before* storing it.
- ELT = Extract, Load, Transform: store raw data first, then clean it
  inside the warehouse.
We use **ELT**: raw data is saved untouched, and cleaning happens later in DuckDB with dbt.
That way you can always go back to the original data.

**Idempotency**
A step is idempotent if running it once or ten times gives the same result.
For example, re-running ingestion for FY2024 replaces the FY2024 file instead of adding
duplicate rows. Analogy: pressing a lift button many times still calls one lift.

## Python project setup

**Module / package**
A module is one `.py` file of reusable code. A package is a folder of modules
(`src/payroll_pipeline/`). Unlike notebooks, these can be imported, tested and
run automatically.

**uv**
A fast, modern tool that creates the project's virtual environment and
installs libraries. It replaces `python -m venv` + `pip`, and keeps everyone's
library versions identical.

**pyproject.toml**
A settings file in the project root. It lists the project name, the Python
version and the libraries it needs. It's the modern replacement for requirements.txt.

**uv.lock (lock file)**
An auto-generated file that records the *exact* version of every library, so
the project installs the same way on any machine or in CI.

## Data source

**API**
Application Programming Interface: a way for programs to request data from
a server through a URL, instead of a human clicking "Download".

**Socrata API / SoQL**
NYC Open Data runs on a platform called Socrata. Its API lets you filter and
group data in the URL using SoQL, a SQL-like language
(`$select`, `$where`, `$group`, `$limit`, `$offset`).

**App token**
A free key from NYC Open Data that identifies your requests, so you aren't
throttled (slowed or blocked).

**Pagination**
APIs return data in pages (e.g. 50,000 rows at a time). Pagination means
requesting page after page until all rows are downloaded.

**Parquet**
A compressed, column-based file format. Much smaller and faster than CSV, and it
keeps data types such as dates and numbers.

## Validation and quality

**Schema**
The expected structure of a table: column names, data types, allowed values.

**pandera**
A Python library that checks a DataFrame against a schema ("salary must be a
number", "pay_basis must be one of these values"). If the data breaks the rules,
the pipeline stops with a clear error. It's like automated test cases for data, much like
the SQL validation you did in QA.

**Reconciliation**
Checking that totals match between stages (e.g. raw total gross pay = mart
total gross pay). You already did this manually in Olist; here it's automated.

## Warehouse and transformation

**Data warehouse**
A database designed for analysis (big reads and aggregations) rather than
for running an app.

**DuckDB**
A free analytical database that runs inside Python as a single file. There's no server
to install, unlike SQL Server, and you query it with normal SQL. It's very fast on millions of rows.

**dbt (data build tool)**
A tool where you write each transformation as a SQL `SELECT` file (a "model").
dbt runs the files in the right order, creates the tables, runs tests and
generates documentation. It's the industry standard for the transform step.

**Model layers: staging → intermediate → marts**
- **Staging:** a light clean of each raw table: rename columns, fix types,
  mask personal data. One staging model per source.
- **Intermediate:** joins and business logic built on staging.
- **Marts:** final, business-ready tables that answer questions
  (e.g. `mart_agency_overtime_by_year`). Reports read from here.
Analogy: raw ingredients → washed and chopped → cooked dish served.

**dbt tests**
Rules attached to models: `not_null`, `unique`, `accepted_values`,
`relationships`, plus custom SQL tests. `dbt test` runs them all.

## Code quality and automation

**pytest**
A Python library for writing automated tests for your Python functions.

**ruff**
A tool that checks code style and common mistakes, and auto-formats code.

**pre-commit**
Runs checks (like ruff) automatically every time you `git commit`, so bad
code never enters the repo.

**CI/CD**
- CI = Continuous Integration: every time code is pushed or a PR opens,
  tests run automatically on a fresh machine.
- CD = Continuous Delivery/Deployment: after the checks pass, results are
  published automatically (for us: the report goes to GitHub Pages).

**GitHub Actions**
GitHub's built-in automation. You write a YAML file describing the steps, and
GitHub runs them on its servers: on every PR (CI) or on a schedule.

**GitHub Pages**
Free website hosting from a GitHub repo. Our report gets a public link
recruiters can open.

## Security and AI

**Secrets / `.env`**
Private values (API keys, tokens). Locally they go in a `.env` file that Git
ignores; in GitHub Actions they go in GitHub Secrets.

**PII and masking**
PII = Personally Identifiable Information (e.g. names). Masking means
removing or hashing it so individuals can't be identified.

**Hashing**
Turning a value into a fixed scrambled code that can't be reversed. The same input always
gives the same code, so you can still count or join on it.

**LLM guardrail**
A code check around an AI step. Here, every number in the AI-written summary
is compared to DuckDB, and the run fails if anything doesn't match.
