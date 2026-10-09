"""Time Analysis page."""
import streamlit as st

import charts
import components as UI
import design as D


def render(df) -> None:
    UI.page_header("Time Analysis", "How news volume moves across days, weekdays and months")
    if df.empty:
        UI.empty_state()
        return

    UI.chart_card("Daily News Volume", charts.daily_trend(df), "time_daily",
                  "Daily count with a 7-day average")

    left, right = st.columns(D.RATIO_1_1, gap=D.GAP)
    with left:
        UI.chart_card("News by Weekday", charts.weekday_bars(df), "time_weekday")
    with right:
        UI.chart_card("Weekday by Month", charts.month_weekday_heatmap(df), "time_wd_month",
                      "News per weekday in each month")

    left, right = st.columns(D.RATIO_1_1, gap=D.GAP)
    with left:
        UI.chart_card("10 Busiest Days", charts.busiest_days(df), "time_busiest")
    with right:
        UI.chart_card("Daily Trend by Language", charts.daily_trend_by_language(df), "time_lang",
                      "7-day average per language")

    UI.chart_card("Category by Month", charts.category_month_heatmap(df, height=420), "time_cat_month",
                  "Top 12 categories, news per month")
