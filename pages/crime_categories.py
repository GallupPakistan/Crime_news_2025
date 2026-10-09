"""Crime Categories page."""
import streamlit as st

import charts
import components as UI
import config as C
import design as D


def render(df) -> None:
    UI.page_header("Crime Categories", "Standardised crime category distribution, volume share and lethality analytics")
    if df.empty:
        UI.empty_state()
        return

    # Category Level KPI Row
    total_cats = df[C.COL_CATEGORY].nunique()
    top_cat = df[C.COL_CATEGORY].value_counts().index[0] if total_cats > 0 else "N/A"
    top_vol = df[C.COL_CATEGORY].value_counts().iloc[0] if total_cats > 0 else 0
    top_share = (top_vol / len(df) * 100) if len(df) > 0 else 0

    g = df.groupby(C.COL_CATEGORY).agg(total=("Fatal", "count"), fatal=("Fatal", "sum"))
    g = g[g["total"] >= 15]
    if not g.empty:
        most_fatal = (g["fatal"] / g["total"] * 100).idxmax()
        most_fatal_rate = (g["fatal"] / g["total"] * 100).max()
    else:
        most_fatal = "N/A"
        most_fatal_rate = 0.0

    total_deaths = int(df["Deaths_Exact"].sum())

    UI.kpi_row([
        ("Total Categories", total_cats, "Standardised groups"),
        ("Highest Volume", f"{top_vol:,}", f"{top_cat} ({top_share:.1f}% share)"),
        ("Most Lethal Category", f"{most_fatal_rate:.1f}%", f"{most_fatal} fatal rate"),
        ("Exact Deaths", f"{total_deaths:,}", "Total exact reported fatalities"),
    ])
    UI.spacer()

    # Section 1: Top Categories Volume Ranking
    UI.chart_card("Category Ranking & Language Split", charts.category_bar(df), "cat_rank",
                  "Top 15 categories ranked with % share of total crime news")

    # Section 2: Category Share Treemap (Standalone Row)
    UI.chart_card("Category Share Treemap", charts.category_treemap(df, height=360), "cat_tree",
                  "Visual tile proportion with direct category percentage badges")

    # Section 3: Risk & Lethality Dynamics
    left, right = st.columns(D.RATIO_1_1, gap=D.GAP)
    with left:
        UI.chart_card("Lethality Rate Ranking (% Fatal)", charts.category_lethality_ranking(df), "cat_lethality",
                      "Categories sorted by percentage of incidents resulting in deaths")
    with right:
        UI.chart_card("Fatal vs Non-fatal Composition", charts.fatal_by_category(df), "cat_fatal",
                      "100% normalized split showing fatal vs non-fatal ratio per category")

    # Section 4: Casualty Scale & Media Coverage
    left, right = st.columns(D.RATIO_1_1, gap=D.GAP)
    with left:
        UI.chart_card("Casualty Impact (Deaths vs Injuries)", charts.category_casualty_impact(df), "cat_casualties",
                      "Comparison of exact fatalities vs injuries across top categories")
    with right:
        UI.chart_card("Language Coverage Bias (% Urdu vs % English)", charts.category_language_bias(df), "cat_lang_bias",
                      "100% normalized language distribution across top categories")

    # Section 5: Monthly Volume Movement
    UI.chart_card("Top 5 Categories: Monthly Trend", charts.category_trend(df), "cat_trend",
                  "Volume movement over time with monthly category share % on hover")

    # Section 6: Weekday by Category Heatmap (Standalone Row)
    UI.chart_card("Weekday by Category Heatmap", charts.category_weekday_heatmap(df, height=360), "cat_weekday",
                  "Top 12 categories, reporting volume per day of week with cell numbers")
