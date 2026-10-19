"""Small reusable UI building blocks (headings, KPI cards, chart cards)."""
from __future__ import annotations

import html

import streamlit as st

import design as D


def page_header(title: str, subtitle: str = "") -> None:
    sub = f"<p>{html.escape(subtitle)}</p>" if subtitle else ""
    st.markdown(
        f'<div class="page-header"><h2>{html.escape(title)}</h2>{sub}<div class="rule"></div></div>',
        unsafe_allow_html=True,
    )


def kpi_card(label: str, value, sub: str = "") -> None:
    value_text = f"{value:,}" if isinstance(value, (int, float)) else str(value)
    sub_html = f'<div class="sub">{html.escape(sub)}</div>' if sub else ""
    st.markdown(
        f'<div class="kpi"><div class="label">{html.escape(label)}</div>'
        f'<div class="value">{value_text}</div>{sub_html}</div>',
        unsafe_allow_html=True,
    )


def kpi_row(items: list[tuple]) -> None:
    """Render KPI cards in equal columns. Each item is (label, value[, sub])."""
    cols = st.columns(len(items), gap=D.GAP)
    for col, item in zip(cols, items):
        with col:
            kpi_card(*item)


def chart_card(title: str, fig, key: str, subtitle: str = "") -> None:
    """A bordered card with a heading and a Plotly chart or fallback notice."""
    with st.container(border=True):
        st.markdown(f'<div class="card-title">{html.escape(title)}</div>', unsafe_allow_html=True)
        if subtitle:
            st.markdown(f'<div class="card-sub">{html.escape(subtitle)}</div>', unsafe_allow_html=True)
        try:
            actual_fig = fig() if callable(fig) else fig
            if actual_fig is None:
                st.info("ℹ️ Please select something to show.")
                return
            st.plotly_chart(
                actual_fig,
                key=key,
                width="stretch",
                config={"displayModeBar": False, "responsive": True},
            )
        except Exception:
            st.info("ℹ️ Please select something to show.")


def note(text: str) -> None:
    st.markdown(f'<div class="note">{text}</div>', unsafe_allow_html=True)


def empty_state(message: str = "Please select something to show.") -> None:
    """Render a clean, user-friendly empty state banner."""
    st.markdown(
        f'''
        <div class="empty-state" style="
            background: #FFFFFF;
            border: 1.5px dashed {D.BORDER};
            border-radius: 14px;
            padding: 2.8rem 1.8rem;
            text-align: center;
            margin: 1.2rem 0;
            box-shadow: 0 1px 8px rgba(110, 15, 26, 0.04);
        ">
            <div style="font-size: 2.2rem; margin-bottom: 0.6rem; color: {D.MAROON};">🔍</div>
            <div style="font-size: 1.15rem; font-weight: 600; color: {D.TEXT}; margin-bottom: 0.35rem;">
                {html.escape(message)}
            </div>
            <div style="font-size: 0.88rem; color: {D.TEXT_MUTED}; max-width: 500px; margin: 0 auto; line-height: 1.5;">
                No news records match the current filter selection. Try adjusting the months, selecting different categories/cities, or clicking <b>Reset</b> in the filter bar above.
            </div>
        </div>
        ''',
        unsafe_allow_html=True,
    )


def spacer(px: int = 8) -> None:
    st.markdown(f'<div style="height:{px}px"></div>', unsafe_allow_html=True)

