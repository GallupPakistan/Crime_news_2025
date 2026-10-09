"""Sidebar: clean navigation brand card, nav links, and dataset summary."""
from __future__ import annotations

import streamlit as st

import config as C


def render(
    pages: list[st.Page],
    shown: int = 0,
    total: int = 0,
) -> None:
    """Draw the full sidebar in order: brand card -> nav links -> dataset summary.

    Streamlit's st.page_link automatically sets aria-current="page" on the
    active link, and design.py has CSS that styles it with the maroon gradient.
    No manual active-index tracking is needed.
    """
    with st.sidebar:
        # 1. Header card at the very TOP
        st.markdown(
            f'''
            <div class="sb-brand-card">
                <div class="sb-eyebrow">MONITOR</div>
                <div class="sb-title">{C.APP_TITLE}</div>
                <div class="sb-desc">{C.DATA_YEAR} Analytics &amp; News Intel</div>
            </div>
            ''',
            unsafe_allow_html=True,
        )

        # 2. Navigation links directly BELOW the header card
        with st.container():
            for page in pages:
                st.page_link(page, use_container_width=True)

        # 3. Record count pill as the LAST element, pinned at the bottom
        share = (shown / total * 100) if total else 0
        st.markdown(
            f'<div class="sb-count">Showing {shown:,} of {total:,} news ({share:.0f}%)</div>',
            unsafe_allow_html=True,
        )


def render_brand() -> None:
    """Draw the clean brand block inside the sidebar."""
    with st.sidebar:
        st.markdown(
            f'''
            <div class="sb-brand-card">
                <div class="sb-eyebrow">MONITOR</div>
                <div class="sb-title">{C.APP_TITLE}</div>
                <div class="sb-desc">{C.DATA_YEAR} Analytics &amp; News Intel</div>
            </div>
            ''',
            unsafe_allow_html=True,
        )


def render_footer(shown: int, total: int) -> None:
    """Draw dataset coverage summary inside the sidebar."""
    share = (shown / total * 100) if total else 0
    with st.sidebar:
        st.markdown(
            f'<div class="sb-count">Showing {shown:,} of {total:,} news ({share:.0f}%)</div>',
            unsafe_allow_html=True,
        )

