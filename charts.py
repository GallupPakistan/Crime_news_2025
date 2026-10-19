"""All chart definitions and shared Plotly configuration.

Every chart is a function that takes a (filtered) DataFrame and returns a
Plotly figure. Pages only call these functions; no Plotly code lives in pages.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.colors import sample_colorscale

import config as C
import design as D

LANGS = C.LANGUAGES
NOT_SPECIFIED = C.NOT_SPECIFIED_CITY

# Global entity order (set once from the full dataset so colours never shift
# when filters change).
_CATEGORY_RANK: dict[str, int] = {}
_CITY_RANK: dict[str, int] = {}


def configure(full: pd.DataFrame) -> None:
    """Register the global category and city ranking used for stable colours."""
    cats = full[C.COL_CATEGORY].value_counts().index.tolist()
    cities = (
        full.loc[full[C.COL_CITY] != NOT_SPECIFIED, C.COL_CITY].value_counts().index.tolist()
    )
    _CATEGORY_RANK.clear()
    _CATEGORY_RANK.update({c: i for i, c in enumerate(cats)})
    _CITY_RANK.clear()
    _CITY_RANK.update({c: i for i, c in enumerate(cities)})


# ============================================================ shared helpers
def _base_layout(fig: go.Figure, height: int, legend: bool = True, margin: dict | None = None) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=margin or dict(l=8, r=12, t=8, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=D.FONT_UI, size=12, color=D.TEXT),
        showlegend=legend,
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
            font=dict(size=11, color=D.TEXT_MUTED), bgcolor="rgba(0,0,0,0)",
            itemclick="toggleothers",
        ),
        hoverlabel=dict(bgcolor="#FFFFFF", bordercolor=D.BORDER, font=dict(family=D.FONT_UI, size=12, color=D.TEXT)),
        bargap=0.28,
    )
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor=D.BORDER, tickfont=dict(color=D.TEXT_MUTED, size=11))
    fig.update_yaxes(showgrid=True, gridcolor=D.GRID, zeroline=False, tickfont=dict(color=D.TEXT_MUTED, size=11))
    return fig


def _empty(message: str = "No data for the selected filters", height: int = D.CHART_HEIGHT) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(text=message, x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False,
                       font=dict(size=13, color=D.TEXT_MUTED))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return _base_layout(fig, height, legend=False)


def _present_langs(df: pd.DataFrame) -> list[str]:
    present = set(df[C.COL_LANGUAGE].unique())
    return [lang for lang in LANGS if lang in present]


def _month_range(df: pd.DataFrame) -> list[int]:
    return list(range(int(df["Month"].min()), int(df["Month"].max()) + 1))


def _month_names(months: list[int]) -> list[str]:
    return [C.MONTH_LABELS[m - 1] for m in months]


def _category_color(name: str) -> tuple[str, str]:
    """(colour, dash) for a category - fixed by its global rank, never cycled."""
    rank = _CATEGORY_RANK.get(name, 99)
    if rank < len(D.CATEGORICAL):
        return D.CATEGORICAL[rank], "solid"
    return D.TEXT_FAINT, "dot"


def _city_color(name: str) -> tuple[str, str]:
    rank = _CITY_RANK.get(name, 99)
    if rank < len(D.CATEGORICAL):
        return D.CATEGORICAL[rank], "solid"
    return D.TEXT_FAINT, "dot"


def _heatmap(matrix: pd.DataFrame, height: int, show_text: bool = True,
             colorbar_title: str = "News", fmt: str = ",d") -> go.Figure:
    if matrix.empty or matrix.to_numpy().sum() == 0:
        return _empty(height=height)
    z = matrix.to_numpy()
    text = np.where(z == 0, "", z.astype(int).astype(str)) if show_text else None
    fig = go.Figure(go.Heatmap(
        z=z, x=matrix.columns.tolist(), y=matrix.index.tolist(),
        colorscale=D.HEAT_SCALE, xgap=2, ygap=2,
        text=text, texttemplate="%{text}" if show_text else None,
        textfont=dict(size=10),
        colorbar=dict(thickness=10, len=0.9, title=dict(text=colorbar_title, font=dict(size=10)),
                      tickfont=dict(size=10), outlinewidth=0),
        hovertemplate="%{y}<br>%{x}: <b>%{z:" + fmt + "}</b><extra></extra>",
    ))
    _base_layout(fig, height, legend=False, margin=dict(l=8, r=8, t=8, b=8))
    fig.update_yaxes(showgrid=False, autorange="reversed")
    fig.update_xaxes(side="top", tickfont=dict(size=11, color=D.TEXT_MUTED))
    return fig


def _ranked_language_bar(
    df: pd.DataFrame, col: str, n: int, height: int, exclude: tuple[str, ...] = (),
    other: bool = False, unit: str = "news", show_percent: bool = False,
) -> go.Figure:
    """Horizontal ranked bars, stacked by language, with an end label."""
    d = df[~df[col].isin(exclude)]
    if d.empty:
        return _empty(height=height)
    totals = d[col].value_counts()
    top = totals.head(n).index.tolist()
    d = d.copy()
    if other and len(totals) > n:
        d[col] = d[col].where(d[col].isin(top), "Other")
        order = top + ["Other"]
    else:
        d = d[d[col].isin(top)]
        order = top
    table = d.groupby([col, C.COL_LANGUAGE]).size().unstack(fill_value=0).reindex(order).fillna(0).astype(int)
    langs = [lang for lang in LANGS if lang in table.columns]
    overall_total = len(df) if len(df) > 0 else 1
    fig = go.Figure()
    for lang in langs:
        hover_texts = []
        for cat_name, cnt in zip(order, table[lang]):
            pct = (cnt / overall_total * 100)
            hover_texts.append(f"{cat_name}<br>{lang}: <b>{cnt:,}</b> {unit} ({pct:.1f}%)")
        fig.add_bar(
            y=order, x=table[lang], orientation="h", name=lang,
            marker=dict(color=D.LANG_COLORS[lang], line=dict(color=D.SURFACE, width=2)),
            hovertext=hover_texts,
            hoverinfo="text",
        )
    total = table.sum(axis=1)
    if show_percent:
        labels = [f"{(v / overall_total * 100):.1f}%" for v in total]
    else:
        labels = [f"{v:,}" for v in total]
    fig.add_trace(go.Scatter(
        x=total, y=order, mode="text", text=labels, textposition="middle right",
        textfont=dict(size=11, color=D.TEXT), showlegend=False, hoverinfo="skip", cliponaxis=False,
    ))
    fig.update_layout(barmode="stack")
    _base_layout(fig, height, legend=len(langs) > 1)
    fig.update_yaxes(autorange="reversed", showgrid=False, automargin=True)
    fig.update_xaxes(showgrid=True, gridcolor=D.GRID, range=[0, float(total.max()) * 1.18])
    return fig


def _stacked_vbar(
    df: pd.DataFrame, x_values: list, x_labels: list[str], x_col: str, height: int,
    show_percent: bool = False,
) -> go.Figure:
    """Vertical bars stacked by language for an ordered x dimension."""
    if df.empty:
        return _empty(height=height)
    table = (df.groupby([x_col, C.COL_LANGUAGE]).size().unstack(fill_value=0)
             .reindex(x_values).fillna(0).astype(int))
    langs = [lang for lang in LANGS if lang in table.columns]
    overall_total = len(df) if len(df) > 0 else 1
    fig = go.Figure()
    for lang in langs:
        hover_texts = []
        for x_val, cnt in zip(x_labels, table[lang]):
            pct = (cnt / overall_total * 100)
            hover_texts.append(f"{x_val}<br>{lang}: <b>{cnt:,}</b> news ({pct:.1f}%)")
        fig.add_bar(
            x=x_labels, y=table[lang], name=lang,
            marker=dict(color=D.LANG_COLORS[lang], line=dict(color=D.SURFACE, width=2)),
            hovertext=hover_texts,
            hoverinfo="text",
        )
    total = table.sum(axis=1)
    if show_percent and not total.empty:
        labels = [f"{(v / overall_total * 100):.1f}%" if v > 0 else "" for v in total]
        fig.add_trace(go.Scatter(
            x=x_labels, y=total, mode="text", text=labels, textposition="top center",
            textfont=dict(size=10, color=D.TEXT), showlegend=False, hoverinfo="skip", cliponaxis=False,
        ))
        fig.update_yaxes(range=[0, float(total.max()) * 1.15])
    fig.update_layout(barmode="stack")
    return _base_layout(fig, height, legend=len(langs) > 1)


# ============================================================ OVERVIEW
def monthly_trend_by_language(df: pd.DataFrame, height: int = D.CHART_HEIGHT) -> go.Figure:
    if df.empty:
        return _empty(height=height)
    months = _month_range(df)
    return _stacked_vbar(df, months, _month_names(months), "Month", height, show_percent=True)


def language_donut(df: pd.DataFrame, height: int = D.CHART_HEIGHT) -> go.Figure:
    if df.empty:
        return _empty(height=height)
    counts = df[C.COL_LANGUAGE].value_counts().reindex(LANGS).dropna().astype(int)
    fig = go.Figure(go.Pie(
        labels=counts.index, values=counts.values, hole=0.62, sort=False,
        marker=dict(colors=[D.LANG_COLORS[x] for x in counts.index], line=dict(color=D.SURFACE, width=3)),
        textinfo="percent", textfont=dict(size=13, color="#FFFFFF"),
        hovertemplate="%{label}<br><b>%{value:,}</b> news (%{percent})<extra></extra>",
    ))
    fig.add_annotation(text=f"<b>{int(counts.sum()):,}</b><br><span style='font-size:11px;color:{D.TEXT_MUTED}'>news</span>",
                       x=0.5, y=0.5, showarrow=False, font=dict(size=22, color=D.MAROON, family=D.FONT_DISPLAY))
    _base_layout(fig, height, legend=True, margin=dict(l=8, r=8, t=8, b=8))
    fig.update_layout(legend=dict(orientation="h", x=0.5, xanchor="center", y=-0.02, yanchor="top"))
    return fig


def top_categories_bar(df: pd.DataFrame, n: int = 10, height: int = D.CHART_HEIGHT) -> go.Figure:
    return _ranked_language_bar(df, C.COL_CATEGORY, n, height, show_percent=True)


def top_cities_bar(df: pd.DataFrame, n: int = 10, height: int = D.CHART_HEIGHT) -> go.Figure:
    return _ranked_language_bar(df, C.COL_CITY, n, height, exclude=(NOT_SPECIFIED,), show_percent=True)


def calendar_heatmap(df: pd.DataFrame, height: int = 230) -> go.Figure:
    """Day-by-day heatmap: weeks on the x axis, weekdays on the y axis."""
    if df.empty:
        return _empty(height=height)
    start = pd.Timestamp(year=C.DATA_YEAR, month=int(df["Month"].min()), day=1)
    end = df["Date"].max()
    days = pd.date_range(start, end, freq="D")
    counts = df.groupby("Date").size().reindex(days, fill_value=0)
    first_monday = start - pd.Timedelta(days=start.weekday())
    week = ((days - first_monday).days // 7).astype(int)
    weekday = days.weekday
    n_weeks = int(week.max()) + 1
    z = np.full((7, n_weeks), np.nan)
    text_matrix = np.full((7, n_weeks), "", dtype=object)
    hover = np.full((7, n_weeks), "", dtype=object)
    overall_total = len(df) if len(df) > 0 else 1
    for d, w, wd, v in zip(days, week, weekday, counts.values):
        z[wd, w] = v
        text_matrix[wd, w] = str(int(v)) if v > 0 else ""
        pct = (v / overall_total * 100) if overall_total > 0 else 0
        hover[wd, w] = f"{d:%a, %d %b %Y}<br><b>{v:,}</b> news ({pct:.2f}%)"
    tick_weeks, tick_text = [], []
    for m in range(int(df["Month"].min()), int(df["Month"].max()) + 1):
        first = pd.Timestamp(year=C.DATA_YEAR, month=m, day=1)
        tick_weeks.append(int((first - first_monday).days // 7))
        tick_text.append(C.MONTH_LABELS[m - 1])
    fig = go.Figure(go.Heatmap(
        z=z, x=list(range(n_weeks)), y=C.WEEKDAY_LABELS, customdata=hover,
        text=text_matrix, texttemplate="%{text}",
        textfont=dict(size=8, family=D.FONT_UI),
        colorscale=D.HEAT_SCALE, xgap=2, ygap=2, zmin=0,
        colorbar=dict(thickness=10, len=0.88, title=dict(text="News", font=dict(size=10)),
                      tickfont=dict(size=10), outlinewidth=0),
        hovertemplate="%{customdata}<extra></extra>",
    ))
    _base_layout(fig, height, legend=False, margin=dict(l=8, r=8, t=8, b=8))
    fig.update_yaxes(showgrid=False, autorange="reversed")
    fig.update_xaxes(tickmode="array", tickvals=tick_weeks, ticktext=tick_text, side="top", showgrid=False)
    return fig


# City coordinates for geospatial map
CITY_COORDS: dict[str, tuple[float, float]] = {
    "Lahore": (31.5204, 74.3587),
    "Faisalabad": (31.4504, 73.1350),
    "Karachi": (24.8607, 67.0011),
    "Islamabad": (33.6844, 73.0479),
    "Kasur": (31.1179, 74.4461),
    "Kamoke": (31.9744, 74.2244),
    "Rawalpindi": (33.5651, 73.0169),
    "Ferozewala": (31.6667, 74.2833),
    "Peshawar": (34.0151, 71.5249),
    "Gujranwala": (32.1877, 74.1945),
    "Quetta": (30.1798, 66.9750),
    "Sialkot": (32.4945, 74.5229),
    "Sargodha": (32.0836, 72.6711),
    "Nowshera Virkan": (31.9564, 73.9667),
    "Multan": (30.1575, 71.5249),
    "Bannu": (32.9861, 70.6042),
    "Hafizabad": (32.0719, 73.6878),
    "Sheikhupura": (31.7167, 73.9850),
    "Nankana Sahib": (31.4492, 73.7125),
    "Hyderabad": (25.3960, 68.3578),
    "Tatlay Aali": (32.0333, 74.0500),
    "Daska": (32.3242, 74.3508),
    "Gojra": (31.1494, 72.6842),
    "Dera Ismail Khan": (31.8314, 70.9019),
    "Gujrat": (32.5742, 74.0754),
    "Narang Mandi": (31.9000, 74.5167),
    "Bajaur": (34.7865, 71.5249),
    "Chunian": (30.9639, 73.9803),
    "Pattoki": (31.0214, 73.8531),
    "Lakki Marwat": (32.6072, 70.9114),
    "Rahim Yar Khan": (28.4212, 70.2989),
    "Muridke": (31.8020, 74.2550),
    "Khuzdar": (27.8119, 66.6053),
    "Sahiwal": (30.6682, 73.1114),
    "Muzaffarabad": (34.3700, 73.4711),
    "Rahwali": (32.2356, 74.2189),
    "Bahawalpur": (29.3544, 71.6911),
    "Dera Ghazi Khan": (30.0561, 70.6348),
    "Jaranwala": (31.3342, 73.4194),
    "Nowshera": (34.0153, 71.9747),
    "North Waziristan": (32.9739, 70.1456),
    "Shikarpur": (27.9570, 68.6378),
    "Vehari": (30.0419, 72.3528),
    "Qila Didar Singh": (32.1333, 74.0167),
    "Kurram": (33.8150, 70.1069),
    "Abbottabad": (34.1688, 73.2215),
    "Pir Mahal": (30.7675, 72.4350),
    "Ladhewala Waraich": (32.1667, 74.1167),
    "Larkana": (27.5590, 68.2120),
    "Sukkur": (27.7052, 68.8574),
    "Jhang": (31.2681, 72.3181),
    "Mardan": (34.1989, 72.0403),
    "Gwadar": (25.1216, 62.3254),
    "Chaman": (30.9210, 66.4597),
    "Wazirabad": (32.4431, 74.1197),
    "Okara": (30.8081, 73.4458),
    "Kasur District": (31.1179, 74.4461),
    "Swat": (35.2227, 72.4258),
    "Kohat": (33.5869, 71.4414),
    "Chiniot": (31.7200, 72.9789),
    "Turbat": (26.0031, 63.0544),
}


def pakistan_crime_map(df: pd.DataFrame, height: int = 440) -> go.Figure:
    """Geographic map of Pakistan highlighting crime news clusters and fatal rates."""
    d = df[df[C.COL_CITY] != NOT_SPECIFIED]
    if d.empty:
        return _empty(height=height)

    # Use standardized city name if available for clean aggregation and non-overlapping bubbles
    city_col = "City_Standard" if "City_Standard" in d.columns else C.COL_CITY
    grouped = d.groupby(city_col).agg(
        total=("Fatal", "count"),
        fatal=("Fatal", "sum"),
        deaths=("Deaths_Exact", "sum"),
    ).reset_index()

    # Filter out very small clusters (< 15 news) to keep map clean and prevent dense bubble clutter
    if len(grouped) > 25:
        grouped = grouped[grouped["total"] >= 15]

    overall_total = len(df) if len(df) > 0 else 1
    lats, lons, cities, counts, pcts, fatal_rates, sizes = [], [], [], [], [], [], []
    for _, row in grouped.iterrows():
        c_name = str(row[city_col])
        coords = CITY_COORDS.get(c_name)
        if not coords:
            for k, v in CITY_COORDS.items():
                if k.lower() == c_name.lower() or k.lower() in c_name.lower():
                    coords = v
                    break
        if coords:
            cnt = int(row["total"])
            fat = int(row["fatal"])
            frate = (fat / cnt * 100) if cnt > 0 else 0
            lats.append(coords[0])
            lons.append(coords[1])
            cities.append(c_name)
            counts.append(cnt)
            pcts.append(cnt / overall_total * 100)
            fatal_rates.append(frate)
            # Balanced bubble size to prevent crowded overlapping
            sizes.append(max(7, min(24, int(np.sqrt(cnt) * 0.95))))

    if not lats:
        return _empty(message="No coordinates mapped for selected cities", height=height)

    customdata = np.stack((cities, counts, pcts, fatal_rates), axis=-1)

    fig = go.Figure(go.Scattergeo(
        lon=lons,
        lat=lats,
        text=cities,
        customdata=customdata,
        mode="markers",
        marker=dict(
            size=sizes,
            color=fatal_rates,
            colorscale=[
                [0.00, "#F5E6E8"],
                [0.25, "#EAA3A8"],
                [0.55, "#C8434F"],
                [0.80, "#A31824"],
                [1.00, "#6E0F1A"],
            ],
            cmin=0,
            cmax=max(fatal_rates) if max(fatal_rates) > 0 else 100,
            colorbar=dict(
                title=dict(text="Lethality (% Fatal)", font=dict(size=10, color=D.TEXT_MUTED)),
                thickness=8,
                len=0.7,
                tickfont=dict(size=9, color=D.TEXT_MUTED),
                outlinewidth=0,
                ticksuffix="%",
                bgcolor="rgba(0,0,0,0)",
            ),
            line=dict(color="#FFFFFF", width=1.2),
            opacity=0.82,
        ),
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Total News: <b>%{customdata[1]:,}</b> (%{customdata[2]:.1f}%)<br>"
            "Lethality Rate: <b>%{customdata[3]:.1f}% Fatal</b>"
            "<extra></extra>"
        ),
    ))

    fig.update_geos(
        fitbounds=False,
        scope="asia",
        # Strictly focused on Pakistan geographic bounds
        lonaxis_range=[60.8, 77.8],
        lataxis_range=[23.6, 37.1],
        visible=True,
        showcountries=True,
        countrycolor=D.MAROON,
        countrywidth=2.2,
        showsubunits=False,
        showcoastlines=True,
        coastlinecolor=D.MAROON,
        coastlinewidth=2.0,
        showland=True,
        landcolor="#FAF5F5",
        showocean=True,
        oceancolor="#EEF2F6",
        showlakes=True,
        lakecolor="#EEF2F6",
        showrivers=False,
        bgcolor="rgba(0,0,0,0)",
    )

    _base_layout(fig, height, legend=False, margin=dict(l=0, r=0, t=4, b=4))
    return fig


def crime_severity_matrix(df: pd.DataFrame, n: int = 10, height: int = 420) -> go.Figure:
    """Quadrant matrix: Volume vs. Lethality (% Fatal) for leading crime categories."""
    if df.empty:
        return _empty(height=height)
    overall_total = len(df) if len(df) > 0 else 1
    top = df[C.COL_CATEGORY].value_counts().head(n).index.tolist()
    d = df[df[C.COL_CATEGORY].isin(top)]
    stats = d.groupby(C.COL_CATEGORY).agg(
        total=("Fatal", "count"),
        fatal=("Fatal", "sum"),
        deaths=("Deaths_Exact", "sum"),
    ).reindex(top).reset_index()

    stats["pct_share"] = (stats["total"] / overall_total * 100)
    stats["lethality_rate"] = (stats["fatal"] / stats["total"] * 100).fillna(0)
    # Reduced and proportionally scaled bubble sizes with clear min and max boundaries
    sizes = np.clip(np.sqrt(stats["total"].to_numpy()) * 0.45 + 7, 8, 22)

    if len(stats) < 2:
        return _empty("Please select 2 or more crime categories (or 'All') to view comparison matrix", height=height)

    # Carefully curated label positions for prominent bubbles to prevent any collisions or edge clipping
    def _get_label(c_name: str, pos: str):
        match = stats.loc[stats[C.COL_CATEGORY] == c_name, "pct_share"]
        if not match.empty:
            return (pos, f"<b>{c_name}</b> ({match.iloc[0]:.1f}%)")
        return (pos, None)

    label_cfg = {
        "Murder": _get_label("Murder", "middle left"),
        "Accident / Hit & Run": _get_label("Accident / Hit & Run", "top center"),
        "Terrorism": _get_label("Terrorism", "bottom right"),
        "Fraud / Corruption": _get_label("Fraud / Corruption", "middle left"),
    }

    fig = go.Figure()

    for i, row in stats.iterrows():
        cat = row[C.COL_CATEGORY]
        color, _ = _category_color(cat)
        pct = row["pct_share"]
        pos, text_val = label_cfg.get(cat, (None, None))
        has_label = text_val is not None

        fig.add_trace(go.Scatter(
            x=[row["total"]],
            y=[row["lethality_rate"]],
            mode="markers+text" if has_label else "markers",
            name=f"{cat} ({pct:.1f}%)",
            text=[text_val] if has_label else None,
            textposition=pos if has_label else None,
            textfont=dict(size=11, color=D.TEXT, family=D.FONT_UI),
            marker=dict(
                size=[sizes[i]],
                color=color,
                opacity=0.82,
                line=dict(color="#FFFFFF", width=1.4),
            ),
            customdata=[[cat, row["total"], row["pct_share"], row["lethality_rate"], int(row["deaths"])]],
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Volume: <b>%{customdata[1]:,}</b> (%{customdata[2]:.1f}%)<br>"
                "Lethality Rate: <b>%{customdata[3]:.1f}% Fatal</b><br>"
                "Total Deaths: <b>%{customdata[4]:,}</b>"
                "<extra></extra>"
            ),
            showlegend=True,
        ))

    # Base layout with adequate bottom margin to accommodate wrapped multi-line legend without scrollbar
    _base_layout(fig, height, legend=True, margin=dict(l=14, r=24, t=12, b=95))
    fig.update_layout(
        legend=dict(
            orientation="h",
            entrywidthmode="fraction",
            entrywidth=0.48,
            yanchor="top",
            y=-0.26,
            xanchor="center",
            x=0.5,
            font=dict(size=10, color=D.TEXT),
            bgcolor="rgba(0,0,0,0)",
            itemclick="toggleothers",
        ),
    )
    # Generous x and y axis padding so bubbles & labels on edges are never clipped
    x_min = float(stats["total"].min())
    x_max = float(stats["total"].max())
    fig.update_xaxes(
        title=dict(text="Total News Volume (Frequency)", font=dict(size=11, color=D.TEXT_MUTED), standoff=14),
        showgrid=True, gridcolor=D.GRID, linecolor=D.BORDER,
        range=[max(0, x_min - 250), x_max + 320],
    )
    fig.update_yaxes(
        title=dict(text="Lethality Rate (% Fatal)", font=dict(size=11, color=D.TEXT_MUTED)),
        showgrid=True, gridcolor=D.GRID, linecolor=D.BORDER, ticksuffix="%",
        range=[-8, 116],
    )
    return fig


def monthly_growth_velocity(df: pd.DataFrame, height: int = 420) -> go.Figure:
    """Month-over-Month (MoM) % change in news volume with directional colouring."""
    if df.empty:
        return _empty(height=height)
    months = _month_range(df)
    m_labels = _month_names(months)
    counts = df.groupby("Month").size().reindex(months, fill_value=0)

    # Compute Month-over-Month percentage changes
    pct_changes = counts.pct_change() * 100
    pct_changes = pct_changes.fillna(0)

    colors = [D.CRIMSON if val >= 0 else D.STEEL_BLUE for val in pct_changes]
    # Bold, clean font with 13px size and clear contrast
    labels = [f"<b>{val:+.1f}%</b>" if idx > 0 else "<b>Base</b>" for idx, val in enumerate(pct_changes)]

    fig = go.Figure()
    fig.add_bar(
        x=m_labels,
        y=pct_changes,
        marker=dict(color=colors, line=dict(color=D.SURFACE, width=1.5)),
        text=labels,
        textposition="outside",
        textfont=dict(size=20, color=D.TEXT, family=D.FONT_UI),
        cliponaxis=False,
        customdata=np.stack((counts.values, pct_changes.values), axis=-1),
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Volume: <b>%{customdata[0]:,}</b> news<br>"
            "MoM Change: <b>%{customdata[1]:+.1f}%</b>"
            "<extra></extra>"
        ),
    )  

    _base_layout(fig, height, legend=False, margin=dict(l=14, r=18, t=14, b=28))
    fig.add_hline(y=0, line_width=1.5, line_color=D.BORDER)
    # Generous vertical range so prominent 13px labels never get clipped at top or bottom
    min_val = float(pct_changes.min())
    max_val = float(pct_changes.max())
    y_lower = min_val * 1.45 if min_val < 0 else -12
    y_upper = max_val * 1.35 if max_val > 0 else 12
    fig.update_yaxes(
        title=dict(text="MoM Change (%)", font=dict(size=11, color=D.TEXT_MUTED)),
        ticksuffix="%", showgrid=True, gridcolor=D.GRID,
        range=[y_lower, y_upper],
    )
    fig.update_xaxes(showgrid=False, tickfont=dict(size=11, color=D.TEXT))
    return fig


def weekday_volume_distribution(df: pd.DataFrame, height: int = D.CHART_HEIGHT) -> go.Figure:
    """Distribution of crime news across days of the week with percentage shares."""
    if df.empty:
        return _empty(height=height)
    overall_total = len(df) if len(df) > 0 else 1
    counts = df.groupby("Weekday_Num").size().reindex(range(7), fill_value=0)
    pcts = (counts / overall_total * 100)
    labels = [f"{p:.1f}%" for p in pcts]

    fig = go.Figure()
    fig.add_bar(
        x=C.WEEKDAY_LABELS,
        y=counts,
        marker=dict(color=D.MAROON, line=dict(color=D.SURFACE, width=1.5)),
        text=labels,
        textposition="outside",
        textfont=dict(size=10, color=D.TEXT),
        customdata=np.stack((counts.values, pcts.values), axis=-1),
        hovertemplate=(
            "<b>%{x}</b><br>"
            "News Count: <b>%{customdata[0]:,}</b><br>"
            "Share of Total: <b>%{customdata[1]:.1f}%</b>"
            "<extra></extra>"
        ),
    )
    _base_layout(fig, height, legend=False)
    fig.update_yaxes(showgrid=True, gridcolor=D.GRID, range=[0, float(counts.max()) * 1.18])
    fig.update_xaxes(showgrid=False)
    return fig


# ============================================================ CATEGORIES
def category_bar(df: pd.DataFrame, n: int = 15, height: int = D.CHART_HEIGHT_TALL) -> go.Figure:
    """Ranked categories with clear % share labels and formatted hovers."""
    return _ranked_language_bar(df, C.COL_CATEGORY, n, height, other=True, show_percent=True)


def category_month_heatmap(df: pd.DataFrame, n: int = 12, height: int = D.CHART_HEIGHT_TALL) -> go.Figure:
    """Heatmap showing crime category reporting across months with cell numbers."""
    if df.empty:
        return _empty(height=height)
    top = df[C.COL_CATEGORY].value_counts().head(n).index
    months = _month_range(df)
    m = (df[df[C.COL_CATEGORY].isin(top)].groupby([C.COL_CATEGORY, "Month"]).size()
         .unstack(fill_value=0).reindex(index=top, columns=months, fill_value=0))
    m.columns = _month_names(months)
    return _heatmap(m, height, show_text=True)


def category_trend(df: pd.DataFrame, n: int = 5, height: int = D.CHART_HEIGHT) -> go.Figure:
    """Monthly volume trend for top categories with clean lines and % of monthly volume on hover."""
    if df.empty:
        return _empty(height=height)
    top = df[C.COL_CATEGORY].value_counts().head(n).index.tolist()
    months = _month_range(df)
    month_totals = df.groupby("Month").size().reindex(months, fill_value=1)
    fig = go.Figure()
    for cat in top:
        s = df[df[C.COL_CATEGORY] == cat].groupby("Month").size().reindex(months, fill_value=0)
        pcts = [(v / max(1, month_totals.get(m, 1)) * 100) for m, v in zip(months, s.values)]
        color, dash = _category_color(cat)
        customdata = np.stack((s.values, pcts), axis=-1)
        fig.add_trace(go.Scatter(
            x=_month_names(months), y=s.values, name=cat, mode="lines+markers",
            customdata=customdata,
            line=dict(color=color, width=2.5, dash=dash),
            marker=dict(size=7, color=color, line=dict(color=D.SURFACE, width=1.5)),
            hovertemplate=(
                "<b>" + cat + "</b><br>"
                "%{x}: <b>%{customdata[0]:,}</b> news (%{customdata[1]:.1f}% of month)<extra></extra>"
            ),
        ))
    _base_layout(fig, height, legend=True)
    fig.update_layout(
        legend=dict(orientation="h", yanchor="top", y=-0.18, xanchor="center", x=0.5, font=dict(size=10)),
        margin=dict(l=10, r=12, t=8, b=45),
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor=D.GRID)
    return fig


def category_treemap(df: pd.DataFrame, n: int = 15, height: int = D.CHART_HEIGHT) -> go.Figure:
    """Treemap of crime category distribution with bold percentages and no clutter."""
    if df.empty:
        return _empty(height=height)
    counts = df[C.COL_CATEGORY].value_counts()
    top = counts.head(n)
    other = counts.iloc[n:].sum()
    labels = top.index.tolist() + (["Other"] if other > 0 else [])
    values = top.values.tolist() + ([int(other)] if other > 0 else [])
    overall_total = len(df) if len(df) > 0 else 1

    tile_texts = []
    for l, v in zip(labels, values):
        pct = (v / overall_total * 100)
        tile_texts.append(f"<b>{l}</b><br>{pct:.1f}%<br><span style='font-size:9px;'>({v:,})</span>")

    lo, hi = min(values), max(values)
    positions = [(v - lo) / (hi - lo) if hi > lo else 0.5 for v in values]
    tile_colors = sample_colorscale(D.HEAT_SCALE, [0.15 + 0.85 * p for p in positions])
    root = "All categories"

    fig = go.Figure(go.Treemap(
        ids=[root] + labels, labels=[root] + tile_texts, parents=[""] + [root] * len(labels),
        values=[sum(values)] + values, branchvalues="total",
        marker=dict(colors=[D.SURFACE] + tile_colors, line=dict(color=D.SURFACE, width=2.5)),
        textinfo="label", textfont=dict(size=11, family=D.FONT_UI, color=D.TEXT),
        hovertemplate="<b>%{id}</b><br>Volume: <b>%{value:,}</b> news (%{percentRoot:.1%})<extra></extra>",
        tiling=dict(pad=3), pathbar=dict(visible=False), maxdepth=2,
    ))
    return _base_layout(fig, height, legend=False, margin=dict(l=4, r=4, t=4, b=4))


def category_weekday_heatmap(df: pd.DataFrame, n: int = 12, height: int = D.CHART_HEIGHT) -> go.Figure:
    """Crime occurrence by day of the week with visible cell counts."""
    if df.empty:
        return _empty(height=height)
    top = df[C.COL_CATEGORY].value_counts().head(n).index
    m = (df[df[C.COL_CATEGORY].isin(top)].groupby([C.COL_CATEGORY, "Weekday"]).size()
         .unstack(fill_value=0).reindex(index=top, columns=C.WEEKDAY_LABELS, fill_value=0))
    return _heatmap(m, height, show_text=True)


def fatal_by_category(df: pd.DataFrame, n: int = 12, height: int = D.CHART_HEIGHT) -> go.Figure:
    """100% Normalized fatal vs non-fatal rate per crime category."""
    if df.empty:
        return _empty(height=height)
    top = df[C.COL_CATEGORY].value_counts().head(n).index.tolist()
    d = df[df[C.COL_CATEGORY].isin(top)]
    table = d.groupby([C.COL_CATEGORY, "Fatal"]).size().unstack(fill_value=0).reindex(top).fillna(0).astype(int)
    total_cat = table.sum(axis=1)

    fatal_pct = (table.get(True, pd.Series(0, index=top)) / total_cat * 100).round(1)
    non_fatal_pct = (100 - fatal_pct).round(1)

    fig = go.Figure()
    fig.add_bar(
        y=top, x=fatal_pct, orientation="h", name="Fatal News (%)",
        marker=dict(color=D.FATAL_COLOR, line=dict(color=D.SURFACE, width=1.5)),
        text=[f"<b>{v:.1f}%</b>" if v >= 6 else "" for v in fatal_pct],
        textposition="inside",
        textfont=dict(size=10, color="#FFFFFF"),
        customdata=table.get(True, pd.Series(0, index=top)),
        hovertemplate="%{y}<br>Fatal: <b>%{customdata:,}</b> news (<b>%{x:.1f}%</b>)<extra></extra>",
    )
    fig.add_bar(
        y=top, x=non_fatal_pct, orientation="h", name="Non-fatal News (%)",
        marker=dict(color=D.NON_FATAL_COLOR, line=dict(color=D.SURFACE, width=1.5)),
        text=[f"{v:.1f}%" if v >= 12 else "" for v in non_fatal_pct],
        textposition="inside",
        textfont=dict(size=10, color=D.TEXT),
        customdata=table.get(False, pd.Series(0, index=top)),
        hovertemplate="%{y}<br>Non-fatal: <b>%{customdata:,}</b> news (<b>%{x:.1f}%</b>)<extra></extra>",
    )
    fig.update_layout(barmode="stack")
    _base_layout(fig, height, legend=True)
    fig.update_layout(
        legend=dict(orientation="h", yanchor="top", y=-0.16, xanchor="center", x=0.5, font=dict(size=10)),
        margin=dict(l=10, r=16, t=8, b=45),
    )
    fig.update_yaxes(autorange="reversed", showgrid=False, automargin=True)
    fig.update_xaxes(showgrid=True, gridcolor=D.GRID, range=[0, 100], ticksuffix="%")
    return fig


def category_lethality_ranking(df: pd.DataFrame, n: int = 12, height: int = D.CHART_HEIGHT) -> go.Figure:
    """Rank categories by lethality percentage (% of incidents that were fatal)."""
    if df.empty:
        return _empty(height=height)
    # Only include categories with at least 15 news for statistical significance
    grouped = df.groupby(C.COL_CATEGORY).agg(
        total=("Fatal", "count"),
        fatal=("Fatal", "sum"),
    )
    grouped = grouped[grouped["total"] >= 15]
    grouped["lethality_pct"] = (grouped["fatal"] / grouped["total"] * 100).round(1)
    ranked = grouped.sort_values("lethality_pct", ascending=True).tail(n)

    fig = go.Figure()
    fig.add_bar(
        y=ranked.index,
        x=ranked["lethality_pct"],
        orientation="h",
        marker=dict(
            color=ranked["lethality_pct"],
            colorscale=[
                [0.0, D.ROSE_LIGHT],
                [0.4, D.CRIMSON],
                [1.0, D.MAROON],
            ],
            line=dict(color=D.SURFACE, width=1.5),
        ),
        text=[f"<b>{v:.1f}%</b>" for v in ranked["lethality_pct"]],
        textposition="outside",
        textfont=dict(size=11, color=D.TEXT),
        cliponaxis=False,
        customdata=np.stack((ranked["fatal"].values, ranked["total"].values), axis=-1),
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Lethality Rate: <b>%{x:.1f}%</b><br>"
            "Fatal Incidents: <b>%{customdata[0]:,}</b> of %{customdata[1]:,}<extra></extra>"
        ),
    )
    _base_layout(fig, height, legend=False)
    fig.update_yaxes(showgrid=False, automargin=True)
    fig.update_xaxes(
        showgrid=True, gridcolor=D.GRID, ticksuffix="%",
        range=[0, max(100, float(ranked["lethality_pct"].max()) * 1.15)],
    )
    return fig


def category_casualty_impact(df: pd.DataFrame, n: int = 10, height: int = D.CHART_HEIGHT) -> go.Figure:
    """Casualty scale comparison: Total Deaths vs Total Injuries across top categories."""
    if df.empty:
        return _empty(height=height)
    top = df[C.COL_CATEGORY].value_counts().head(n).index.tolist()
    d = df[df[C.COL_CATEGORY].isin(top)]
    stats = d.groupby(C.COL_CATEGORY).agg(
        deaths=("Deaths_Exact", "sum"),
        injured=("Injured_Exact", "sum"),
    ).reindex(top).fillna(0)

    total_deaths = df["Deaths_Exact"].sum() if df["Deaths_Exact"].sum() > 0 else 1
    total_injured = df["Injured_Exact"].sum() if df["Injured_Exact"].sum() > 0 else 1

    fig = go.Figure()
    fig.add_bar(
        x=top, y=stats["deaths"], name="Deaths (Exact)",
        marker=dict(color=D.DEATHS_COLOR, line=dict(color=D.SURFACE, width=1.5)),
        customdata=[(v / total_deaths * 100) for v in stats["deaths"]],
        hovertemplate="%{x}<br>Deaths: <b>%{y:,}</b> (<b>%{customdata:.1f}%</b> of all deaths)<extra></extra>",
    )
    fig.add_bar(
        x=top, y=stats["injured"], name="Injured (Exact)",
        marker=dict(color=D.INJURED_COLOR, line=dict(color=D.SURFACE, width=1.5)),
        customdata=[(v / total_injured * 100) for v in stats["injured"]],
        hovertemplate="%{x}<br>Injuries: <b>%{y:,}</b> (<b>%{customdata:.1f}%</b> of all injuries)<extra></extra>",
    )
    fig.update_layout(barmode="group")
    _base_layout(fig, height, legend=True)
    fig.update_layout(
        legend=dict(orientation="h", yanchor="top", y=-0.22, xanchor="center", x=0.5, font=dict(size=10)),
        margin=dict(l=10, r=12, t=8, b=55),
    )
    fig.update_xaxes(tickangle=-30, showgrid=False, tickfont=dict(size=10))
    fig.update_yaxes(showgrid=True, gridcolor=D.GRID)
    return fig


def category_language_bias(df: pd.DataFrame, n: int = 12, height: int = D.CHART_HEIGHT) -> go.Figure:
    """100% Normalized language split showing Urdu vs English coverage bias per category."""
    if df.empty:
        return _empty(height=height)
    top = df[C.COL_CATEGORY].value_counts().head(n).index.tolist()
    d = df[df[C.COL_CATEGORY].isin(top)]
    table = d.groupby([C.COL_CATEGORY, C.COL_LANGUAGE]).size().unstack(fill_value=0).reindex(top).fillna(0).astype(int)
    row_totals = table.sum(axis=1)

    urdu_pct = (table.get("Urdu", pd.Series(0, index=top)) / row_totals * 100).round(1)
    eng_pct = (table.get("English", pd.Series(0, index=top)) / row_totals * 100).round(1)

    fig = go.Figure()
    fig.add_bar(
        y=top, x=urdu_pct, orientation="h", name="Urdu (%)",
        marker=dict(color=D.CRIMSON, line=dict(color=D.SURFACE, width=1.5)),
        text=[f"<b>{v:.1f}%</b>" if v >= 10 else "" for v in urdu_pct],
        textposition="inside",
        textfont=dict(size=10, color="#FFFFFF"),
        customdata=table.get("Urdu", pd.Series(0, index=top)),
        hovertemplate="%{y}<br>Urdu: <b>%{customdata:,}</b> news (<b>%{x:.1f}%</b>)<extra></extra>",
    )
    fig.add_bar(
        y=top, x=eng_pct, orientation="h", name="English (%)",
        marker=dict(color=D.STEEL_BLUE, line=dict(color=D.SURFACE, width=1.5)),
        text=[f"<b>{v:.1f}%</b>" if v >= 10 else "" for v in eng_pct],
        textposition="inside",
        textfont=dict(size=10, color="#FFFFFF"),
        customdata=table.get("English", pd.Series(0, index=top)),
        hovertemplate="%{y}<br>English: <b>%{customdata:,}</b> news (<b>%{x:.1f}%</b>)<extra></extra>",
    )
    fig.update_layout(barmode="stack")
    _base_layout(fig, height, legend=True)
    fig.update_layout(
        legend=dict(orientation="h", yanchor="top", y=-0.16, xanchor="center", x=0.5, font=dict(size=10)),
        margin=dict(l=10, r=16, t=8, b=45),
    )
    fig.update_yaxes(autorange="reversed", showgrid=False, automargin=True)
    fig.update_xaxes(showgrid=True, gridcolor=D.GRID, range=[0, 100], ticksuffix="%")
    return fig


# ============================================================ GEOGRAPHY
def city_bar(df: pd.DataFrame, n: int = 15, height: int = D.CHART_HEIGHT_TALL) -> go.Figure:
    return _ranked_language_bar(df, C.COL_CITY, n, height, exclude=(NOT_SPECIFIED,), show_percent=True)


def city_category_heatmap(df: pd.DataFrame, n_cities: int = 12, n_categories: int = 10,
                          height: int = D.CHART_HEIGHT_TALL) -> go.Figure:
    d = df[df[C.COL_CITY] != NOT_SPECIFIED]
    if d.empty:
        return _empty(height=height)
    cities = d[C.COL_CITY].value_counts().head(n_cities).index
    cats = d[C.COL_CATEGORY].value_counts().head(n_categories).index
    m = (d[d[C.COL_CITY].isin(cities) & d[C.COL_CATEGORY].isin(cats)]
         .groupby([C.COL_CITY, C.COL_CATEGORY]).size().unstack(fill_value=0)
         .reindex(index=cities, columns=cats, fill_value=0))
    fig = _heatmap(m, height)
    fig.update_xaxes(tickangle=-35, side="bottom")
    return fig


def city_trend(df: pd.DataFrame, n: int = 5, height: int = D.CHART_HEIGHT) -> go.Figure:
    d = df[df[C.COL_CITY] != NOT_SPECIFIED]
    if d.empty:
        return _empty(height=height)
    top = d[C.COL_CITY].value_counts().head(n).index.tolist()
    months = _month_range(d)
    fig = go.Figure()
    for city in top:
        s = d[d[C.COL_CITY] == city].groupby("Month").size().reindex(months, fill_value=0)
        color, dash = _city_color(city)
        fig.add_trace(go.Scatter(
            x=_month_names(months), y=s.values, name=city, mode="lines+markers",
            line=dict(color=color, width=2, dash=dash), marker=dict(size=7, color=color, line=dict(color=D.SURFACE, width=2)),
            hovertemplate="%{x}<br>" + city + ": <b>%{y:,}</b><extra></extra>",
        ))
    return _base_layout(fig, height, legend=True)


def city_language_mix(df: pd.DataFrame, n: int = 10, height: int = D.CHART_HEIGHT) -> go.Figure:
    d = df[df[C.COL_CITY] != NOT_SPECIFIED]
    if d.empty:
        return _empty(height=height)
    top = d[C.COL_CITY].value_counts().head(n).index.tolist()
    table = (d[d[C.COL_CITY].isin(top)].groupby([C.COL_CITY, C.COL_LANGUAGE]).size()
             .unstack(fill_value=0).reindex(top).fillna(0))
    share = table.div(table.sum(axis=1), axis=0) * 100
    fig = go.Figure()
    for lang in [x for x in LANGS if x in table.columns]:
        fig.add_bar(
            y=top, x=share[lang], orientation="h", name=lang,
            marker=dict(color=D.LANG_COLORS[lang], line=dict(color=D.SURFACE, width=2)),
            customdata=table[lang].astype(int),
            hovertemplate="%{y}<br>" + lang + ": <b>%{x:.0f}%</b> (%{customdata:,} news)<extra></extra>",
        )
    fig.update_layout(barmode="stack")
    _base_layout(fig, height, legend=True)
    fig.update_yaxes(autorange="reversed", showgrid=False, automargin=True)
    fig.update_xaxes(range=[0, 100], ticksuffix="%", showgrid=True, gridcolor=D.GRID)
    return fig


def city_fatal_bar(df: pd.DataFrame, n: int = 10, height: int = D.CHART_HEIGHT) -> go.Figure:
    d = df[(df[C.COL_CITY] != NOT_SPECIFIED) & df["Fatal"]]
    if d.empty:
        return _empty(height=height)
    s = d[C.COL_CITY].value_counts().head(n)
    total_fatal = int(df["Fatal"].sum())
    total_fatal = max(total_fatal, 1)
    pcts = (s / total_fatal * 100).round(1)
    fig = go.Figure(go.Bar(
        y=s.index, x=s.values, orientation="h",
        marker=dict(color=D.FATAL_COLOR, line=dict(color=D.SURFACE, width=2)),
        text=[f"{p:.1f}%" for p in pcts], textposition="outside", textfont=dict(size=11, color=D.TEXT),
        customdata=list(zip(s.values, pcts)),
        hovertemplate="%{y}<br>Fatal news: <b>%{customdata[0]:,}</b> (%{customdata[1]:.1f}%)<extra></extra>",
        cliponaxis=False,
    ))
    _base_layout(fig, height, legend=False)
    fig.update_yaxes(autorange="reversed", showgrid=False, automargin=True)
    fig.update_xaxes(range=[0, float(s.max()) * 1.16], showgrid=True, gridcolor=D.GRID)
    return fig



def city_lethality_rate(df: pd.DataFrame, n: int = 12, min_news: int = 80,
                       height: int = D.CHART_HEIGHT_TALL) -> go.Figure:
    """Horizontal bar: fatality rate (%) per city, filtered by min news count."""
    d = df[df[C.COL_CITY] != NOT_SPECIFIED]
    if d.empty:
        return _empty(height=height)
    agg = d.groupby(C.COL_CITY).agg(
        total=(C.COL_CITY, "count"), fatal=("Fatal", "sum")
    )
    agg = agg[agg["total"] >= min_news].copy()
    if agg.empty:
        return _empty(height=height)
    agg["rate"] = (agg["fatal"] / agg["total"] * 100).round(1)
    agg = agg.sort_values("rate", ascending=True).tail(n)
    cities = agg.index.tolist()
    rates = agg["rate"].tolist()
    totals = agg["total"].tolist()
    fatals = agg["fatal"].astype(int).tolist()
    # Gradient colour from rose to deep crimson based on rate
    max_rate = max(rates) if rates else 1
    colors = [sample_colorscale(
        [[0, D.ROSE], [0.5, D.CRIMSON], [1, D.MAROON]],
        r / max_rate if max_rate else 0
    )[0] for r in rates]
    fig = go.Figure(go.Bar(
        y=cities, x=rates, orientation="h",
        marker=dict(color=colors, line=dict(color=D.SURFACE, width=2)),
        text=[f"<b>{r:.1f}%</b>" for r in rates],
        textposition="outside", textfont=dict(size=11, color=D.TEXT),
        customdata=list(zip(fatals, totals)),
        hovertemplate="%{y}<br>Fatality rate: <b>%{x:.1f}%</b><br>"
                      "Fatal news: %{customdata[0]:,} / %{customdata[1]:,} total<extra></extra>",
        cliponaxis=False,
    ))
    _base_layout(fig, height, legend=False, margin=dict(l=8, r=16, t=8, b=8))
    fig.update_yaxes(showgrid=False, automargin=True)
    fig.update_xaxes(showgrid=True, gridcolor=D.GRID, range=[0, max(rates) * 1.22],
                     ticksuffix="%")
    return fig



def city_casualty_severity(df: pd.DataFrame, n: int = 10, min_news: int = 80,
                           height: int = D.CHART_HEIGHT_TALL) -> go.Figure:
    """Dumbbell: deaths and injuries per 100 news reports for top cities."""
    d = df[df[C.COL_CITY] != NOT_SPECIFIED]
    if d.empty:
        return _empty(height=height)
    agg = d.groupby(C.COL_CITY).agg(
        total=(C.COL_CITY, "count"),
        deaths=("Deaths_Exact", "sum"),
        injured=("Injured_Exact", "sum"),
    )
    agg = agg[agg["total"] >= min_news].copy()
    if agg.empty:
        return _empty(height=height)
    agg["deaths_per_100"] = (agg["deaths"] / agg["total"] * 100).round(1)
    agg["injured_per_100"] = (agg["injured"] / agg["total"] * 100).round(1)
    agg["combined"] = agg["deaths_per_100"] + agg["injured_per_100"]
    agg = agg.sort_values("combined", ascending=True).tail(n)
    cities = agg.index.tolist()
    d_vals = agg["deaths_per_100"].tolist()
    i_vals = agg["injured_per_100"].tolist()
    totals = agg["total"].astype(int).tolist()
    # Connector lines
    fig = go.Figure()
    for j, city in enumerate(cities):
        fig.add_trace(go.Scatter(
            x=[d_vals[j], i_vals[j]], y=[city, city], mode="lines",
            line=dict(color=D.GRID, width=2), showlegend=False, hoverinfo="skip",
        ))
    # Deaths dots
    fig.add_trace(go.Scatter(
        x=d_vals, y=cities, mode="markers", name="Deaths / 100 news",
        marker=dict(size=12, color=D.DEATHS_COLOR, line=dict(color=D.SURFACE, width=2),
                    symbol="circle"),
        customdata=list(zip(agg["deaths"].astype(int).tolist(), totals)),
        hovertemplate="%{y}<br>Deaths per 100 news: <b>%{x:.1f}</b>"
                      "<br>Total deaths: %{customdata[0]:,} (from %{customdata[1]:,} news)<extra></extra>",
    ))
    # Injured dots
    fig.add_trace(go.Scatter(
        x=i_vals, y=cities, mode="markers", name="Injured / 100 news",
        marker=dict(size=12, color=D.INJURED_COLOR, line=dict(color=D.SURFACE, width=2),
                    symbol="diamond"),
        customdata=list(zip(agg["injured"].astype(int).tolist(), totals)),
        hovertemplate="%{y}<br>Injured per 100 news: <b>%{x:.1f}</b>"
                      "<br>Total injured: %{customdata[0]:,} (from %{customdata[1]:,} news)<extra></extra>",
    ))
    _base_layout(fig, height, legend=True, margin=dict(l=8, r=16, t=8, b=8))
    fig.update_yaxes(showgrid=False, automargin=True)
    max_val = max(max(d_vals), max(i_vals)) if d_vals and i_vals else 100
    fig.update_xaxes(showgrid=True, gridcolor=D.GRID, range=[0, max_val * 1.15])
    return fig


# ============================================================ CASUALTIES
def monthly_casualties(df: pd.DataFrame, height: int = D.CHART_HEIGHT) -> go.Figure:
    if df.empty:
        return _empty(height=height)
    months = _month_range(df)
    grp = df.groupby("Month")[["Deaths_Exact", "Injured_Exact"]].sum().reindex(months, fill_value=0)
    fig = go.Figure()
    for col, name, color in (("Deaths_Exact", "Deaths", D.DEATHS_COLOR), ("Injured_Exact", "Injured", D.INJURED_COLOR)):
        fig.add_trace(go.Scatter(
            x=_month_names(months), y=grp[col].values, name=name, mode="lines+markers",
            line=dict(color=color, width=2.5), marker=dict(size=7, color=color, line=dict(color=D.SURFACE, width=2)),
            hovertemplate="%{x}<br>" + name + ": <b>%{y:,.0f}</b><extra></extra>",
        ))
    fig = _base_layout(fig, height, legend=True)
    fig.update_yaxes(rangemode="tozero")
    return fig


def _casualty_bar(df: pd.DataFrame, group_col: str, value_col: str, label: str, color: str,
                  n: int, height: int, exclude: tuple[str, ...] = ()) -> go.Figure:
    d = df[~df[group_col].isin(exclude)]
    s = d.groupby(group_col)[value_col].sum().sort_values(ascending=False).head(n)
    s = s[s > 0]
    if s.empty:
        return _empty(height=height)
    fig = go.Figure(go.Bar(
        y=s.index, x=s.values, orientation="h",
        marker=dict(color=color, line=dict(color=D.SURFACE, width=2)),
        text=[f"{v:,.0f}" for v in s.values], textposition="outside", textfont=dict(size=11, color=D.TEXT),
        hovertemplate="%{y}<br>" + label + ": <b>%{x:,.0f}</b><extra></extra>", cliponaxis=False,
    ))
    _base_layout(fig, height, legend=False)
    fig.update_yaxes(autorange="reversed", showgrid=False, automargin=True)
    fig.update_xaxes(range=[0, float(s.max()) * 1.16], showgrid=True, gridcolor=D.GRID)
    return fig


def deaths_by_category(df: pd.DataFrame, n: int = 10, height: int = D.CHART_HEIGHT) -> go.Figure:
    return _casualty_bar(df, C.COL_CATEGORY, "Deaths_Exact", "Deaths", D.DEATHS_COLOR, n, height)


def injured_by_category(df: pd.DataFrame, n: int = 10, height: int = D.CHART_HEIGHT) -> go.Figure:
    return _casualty_bar(df, C.COL_CATEGORY, "Injured_Exact", "Injured", D.INJURED_COLOR, n, height)


def deaths_by_city(df: pd.DataFrame, n: int = 10, height: int = D.CHART_HEIGHT) -> go.Figure:
    return _casualty_bar(df, C.COL_CITY, "Deaths_Exact", "Deaths", D.DEATHS_COLOR, n, height, exclude=(NOT_SPECIFIED,))


def casualty_news_by_category(df: pd.DataFrame, n: int = 10, height: int = D.CHART_HEIGHT) -> go.Figure:
    return _ranked_language_bar(df[df["Has_Casualty"]], C.COL_CATEGORY, n, height)


# ============================================================ TIME
def daily_trend(df: pd.DataFrame, height: int = D.CHART_HEIGHT) -> go.Figure:
    if df.empty:
        return _empty(height=height)
    days = pd.date_range(df["Date"].min(), df["Date"].max(), freq="D")
    s = df.groupby("Date").size().reindex(days, fill_value=0)
    avg = s.rolling(7, min_periods=1).mean()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=days, y=s.values, name="Daily news", mode="lines",
                             line=dict(color=D.ROSE, width=1.2),
                             hovertemplate="%{x|%a, %d %b}<br>Daily: <b>%{y:,}</b><extra></extra>"))
    fig.add_trace(go.Scatter(x=days, y=avg.values, name="7-day average", mode="lines",
                             line=dict(color=D.CRIMSON, width=2.5),
                             hovertemplate="%{x|%a, %d %b}<br>7-day avg: <b>%{y:.1f}</b><extra></extra>"))
    fig = _base_layout(fig, height, legend=True)
    fig.update_yaxes(rangemode="tozero")
    return fig


def daily_trend_by_language(df: pd.DataFrame, height: int = D.CHART_HEIGHT) -> go.Figure:
    if df.empty:
        return _empty(height=height)
    days = pd.date_range(df["Date"].min(), df["Date"].max(), freq="D")
    fig = go.Figure()
    for lang in _present_langs(df):
        s = df[df[C.COL_LANGUAGE] == lang].groupby("Date").size().reindex(days, fill_value=0)
        avg = s.rolling(7, min_periods=1).mean()
        fig.add_trace(go.Scatter(
            x=days, y=avg.values, name=lang, mode="lines", line=dict(color=D.LANG_COLORS[lang], width=2.2),
            hovertemplate="%{x|%a, %d %b}<br>" + lang + " (7-day avg): <b>%{y:.1f}</b><extra></extra>",
        ))
    fig = _base_layout(fig, height, legend=len(_present_langs(df)) > 1)
    fig.update_yaxes(rangemode="tozero")
    return fig


def weekday_bars(df: pd.DataFrame, height: int = D.CHART_HEIGHT) -> go.Figure:
    return _stacked_vbar(df, C.WEEKDAY_LABELS, C.WEEKDAY_LABELS, "Weekday", height)


def month_weekday_heatmap(df: pd.DataFrame, height: int = D.CHART_HEIGHT) -> go.Figure:
    if df.empty:
        return _empty(height=height)
    months = _month_range(df)
    m = (df.groupby(["Weekday", "Month"]).size().unstack(fill_value=0)
         .reindex(index=C.WEEKDAY_LABELS, columns=months, fill_value=0))
    m.columns = _month_names(months)
    return _heatmap(m, height)


def busiest_days(df: pd.DataFrame, n: int = 10, height: int = D.CHART_HEIGHT) -> go.Figure:
    if df.empty:
        return _empty(height=height)
    s = df.groupby("Date").size().sort_values(ascending=False).head(n)
    labels = [f"{d:%d %b} ({d:%a})" for d in s.index]
    fig = go.Figure(go.Bar(
        y=labels, x=s.values, orientation="h",
        marker=dict(color=D.CRIMSON, line=dict(color=D.SURFACE, width=2)),
        text=[f"{v:,}" for v in s.values], textposition="outside", textfont=dict(size=11, color=D.TEXT),
        hovertemplate="%{y}<br><b>%{x:,}</b> news<extra></extra>", cliponaxis=False,
    ))
    _base_layout(fig, height, legend=False)
    fig.update_yaxes(autorange="reversed", showgrid=False, automargin=True)
    fig.update_xaxes(range=[0, float(s.max()) * 1.16], showgrid=True, gridcolor=D.GRID)
    return fig


# ============================================================ SOURCES & LANGUAGE
def source_ranking(df: pd.DataFrame, height: int = D.CHART_HEIGHT_TALL) -> go.Figure:
    return _ranked_language_bar(df, C.COL_SOURCE, 20, height)


def language_category_share(df: pd.DataFrame, n: int = 12, height: int = D.CHART_HEIGHT_TALL) -> go.Figure:
    """Share (%) of each language's news in the top categories."""
    if df.empty:
        return _empty(height=height)
    top = df[C.COL_CATEGORY].value_counts().head(n).index.tolist()
    langs = _present_langs(df)
    fig = go.Figure()
    for lang in langs:
        part = df[df[C.COL_LANGUAGE] == lang]
        counts = part[C.COL_CATEGORY].value_counts().reindex(top, fill_value=0)
        share = counts / len(part) * 100
        fig.add_bar(
            y=top, x=share.values, orientation="h", name=lang,
            marker=dict(color=D.LANG_COLORS[lang], line=dict(color=D.SURFACE, width=2)),
            customdata=counts.values,
            hovertemplate="%{y}<br>" + lang + ": <b>%{x:.1f}%</b> of " + lang + " news (%{customdata:,})<extra></extra>",
        )
    fig.update_layout(barmode="group", bargap=0.35, bargroupgap=0.08)
    _base_layout(fig, height, legend=len(langs) > 1)
    fig.update_yaxes(autorange="reversed", showgrid=False, automargin=True)
    fig.update_xaxes(ticksuffix="%", showgrid=True, gridcolor=D.GRID)
    return fig


def source_category_heatmap(df: pd.DataFrame, n_categories: int = 10, height: int = D.CHART_HEIGHT_TALL) -> go.Figure:
    """Row share (%) of each source's news by category."""
    if df.empty:
        return _empty(height=height)
    cats = df[C.COL_CATEGORY].value_counts().head(n_categories).index
    sources = df[C.COL_SOURCE].value_counts().index
    table = (df.groupby([C.COL_SOURCE, C.COL_CATEGORY]).size().unstack(fill_value=0)
             .reindex(index=sources, columns=cats, fill_value=0))
    share = table.div(df.groupby(C.COL_SOURCE).size().reindex(sources), axis=0) * 100
    z = share.to_numpy()
    text = np.where(z < 0.5, "", np.round(z).astype(int).astype(str))
    fig = go.Figure(go.Heatmap(
        z=z, x=cats.tolist(), y=sources.tolist(), colorscale=D.HEAT_SCALE, xgap=2, ygap=2,
        text=text, texttemplate="%{text}", textfont=dict(size=10),
        colorbar=dict(thickness=10, len=0.9, title=dict(text="% of source", font=dict(size=10)),
                      tickfont=dict(size=10), outlinewidth=0),
        hovertemplate="%{y}<br>%{x}: <b>%{z:.1f}%</b> of the source's news<extra></extra>",
    ))
    _base_layout(fig, height, legend=False, margin=dict(l=8, r=8, t=8, b=8))
    fig.update_yaxes(showgrid=False, autorange="reversed", automargin=True)
    fig.update_xaxes(tickangle=-35, side="bottom")
    return fig


def source_month_heatmap(df: pd.DataFrame, height: int = D.CHART_HEIGHT_TALL) -> go.Figure:
    if df.empty:
        return _empty(height=height)
    months = _month_range(df)
    sources = df[C.COL_SOURCE].value_counts().index
    m = (df.groupby([C.COL_SOURCE, "Month"]).size().unstack(fill_value=0)
         .reindex(index=sources, columns=months, fill_value=0))
    m.columns = _month_names(months)
    return _heatmap(m, height)


def source_city_coverage(df: pd.DataFrame, height: int = D.CHART_HEIGHT) -> go.Figure:
    d = df[df[C.COL_CITY] != NOT_SPECIFIED]
    if d.empty:
        return _empty(height=height)
    s = d.groupby(C.COL_SOURCE)[C.COL_CITY].nunique().sort_values(ascending=False)
    lang_of = df.groupby(C.COL_SOURCE)[C.COL_LANGUAGE].agg(lambda x: x.mode().iat[0])
    colors = [D.LANG_COLORS.get(lang_of.get(src, ""), D.NEUTRAL_BAR) for src in s.index]
    fig = go.Figure(go.Bar(
        y=s.index, x=s.values, orientation="h",
        marker=dict(color=colors, line=dict(color=D.SURFACE, width=2)),
        text=[f"{v:,}" for v in s.values], textposition="outside", textfont=dict(size=11, color=D.TEXT),
        hovertemplate="%{y}<br><b>%{x:,}</b> different cities<extra></extra>", cliponaxis=False,
    ))
    _base_layout(fig, height, legend=False)
    fig.update_yaxes(autorange="reversed", showgrid=False, automargin=True)
    fig.update_xaxes(range=[0, float(s.max()) * 1.16], showgrid=True, gridcolor=D.GRID)
    return fig


def language_monthly_share(df: pd.DataFrame, height: int = D.CHART_HEIGHT) -> go.Figure:
    if df.empty:
        return _empty(height=height)
    months = _month_range(df)
    table = (df.groupby(["Month", C.COL_LANGUAGE]).size().unstack(fill_value=0).reindex(months, fill_value=0))
    share = table.div(table.sum(axis=1).replace(0, np.nan), axis=0) * 100
    fig = go.Figure()
    for lang in [x for x in LANGS if x in table.columns]:
        fig.add_trace(go.Scatter(
            x=_month_names(months), y=share[lang].values, name=lang, mode="lines+markers",
            line=dict(color=D.LANG_COLORS[lang], width=2.5),
            marker=dict(size=7, color=D.LANG_COLORS[lang], line=dict(color=D.SURFACE, width=2)),
            hovertemplate="%{x}<br>" + lang + ": <b>%{y:.1f}%</b> of the month's news<extra></extra>",
        ))
    fig = _base_layout(fig, height, legend=len(table.columns) > 1)
    fig.update_yaxes(ticksuffix="%", range=[0, 100])
    return fig


def language_city_share(df: pd.DataFrame, n: int = 10, height: int = D.CHART_HEIGHT) -> go.Figure:
    """Share (%) of each language's news coming from the top cities."""
    d = df[df[C.COL_CITY] != NOT_SPECIFIED]
    if d.empty:
        return _empty(height=height)
    top = d[C.COL_CITY].value_counts().head(n).index.tolist()
    langs = _present_langs(d)
    fig = go.Figure()
    for lang in langs:
        part = d[d[C.COL_LANGUAGE] == lang]
        counts = part[C.COL_CITY].value_counts().reindex(top, fill_value=0)
        share = counts / len(part) * 100
        fig.add_bar(
            y=top, x=share.values, orientation="h", name=lang,
            marker=dict(color=D.LANG_COLORS[lang], line=dict(color=D.SURFACE, width=2)),
            customdata=counts.values,
            hovertemplate="%{y}<br>" + lang + ": <b>%{x:.1f}%</b> of " + lang + " news (%{customdata:,})<extra></extra>",
        )
    fig.update_layout(barmode="group", bargap=0.35, bargroupgap=0.08)
    _base_layout(fig, height, legend=len(langs) > 1)
    fig.update_yaxes(autorange="reversed", showgrid=False, automargin=True)
    fig.update_xaxes(ticksuffix="%", showgrid=True, gridcolor=D.GRID)
    return fig


# ============================================================ Crime Index & Quarterly Reports

def calculate_crime_index(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate monthly Crime Index with Jan 2025 as the base benchmark (100.0)."""
    if df.empty:
        return pd.DataFrame(columns=["Month", "Month_Label", "Volume", "Index", "Delta_Base_Pct", "MoM_Pct"])
    
    months = _month_range(df)
    m_labels = _month_names(months)
    counts = df.groupby("Month").size().reindex(months, fill_value=0)
    
    # Baseline: January (Month 1) volume if present and > 0, else first available positive month
    jan_volume = counts.get(1, 0)
    if jan_volume == 0:
        pos_counts = counts[counts > 0]
        jan_volume = pos_counts.iloc[0] if not pos_counts.empty else 1
    
    index_values = (counts / jan_volume * 100).round(1)
    delta_base = (index_values - 100.0).round(1)
    mom_pct = (counts.pct_change() * 100).fillna(0.0).round(1)
    
    return pd.DataFrame({
        "Month": months,
        "Month_Label": m_labels,
        "Volume": counts.values,
        "Index": index_values.values,
        "Delta_Base_Pct": delta_base.values,
        "MoM_Pct": mom_pct.values,
    })


def crime_index_trend(df: pd.DataFrame, height: int = 400) -> go.Figure:
    """Monthly Crime Index Trend with Jan 2025 = 100 Baseline indicator."""
    if df.empty:
        return _empty(height=height)
    
    idx_df = calculate_crime_index(df)
    if idx_df.empty:
        return _empty(height=height)
    
    fig = go.Figure()
    
    # Baseline 100 reference shading / line
    fig.add_hline(
        y=100,
        line_width=2,
        line_dash="dash",
        line_color=D.MAROON,
        annotation_text="Jan 2025 Baseline (100.0)",
        annotation_position="top left",
        annotation_font=dict(size=11, color=D.MAROON, family=D.FONT_UI),
    )
    
    # Area fill under the line
    fig.add_trace(go.Scatter(
        x=idx_df["Month_Label"],
        y=idx_df["Index"],
        mode="lines",
        line=dict(color=D.CRIMSON, width=3, shape="spline"),
        fill="tozeroy",
        fillcolor="rgba(179, 32, 42, 0.07)",
        showlegend=False,
        hoverinfo="skip",
    ))
    
    # Marker colors: Crimson if >= 100 (more crime than baseline), Steel Blue if < 100 (less crime)
    marker_colors = [D.CRIMSON if val >= 100 else D.STEEL_BLUE for val in idx_df["Index"]]
    
    # Formatted labels: Base for Jan, e.g. "90.6 (-9.4%)", "123.5 (+23.5%)"
    labels = []
    for i, row in idx_df.iterrows():
        if row["Month"] == 1:
            labels.append("<b>100.0</b><br><span style='font-size:10px;color:#6B7280;'>Base</span>")
        else:
            diff_sign = "+" if row["Delta_Base_Pct"] > 0 else ""
            color = D.CRIMSON if row["Delta_Base_Pct"] >= 0 else D.STEEL_BLUE
            labels.append(f"<b>{row['Index']:.1f}</b><br><span style='font-size:10px;color:{color};'>({diff_sign}{row['Delta_Base_Pct']:.1f}%)</span>")
            
    fig.add_trace(go.Scatter(
        x=idx_df["Month_Label"],
        y=idx_df["Index"],
        mode="markers+text",
        marker=dict(
            size=11,
            color=marker_colors,
            line=dict(color=D.SURFACE, width=2.5),
        ),
        text=labels,
        textposition="top center",
        textfont=dict(family=D.FONT_UI, size=11, color=D.TEXT),
        customdata=np.stack((idx_df["Volume"].values, idx_df["Delta_Base_Pct"].values, idx_df["MoM_Pct"].values), axis=-1),
        hovertemplate=(
            "<b>%{x} 2025</b><br>"
            "Crime Index: <b>%{y:.1f}</b><br>"
            "Reported Crimes: <b>%{customdata[0]:,}</b><br>"
            "Vs Jan Baseline: <b>%{customdata[1]:+.1f}%</b><br>"
            "Month-over-Month: <b>%{customdata[2]:+.1f}%</b>"
            "<extra></extra>"
        ),
        showlegend=False,
    ))
    
    min_idx = idx_df["Index"].min()
    max_idx = idx_df["Index"].max()
    y_min = max(0, min_idx - 18)
    y_max = max_idx + 22
    
    _base_layout(fig, height, legend=False, margin=dict(l=16, r=16, t=24, b=24))
    fig.update_yaxes(
        title=dict(text="Crime Index (Jan 2025 = 100)", font=dict(size=11, color=D.TEXT_MUTED)),
        range=[y_min, y_max],
        showgrid=True,
        gridcolor=D.GRID,
    )
    fig.update_xaxes(showgrid=False, tickfont=dict(size=11, color=D.TEXT))
    return fig


def crime_index_by_category(df: pd.DataFrame, top_n: int = 5, height: int = 380) -> go.Figure:
    """Index trajectories of the top N crime categories benchmarked to their Jan volume."""
    if df.empty:
        return _empty(height=height)
    
    top_cats = df[C.COL_CATEGORY].value_counts().head(top_n).index.tolist()
    months = _month_range(df)
    m_labels = _month_names(months)
    
    fig = go.Figure()
    
    # Baseline line at 100
    fig.add_hline(
        y=100, line_width=1.5, line_dash="dash", line_color=D.BORDER,
        annotation_text="Jan Baseline (100)", annotation_position="top left",
        annotation_font=dict(size=10, color=D.TEXT_MUTED),
    )
    
    for i, cat in enumerate(top_cats):
        cat_df = df[df[C.COL_CATEGORY] == cat]
        counts = cat_df.groupby("Month").size().reindex(months, fill_value=0)
        jan_vol = counts.get(1, 0)
        if jan_vol == 0:
            pos = counts[counts > 0]
            jan_vol = pos.iloc[0] if not pos.empty else 1
            
        index_vals = (counts / jan_vol * 100).round(1)
        color, _ = _category_color(cat)
        
        fig.add_trace(go.Scatter(
            x=m_labels,
            y=index_vals.values,
            mode="lines+markers",
            name=cat,
            line=dict(color=color, width=2.5),
            marker=dict(size=6, color=color, line=dict(color=D.SURFACE, width=1.5)),
            customdata=counts.values,
            hovertemplate=(
                f"<b>{cat}</b> - %{{x}}<br>"
                "Index: <b>%{y:.1f}</b><br>"
                "Volume: <b>%{customdata:,}</b> news"
                "<extra></extra>"
            ),
        ))
        
    _base_layout(fig, height, legend=True, margin=dict(l=16, r=16, t=28, b=24))
    fig.update_yaxes(title=dict(text="Index (Jan = 100)", font=dict(size=11, color=D.TEXT_MUTED)), showgrid=True, gridcolor=D.GRID)
    fig.update_xaxes(showgrid=False)
    return fig


def quarterly_performance_chart(df: pd.DataFrame, height: int = 380) -> go.Figure:
    """Quarterly Crime Volume and Crime Index (Q1, Q2, Q3, Q4) with QoQ indicators."""
    if df.empty:
        return _empty(height=height)
    
    temp = df.copy()
    temp["Quarter"] = "Q" + ((temp["Month"] - 1) // 3 + 1).astype(str)
    all_quarters = ["Q1", "Q2", "Q3", "Q4"]
    q_counts = temp.groupby("Quarter").size().reindex(all_quarters, fill_value=0)
    
    # Base Q1 volume for quarterly index
    q1_vol = q_counts.get("Q1", 0)
    if q1_vol == 0:
        pos = q_counts[q_counts > 0]
        q1_vol = pos.iloc[0] if not pos.empty else 1
        
    q_index = (q_counts / q1_vol * 100).round(1)
    qoq_growth = (q_counts.pct_change() * 100).round(1)
    
    fig = go.Figure()
    
    q_labels = ["Q1 (Jan–Mar)", "Q2 (Apr–Jun)", "Q3 (Jul–Sep)", "Q4 (Oct–Dec)"]
    bar_colors = [D.MAROON, D.STEEL_BLUE, D.CRIMSON, "#8A1821"]
    
    bar_labels = []
    for i, (q, vol) in enumerate(q_counts.items()):
        if i == 0:
            bar_labels.append(f"<b>{vol:,}</b><br><span style='font-size:11px;color:#6B7280;'>Base (100.0)</span>")
        else:
            growth = qoq_growth.iloc[i]
            sign = "+" if growth > 0 else ""
            color = D.CRIMSON if growth >= 0 else D.STEEL_BLUE
            bar_labels.append(f"<b>{vol:,}</b><br><span style='font-size:11px;color:{color};'>{sign}{growth:.1f}% QoQ</span>")
            
    fig.add_bar(
        x=q_labels,
        y=q_counts.values,
        marker=dict(color=bar_colors, line=dict(color=D.SURFACE, width=2)),
        text=bar_labels,
        textposition="outside",
        textfont=dict(family=D.FONT_UI, size=12, color=D.TEXT),
        customdata=np.stack((q_index.values, qoq_growth.fillna(0).values), axis=-1),
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Total Crimes: <b>%{y:,}</b><br>"
            "Quarterly Index (Q1=100): <b>%{customdata[0]:.1f}</b><br>"
            "QoQ Growth: <b>%{customdata[1]:+.1f}%</b>"
            "<extra></extra>"
        ),
        cliponaxis=False,
    )
    
    max_vol = q_counts.max()
    _base_layout(fig, height, legend=False, margin=dict(l=16, r=16, t=28, b=28))
    fig.update_yaxes(
        title=dict(text="Total Reported News", font=dict(size=11, color=D.TEXT_MUTED)),
        showgrid=True,
        gridcolor=D.GRID,
        range=[0, max_vol * 1.32 if max_vol > 0 else 100],
    )
    fig.update_xaxes(showgrid=False, tickfont=dict(size=11, color=D.TEXT))
    return fig


def quarterly_lethality_chart(df: pd.DataFrame, height: int = 360) -> go.Figure:
    """Fatal vs Non-fatal crimes and Lethality Rate across the four quarters."""
    if df.empty:
        return _empty(height=height)
    
    temp = df.copy()
    temp["Quarter"] = "Q" + ((temp["Month"] - 1) // 3 + 1).astype(str)
    all_quarters = ["Q1", "Q2", "Q3", "Q4"]
    q_labels = ["Q1 (Jan–Mar)", "Q2 (Apr–Jun)", "Q3 (Jul–Sep)", "Q4 (Oct–Dec)"]
    
    grouped = temp.groupby(["Quarter", "Fatal"]).size().unstack(fill_value=0).reindex(all_quarters, fill_value=0)
    fatal_counts = grouped.get(True, pd.Series(0, index=all_quarters))
    non_fatal_counts = grouped.get(False, pd.Series(0, index=all_quarters))
    total_q = fatal_counts + non_fatal_counts
    lethality_rate = (fatal_counts / total_q.replace(0, np.nan) * 100).fillna(0.0).round(1)
    
    fig = go.Figure()
    
    fig.add_bar(
        x=q_labels, y=fatal_counts.values, name="Fatal News",
        marker=dict(color=D.FATAL_COLOR, line=dict(color=D.SURFACE, width=1.5)),
        hovertemplate="%{x}<br>Fatal News: <b>%{y:,}</b><extra></extra>",
    )
    fig.add_bar(
        x=q_labels, y=non_fatal_counts.values, name="Non-Fatal News",
        marker=dict(color=D.NON_FATAL_COLOR, line=dict(color=D.SURFACE, width=1.5)),
        hovertemplate="%{x}<br>Non-Fatal News: <b>%{y:,}</b><extra></extra>",
    )
    
    fig.add_trace(go.Scatter(
        x=q_labels, y=lethality_rate.values, name="Lethality Rate (%)",
        mode="lines+markers+text", yaxis="y2",
        line=dict(color="#C26A10", width=3),
        marker=dict(size=9, color="#C26A10", line=dict(color=D.SURFACE, width=2)),
        text=[f"<b>{lr:.1f}%</b>" for lr in lethality_rate.values],
        textposition="top center",
        textfont=dict(size=11, color="#C26A10", family=D.FONT_UI),
        hovertemplate="%{x}<br>Lethality Rate: <b>%{y:.1f}%</b><extra></extra>",
    ))
    
    _base_layout(fig, height, legend=True, margin=dict(l=16, r=40, t=28, b=24))
    fig.update_layout(
        barmode="stack",
        yaxis2=dict(
            title=dict(text="Lethality Rate (%)", font=dict(size=11, color="#C26A10")),
            overlaying="y",
            side="right",
            range=[0, max(lethality_rate.max() * 1.5, 40)],
            ticksuffix="%",
            showgrid=False,
            tickfont=dict(size=11, color="#C26A10"),
        ),
    )
    fig.update_yaxes(title=dict(text="News Count", font=dict(size=11, color=D.TEXT_MUTED)), showgrid=True, gridcolor=D.GRID)
    fig.update_xaxes(showgrid=False)
    return fig


def quarterly_category_shift(df: pd.DataFrame, top_n: int = 6, height: int = 380) -> go.Figure:
    """Quarterly breakdown of top crime categories to spot seasonal shifts."""
    if df.empty:
        return _empty(height=height)
    
    top_cats = df[C.COL_CATEGORY].value_counts().head(top_n).index.tolist()
    temp = df[df[C.COL_CATEGORY].isin(top_cats)].copy()
    temp["Quarter"] = "Q" + ((temp["Month"] - 1) // 3 + 1).astype(str)
    all_quarters = ["Q1", "Q2", "Q3", "Q4"]
    q_labels = ["Q1 (Jan–Mar)", "Q2 (Apr–Jun)", "Q3 (Jul–Sep)", "Q4 (Oct–Dec)"]
    
    matrix = temp.groupby(["Quarter", C.COL_CATEGORY]).size().unstack(fill_value=0).reindex(all_quarters, fill_value=0)
    
    fig = go.Figure()
    for cat in top_cats:
        if cat in matrix.columns:
            color, _ = _category_color(cat)
            fig.add_bar(
                x=q_labels,
                y=matrix[cat].values,
                name=cat,
                marker=dict(color=color, line=dict(color=D.SURFACE, width=1.5)),
                hovertemplate=f"<b>{cat}</b><br>%{{x}}: <b>%{{y:,}}</b> news<extra></extra>",
            )
            
    fig.update_layout(barmode="group", bargap=0.28, bargroupgap=0.08)
    _base_layout(fig, height, legend=True, margin=dict(l=16, r=16, t=28, b=24))
    fig.update_yaxes(title=dict(text="News Volume", font=dict(size=11, color=D.TEXT_MUTED)), showgrid=True, gridcolor=D.GRID)
    fig.update_xaxes(showgrid=False)
    return fig

