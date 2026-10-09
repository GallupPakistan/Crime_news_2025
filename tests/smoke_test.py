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
        if name.startswith("_") or name == "configure":
            continue
        if fn.__module__ != charts.__name__:
            continue
        yield name, fn


def check_data(df: pd.DataFrame) -> list[str]:
    """Data-level assertions that mirror the design spec."""
    problems = []
    if len(df) != 20482:
        problems.append(f"expected 20,482 rows, found {len(df):,}")
    if df[C.COL_LANGUAGE].value_counts().to_dict() != {"Urdu": 15816, "English": 4666}:
        problems.append(f"unexpected language split {df[C.COL_LANGUAGE].value_counts().to_dict()}")
    if df[C.COL_CATEGORY].nunique() != 37:
        problems.append("expected 37 categories")
    if df[C.COL_CATEGORY].str.contains(r"[؀-ۿ]").any():
        problems.append("Urdu script found in Crime_Category")
    if round(df["Deaths_Exact"].sum()) != 20616 or round(df["Injured_Exact"].sum()) != 15759:
        problems.append("exact casualty totals differ from the spec rule")
    if (df["Deaths_Exact"] > C.CASUALTY_CAP).any() or (df["Injured_Exact"] > C.CASUALTY_CAP).any():
        problems.append("exact casualty column contains values above the cap")
    if (df[C.COL_DATE].dt.year != C.DATA_YEAR).any():
        problems.append("rows outside the data year are present")
    if "City42_Urdu_Crime_News_2025" in set(df[C.COL_SOURCE]):
        problems.append("source typo was not merged")
    cyber = df[df[C.COL_CATEGORY] == "Cybercrime"]
    if len(cyber) != 530:
        problems.append(f"Cybercrime should have 530 rows, found {len(cyber)}")
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
