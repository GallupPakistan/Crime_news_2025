# SPEC.md — Project Specification: Crime Index & Quarterly Reports

> **Status**: `FINALIZED`
>
> ⚠️ **Planning Lock**: Requirements approved and finalized.

## Vision
Empower policy makers, researchers, journalists, and Gallup Pakistan analysts with a standardized **Crime Index (Jan 2025 = 100 Base)** and **Quarterly Crime Reports (Q1–Q4)**. Rather than relying solely on raw crime counts, this index tracks percentage shifts in crime reporting against the January 2025 baseline and structures the year into 4 executive quarterly intelligence reports.

## Goals
1. **Crime Index Engine (Jan 2025 = 100 Base)**:
   - Establish January 2025 as the benchmark (value = 100.0).
   - Track monthly index movement across 2025 (e.g. Feb 90.6, Mar 123.5) with delta percentage vs baseline.
   - Provide category-level index tracking to uncover which crimes escalated or declined relative to January.
2. **Dedicated "Crime Index & Quarterly Reports" Page**:
   - Executive-grade page with dual views: **Monthly Crime Index** and **Quarterly Intelligence Reports (Q1–Q4)**.
   - Interactive Quarter switcher (Q1, Q2, Q3, Q4, and Full Year Comparison).
   - Comprehensive quarterly breakdown: Total Crimes, Index, QoQ Growth %, Fatalities, Lethality Rate, Top Crimes, Top Cities, and Language share.
   - Printable / Exportable Quarterly Intelligence Briefing card with key takeaways and CSV export.
3. **Overview Page Integration**:
   - Add Crime Index summary KPI and chart to `pages/overview.py` so visitors immediately see the macro benchmark index.

## Non-Goals (Out of Scope)
- Predicting future crime rates for 2026 (this is historical 2025 indexation).
- Altering raw Excel source data schemas.

## Constraints
- Streamlit + Plotly Python stack.
- Comply with design system tokens in `design.py` (Inter typography, Crimson/Maroon/Steel Blue palette).
- All charts must handle filtered states (empty data, single category, filtered month ranges) gracefully.

## Success Criteria
- [ ] Crime Index accurately calculates Jan 2025 as 100.0 with correct relative indices for all months.
- [ ] New page `pages/crime_index.py` created and registered in `app.py`.
- [ ] Quarterly reporting accurately aggregates Q1 (Jan-Mar), Q2 (Apr-Jun), Q3 (Jul-Sep), Q4 (Oct-Dec) with QoQ growth and lethality.
- [ ] Overview page displays the Index KPI and comparative chart.
- [ ] Automated headless test / syntax check passes with 0 errors.

---

*Last updated: 2026-10-19*
