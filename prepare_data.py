"""Prepare the crime news dataset.

Reads the Excel workbook once, applies the agreed cleaning rules and writes a
compact parquet file that the dashboard loads.

Run:  python prepare_data.py
"""
from __future__ import annotations

import re
import sys

import pandas as pd

import config as C

_URDU_SCRIPT = re.compile(r"[؀-ۿ]")
_URDU_NORMALISE = str.maketrans({"ي": "ی", "ك": "ک", "ە": "ہ", "ۀ": "ہ", "ہ": "ہ"})
_INVISIBLE = re.compile(r"[​-‏ً-ٟ\s]+")


def normalise_urdu(text: str) -> str:
    """Normalise Urdu text so that spelling variants of the same name match."""
    text = str(text).replace("آ", "آ")  # alef + maddah -> alef madda
    text = text.translate(_URDU_NORMALISE)
    return _INVISIBLE.sub("", text)


def parse_count(value) -> float | None:
    """Return a number if the cell holds an exact number, otherwise None."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(",", "")
    if re.fullmatch(r"\d+(\.\d+)?", text):
        return float(text)
    return None


def casualty_columns(series: pd.Series, prefix: str) -> pd.DataFrame:
    """Split a Deaths/Injured column into exact value, numeric value and status."""
    numeric = series.map(parse_count)
    num = pd.to_numeric(numeric, errors="coerce")
    status = pd.Series("not_specified", index=series.index, dtype="object")
    status[num.notna() & (num <= C.CASUALTY_CAP)] = "exact"
    status[num.notna() & (num > C.CASUALTY_CAP)] = "above_cap"
    exact = num.where(status == "exact")
    return pd.DataFrame({
        f"{prefix}_Exact": exact,
        f"{prefix}_Num": num,
        f"{prefix}_Status": status,
    })


def apply_city_aliases(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    """Map Urdu-script city names to existing English names (data-backed only)."""
    english_names = set(
        df.loc[~df[C.COL_CITY].str.contains(_URDU_SCRIPT), C.COL_CITY].unique()
    )
    alias_lookup = {
        normalise_urdu(urdu): english
        for urdu, english in C.CITY_ALIASES.items()
        if english in english_names
    }
    normalised = df[C.COL_CITY].map(normalise_urdu)
    mapped = normalised.map(alias_lookup)
    applied = mapped.notna()
    df.loc[applied, C.COL_CITY] = mapped[applied]
    counts = mapped[applied].value_counts().to_dict()
    return df, counts


def main() -> int:
    if not C.EXCEL_PATH.exists():
        print(f"ERROR: Excel file not found: {C.EXCEL_PATH}")
        return 1

    print(f"Reading {C.EXCEL_PATH.name} ...")
    df = pd.read_excel(C.EXCEL_PATH, sheet_name=C.EXCEL_SHEET)
    total_rows = len(df)

    for col in df.select_dtypes(include=["object", "string"]).columns:
        df[col] = df[col].astype("string").str.strip()

    # 1. Keep the dataset year only
    df[C.COL_DATE] = pd.to_datetime(df[C.COL_DATE], errors="coerce")
    in_year = df[C.COL_DATE].dt.year == C.DATA_YEAR
    excluded = int((~in_year).sum())
    df = df[in_year].copy()

    # 2. Source typo
    df[C.COL_SOURCE] = df[C.COL_SOURCE].replace(C.SOURCE_FIXES)

    # 3. City aliases (only where the English name already exists in the data)
    df[C.COL_CITY] = df[C.COL_CITY].astype("object")
    df, alias_counts = apply_city_aliases(df)

    # 4. Date helper columns
    df["Date"] = df[C.COL_DATE].dt.normalize()
    df["Month"] = df[C.COL_DATE].dt.month.astype("int8")
    df["Weekday_Num"] = df[C.COL_DATE].dt.weekday.astype("int8")
    df["Weekday"] = df["Weekday_Num"].map(dict(enumerate(C.WEEKDAY_LABELS)))

    # 5. Casualty columns
    df = pd.concat([
        df,
        casualty_columns(df["Deaths"], "Deaths"),
        casualty_columns(df["Injured"], "Injured"),
    ], axis=1)
    df["Fatal"] = df["Deaths_Num"].fillna(0) >= 1
    df["Has_Casualty"] = (df["Deaths_Num"].fillna(0) >= 1) | (df["Injured_Num"].fillna(0) >= 1)

    keep = [
        C.COL_DATE, "Date", "Month", "Weekday", "Weekday_Num",
        C.COL_LANGUAGE, C.COL_SOURCE, "Source_URL",
        C.COL_CITY_RAW, C.COL_CITY, C.COL_CRIME_TYPE_RAW, C.COL_CATEGORY,
        "Deaths", "Injured",
        "Deaths_Exact", "Deaths_Num", "Deaths_Status",
        "Injured_Exact", "Injured_Num", "Injured_Status",
        "Fatal", "Has_Casualty", "Summary",
    ]
    out = df[keep].copy()
    for col in ("Deaths", "Injured"):
        out[col] = out[col].astype("string")
    for col in (C.COL_LANGUAGE, C.COL_SOURCE, C.COL_CITY, C.COL_CATEGORY,
                "Weekday", "Deaths_Status", "Injured_Status"):
        out[col] = out[col].astype("string")
    out = out.sort_values(C.COL_DATE).reset_index(drop=True)

    C.DATA_DIR.mkdir(exist_ok=True)
    out.to_parquet(C.PARQUET_PATH, index=False)

    # ----------------------------------------------------------- Verification
    print("\nPreparation summary")
    print(f"  Rows read from Excel        : {total_rows:,}")
    print(f"  Rows outside {C.DATA_YEAR} (excluded) : {excluded:,}")
    print(f"  Rows written                : {len(out):,}")
    print(f"  Language split              : {out[C.COL_LANGUAGE].value_counts().to_dict()}")
    print(f"  Categories                  : {out[C.COL_CATEGORY].nunique()}")
    print(f"  Cities                      : {out[C.COL_CITY].nunique()}")
    print(f"  Sources                     : {out[C.COL_SOURCE].nunique()}")
    print(f"  City aliases applied        : {sum(alias_counts.values())} rows {alias_counts}")
    print(f"  Deaths status               : {out['Deaths_Status'].value_counts().to_dict()}")
    print(f"  Injured status              : {out['Injured_Status'].value_counts().to_dict()}")
    print(f"  Exact deaths / injured sum  : {out['Deaths_Exact'].sum():,.0f} / {out['Injured_Exact'].sum():,.0f}")
    assert out[C.COL_CATEGORY].str.contains(_URDU_SCRIPT).sum() == 0, "Urdu script in category"
    print(f"\nSaved: {C.PARQUET_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
