"""Crime Index & Quarterly Reports page.

Provides a standardized Base-100 Crime Index (Jan 2025 = 100) and
structured 4-Quarter (Q1-Q4) Executive Intelligence Reports.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

import charts
import components as UI
import config as C
import design as D


def render(df: pd.DataFrame) -> None:
    UI.page_header(
        "Crime Index & Quarterly Reports",
        "Standardized Base-100 Crime Index (Jan 2025 = 100) and 4-Quarter Executive Intelligence Briefings",
    )
    if df.empty:
        UI.empty_state()
        return

    # Calculate monthly index dataframe
    idx_df = charts.calculate_crime_index(df)
    
    if idx_df.empty:
        UI.empty_state("Insufficient data to compute monthly crime index.")
        return

    # High-level KPIs
    jan_row = idx_df[idx_df["Month"] == 1]
    jan_vol = int(jan_row["Volume"].iloc[0]) if not jan_row.empty else int(idx_df["Volume"].iloc[0])
    
    latest_row = idx_df.iloc[-1]
    latest_month = latest_row["Month_Label"]
    latest_idx = latest_row["Index"]
    latest_delta = latest_row["Delta_Base_Pct"]
    delta_sign = "+" if latest_delta > 0 else ""
    
    peak_row = idx_df.loc[idx_df["Index"].idxmax()]
    low_row = idx_df.loc[idx_df["Index"].idxmin()]
    avg_index = idx_df["Index"].mean()

    UI.kpi_row([
        ("Baseline (Jan 2025)", "100.0", f"{jan_vol:,} reported crimes (Base)"),
        (f"Latest Index ({latest_month})", f"{latest_idx:.1f}", f"{delta_sign}{latest_delta:.1f}% vs Jan baseline"),
        ("Peak Month Index", f"{peak_row['Index']:.1f}", f"{peak_row['Month_Label']} ({peak_row['Volume']:,} crimes)"),
        ("Lowest Month Index", f"{low_row['Index']:.1f}", f"{low_row['Month_Label']} ({low_row['Volume']:,} crimes)"),
        ("Annual Mean Index", f"{avg_index:.1f}", "Average 2025 index level"),
    ])
    UI.spacer(12)

    # Main Tabs: Monthly Index & Quarterly Intelligence Reports
    tab_monthly, tab_quarterly = st.tabs([
        "📈 Monthly Crime Index (Jan = 100)",
        "📑 Quarterly Intelligence Reports (Q1 – Q4)",
    ])

    # ------------------------------------------------------------- TAB 1: Monthly Index
    with tab_monthly:
        UI.spacer(6)
        
        # Primary Chart: Crime Index Trend with Baseline
        UI.chart_card(
            "Monthly Crime Index Trend (Jan 2025 = 100)",
            charts.crime_index_trend(df, height=390),
            "ci_trend",
            "Values above 100 indicate higher crime volume than January; values below 100 indicate lower crime volume.",
        )
        
        # Two columns: Category Trajectory & Table
        left, right = st.columns(D.RATIO_1_1, gap=D.GAP)
        with left:
            UI.chart_card(
                "Crime Index by Top Categories",
                charts.crime_index_by_category(df, top_n=5, height=390),
                "ci_cat",
                "Relative index movement for top crime categories indexed to their Jan volume.",
            )
        with right:
            with st.container(border=True):
                st.markdown('<div class="card-title">Monthly Index Benchmark Summary</div>', unsafe_allow_html=True)
                st.markdown('<div class="card-sub">Exact numbers and percentage shifts vs January benchmark</div>', unsafe_allow_html=True)
                
                # Styled Display Table
                display_table = idx_df[["Month_Label", "Volume", "Index", "Delta_Base_Pct", "MoM_Pct"]].copy()
                display_table.columns = ["Month", "News Volume", "Crime Index", "Vs Jan Base (%)", "MoM Shift (%)"]
                
                st.dataframe(
                    display_table.style.format({
                        "News Volume": "{:,}",
                        "Crime Index": "{:.1f}",
                        "Vs Jan Base (%)": "{:+.1f}%",
                        "MoM Shift (%)": "{:+.1f}%",
                    }),
                    hide_index=True,
                    use_container_width=True,
                    height=330,
                )

        # Methodology & Index Explanation Banner
        with st.container(border=True):
            st.markdown(
                """
                <div style="font-size: 13.5px; line-height: 1.6; color: #2B2F36;">
                    <b style="color: #6E0F1A; font-size: 15px;">📌 How the Crime Index Works (Methodology):</b><br>
                    • <b>Benchmark Base:</b> January 2025 is pegged at a standardized baseline value of <b>100.0</b>.<br>
                    • <b>Index Formula:</b> <code>Crime Index = (Current Month Crime Volume / January 2025 Crime Volume) × 100</code>.<br>
                    • <b>Interpretation:</b> An index of <b>114.6</b> in October means reported crimes were <b>14.6% higher</b> than in January. 
                    Conversely, an index of <b>90.6</b> in February signifies a <b>9.4% decline</b> relative to January.<br>
                    • <b>Public & Policy Value:</b> Eliminates confusion over raw volume fluctuations and provides a clean, macroeconomic-style benchmark for crime monitoring.
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ------------------------------------------------------------- TAB 2: Quarterly Reports
    with tab_quarterly:
        UI.spacer(6)
        
        # Quarter Selector
        q_options = [
            "All Quarters Overview",
            "Q1 2025 (Jan – Mar)",
            "Q2 2025 (Apr – Jun)",
            "Q3 2025 (Jul – Sep)",
            "Q4 2025 (Oct – Dec)",
        ]
        selected_q_view = st.pills("Select Quarterly Report View:", q_options, default=q_options[0])
        
        # Prepare quarterly dataset
        df_q = df.copy()
        df_q["Quarter_Code"] = "Q" + ((df_q["Month"] - 1) // 3 + 1).astype(str)
        
        if selected_q_view == "All Quarters Overview":
            # 4-Quarter High Level Performance
            left, right = st.columns(D.RATIO_1_1, gap=D.GAP)
            with left:
                UI.chart_card(
                    "Quarterly Volume & QoQ Growth",
                    charts.quarterly_performance_chart(df, height=370),
                    "q_vol_chart",
                    "Total crime reports per quarter with Quarter-over-Quarter (QoQ) % shift.",
                )
            with right:
                UI.chart_card(
                    "Quarterly Lethality & Casualties",
                    charts.quarterly_lethality_chart(df, height=370),
                    "q_lethal_chart",
                    "Fatal crime news volume and lethality rate (%) across the 4 quarters.",
                )
            
            # Bottom row: Category shift across quarters
            UI.chart_card(
                "Seasonal Category Shift Across Quarters",
                charts.quarterly_category_shift(df, top_n=6, height=380),
                "q_cat_shift",
                "How top crime categories evolved across Q1, Q2, Q3, and Q4.",
            )
            
            # Full 4-Quarter Comparative Table
            with st.container(border=True):
                st.markdown('<div class="card-title">4-Quarter Executive Performance Matrix (2025)</div>', unsafe_allow_html=True)
                
                q_summary = []
                q_codes = ["Q1", "Q2", "Q3", "Q4"]
                q_names = ["Q1 (Jan–Mar)", "Q2 (Apr–Jun)", "Q3 (Jul–Sep)", "Q4 (Oct–Dec)"]
                
                base_q1_vol = len(df_q[df_q["Quarter_Code"] == "Q1"])
                prev_vol = None
                
                for code, name in zip(q_codes, q_names):
                    sub = df_q[df_q["Quarter_Code"] == code]
                    vol = len(sub)
                    fatal = int(sub["Fatal"].sum())
                    deaths = int(sub["Deaths_Num"].sum())
                    injured = int(sub["Injured_Num"].sum())
                    lethality = (fatal / vol * 100) if vol > 0 else 0.0
                    idx = (vol / base_q1_vol * 100) if base_q1_vol > 0 else 100.0
                    
                    if prev_vol is None:
                        qoq = 0.0
                    else:
                        qoq = ((vol - prev_vol) / prev_vol * 100) if prev_vol > 0 else 0.0
                    prev_vol = vol
                    
                    top_cat = sub[C.COL_CATEGORY].value_counts().index[0] if not sub.empty else "N/A"
                    top_city = sub.loc[sub[C.COL_CITY] != C.NOT_SPECIFIED_CITY, C.COL_CITY].value_counts().index[0] if not sub.empty else "N/A"
                    
                    q_summary.append({
                        "Quarter": name,
                        "News Volume": vol,
                        "Quarterly Index (Q1=100)": idx,
                        "QoQ Shift (%)": qoq,
                        "Fatal News": fatal,
                        "Lethality Rate (%)": lethality,
                        "Total Deaths": deaths,
                        "Total Injured": injured,
                        "Leading Category": top_cat,
                        "Leading City": top_city,
                    })
                
                q_df = pd.DataFrame(q_summary)
                st.dataframe(
                    q_df.style.format({
                        "News Volume": "{:,}",
                        "Quarterly Index (Q1=100)": "{:.1f}",
                        "QoQ Shift (%)": "{:+.1f}%",
                        "Fatal News": "{:,}",
                        "Lethality Rate (%)": "{:.1f}%",
                        "Total Deaths": "{:,}",
                        "Total Injured": "{:,}",
                    }),
                    hide_index=True,
                    use_container_width=True,
                )
                
                # CSV Export button
                csv_data = q_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="📥 Download 4-Quarter Executive Summary (CSV)",
                    data=csv_data,
                    file_name="Gallup_Pakistan_Crime_Quarterly_Report_2025.csv",
                    mime="text/csv",
                    use_container_width=False,
                )
        
        else:
            # Individual Quarter Deep Dive Report
            q_code = selected_q_view[:2]  # "Q1", "Q2", "Q3", or "Q4"
            q_sub = df_q[df_q["Quarter_Code"] == q_code]
            
            if q_sub.empty:
                UI.empty_state(f"No records available for {selected_q_view}.")
            else:
                q_vol = len(q_sub)
                q_fatal = int(q_sub["Fatal"].sum())
                q_deaths = int(q_sub["Deaths_Num"].sum())
                q_injured = int(q_sub["Injured_Num"].sum())
                q_lethality = (q_fatal / q_vol * 100) if q_vol > 0 else 0.0
                
                # Baseline comparison: Q1 volume
                q1_vol = len(df_q[df_q["Quarter_Code"] == "Q1"])
                q_index = (q_vol / q1_vol * 100) if q1_vol > 0 else 100.0
                
                top_cats = q_sub[C.COL_CATEGORY].value_counts()
                top_cat_name = top_cats.index[0] if not top_cats.empty else "N/A"
                top_cat_vol = top_cats.iloc[0] if not top_cats.empty else 0
                top_cat_share = (top_cat_vol / q_vol * 100) if q_vol > 0 else 0.0
                
                valid_cities = q_sub.loc[q_sub[C.COL_CITY] != C.NOT_SPECIFIED_CITY, C.COL_CITY].value_counts()
                top_city_name = valid_cities.index[0] if not valid_cities.empty else "N/A"
                top_city_vol = valid_cities.iloc[0] if not valid_cities.empty else 0
                
                urdu_count = int((q_sub[C.COL_LANGUAGE] == "Urdu").sum())
                urdu_share = (urdu_count / q_vol * 100) if q_vol > 0 else 0.0

                # Executive Intelligence Briefing Card
                with st.container(border=True):
                    st.markdown(
                        f"""
                        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid {D.ROSE_LIGHT}; padding-bottom: 8px; margin-bottom: 14px;">
                            <div>
                                <h3 style="color: {D.MAROON}; margin: 0; font-family: {D.FONT_DISPLAY}; font-size: 22px;">
                                    Gallup Pakistan Quarterly Intelligence Briefing: {selected_q_view}
                                </h3>
                                <p style="color: {D.TEXT_MUTED}; margin: 4px 0 0 0; font-size: 13px;">
                                    Official Quarterly Analytical Release & Crime Monitoring Report
                                </p>
                            </div>
                            <div style="background: {D.ROSE_LIGHT}; color: {D.MAROON}; font-weight: 700; padding: 6px 14px; border-radius: 20px; font-size: 13px;">
                                Index: {q_index:.1f} (Q1=100)
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    
                    c1, c2, c3, c4, c5 = st.columns(5)
                    with c1:
                        st.metric("Total Crimes", f"{q_vol:,}")
                    with c2:
                        st.metric("Quarterly Index", f"{q_index:.1f}")
                    with c3:
                        st.metric("Fatal Crimes", f"{q_fatal:,}", f"{q_lethality:.1f}% lethality")
                    with c4:
                        st.metric("Casualties", f"{q_deaths:,} Deaths", f"{q_injured:,} Injured")
                    with c5:
                        st.metric("Language Share", f"{urdu_share:.1f}% Urdu", f"{100 - urdu_share:.1f}% English")
                    
                    UI.spacer(8)
                    st.markdown(
                        f"""
                        <div style="background: {D.BACKGROUND}; border-left: 4px solid {D.CRIMSON}; padding: 12px 16px; border-radius: 4px; font-size: 13.5px; line-height: 1.6;">
                            <b>Executive Key Findings for {selected_q_view}:</b><br>
                            • <b>Volume & Trajectory:</b> Reported crime volume stood at <b>{q_vol:,}</b> incidents, representing an overall Quarterly Index of <b>{q_index:.1f}</b>.<br>
                            • <b>Primary Crime Driver:</b> The leading category of concern was <b>{top_cat_name}</b>, accounting for <b>{top_cat_vol:,}</b> reports (<b>{top_cat_share:.1f}%</b> of all quarterly news).<br>
                            • <b>Geographic Epicenter:</b> The highest reporting density among named locations was registered in <b>{top_city_name}</b> with <b>{top_city_vol:,}</b> reports.<br>
                            • <b>Lethality & Casualties:</b> <b>{q_lethality:.1f}%</b> of incidents were fatal, resulting in <b>{q_deaths:,}</b> fatalities and <b>{q_injured:,}</b> injuries across the quarter.
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                
                UI.spacer(10)
                
                # Detailed Charts for this quarter
                q_left, q_right = st.columns(D.RATIO_1_1, gap=D.GAP)
                with q_left:
                    UI.chart_card(
                        f"Top 10 Crime Categories in {q_code}",
                        charts.top_categories_bar(q_sub),
                        f"q_top_cats_{q_code}",
                        f"Crime category distribution within {selected_q_view}",
                    )
                with q_right:
                    UI.chart_card(
                        f"Top 10 Reporting Cities in {q_code}",
                        charts.top_cities_bar(q_sub),
                        f"q_top_cities_{q_code}",
                        f"Urban distribution of reported crime in {selected_q_view}",
                    )
                
                # Download Quarter Data
                UI.spacer(6)
                q_export_data = q_sub[[
                    "Published_Date", "Month", "City_Standard", "Crime_Category",
                    "Language", "Source_Name", "Fatal", "Deaths_Num", "Injured_Num"
                ]].copy()
                csv_bytes = q_export_data.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label=f"📥 Download {q_code} 2025 Incident Data (CSV)",
                    data=csv_bytes,
                    file_name=f"Gallup_Crime_Data_{q_code}_2025.csv",
                    mime="text/csv",
                )
