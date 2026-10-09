"""Global filter bar rendered right beneath the top banner across all pages."""
from __future__ import annotations

import pandas as pd
import streamlit as st

import config as C
from data import Filters
import design as D

_KEYS = {
    "language": "flt_language",
    "months": "flt_months",
    "categories": "flt_categories",
    "sources": "flt_sources",
}


def _reset() -> None:
    st.session_state[_KEYS["language"]] = "All"
    st.session_state.pop(_KEYS["months"], None)
    st.session_state[_KEYS["categories"]] = []
    st.session_state[_KEYS["sources"]] = []


def render(full: pd.DataFrame) -> Filters:
    """Render a sleek horizontal filter bar right beneath the topbar."""
    month_numbers = sorted(full["Month"].unique().tolist())
    month_names = [C.MONTH_LABELS[m - 1] for m in month_numbers]
    categories = full[C.COL_CATEGORY].value_counts().index.tolist()
    sources = sorted(full[C.COL_SOURCE].unique().tolist())

    with st.container(border=True):
        st.markdown(
            f'''
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.4rem;">
                <div style="font-size:0.75rem; font-weight:700; letter-spacing:0.12em; text-transform:uppercase; color:{D.MAROON};">
                    Global Filters &amp; Controls
                </div>
            </div>
            ''',
            unsafe_allow_html=True,
        )

        c1, c2, c3, c4, c5 = st.columns([1.1, 1.4, 1.5, 1.4, 0.7], gap="medium")

        with c1:
            language = st.radio(
                "Language",
                ["All", "Urdu", "English"],
                key=_KEYS["language"],
                horizontal=True,
                help="Filter news by publication language",
            )
        with c2:
            month_sel = st.select_slider(
                "Months (Range)",
                options=month_names,
                value=(month_names[0], month_names[-1]),
                key=_KEYS["months"],
            )
            if isinstance(month_sel, str):
                month_sel = (month_sel, month_sel)

        with c3:
            chosen_categories = st.multiselect(
                "Crime Category",
                categories,
                key=_KEYS["categories"],
                placeholder="All categories",
            )

        with c4:
            chosen_sources = st.multiselect(
                "Source / Channel",
                sources,
                key=_KEYS["sources"],
                placeholder="All sources",
            )

        with c5:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            st.button("Reset", on_click=_reset, width="stretch", help="Reset all filters")

    first, last = month_sel
    return Filters(
        language=language,
        month_range=(
            C.MONTH_LABELS.index(first) + 1,
            C.MONTH_LABELS.index(last) + 1,
        ),
        categories=list(chosen_categories),
        sources=list(chosen_sources),
    )
