"""Pakistan Crime News Analytics - Streamlit entry point.

Run:  streamlit run app.py
"""
import streamlit as st

import charts
import config as C
import data
import design as D
import filterbar
import sidebar
import topbar
from pages import (casualties, crime_categories, crime_index, geography, news_explorer,
                   overview, sources_language, time_analysis)

st.set_page_config(
    page_title=C.APP_TITLE,
    page_icon=":material/policy:",
    layout="wide",
    initial_sidebar_state="expanded",
)
D.apply_theme()

full = data.load_data()
charts.configure(full)


def _make_page(module):
    """Wrap a page module so Streamlit can run it with the filtered data."""
    def run() -> None:
        module.render(st.session_state["filtered_df"])
    run.__name__ = module.__name__.split(".")[-1]
    return run


PAGES = [
    ("Overview", ":material/dashboard:", overview, True),
    ("Crime Index & Reports", ":material/trending_up:", crime_index, False),
    ("Crime Categories", ":material/category:", crime_categories, False),
    ("Geography", ":material/location_on:", geography, False),
    ("Casualties", ":material/healing:", casualties, False),
    ("Time Analysis", ":material/calendar_month:", time_analysis, False),
    ("Sources & Language", ":material/translate:", sources_language, False),
    ("News Explorer", ":material/search:", news_explorer, False),
]

pages_list = [
    st.Page(_make_page(module), title=title, icon=icon, default=default,
            url_path=module.__name__.split(".")[-1])
    for title, icon, module, default in PAGES
]

navigation = st.navigation(pages_list, position="hidden")

# Create two top placeholders in the main content container:
# 1. Topbar banner
# 2. Filter bar right below it
topbar_container = st.container()
filters_container = st.container()

with filters_container:
    filters = filterbar.render(full)

filtered = data.apply_filters(full, filters)
st.session_state["filtered_df"] = filtered

# Render topbar in its container at the very top
with topbar_container:
    topbar.render(len(filtered), len(full), filters.language, filters.month_range)

# Render full sidebar: Header Card -> Navigation Links -> Record Count Pill
sidebar.render(pages_list, len(filtered), len(full))

# Run the selected page
navigation.run()

