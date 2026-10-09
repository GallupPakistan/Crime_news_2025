"""Data loading and filtering."""
from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd
import streamlit as st

import config as C


@st.cache_data(show_spinner="Loading data ...")
def load_data() -> pd.DataFrame:
    """Load the prepared parquet file (cached)."""
    if not C.PARQUET_PATH.exists():
        st.error(
            "The prepared data file is missing. Run `python prepare_data.py` "
            "once to create it, then restart the dashboard."
        )
        st.stop()
    df = pd.read_parquet(C.PARQUET_PATH)
    df[C.COL_DATE] = pd.to_datetime(df[C.COL_DATE])
    df["Date"] = pd.to_datetime(df["Date"])
    return df


@dataclass
class Filters:
    """Global filter selection."""

    language: str = "All"                       # All / Urdu / English
    month_range: tuple[int, int] = (1, 12)      # inclusive month numbers
    categories: list[str] = field(default_factory=list)   # empty = all
    sources: list[str] = field(default_factory=list)      # empty = all


def apply_filters(df: pd.DataFrame, f: Filters) -> pd.DataFrame:
    """Return the rows that match the selected filters."""
    mask = df["Month"].between(f.month_range[0], f.month_range[1])
    if f.language in C.LANGUAGES:
        mask &= df[C.COL_LANGUAGE] == f.language
    if f.categories:
        mask &= df[C.COL_CATEGORY].isin(f.categories)
    if f.sources:
        mask &= df[C.COL_SOURCE].isin(f.sources)
    return df[mask]
