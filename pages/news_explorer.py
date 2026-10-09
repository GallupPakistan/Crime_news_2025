"""News Explorer page: filterable table with original-language reading view."""
import html

import streamlit as st

import components as UI
import config as C

TABLE_COLUMNS = ["Published_Date", C.COL_CITY, C.COL_CATEGORY, C.COL_SOURCE, C.COL_LANGUAGE,
                 C.COL_CRIME_TYPE_RAW, "Deaths", "Injured", "Summary", "Source_URL"]


def render(df) -> None:
    UI.page_header("News Explorer", "Search and read the original news summaries")
    if df.empty:
        UI.empty_state()
        return

    query = st.text_input(
        "Search", placeholder="Search city, category, source or summary text (Urdu or English)",
        label_visibility="collapsed", key="explorer_search",
    )
    view = df
    if query.strip():
        q = query.strip()
        fields = [C.COL_CITY, C.COL_CATEGORY, C.COL_SOURCE, C.COL_CRIME_TYPE_RAW, C.COL_CITY_RAW, "Summary"]
        mask = False
        for col in fields:
            mask = mask | view[col].astype("string").str.contains(q, case=False, regex=False, na=False)
        view = view[mask]

    view = view.sort_values("Published_Date", ascending=False)
    top_left, top_right = st.columns([3, 1], gap="medium")
    with top_left:
        st.markdown(f"**{len(view):,}** news match. Select a row to read it.")
    with top_right:
        csv = view[TABLE_COLUMNS].to_csv(index=False).encode("utf-8-sig")
        st.download_button("Download CSV", csv, file_name="crime_news_filtered.csv",
                           mime="text/csv", width="stretch")

    table = view[TABLE_COLUMNS].rename(columns={
        "Published_Date": "Date", C.COL_CITY: "City", C.COL_CATEGORY: "Category",
        C.COL_SOURCE: "Source", C.COL_LANGUAGE: "Language", C.COL_CRIME_TYPE_RAW: "Crime Type (original)",
        "Source_URL": "Link",
    })
    event = st.dataframe(
        table, hide_index=True, width="stretch", height=430,
        on_select="rerun", selection_mode="single-row", key="explorer_table",
        column_config={
            "Date": st.column_config.DateColumn("Date", format="DD MMM YYYY"),
            "Summary": st.column_config.TextColumn("Summary", width="large"),
            "Link": st.column_config.LinkColumn("Link", display_text="Open"),
        },
    )

    rows = event.selection.rows if event and event.selection else []
    if rows:
        item = view.iloc[rows[0]]
        is_urdu = item[C.COL_LANGUAGE] == "Urdu"
        chips = "".join(
            f'<span class="meta-chip">{html.escape(str(v))}</span>'
            for v in (item["Published_Date"].strftime("%d %b %Y"), item[C.COL_CITY], item[C.COL_CATEGORY],
                      item[C.COL_SOURCE], item[C.COL_LANGUAGE])
        )
        css_class = "urdu-text" if is_urdu else "english-text"
        with st.container(border=True):
            st.markdown(
                f'<div class="card-title">Selected News</div>{chips}'
                f'<div class="{css_class}">{html.escape(str(item["Summary"]))}</div>',
                unsafe_allow_html=True,
            )
