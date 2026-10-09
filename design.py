"""Visual design system: palette, typography, spacing constants and global CSS.

This is the single source for colours, layout ratios and styling. Charts, the
top bar and all pages import their values from here.
"""
import streamlit as st

# ------------------------------------------------------------------ Palette
BACKGROUND = "#F7F4F3"      # page background (soft off-white)
SURFACE = "#FFFFFF"         # cards / chart surface
BORDER = "#E7DEDC"          # card border
GRID = "#EFE7E5"            # chart grid lines

CRIMSON = "#B3202A"         # primary accent
MAROON = "#6E0F1A"          # top bar, headings, strong emphasis
ROSE_LIGHT = "#F3D4D6"
ROSE = "#E8A3A8"
STEEL_BLUE = "#3F6FA8"      # second language colour

TEXT = "#2B2F36"
TEXT_MUTED = "#6B7280"
TEXT_FAINT = "#9AA1AB"

# Fixed language colours (identical on every chart)
LANG_COLORS = {"Urdu": CRIMSON, "English": STEEL_BLUE}

# Casualty colours
DEATHS_COLOR = MAROON
INJURED_COLOR = "#C26A10"
FATAL_COLOR = MAROON
NON_FATAL_COLOR = "#D8C9CA"
NEUTRAL_BAR = "#CFC6C4"     # "Other" and secondary bars

# Categorical order (validated: lightness band, chroma, CVD separation, contrast)
CATEGORICAL = ["#B3202A", "#3F6FA8", "#C26A10", "#14907F", "#8A4FA0", "#6B8E23"]

# Sequential scale for heatmaps (off-white -> rose -> crimson -> maroon)
HEAT_SCALE = [
    [0.00, "#FBF3F2"],
    [0.20, "#F3D4D6"],
    [0.45, "#E8A3A8"],
    [0.70, "#C94450"],
    [0.88, "#B3202A"],
    [1.00, "#6E0F1A"],
]

# ------------------------------------------------------------------ Typography
FONT_UI = "Inter, 'Segoe UI', -apple-system, 'Helvetica Neue', Arial, sans-serif"
FONT_DISPLAY = "'Playfair Display', Georgia, 'Times New Roman', serif"
FONT_URDU = "'Noto Nastaliq Urdu', 'Jameel Noori Nastaleeq', 'Segoe UI', serif"

# ------------------------------------------------------------------ Layout ratios
KPI_COLS = 5
RATIO_1_1 = [1, 1]
RATIO_2_1 = [2, 1]
RATIO_1_2 = [1, 2]
RATIO_1_1_1 = [1, 1, 1]
GAP = "medium"

CHART_HEIGHT = 330          # standard chart height (px)
CHART_HEIGHT_TALL = 420
CHART_HEIGHT_WIDE = 300     # full-width charts


def _css() -> str:
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:wght@600;700&family=Noto+Nastaliq+Urdu:wght@400;600&display=swap');

html, body, [class*="css"], .stApp {{
    font-family: {FONT_UI};
    color: {TEXT};
}}
.stApp {{ background: {BACKGROUND}; }}

/* Layout & Streamlit Header */
[data-testid="stHeader"] {{
    background: transparent !important;
    z-index: 999999 !important;
}}
/* Hide only the hamburger menu and deploy button */
#MainMenu, [data-testid="stAppDeployButton"], footer {{
    display: none !important;
    visibility: hidden !important;
}}
/* Collapsed state chevron button (when sidebar is closed) */
[data-testid="collapsedControl"] {{
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    color: {MAROON} !important;
    background: #FFFFFF !important;
    border: 1px solid {ROSE} !important;
    border-radius: 10px !important;
    box-shadow: 0 2px 10px rgba(110, 15, 26, 0.12) !important;
    transition: all 0.2s ease !important;
    margin: 0.4rem !important;
    position: fixed !important;
    top: 0.6rem !important;
    left: 0.6rem !important;
    z-index: 999999 !important;
}}
[data-testid="collapsedControl"]:hover {{
    background: {ROSE_LIGHT} !important;
    color: {CRIMSON} !important;
    border-color: {CRIMSON} !important;
    transform: scale(1.05);
}}
.block-container {{
    padding-top: 2rem; padding-bottom: 3rem;
    padding-left: 2rem; padding-right: 2rem; max-width: 1500px;
}}

/* Sidebar Clean Rounded Card Layout (matching Topbar language) */
/* Sidebar Clean Rounded Card Layout (matching Topbar language) */
[data-testid="stSidebar"] {{
    background-color: transparent !important;
}}
[data-testid="stSidebar"] > div:first-child {{
    background: transparent !important;
    padding: 0 !important;
    margin: 0 !important;
    height: 100vh !important;
    overflow: hidden !important;
}}
[data-testid="stSidebarContent"] {{
    background: #FFFFFF !important;
    border: 1px solid #E8DFE0 !important;
    border-radius: 16px !important;
    box-shadow: 0 4px 20px rgba(110, 15, 26, 0.06) !important;
    padding: 14px !important;
    margin: 10px 8px 10px 10px !important;
    display: flex !important;
    flex-direction: column !important;
    height: calc(100vh - 20px) !important;
    max-height: calc(100vh - 20px) !important;
    box-sizing: border-box !important;
    position: relative !important;
    overflow: hidden !important;
    overflow-y: auto !important;
    scrollbar-width: none !important;
    -ms-overflow-style: none !important;
    gap: 16px !important;
}}
[data-testid="stSidebarContent"]::-webkit-scrollbar {{
    display: none !important;
    width: 0 !important;
}}

/* Outer sidebar content wrapper */
[data-testid="stSidebarUserContent"] {{
    display: flex !important;
    flex-direction: column !important;
    height: 100% !important;
    min-height: 100% !important;
    max-height: 100% !important;
    padding: 0 !important;
    margin: 0 !important;
    box-sizing: border-box !important;
    overflow: hidden !important;
    flex: 1 1 auto !important;
}}
[data-testid="stSidebarUserContent"] > [data-testid="stVerticalBlock"],
[data-testid="stSidebarUserContent"] > div > [data-testid="stVerticalBlock"] {{
    display: flex !important;
    flex-direction: column !important;
    height: 100% !important;
    min-height: 100% !important;
    gap: 16px !important;
    overflow: hidden !important;
    padding: 0 !important;
    margin: 0 !important;
    box-sizing: border-box !important;
}}

/* Child 1: Brand Header Card */
[data-testid="stSidebarUserContent"] > [data-testid="stVerticalBlock"] > div:first-child,
[data-testid="stSidebarUserContent"] > div > [data-testid="stVerticalBlock"] > div:first-child {{
    flex: 0 0 auto !important;
    margin: 0 !important;
    padding: 0 !important;
}}

/* Child 2: Navigation Links Container (takes remaining space and scrolls cleanly) */
[data-testid="stSidebarUserContent"] > [data-testid="stVerticalBlock"] > div:nth-child(2),
[data-testid="stSidebarUserContent"] > div > [data-testid="stVerticalBlock"] > div:nth-child(2),
[data-testid="stSidebarNav"] {{
    flex: 1 1 auto !important;
    min-height: 0 !important;
    overflow-y: auto !important;
    scrollbar-width: none !important;
    -ms-overflow-style: none !important;
    margin: 0 !important;
    padding: 0 !important;
    display: flex !important;
    flex-direction: column !important;
}}
[data-testid="stSidebarUserContent"] > [data-testid="stVerticalBlock"] > div:nth-child(2)::-webkit-scrollbar,
[data-testid="stSidebarUserContent"] > div > [data-testid="stVerticalBlock"] > div:nth-child(2)::-webkit-scrollbar,
[data-testid="stSidebarNav"]::-webkit-scrollbar {{
    display: none !important;
    width: 0 !important;
    height: 0 !important;
}}

/* Inner nav list layout (inside st.container) */
[data-testid="stSidebarUserContent"] > [data-testid="stVerticalBlock"] > div:nth-child(2) [data-testid="stVerticalBlock"],
[data-testid="stSidebarUserContent"] > div > [data-testid="stVerticalBlock"] > div:nth-child(2) [data-testid="stVerticalBlock"] {{
    display: flex !important;
    flex-direction: column !important;
    gap: 6px !important;
    height: auto !important;
    min-height: 0 !important;
    overflow: visible !important;
    margin: 0 !important;
    padding: 0 !important;
}}

/* Individual nav item containers */
[data-testid="stSidebarUserContent"] [data-testid="stPageLink"],
[data-testid="stSidebarUserContent"] [data-testid="stElementContainer"]:has([data-testid="stPageLink"]) {{
    flex: 0 0 auto !important;
    height: auto !important;
    min-height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
}}

/* Child 3: Record Count Pill Container — pinned to bottom */
[data-testid="stSidebarUserContent"] > [data-testid="stVerticalBlock"] > div:last-child,
[data-testid="stSidebarUserContent"] > div > [data-testid="stVerticalBlock"] > div:last-child,
[data-testid="stSidebarUserContent"] [data-testid="stElementContainer"]:has(.sb-count),
[data-testid="stSidebarUserContent"] [data-testid="stMarkdownContainer"]:has(.sb-count) {{
    flex-shrink: 0 !important;
    margin-top: auto !important;
    margin-bottom: 0 !important;
    padding: 0 !important;
    height: auto !important;
    min-height: auto !important;
    overflow: visible !important;
}}

/* Streamlit built-in sidebar header area (contains the collapse « button) */
[data-testid="stSidebarHeader"] {{
    position: absolute !important;
    top: 22px !important;
    right: 22px !important;
    z-index: 100 !important;
    padding: 0 !important;
    margin: 0 !important;
    height: auto !important;
    min-height: 0 !important;
    background: transparent !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}}
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarHeader"] button {{
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    visibility: visible !important;
    opacity: 1 !important;
    color: #FFFFFF !important;
    background: rgba(255, 255, 255, 0.18) !important;
    border: 1px solid rgba(255, 255, 255, 0.35) !important;
    border-radius: 8px !important;
    padding: 0 !important;
    width: 30px !important;
    height: 30px !important;
    min-width: 30px !important;
    min-height: 30px !important;
    box-shadow: none !important;
    transition: all 0.2s ease !important;
    cursor: pointer !important;
}}
[data-testid="stSidebarCollapseButton"]:hover,
[data-testid="stSidebarHeader"] button:hover {{
    background: rgba(255, 255, 255, 0.3) !important;
    color: #FFFFFF !important;
    transform: scale(1.05);
}}
[data-testid="stSidebarCollapseButton"] svg,
[data-testid="stSidebarHeader"] button svg {{
    fill: #FFFFFF !important;
    color: #FFFFFF !important;
    width: 16px !important;
    height: 16px !important;
}}

/* Brand Card at top of sidebar */
.sb-brand-card {{
    background: linear-gradient(135deg, #7a1420 0%, #a51c2a 100%) !important;
    border-radius: 12px !important;
    padding: 12px 14px !important;
    color: #FFFFFF !important;
    margin: 0 !important;
    margin-bottom: 0 !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    box-shadow: 0 3px 10px rgba(110, 15, 26, 0.18) !important;
    position: relative !important;
    padding-right: 48px !important; /* leaves space for collapse button */
    flex-shrink: 0 !important;
    box-sizing: border-box !important;
}}
.sb-eyebrow {{
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: {ROSE_LIGHT};
    opacity: 0.95;
    margin-bottom: 0.12rem;
}}
.sb-title {{
    font-family: {FONT_DISPLAY};
    font-size: 1.02rem;
    font-weight: 700;
    line-height: 1.25;
    color: #FFFFFF;
    padding-right: 4px;
}}
.sb-desc {{
    font-size: 0.69rem;
    color: {ROSE_LIGHT};
    margin-top: 0.2rem;
    opacity: 0.88;
}}

/* Record Count Pill pinned to the bottom */
.sb-count {{
    flex-shrink: 0 !important;
    margin-top: auto !important;
    margin-bottom: 0 !important;
    padding: 10px 12px !important;
    line-height: 1.4 !important;
    height: auto !important;
    min-height: auto !important;
    overflow: visible !important;
    white-space: normal !important;
    text-align: center !important;
    background: #FBF3F2 !important;
    color: #6E0F1A !important;
    border: 1px solid #E8A3A8 !important;
    border-radius: 10px !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    box-sizing: border-box !important;
    display: block !important;
}}

/* Page header */
.page-header {{ margin: 1.1rem 0 1rem 0; }}
.page-header h2 {{
    font-family: {FONT_DISPLAY}; color: {MAROON}; font-size: 1.7rem;
    font-weight: 700; margin: 0; padding: 0; letter-spacing: .2px;
}}
.page-header p {{ color: {TEXT_MUTED}; font-size: .9rem; margin: .25rem 0 0 0; }}
.page-header .rule {{
    width: 56px; height: 3px; background: {CRIMSON}; border-radius: 2px; margin-top: .6rem;
}}

/* Cards (bordered containers) */
[data-testid="stVerticalBlockBorderWrapper"] {{
    background: {SURFACE};
    border: 1px solid {BORDER} !important;
    border-radius: 14px !important;
    box-shadow: 0 1px 2px rgba(110, 15, 26, .05), 0 4px 14px rgba(110, 15, 26, .04);
}}
.card-title {{
    font-size: .98rem; font-weight: 600; color: {MAROON}; margin: .1rem 0 .1rem 0;
}}
.card-sub {{ font-size: .76rem; color: {TEXT_MUTED}; margin-bottom: .2rem; }}

/* KPI cards */
.kpi {{
    background: {SURFACE}; border: 1px solid {BORDER}; border-radius: 14px;
    padding: 1rem 1.15rem; position: relative; overflow: hidden;
    box-shadow: 0 1px 2px rgba(110, 15, 26, .05), 0 4px 14px rgba(110, 15, 26, .04);
}}
.kpi::before {{
    content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 4px;
    background: linear-gradient(180deg, {CRIMSON}, {MAROON});
}}
.kpi .label {{
    font-size: .72rem; font-weight: 600; letter-spacing: .1em;
    text-transform: uppercase; color: {TEXT_MUTED};
}}
.kpi .value {{
    font-family: {FONT_DISPLAY}; font-size: 1.95rem; font-weight: 700;
    color: {MAROON}; line-height: 1.15; margin-top: .2rem;
}}
.kpi .sub {{ font-size: .76rem; color: {TEXT_MUTED}; margin-top: .15rem; }}

/* Notes */
.note {{
    background: #FBF3F2; border: 1px solid {ROSE_LIGHT}; border-left: 4px solid {CRIMSON};
    border-radius: 10px; padding: .7rem .95rem; font-size: .84rem; color: {TEXT};
}}
.empty-state {{
    text-align: center; padding: 3rem 1rem; color: {TEXT_MUTED};
    background: {SURFACE}; border: 1px dashed {BORDER}; border-radius: 14px;
}}

/* Urdu reading card */
.urdu-text {{
    direction: rtl; text-align: right; font-family: {FONT_URDU};
    font-size: 1.15rem; line-height: 2.3; color: {TEXT};
}}
.english-text {{ font-size: 1rem; line-height: 1.7; color: {TEXT}; }}
.meta-chip {{
    display: inline-block; background: {ROSE_LIGHT}; color: {MAROON};
    border-radius: 999px; padding: .15rem .65rem; font-size: .75rem;
    font-weight: 600; margin: 0 .35rem .35rem 0;
}}

/* Navigation links & Sidebar Controls */
[data-testid="stSidebarNav"] a,
[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"],
[data-testid="stSidebar"] [data-testid="stPageLink"] a,
[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"] {{
    padding: 12px 14px !important;
    min-height: 44px !important;
    border-radius: 12px !important;
    display: flex !important;
    align-items: center !important;
    gap: 12px !important;
    box-sizing: border-box !important;
    transition: all 0.2s ease !important;
    font-weight: 500 !important;
    color: {TEXT} !important;
    background: transparent !important;
    position: relative !important;
    border-left: 3px solid transparent !important;
    text-decoration: none !important;
    margin: 0 !important;
}}
/* Non-active item hover effect: soft tint, theme maroon text, 3px accent bar, translateX(2px) */
[data-testid="stSidebarNav"] a:not([aria-current="page"]):hover, 
[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"]:not([aria-current="page"]):hover,
[data-testid="stSidebar"] [data-testid="stPageLink"] a:not([aria-current="page"]):hover,
[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"]:not([aria-current="page"]):hover {{
    background: rgba(158, 27, 40, 0.08) !important;
    color: {MAROON} !important;
    border-left: 3px solid {CRIMSON} !important;
    transform: translateX(2px) !important;
}}
[data-testid="stSidebarNav"] a:not([aria-current="page"]):hover *,
[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"]:not([aria-current="page"]):hover *,
[data-testid="stSidebar"] [data-testid="stPageLink"] a:not([aria-current="page"]):hover *,
[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"]:not([aria-current="page"]):hover * {{
    color: {MAROON} !important;
    fill: {MAROON} !important;
}}

/* Active Page state: permanent crimson/maroon gradient untouched by hover */
[data-testid="stSidebarNav"] a[aria-current="page"], 
[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"][aria-current="page"],
[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"],
[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"][aria-current="page"],
[data-testid="stSidebar"] [data-testid="stPageLink"] a[data-active="true"],
[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"][data-active="true"] {{
    background: linear-gradient(135deg, #7a1420 0%, #a51c2a 100%) !important;
    background-color: #7a1420 !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 12px rgba(110, 15, 26, 0.25) !important;
    border-left: 3px solid rgba(255, 255, 255, 0.6) !important;
    transform: none !important;
}}
[data-testid="stSidebarNav"] a[aria-current="page"] *, 
[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"][aria-current="page"] *,
[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"] *,
[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"][aria-current="page"] *,
[data-testid="stSidebar"] [data-testid="stPageLink"] a[data-active="true"] *,
[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"][data-active="true"] * {{
    color: #FFFFFF !important;
    fill: #FFFFFF !important;
}}

/* Keyboard focus-visible state */
[data-testid="stSidebarNav"] a:focus-visible,
[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"]:focus-visible,
[data-testid="stSidebar"] [data-testid="stPageLink"] a:focus-visible,
[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"]:focus-visible {{
    outline: 2px solid {CRIMSON} !important;
    outline-offset: 1px !important;
}}

/* Global Filter Bar & Action Buttons */
button[kind="secondary"] {{
    border-radius: 10px !important;
    border: 1px solid {ROSE} !important;
    background: #FFFFFF !important;
    color: {MAROON} !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 1px 4px rgba(110, 15, 26, 0.05) !important;
}}
button[kind="secondary"]:hover {{
    background: linear-gradient(135deg, {MAROON} 0%, {CRIMSON} 100%) !important;
    color: #FFFFFF !important;
    border-color: {CRIMSON} !important;
    box-shadow: 0 4px 12px rgba(110, 15, 26, 0.22) !important;
}}
div[data-testid="stRadio"] > div {{
    gap: 0.6rem !important;
}}
div[data-baseweb="select"] > div {{
    border-radius: 10px !important;
    border-color: {BORDER} !important;
}}
div[data-baseweb="select"] > div:focus-within {{
    border-color: {CRIMSON} !important;
    box-shadow: 0 0 0 1px {CRIMSON} !important;
}}
</style>
"""


def apply_theme() -> None:
    """Inject the global stylesheet."""
    st.markdown(_css(), unsafe_allow_html=True)
