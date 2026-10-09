"""Casualties page."""
import pandas as pd
import streamlit as st

import charts
import components as UI
import config as C
import design as D


def render(df) -> None:
    UI.page_header("Casualties", "Deaths and injuries where the news reports an exact number")
    if df.empty:
        UI.empty_state()
        return

    deaths = int(df["Deaths_Exact"].sum())
    injured = int(df["Injured_Exact"].sum())
    UI.kpi_row([
        ("Deaths (exact)", deaths, f"Counts up to {C.CASUALTY_CAP} per news"),
        ("Injured (exact)", injured, f"Counts up to {C.CASUALTY_CAP} per news"),
        ("News with Casualties", int(df["Has_Casualty"].sum()), "At least 1 death or injury"),
        ("Fatal News", int(df["Fatal"].sum()), "At least 1 death"),
        ("Avg Deaths / Fatal News", round(deaths / max(int((df["Deaths_Exact"] >= 1).sum()), 1), 2), "Exact counts only"),
    ])
    UI.spacer(6)

    above_d = int((df["Deaths_Status"] == "above_cap").sum())
    above_i = int((df["Injured_Status"] == "above_cap").sum())
    na_d = int((df["Deaths_Status"] == "not_specified").sum())
    na_i = int((df["Injured_Status"] == "not_specified").sum())
    UI.note(
        f"<b>How casualties are counted.</b> Totals include only exact numbers up to {C.CASUALTY_CAP} per news. "
        f"News reporting more than {C.CASUALTY_CAP} are listed separately below "
        f"(deaths: <b>{above_d:,}</b>, injured: <b>{above_i:,}</b> news). "
        f"News where the number is not stated as a figure, for example \"Multiple\" or \"Dozens\", "
        f"are not counted (deaths: <b>{na_d:,}</b>, injured: <b>{na_i:,}</b> news)."
    )
    UI.spacer()

    left, right = st.columns(D.RATIO_1_1, gap=D.GAP)
    with left:
        UI.chart_card("Monthly Deaths and Injuries", charts.monthly_casualties(df), "cas_monthly")
    with right:
        UI.chart_card("Deaths by Category", charts.deaths_by_category(df), "cas_deaths_cat",
                      "Top 10 categories, exact counts")

    left, right = st.columns(D.RATIO_1_1, gap=D.GAP)
    with left:
        UI.chart_card("Injured by Category", charts.injured_by_category(df), "cas_inj_cat",
                      "Top 10 categories, exact counts")
    with right:
        UI.chart_card("Deaths by City", charts.deaths_by_city(df), "cas_deaths_city",
                      "Top 10 cities, exact counts")

    UI.chart_card("News with Casualties by Category", charts.casualty_news_by_category(df), "cas_news_cat",
                  "Top 10 categories; news with at least 1 death or injury")

    big = df[(df["Deaths_Status"] == "above_cap") | (df["Injured_Status"] == "above_cap")]
    with st.container(border=True):
        st.markdown(
            f'<div class="card-title">Reports with More than {C.CASUALTY_CAP} Casualties</div>'
            f'<div class="card-sub">Listed separately and excluded from the totals above ({len(big):,} news)</div>',
            unsafe_allow_html=True,
        )
        if big.empty:
            st.caption("No such reports for the selected filters.")
        else:
            table = big[["Date", C.COL_CITY, C.COL_CATEGORY, C.COL_SOURCE, C.COL_LANGUAGE,
                         "Deaths", "Injured", "Summary"]].sort_values("Date")
            table = table.rename(columns={C.COL_CITY: "City", C.COL_CATEGORY: "Category",
                                          C.COL_SOURCE: "Source", C.COL_LANGUAGE: "Language"})
            st.dataframe(
                table, hide_index=True, width="stretch", height=300,
                column_config={
                    "Date": st.column_config.DateColumn("Date", format="DD MMM YYYY"),
                    "Summary": st.column_config.TextColumn("Summary", width="large"),
                },
            )
