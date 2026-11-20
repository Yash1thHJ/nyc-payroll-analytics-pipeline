# Data Profile: NYC Citywide Payroll

> Profiled on 2026-11-20 using SoQL queries against the NYC Open Data API.
> All figures below come from those queries (listed in section 8).
> This document is the basis for the cleaning rules, tests and metric
> definitions used in the pipeline.

---

## 1. Source

- **Dataset:** Citywide Payroll Data (Fiscal Year), published by the City of New York on NYC Open Data
- **Link:** https://data.cityofnewyork.us/d/k397-673e (dataset ID `k397-673e`)
- **Access method:** Socrata Open Data API (SoQL queries), JSON responses
- **Update frequency:** annually
- **Coverage:** fiscal years 2014 to 2026 (13 years). NYC's fiscal year runs from July 1 to June 30.
- **Size:** 7,337,410 rows in total, between 509,525 (FY2014, the smallest) and 613,008 (FY2022, the largest) per year

| Fiscal year | Rows |
|---|---:|
| 2014 | 509,525 |
| 2015 | 577,880 |
| 2016 | 544,817 |
| 2017 | 562,266 |
| 2018 | 546,161 |
| 2019 | 592,431 |
| 2020 | 590,210 |
| 2021 | 573,477 |
| 2022 | 613,008 |
| 2023 | 552,938 |
| 2024 | 562,898 |
| 2025 | 550,219 |
| 2026 | 561,580 |
| **Total** | **7,337,410** |

The yearly counts add up to the dataset's published total row count.

---

## 2. Columns

All 17 columns arrive from the API as **text**, including numbers and dates.

| Column | Meaning | Example |
|---|---|---|
| `fiscal_year` | Fiscal year of the payroll record (July 1 – June 30) | `2025` |
| `payroll_number` | Numeric code that appears to identify the payroll agency | `67` |
| `agency_name` | Name of the agency that paid the employee | `ADMIN FOR CHILDREN'S SVCS` |
| `last_name` | Employee's last name (PII) | *(not shown)* |
| `first_name` | Employee's first name (PII) | *(not shown)* |
| `mid_init` | Employee's middle initial (PII) | *(not shown)* |
| `agency_start_date` | Date the employee started at the agency | `2011-02-22T00:00:00.000` |
| `work_location_borough` | Borough or location where the employee works | `MANHATTAN` |
| `title_description` | Job title | `OCCUPATIONAL THERAPIST` |
| `leave_status_as_of_june_30` | Employment status on the last day of the fiscal year | `ACTIVE` |
| `base_salary` | Pay **rate**; its unit depends on `pay_basis` (annual, daily or hourly) | `88715.00` (annual), `73.14` (hourly) |
| `pay_basis` | How the employee is paid | `per Annum` |
| `regular_hours` | Regular hours worked in the fiscal year | `1820` |
| `regular_gross_paid` | Regular pay actually received in the fiscal year | `86914.91` |
| `ot_hours` | Overtime hours worked in the fiscal year | `354.75` |
| `total_ot_paid` | Overtime pay received in the fiscal year | `10000.28` |
| `total_other_pay` | All other pay received (e.g. adjustments, lump sums) | `21706.15` |

---

## 3. Grain

**One row = one pay record: a person's earnings under one agency, title, pay basis and work location in one fiscal year.**

A person can appear in more than one row in the same year.

**Evidence:**
- Grouping FY2025 rows by `payroll_number`, `last_name`, `first_name` and `agency_start_date` returned people with **2 rows** in the same year. Most of them were in payroll number 740, with a few in 469 and 463.
- Comparing one such person's two rows: the same agency (Department of Education Admin) and the same title (Occupational Therapist), but one row was **per Annum** (Manhattan) and the other **per Hour** (Queens). The person held a salaried arrangement and a separate hourly arrangement in the same year.

**Consequences:**
- **Row count ≠ headcount.** Counting employees needs a distinct count of people, not `COUNT(*)`.
- **There is no employee ID column.** A person can only be identified approximately, by combining `payroll_number`, `last_name`, `first_name`, `mid_init` and `agency_start_date`.
- **Total pay per person** must be summed across all of that person's rows.

---

## 4. Personal data (PII)

- **Columns that identify an individual:** `last_name`, `first_name`, `mid_init`
- **Columns that become identifying when combined with those:** `agency_start_date`, `title_description`, `work_location_borough`
- **Handling rule:** in the staging layer, the identifying columns are combined and **hashed** into a `person_key`, and the name columns are dropped. Names never appear in marts, reports, screenshots or the AI summary.
- **Known limitation:** the `person_key` is approximate. Two different people with identical names, agency and start date would be counted as one person.

---

## 5. Data quality observations

### 5.1 Data types
- Every value arrives as text (e.g. `"106346.00"`, `"2014"`), so all numeric and date fields need explicit type conversion in staging.
- `agency_start_date` is a timestamp whose time is always midnight (`T00:00:00.000`). It will be stored as a date.

### 5.2 `base_salary` depends on `pay_basis`

| pay_basis | Rows | Share |
|---|---:|---:|
| per Annum | 4,393,964 | 59.9% |
| per Day | 1,683,122 | 22.9% |
| per Hour | 1,229,156 | 16.8% |
| Prorated Annual | 31,168 | 0.4% |
| **Total** | **7,337,410** | 100% |

- No rows are missing `pay_basis`: the counts add up to the full total.
- `base_salary` is an annual salary for `per Annum` but a daily or hourly **rate** for the other values (confirmed: an hourly row had `base_salary` = 73.14). **Averaging `base_salary` across pay bases is meaningless.** Salary metrics must be filtered to, or split by, `pay_basis`.
- Casing is inconsistent (`per Annum` vs `Prorated Annual`) and will be standardised in staging.

### 5.3 Base salary vs actual pay
- `base_salary` is a rate; `regular_gross_paid` is what was actually received. They can differ a lot. For example, one sampled employee had a base salary of 127,802 but regular gross pay of 82,894. Likely causes are partial-year employment, leave or a title change.

### 5.4 Leave status is a year-end snapshot

| Leave status (as of June 30) | Rows | Share |
|---|---:|---:|
| ACTIVE | 6,238,163 | 85.0% |
| CEASED | 940,456 | 12.8% |
| ON LEAVE | 84,654 | 1.2% |
| SEASONAL | 60,902 | 0.8% |
| ON SEPARATION LEAVE | 13,235 | 0.2% |
| **Total** | **7,337,410** | 100% |

- No missing values.
- Because this is a snapshot on June 30, "headcount" has two valid definitions: everyone **paid** during the year, or everyone **active on June 30**. Reports must state which one they use.

### 5.5 Negative regular pay
- **16,629 rows (0.23%)** have negative `regular_gross_paid`.
- They are concentrated in employees who left or were on leave:

| Leave status | Negative rows | Share of negatives | Rate within that status |
|---|---:|---:|---:|
| CEASED | 14,468 | 87.0% | 1.54% |
| ON LEAVE | 1,092 | 6.6% | 1.29% |
| ACTIVE | 958 | 5.8% | 0.015% |
| SEASONAL | 111 | 0.7% | 0.18% |
| ON SEPARATION LEAVE | 0 | 0% | 0% |

- In sampled rows, large negative regular pay was often offset by large positive `total_other_pay` (e.g. −205,452 regular and +294,521 other).
- **Hypothesis (not confirmed):** these are payroll adjustments, such as recovered overpayments or pay reclassified into another category when an employee separates.
- **Handling rule:** keep and flag these rows (`is_negative_regular_pay`); include them in total spend; exclude them from "typical salary" statistics; analyse **total pay** (regular + overtime + other) rather than regular pay alone.

### 5.6 Missing work location borough
- **506,236 rows (6.9%)** have no `work_location_borough`.
- The missing values are **systematic**: 506,196 of them are in FY2014 (99.3% of that year's rows). Only 40 rows are missing across FY2015–FY2026 combined.
- **Handling rule:** do not impute. Borough analyses start at FY2015 or show FY2014 as "Not reported"; the 40 scattered rows are labelled `UNKNOWN`.

### 5.7 Missing agency name
- At least one sampled row (FY2026) had no `agency_name`. The API omits blank fields from its responses.
- The full count will be measured when the raw data is loaded (Day 3). These rows will be labelled `UNKNOWN`, not dropped.

---

## 6. Business questions

1. **Overtime concentration:** which agencies, job titles and boroughs account for the most overtime pay?
2. **Overtime growth:** which agencies' overtime spending has grown fastest from year to year?
3. **Workforce mix:** how have headcount and the mix of annual, daily and hourly workers changed from FY2015 to FY2026?
4. **Rate vs actual pay:** for annual-salaried employees, how large is the gap between base salary and total pay received, and where is it largest?
5. **Workforce turnover:** what share of each agency's paid workforce had ceased employment by the end of the year, and how has that changed over time?

---

## 7. Implications for the pipeline

| Finding | Pipeline decision |
|---|---|
| All values arrive as text | Cast types in staging; the pandera schema validates them |
| `base_salary` unit depends on `pay_basis` | Salary metrics always filtered to, or split by, pay basis |
| Multiple rows per person | Build a hashed `person_key`; headcount = distinct `person_key` |
| PII in name columns | Hash and drop in staging; never in outputs |
| Negative regular pay | Flag, keep, analyse total pay; test that alerts if the share rises above 1% |
| FY2014 borough not recorded | Borough analyses from FY2015; test that alerts if missing boroughs rise above 0.1% in later years |
| Leave status is a snapshot | Two documented headcount definitions |
| Missing agency names | Label `UNKNOWN`; measure the count on Day 3 |

---

## 8. Profiling queries (reproducible)

Base URL: `https://data.cityofnewyork.us/resource/k397-673e.json`

| Purpose | Query parameters |
|---|---|
| Rows per year | `?$select=fiscal_year,count(*)&$group=fiscal_year&$order=fiscal_year` |
| Sample rows | `?$limit=10` |
| Pay basis values | `?$select=pay_basis,count(*)&$group=pay_basis` |
| Leave status values | `?$select=leave_status_as_of_june_30,count(*)&$group=leave_status_as_of_june_30` |
| Negative regular pay | `?$select=count(*)&$where=regular_gross_paid<0` |
| Negative pay by status | `?$select=leave_status_as_of_june_30,count(*)&$where=regular_gross_paid<0&$group=leave_status_as_of_june_30` |
| Missing borough | `?$select=count(*)&$where=work_location_borough IS NULL` |
| Missing borough by year | `?$select=fiscal_year,count(*)&$where=work_location_borough IS NULL&$group=fiscal_year&$order=fiscal_year` |
| Grain check (FY2025) | `?$select=payroll_number,last_name,first_name,agency_start_date,count(*) as n&$where=fiscal_year=2025&$group=payroll_number,last_name,first_name,agency_start_date&$having=count(*)>1&$limit=20` |
