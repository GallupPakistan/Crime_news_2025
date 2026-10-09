"""Geography page."""
import streamlit as st

import charts
import components as UI
import design as D


def render(df) -> None:
    UI.page_header("Geography", "Where the news comes from: cities, categories and language coverage")
    if df.empty:
        UI.empty_state()
        return

    # ── Row 1: Top Cities (%) + City by Category Heatmap ──
    left, right = st.columns(D.RATIO_1_1, gap=D.GAP)
    with left:
        UI.chart_card("Top 15 Cities", charts.city_bar(df), "geo_cities",
                      "Share of total news coverage per city")
    with right:
        UI.chart_card("City by Category", charts.city_category_heatmap(df), "geo_heat",
                      "Top 12 cities and top 10 categories")

    # ── Row 2: City Lethality Rate + Casualty Severity ──
    left, right = st.columns(D.RATIO_1_1, gap=D.GAP)
    with left:
        UI.chart_card("City Lethality Rate", charts.city_lethality_rate(df), "geo_lethality",
                      "Percentage of news with at least 1 death — cities with 80+ news only")
    with right:
        UI.chart_card("Casualty Severity Index", charts.city_casualty_severity(df), "geo_severity",
                      "Deaths and injuries per 100 news — cities with 80+ news only")

    # ── Row 3: Monthly Trend + Language Mix ──
    left, right = st.columns(D.RATIO_1_1, gap=D.GAP)
    with left:
        UI.chart_card("Top 5 Cities: Monthly Trend", charts.city_trend(df), "geo_trend")
    with right:
        UI.chart_card("Language Mix by City", charts.city_language_mix(df), "geo_lang",
                      "Share of Urdu and English news in the top 10 cities")

    # ── Row 4: Fatal News by City ──
    left, right = st.columns(D.RATIO_2_1, gap=D.GAP)
    with left:
        UI.chart_card("Fatal News by City", charts.city_fatal_bar(df), "geo_fatal",
                      "Top 10 cities as share of all fatal news")
