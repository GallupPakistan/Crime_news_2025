"""Smoke test: build every chart under every language filter and an empty filter.

Run from the project folder:  python tests/smoke_test.py
"""
from __future__ import annotations

import inspect
import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import charts  # noqa: E402
import config as C  # noqa: E402


def load() -> pd.DataFrame:
    df = pd.read_parquet(C.PARQUET_PATH)
    df[C.COL_DATE] = pd.to_datetime(df[C.COL_DATE])
    df["Date"] = pd.to_datetime(df["Date"])
    return df


def chart_functions():
    for name, fn in inspect.getmembers(charts, inspect.isfunction):
        if name.startswith("_") or name in ("configure", "calculate_crime_index"):
            continue
        if fn.__module__ != charts.__name__:
            continue
        yield name, fn


def check_data(df: pd.DataFrame) -> list[str]:
    """Data-level assertions that mirror the design spec."""
    problems = []
    if len(df) != 44598:
        problems.append(f"expected 44,598 rows, found {len(df):,}")
    if df[C.COL_CATEGORY].nunique() != 37:
        problems.append("expected 37 categories")
    if df[C.COL_CATEGORY].str.contains(r"[؀-ۿ]").any():
        problems.append("Urdu script found in Crime_Category")
    if (df["Deaths_Exact"] > C.CASUALTY_CAP).any() or (df["Injured_Exact"] > C.CASUALTY_CAP).any():
        problems.append("exact casualty column contains values above the cap")
    if not set(df["Year"].unique()).issubset({2025, 2026}):
        problems.append("rows outside the data years (2025, 2026) are present")
    if "City42_Urdu_Crime_News_2025" in set(df[C.COL_SOURCE]):
        problems.append("source typo was not merged")
    return problems


def main() -> int:
    df = load()
    charts.configure(df)
    failures = check_data(df)

    scenarios = {
        "All": df,
        "Urdu": df[df[C.COL_LANGUAGE] == "Urdu"],
        "English": df[df[C.COL_LANGUAGE] == "English"],
        "Single month": df[df["Month"] == 3],
        "Tiny (5 rows)": df.head(5),
        "Empty": df.iloc[0:0],
    }
    built = 0
    for scenario, frame in scenarios.items():
        try:
            idf = charts.calculate_crime_index(frame)
            assert isinstance(idf, pd.DataFrame), "calculate_crime_index did not return a DataFrame"
        except Exception as exc:  # noqa: BLE001
            failures.append(f"[{scenario}] calculate_crime_index: {type(exc).__name__}: {exc}")

        for name, fn in chart_functions():
            try:
                fig = fn(frame)
                assert isinstance(fig, go.Figure), "did not return a Figure"
                fig.to_dict()          # forces Plotly validation
                built += 1
            except Exception as exc:   # noqa: BLE001
                failures.append(f"[{scenario}] {name}: {type(exc).__name__}: {exc}")

    print(f"Charts built without error: {built}")
    if failures:
        print("\nFAILURES")
        for line in failures:
            print(" -", line)
        return 1
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
