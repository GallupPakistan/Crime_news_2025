"""Overview page."""
import streamlit as st

import charts
import components as UI
import config as C
import design as D


def render(df) -> None:
    UI.page_header("Overview", "Volume, language mix, leading categories and cities at a glance")
    if df.empty:
        UI.empty_state()
        return

    cities = df.loc[df[C.COL_CITY] != C.NOT_SPECIFIED_CITY, C.COL_CITY].nunique()
    UI.kpi_row([
        ("Total News", len(df), f"{df['Date'].min():%d %b} - {df['Date'].max():%d %b %Y}"),
        ("Cities", cities, "Named in the news"),
        ("Sources", df[C.COL_SOURCE].nunique(), "Newspapers and channels"),
        ("Crime Categories", df[C.COL_CATEGORY].nunique(), "Standardised"),
        ("Fatal News", int(df["Fatal"].sum()), "Reports with at least 1 death"),
    ])
    UI.spacer()

    # Row 1: Monthly News Volume (Full analytical view)
    UI.chart_card("Monthly News Volume", charts.monthly_trend_by_language(df), "ov_monthly",
                  "News per month, split by language with % share")

    # Row 2: Language Split & Weekday Distribution in ONE ROW
    left, right = st.columns(D.RATIO_1_1, gap=D.GAP)
    with left:
        UI.chart_card("Language Split", charts.language_donut(df), "ov_lang",
                      "Share of Urdu and English news")
    with right:
        UI.chart_card("Weekday Distribution", charts.weekday_volume_distribution(df), "ov_weekday",
                      "Crime reporting distribution across days of the week with % share")

    # Row 3: Geographic Crime Map of Pakistan
    UI.chart_card("Geographic Crime Map of Pakistan", charts.pakistan_crime_map(df, height=440), "ov_map",
                  "Circle size = News volume; Heat color = Lethality (% fatal crimes)")

    # Row 4: Top Categories and Top Cities
    left, right = st.columns(D.RATIO_1_1, gap=D.GAP)
    with left:
        UI.chart_card("Top 10 Crime Categories", charts.top_categories_bar(df), "ov_cats",
                      "Ranked by frequency with percentage of total")
    with right:
        UI.chart_card("Top 10 Cities", charts.top_cities_bar(df), "ov_cities",
                      "Excludes news without a named city, with percentage share")

    # Row 5: Severity Matrix & MoM Growth Velocity
    left, right = st.columns(D.RATIO_1_1, gap=D.GAP)
    with left:
        UI.chart_card("Crime Severity & Lethality Matrix", charts.crime_severity_matrix(df), "ov_matrix",
                      "Volume vs. Lethality Rate (% fatal incidents) across top crime categories")
    with right:
        UI.chart_card("Month-over-Month (MoM) Growth Velocity", charts.monthly_growth_velocity(df), "ov_growth",
                      "Percentage change in news reporting compared to prior month")

    # Row 6: Daily News Calendar (Full width so day numbers are crystal clear)
    UI.chart_card("Daily News Calendar", charts.calendar_heatmap(df, height=240), "ov_calendar",
                  "Day-by-day crime volume with exact numbers inside each cell; darker indicates higher intensity")
