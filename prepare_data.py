"""Prepare the crime news dataset.

Reads the Excel workbook (2025) and CSV dataset (2026), applies the agreed
cleaning and harmonization rules, and writes a compact parquet file that
the dashboard loads.

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

EXTRA_CRIME_MAPPINGS = {
    "اسلحہ کی اسمگلنگ": "Illegal Weapons",
    "آن لائن ہراسانی": "Cybercrime",
    "ہیومن سمگلنگ": "Human Trafficking",
    "انسانی اعضا کی سمگلنگ": "Human Trafficking",
    "ہراسگی": "Rape / Sexual Assault",
    "ہراسانی": "Rape / Sexual Assault",
    "جنسی زیادتی/اغوا": "Rape / Sexual Assault",
}


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
        df.loc[~df[C.COL_CITY].str.contains(_URDU_SCRIPT, na=False), C.COL_CITY].unique()
    )
    alias_lookup = {
        normalise_urdu(urdu): english
        for urdu, english in C.CITY_ALIASES.items()
        if english in english_names
    }
    normalised = df[C.COL_CITY].astype(str).map(normalise_urdu)
    mapped = normalised.map(alias_lookup)
    applied = mapped.notna()
    df.loc[applied, C.COL_CITY] = mapped[applied]
    counts = mapped[applied].value_counts().to_dict()
    return df, counts


def prepare_2025_data(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, str], dict[str, str]]:
    """Process the 2025 Excel dataset."""
    for col in df.select_dtypes(include=["object", "string"]).columns:
        df[col] = df[col].astype("string").str.strip()

    # Build reference lookup mappings before filtering
    crime_type_to_cat = (
        df.dropna(subset=["Crime_Type", "Crime_Category"])
        .groupby("Crime_Type")["Crime_Category"]
        .agg(lambda x: x.mode()[0])
        .to_dict()
    )
    crime_type_to_cat.update(EXTRA_CRIME_MAPPINGS)

    city_to_std = (
        df.dropna(subset=["City", "City_Standard"])
        .groupby("City")["City_Standard"]
        .agg(lambda x: x.mode()[0])
        .to_dict()
    )

    df[C.COL_DATE] = pd.to_datetime(df[C.COL_DATE], errors="coerce")
    in_year = df[C.COL_DATE].dt.year == 2025
    df = df[in_year].copy()

    # Source & Language fixes
    df[C.COL_SOURCE] = df[C.COL_SOURCE].replace(C.SOURCE_FIXES)
    if hasattr(C, "LANGUAGE_FIXES"):
        df[C.COL_LANGUAGE] = df[C.COL_LANGUAGE].replace(C.LANGUAGE_FIXES)

    df[C.COL_CITY] = df[C.COL_CITY].astype("object")
    df, _ = apply_city_aliases(df)

    # Date helper columns
    df["Year"] = df[C.COL_DATE].dt.year.astype("int16")
    df["Date"] = df[C.COL_DATE].dt.normalize()
    df["Month"] = df[C.COL_DATE].dt.month.astype("int8")
    df["Weekday_Num"] = df[C.COL_DATE].dt.weekday.astype("int8")
    df["Weekday"] = df["Weekday_Num"].map(dict(enumerate(C.WEEKDAY_LABELS)))

    # Casualty columns
    df = pd.concat([
        df,
        casualty_columns(df["Deaths"], "Deaths"),
        casualty_columns(df["Injured"], "Injured"),
    ], axis=1)
    df["Fatal"] = df["Deaths_Num"].fillna(0) >= 1
    df["Has_Casualty"] = (df["Deaths_Num"].fillna(0) >= 1) | (df["Injured_Num"].fillna(0) >= 1)

    return df, crime_type_to_cat, city_to_std


def prepare_2026_data(df: pd.DataFrame, crime_type_to_cat: dict[str, str], city_to_std: dict[str, str]) -> pd.DataFrame:
    """Process the 2026 CSV dataset."""
    for col in df.select_dtypes(include=["object", "string"]).columns:
        df[col] = df[col].astype("string").str.strip()

    # Rename CSV columns to standard schema
    if "Source" in df.columns:
        df = df.rename(columns={"Source": C.COL_SOURCE})
    if "Article_Language" in df.columns:
        df = df.rename(columns={"Article_Language": C.COL_LANGUAGE})

    # Language cleanup
    df[C.COL_LANGUAGE] = df[C.COL_LANGUAGE].fillna("Urdu").replace({"ur": "Urdu"})

    # Parse Published_Date (split pipe if present, handle 12h/24h)
    raw_dates = df[C.COL_DATE].astype(str).str.split("|").str[0].str.strip()
    df[C.COL_DATE] = pd.to_datetime(raw_dates, format="mixed", errors="coerce")
    df = df[df[C.COL_DATE].dt.year == 2026].copy()

    # Source harmonization
    df[C.COL_SOURCE] = df[C.COL_SOURCE].replace(C.SOURCE_FIXES)

    # Map Crime Category
    df[C.COL_CRIME_TYPE_RAW] = df["Crime_Type"]
    df[C.COL_CATEGORY] = df[C.COL_CRIME_TYPE_RAW].map(crime_type_to_cat).fillna("Other")

    # Map City
    df[C.COL_CITY_RAW] = df["City"]
    df[C.COL_CITY] = df[C.COL_CITY_RAW].map(city_to_std).fillna(df[C.COL_CITY_RAW]).fillna(C.NOT_SPECIFIED_CITY)
    df, _ = apply_city_aliases(df)

    # Date helper columns
    df["Year"] = df[C.COL_DATE].dt.year.astype("int16")
    df["Date"] = df[C.COL_DATE].dt.normalize()
    df["Month"] = df[C.COL_DATE].dt.month.astype("int8")
    df["Weekday_Num"] = df[C.COL_DATE].dt.weekday.astype("int8")
    df["Weekday"] = df["Weekday_Num"].map(dict(enumerate(C.WEEKDAY_LABELS)))

    # Casualty columns
    df = pd.concat([
        df,
        casualty_columns(df["Deaths"], "Deaths"),
        casualty_columns(df["Injured"], "Injured"),
    ], axis=1)
    df["Fatal"] = df["Deaths_Num"].fillna(0) >= 1
    df["Has_Casualty"] = (df["Deaths_Num"].fillna(0) >= 1) | (df["Injured_Num"].fillna(0) >= 1)

    return df


def main() -> int:
    if not C.EXCEL_PATH.exists():
        print(f"ERROR: Excel file not found: {C.EXCEL_PATH}")
        return 1

    print(f"Reading {C.EXCEL_PATH.name} (2025) ...")
    raw_2025 = pd.read_excel(C.EXCEL_PATH, sheet_name=C.EXCEL_SHEET)
    df_2025, crime_map, city_map = prepare_2025_data(raw_2025)
    print(f"  Processed 2025 rows: {len(df_2025):,}")

    frames = [df_2025]

    if hasattr(C, "CSV_2026_PATH") and C.CSV_2026_PATH.exists():
        print(f"Reading {C.CSV_2026_PATH.name} (2026) ...")
        raw_2026 = pd.read_csv(C.CSV_2026_PATH)
        df_2026 = prepare_2026_data(raw_2026, crime_map, city_map)
        print(f"  Processed 2026 rows: {len(df_2026):,}")
        frames.append(df_2026)
    else:
        print("  Notice: 2026 CSV file not found; skipping 2026.")

    combined = pd.concat(frames, ignore_index=True)

    keep = [
        "Year", C.COL_DATE, "Date", "Month", "Weekday", "Weekday_Num",
        C.COL_LANGUAGE, C.COL_SOURCE, "Source_URL",
        C.COL_CITY_RAW, C.COL_CITY, C.COL_CRIME_TYPE_RAW, C.COL_CATEGORY,
        "Deaths", "Injured",
        "Deaths_Exact", "Deaths_Num", "Deaths_Status",
        "Injured_Exact", "Injured_Num", "Injured_Status",
        "Fatal", "Has_Casualty", "Summary",
    ]
    out = combined[keep].copy()
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
    print(f"  Total combined rows written : {len(out):,}")
    print(f"  Year breakdown              : {out['Year'].value_counts().to_dict()}")
    print(f"  Language split              : {out[C.COL_LANGUAGE].value_counts().to_dict()}")
    print(f"  Categories                  : {out[C.COL_CATEGORY].nunique()}")
    print(f"  Cities                      : {out[C.COL_CITY].nunique()}")
    print(f"  Sources                     : {out[C.COL_SOURCE].nunique()}")
    print(f"  Deaths status               : {out['Deaths_Status'].value_counts().to_dict()}")
    print(f"  Injured status              : {out['Injured_Status'].value_counts().to_dict()}")
    print(f"  Exact deaths / injured sum  : {out['Deaths_Exact'].sum():,.0f} / {out['Injured_Exact'].sum():,.0f}")
    assert out[C.COL_CATEGORY].str.contains(_URDU_SCRIPT).sum() == 0, "Urdu script in category"
    print(f"\nSaved: {C.PARQUET_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
