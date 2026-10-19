---
milestone: Crime Index & Quarterly Reports
version: 1.0.0
updated: 2026-10-19
---

# Roadmap: Crime Index & Quarterly Reports

> **Current Phase:** Complete
> **Status:** ✅ Complete

## Must-Haves (from SPEC)

- [x] Accurate calculation of monthly Crime Index with Jan 2025 = 100 benchmark.
- [x] Visual charts for Monthly Crime Index Trend with baseline indicator & Category Index comparison.
- [x] Visual charts & KPIs for Quarterly Analysis (Q1-Q4) with QoQ growth, fatalities, and top crimes.
- [x] Dedicated page `pages/crime_index.py` with Quarterly Intelligence Briefing and CSV export.
- [x] Integration of Crime Index into `pages/overview.py`.
- [x] Verification evidence and testing.

---

## Phases

### Phase 1: Core Crime Index & Quarterly Calculations in `charts.py`
**Status:** ✅ Complete
**Objective:** Add calculation helpers and Plotly chart functions for monthly crime index, category index, and quarterly performance metrics.

**Plans:**
- [x] Plan 1.1: Implement `calculate_crime_index()`, `crime_index_trend()`, `crime_index_by_category()`.
- [x] Plan 1.2: Implement `quarterly_performance_chart()`, `quarterly_category_shift()`, `quarterly_lethality_chart()`.

---

### Phase 2: Dedicated Page `pages/crime_index.py` & Navigation Registration
**Status:** ✅ Complete
**Objective:** Create the "Crime Index & Quarterly Reports" page with interactive quarter tabs, quarterly briefing cards, top crimes table, and export options. Register in `app.py`.
**Depends on:** Phase 1

**Plans:**
- [x] Plan 2.1: Create `pages/crime_index.py` featuring tabs for "Monthly Index Benchmark" and "Quarterly Intelligence Reports (Q1-Q4)".
- [x] Plan 2.2: Register page in `app.py` under `PAGES`.

---

### Phase 3: Overview Page Integration
**Status:** ✅ Complete
**Objective:** Add Crime Index summary KPI and chart to `pages/overview.py`.
**Depends on:** Phase 2

**Plans:**
- [x] Plan 3.1: Add Crime Index KPI and Index Trend chart to `pages/overview.py`.

---

### Phase 4: Verification & Automated Validation
**Status:** ✅ Complete
**Objective:** Validate end-to-end functionality, calculations, visual rendering, and ensure 0 errors.
**Depends on:** Phase 3

---

## Progress Summary

| Phase | Status | Plans | Complete |
|-------|--------|-------|----------|
| 1 | ✅ | 2/2 | 100% |
| 2 | ✅ | 2/2 | 100% |
| 3 | ✅ | 1/1 | 100% |
| 4 | ✅ | 1/1 | 100% |
