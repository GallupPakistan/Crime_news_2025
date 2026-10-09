# Crime News Dashboard — Design Spec

Date: 2026-10-08
Status: Draft for review

## 1. Purpose

A professional, multi-page Streamlit dashboard over the combined 2025 Pakistan
crime news dataset (Urdu and English news in one Excel file). The audience is
client and management presentation, so the result must look polished and
consistent. The dashboard contains headings and visuals only: no generated
insight text, no estimates.

## 2. Principles (agreed with the user)

1. **No estimates.** Only values that exist in the columns are shown. No
   keyword-derived or guessed groupings.
2. **One dataset, one set of charts.** Urdu and English news live in the same
   dataset; `Language` is a filter and a colour dimension, not a separate app.
3. **Modular code.** All chart configuration lives in a single `charts.py`.
   Pages only call chart functions and arrange layout. Design, top bar and
   sidebar each have their own file, and every page has its own file.
4. **Clean, professional English** in all code comments, labels and console
   messages.
5. **Step-by-step delivery** with review between stages.

## 3. Source data

File: `Crime_News_Analysis.xlsx`, sheet `Data` (20,511 rows, 16 columns).

| Column | Letter | Use in dashboard |
|---|---|---|
| Published_Date | A | Time analysis, filters |
| City | B | Not used (raw) |
| Crime_Type | C | News Explorer table only (raw label) |
| Accused, Motive, Method, Police_Action, Victim_Details | D-F, I-J | Not used in charts (bilingual raw text); Explorer table may show them |
| Deaths, Injured | G, H | Casualties (see section 5) |
| Summary | K | News Explorer (original language, RTL for Urdu) |
| Source_Name | L | Sources, filters |
| Source_URL | M | News Explorer link |
| Language | N | Global filter, colour dimension |
| City_Standard | O | Geography, filters |
| Crime_Category | P | Categories, filters (37 English values shared by both languages) |

Filters and charts use `Crime_Category` (P) and `City_Standard` (O). The raw
`Crime_Type` (C) is never used for filtering, so an Urdu label such as
"سائبر کرائم" is counted under "Cybercrime" together with the English rows.

## 4. Data preparation (`prepare_data.py`)

Runs once and writes `data/crime.parquet`.

1. Keep rows with `Published_Date` in 2025 (20,482 rows). The 29 rows dated
   outside 2025 are excluded.
2. Merge the source typo `City42_Urdu_Crime_News_2025` into `City42 News`.
3. **City aliasing.** 1,038 Urdu rows keep an Urdu-script `City_Standard`
   value. A small `CITY_ALIASES` dictionary maps an Urdu name to its English
   name only when that English name already exists in the dataset (for example
   حیدرآباد → Hyderabad, سبی → Sibi, پارا چنار → Parachinar). All other Urdu
   city names stay unchanged.
4. Add derived columns: `Month`, `Weekday`, `Date`.
5. **Casualty columns** (see section 5): `Deaths_Exact`, `Injured_Exact`,
   `Deaths_Status`, `Injured_Status`, `Fatal` flag.

## 5. Casualty rules

`Deaths` and `Injured` contain numbers and some text ("Multiple", "Dozens",
"2; 1"). Nothing is guessed.

- **Exact:** value parses to a number between 0 and 50. Used in sums and
  averages.
- **Above 50:** numeric but greater than 50 (for example 47,000). Excluded from
  sums, reported separately as a count and listed in a "mass-casualty" table.
- **Not specified:** text values. Excluded from sums, reported as a count.
- **Fatal news** = news with an exact or above-50 deaths value of at least 1.
  Text values are not counted as fatal.

The Casualties page shows the three counts in a small note beneath the KPIs.

## 6. Architecture

```
crime_dashboard/
├── app.py                 # page config, navigation, wiring
├── config.py              # paths, column names, constants
├── data.py                # parquet load (cached), filter application
├── prepare_data.py        # Excel -> parquet
├── design.py              # palette, fonts, global CSS, spacing/ratio constants
├── topbar.py              # top header bar
├── sidebar.py             # global filters
├── charts.py              # ALL chart definitions and shared Plotly layout config
├── components.py          # KPI card, section heading helpers
├── data/crime.parquet
└── pages/
    ├── overview.py
    ├── crime_categories.py
    ├── geography.py
    ├── casualties.py
    ├── time_analysis.py
    ├── sources_language.py
    └── news_explorer.py
```

Rules:
- `charts.py` holds every chart as a function that takes a DataFrame and
  returns a Plotly figure (for example `monthly_trend(df)`, `category_bar(df)`,
  `calendar_heatmap(df)`). Common layout (fonts, margins, hover, legend, colours)
  is defined once there.
- Pages contain layout only: columns, headings and `st.plotly_chart(charts.x(df))`.
- `design.py` is the single source for colours, CSS and column ratios.

## 7. Global filters (sidebar)

- **Language:** All (default), Urdu, English.
- **Month range**, **Crime Category** (multi-select, all 37 always listed), **Source**.

Filters apply to every page. A category with no rows in the selected language
stays in the list and simply shows a count of 0.

## 8. Language handling

- One unified dataset. With "All" selected, charts that can be split are
  coloured by language (Urdu / English).
- Dashboard labels are in English. Urdu appears only in the Summary text of the
  News Explorer (right-to-left, Nastaliq font).
- Sources & Language page uses percentage shares, not counts, because Urdu is
  about 77% of the news and English about 23%.
- A short note on that page states that differences reflect news coverage by
  the sources, not the underlying crime. Urdu sources cover smaller towns more;
  English sources cover Karachi, Islamabad and terrorism more.

## 9. Pages and visuals (6-8 per page)

1. **Overview:** 5 KPI cards (News, Cities, Sources, Categories, Fatal News),
   monthly trend by language, language donut, top 10 categories, top 10 cities,
   daily calendar heatmap.
2. **Crime Categories:** category ranking (top 15 + Other), month × category
   heatmap, monthly trend of top 5 categories, treemap, category × weekday
   heatmap, fatal vs non-fatal news by category.
3. **Geography:** top 15 cities, city × category heatmap, monthly trend of top
   5 cities, language mix per city, fatal news count per city, Not Specified
   share.
4. **Casualties:** Deaths and Injured KPIs, monthly casualties trend, deaths by
   category, injured by category, top 10 cities by deaths, news with casualties
   by category, plus the three-count note and mass-casualty table.
5. **Time Analysis:** daily news trend, weekday bars, month × weekday heatmap,
   10 busiest days, category × month heatmap, daily trend by language.
6. **Sources & Language:** source ranking, source × language, source-wise
   category mix, Urdu vs English category share (%), source-wise city coverage,
   monthly volume per source.
7. **News Explorer:** filterable table (Date, City, Category, Source, Language,
   raw Crime_Type, Summary, link) with CSV download.

Long tails: category and city charts show the top N plus "Other". Cities
marked "Not Specified" are reported separately.

## 10. Visual design

This dashboard does not use the gold and navy/black style of the user's other
dashboards. It has its own red-based identity.

- **Palette (defined once in `design.py`):** page background soft off-white
  `#F7F4F3`; cards white with a thin warm-grey border and a light shadow;
  primary crimson `#B3202A`; deep maroon `#6E0F1A` for the top bar and headings;
  rose tints `#F3D4D6` and `#E8A3A8` for highlights and heatmap lows; slate
  `#64748B` as the neutral second colour; body text dark slate `#2B2F36`.
  No gold and no black.
- **Language colours (fixed on every chart):** Urdu = crimson `#B3202A`,
  English = slate `#64748B`.
- **Sequential scale for heatmaps:** off-white → rose → crimson → maroon.
- **Top bar (`topbar.py`):** a full-width maroon-to-crimson gradient banner
  with the dashboard title, a period badge and a record-count badge. Its
  background carries a crime-themed pattern drawn only with code (inline SVG
  and CSS gradients, no image files): faint diagonal crime-scene-tape stripes
  along the edge, a fingerprint made of concentric arcs on the right, a city
  skyline silhouette along the bottom, and a few numbered evidence markers
  with a subtle map-grid and crosshair. All shapes are low-opacity so the
  title stays readable.
- **Typography:** a clean sans-serif for UI and numbers, a serif display font
  for page headings. Urdu text is right-to-left with an Urdu-capable font.
- **Layout:** KPI rows use equal columns; chart rows use 1:1 or 2:1 ratios
  defined in `design.py`; consistent card padding and section-heading style on
  every page.

## 11. Error handling and testing

- `data.py` fails with a clear message if `crime.parquet` is missing and tells
  the user to run `prepare_data.py`.
- Charts return an empty-state figure ("No data for the selected filters")
  instead of raising.
- Verification: row-count checks after preparation (2025 rows, language totals,
  category totals equal Analysis sheet), casualty-rule counts, and a smoke test
  that imports every page and builds every chart with the full dataset and with
  each language filter.

## 12. Delivery stages (review between stages)

1. Data preparation and checks (`prepare_data.py`, `config.py`, `data.py`).
2. App shell: `design.py`, `topbar.py`, `sidebar.py`, `components.py`, `app.py`.
3. Overview page with its charts in `charts.py`.
4. Remaining pages, one at a time.
5. Final polish and run instructions (Windows, PowerShell, virtual environment).

## 13. Out of scope

Province view, keyword-based groupings (Police Action, Method, Motive, Women &
Children), cross-language duplicate detection, translation of Urdu text.
