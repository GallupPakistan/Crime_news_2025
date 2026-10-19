"""Overview page."""
import importlib
import streamlit as st

import charts
if not hasattr(charts, "calculate_crime_index"):
    charts = importlib.reload(charts)

import components as UI
import config as C
import design as D


def render(df) -> None:
    UI.page_header("Overview", "Volume, language mix, leading categories and cities at a glance")
    if df.empty:
        UI.empty_state()
        return

    cities = df.loc[df[C.COL_CITY] != C.NOT_SPECIFIED_CITY, C.COL_CITY].nunique()
    idx_df = charts.calculate_crime_index(df)
    if not idx_df.empty:
        latest_row = idx_df.iloc[-1]
        latest_idx = f"{latest_row['Index']:.1f}"
        latest_delta = latest_row["Delta_Base_Pct"]
        delta_sign = "+" if latest_delta > 0 else ""
        idx_sub = f"{latest_row['Month_Label']}: {delta_sign}{latest_delta:.1f}% vs Jan"
    else:
        latest_idx = "100.0"
        idx_sub = "Jan Base"

    UI.kpi_row([
        ("Total News", len(df), f"{df['Date'].min():%d %b} - {df['Date'].max():%d %b %Y}"),
        ("Crime Index (Jan=100)", latest_idx, idx_sub),
        ("Cities", cities, "Named in the news"),
        ("Sources", df[C.COL_SOURCE].nunique(), "Newspapers and channels"),
        ("Crime Categories", df[C.COL_CATEGORY].nunique(), "Standardised"),
        ("Fatal News", int(df["Fatal"].sum()), "Reports with at least 1 death"),
    ])
    UI.spacer()

    # Row 1: Monthly News Volume (Full analytical view)
    UI.chart_card("Monthly News Volume", charts.monthly_trend_by_language(df), "ov_monthly",
                  "News per month, split by language with % share")

    # Row 2: Monthly Crime Index Trend & MoM Growth Velocity
    left, right = st.columns(D.RATIO_1_1, gap=D.GAP)
    with left:
        UI.chart_card("Monthly Crime Index Trend (Jan 2025 = 100)", charts.crime_index_trend(df, height=360), "ov_index",
                      "Standardized benchmark tracking if months saw more or fewer crimes than January")
    with right:
        UI.chart_card("Month-over-Month (MoM) Growth Velocity", charts.monthly_growth_velocity(df, height=360), "ov_growth",
                      "Percentage change in news reporting compared to prior month")

    # Row 3: Language Split & Weekday Distribution in ONE ROW
    left, right = st.columns(D.RATIO_1_1, gap=D.GAP)
    with left:
        UI.chart_card("Language Split", charts.language_donut(df), "ov_lang",
                      "Share of Urdu and English news")
    with right:
        UI.chart_card("Weekday Distribution", charts.weekday_volume_distribution(df), "ov_weekday",
                      "Crime reporting distribution across days of the week with % share")

    # Row 4: Geographic Crime Map of Pakistan
    UI.chart_card("Geographic Crime Map of Pakistan", charts.pakistan_crime_map(df, height=440), "ov_map",
                  "Circle size = News volume; Heat color = Lethality (% fatal crimes)")

    # Row 5: Top Categories and Top Cities
    left, right = st.columns(D.RATIO_1_1, gap=D.GAP)
    with left:
        UI.chart_card("Top 10 Crime Categories", charts.top_categories_bar(df), "ov_cats",
                      "Ranked by frequency with percentage of total")
    with right:
        UI.chart_card("Top 10 Cities", charts.top_cities_bar(df), "ov_cities",
                      "Excludes news without a named city, with percentage share")

    # Row 6: Crime Severity & Lethality Matrix
    UI.chart_card("Crime Severity & Lethality Matrix", charts.crime_severity_matrix(df, height=380), "ov_matrix",
                  "Volume vs. Lethality Rate (% fatal incidents) across top crime categories")

    # Row 7: Daily News Calendar (Full width so day numbers are crystal clear)
    UI.chart_card("Daily News Calendar", charts.calendar_heatmap(df, height=240), "ov_calendar",
                  "Day-by-day crime volume with exact numbers inside each cell; darker indicates higher intensity")

