"""Sources & Language page."""
import streamlit as st

import charts
import components as UI
import design as D


def render(df) -> None:
    UI.page_header("Sources & Language", "Coverage by newspaper and by news language")
    if df.empty:
        UI.empty_state()
        return

    UI.note(
        "<b>Reading this page.</b> Urdu news is about three quarters of the dataset, so Urdu and English "
        "are compared as <b>shares (%)</b>, not counts. Differences between them describe what each group of "
        "sources chooses to cover, not the underlying level of crime: Urdu sources report more from smaller "
        "towns, English sources more from Karachi and Islamabad and more on terrorism."
    )
    UI.spacer()

    left, right = st.columns(D.RATIO_1_1, gap=D.GAP)
    with left:
        UI.chart_card("News by Source", charts.source_ranking(df), "src_rank",
                      "Colour shows the language of the source")
    with right:
        UI.chart_card("Category Share: Urdu vs English", charts.language_category_share(df), "src_lang_cat",
                      "Share of each language's own news")

    left, right = st.columns(D.RATIO_1_1, gap=D.GAP)
    with left:
        UI.chart_card("Category Mix by Source", charts.source_category_heatmap(df), "src_cat_mix",
                      "Share (%) of each source's news in the top 10 categories")
    with right:
        UI.chart_card("Monthly Volume by Source", charts.source_month_heatmap(df), "src_month",
                      "News per month")

    left, right = st.columns(D.RATIO_1_1, gap=D.GAP)
    with left:
        UI.chart_card("Cities Covered by Source", charts.source_city_coverage(df), "src_cities",
                      "Number of different cities named")
    with right:
        UI.chart_card("Monthly Language Share", charts.language_monthly_share(df), "src_lang_month",
                      "Share of each month's news")

    UI.chart_card("City Share: Urdu vs English", charts.language_city_share(df), "src_lang_city",
                  "Share of each language's own news from the top 10 cities")
