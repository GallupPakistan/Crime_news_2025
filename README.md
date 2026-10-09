# Pakistan Crime News Analytics Dashboard

Multi-page Streamlit dashboard over the 2025 Pakistan crime news dataset
(Urdu and English news in one workbook). Red theme with a code-drawn
crime-themed top bar (no image files).

## Run (Windows, PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python prepare_data.py        # Excel -> data/crime.parquet (already included)
streamlit run app.py
```

## Structure

| File | Purpose |
|---|---|
| `app.py` | Entry point: theme, navigation, top bar, sidebar filters |
| `config.py` | Paths, column names, casualty cap (50), source fixes, city aliases |
| `prepare_data.py` | Excel to parquet (2025 only, city aliases, casualty rules) |
| `data.py` | Cached load and filter application |
| `design.py` | Palette, fonts, global CSS, layout ratios |
| `topbar.py` | Top banner with code-drawn background |
| `sidebar.py` | Global filters: Language, Months, Crime category, Source |
| `charts.py` | Every chart definition (pages only call these functions) |
| `components.py` | Page header, KPI cards, chart cards |
| `pages/` | One file per page (layout only) |
| `tests/smoke_test.py` | Builds every chart for All / Urdu / English / empty filters |
| `docs/` | Design spec |

## Pages

Overview, Crime Categories, Geography, Casualties, Time Analysis,
Sources & Language, News Explorer.

## Data rules

- Filters and charts use `Crime_Category` and `City_Standard` (English values
  shared by Urdu and English rows). Raw `Crime_Type` appears only in the
  News Explorer table.
- Only rows dated 2025 are used (29 rows outside 2025 are excluded).
- Casualty totals count exact numbers up to 50 per news. Larger values and text
  values ("Multiple", "Dozens") are reported separately, never estimated.
- Urdu city names are mapped to an English name only when that English name
  already exists in the dataset (`CITY_ALIASES` in `config.py`).

## Status

Verified: data preparation numbers, 204 chart builds with no errors, and all
seven pages loaded in a browser with no errors and inspected visually.

Known data note: some `City_Standard` values are regions rather than cities
(for example Balochistan, Khyber Pakhtunkhwa), so they appear in city rankings.
