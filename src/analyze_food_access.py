"""Reproducible food-access analysis for Data for Dinner 2026.

Outputs are deliberately descriptive. The script does not make causal claims and
does not treat the global, household, and retailer-access measures as identical.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "2026-08-22"
PROCESSED = ROOT / "data" / "processed"
METADATA = ROOT / "data" / "metadata"
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
VENDOR = ROOT / "tools" / "vendor"
sys.path.insert(0, str(VENDOR))
import shapefile  # type: ignore  # vendored by requirements.txt


SOUTHEAST = {
    "Alabama": "AL",
    "Arkansas": "AR",
    "Florida": "FL",
    "Georgia": "GA",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Mississippi": "MS",
    "North Carolina": "NC",
    "South Carolina": "SC",
    "Tennessee": "TN",
}

STATE_ABBR = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
    "District of Columbia": "DC", "Florida": "FL", "Georgia": "GA", "Hawaii": "HI",
    "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
    "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
    "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
    "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
    "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
    "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT",
    "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
    "Wisconsin": "WI", "Wyoming": "WY",
}

COLORS = {
    "navy": "#0B2545",
    "blue": "#2E74B5",
    "mid_blue": "#5B9BD5",
    "light_blue": "#DCEAF7",
    "gold": "#D6A84B",
    "gray": "#687386",
    "light_gray": "#EEF2F6",
    "grid": "#D5DCE5",
    "white": "#FFFFFF",
    "red": "#9B1C1C",
}


def ensure_dirs() -> None:
    for path in (PROCESSED, METADATA, RESULTS, FIGURES):
        path.mkdir(parents=True, exist_ok=True)


def numeric(value) -> float:
    if pd.isna(value):
        return math.nan
    text = str(value).strip()
    if text.startswith("<"):
        return float(text[1:])
    if text.startswith(">"):
        return float(text[1:])
    return float(text)


def ratio_percent(numerator: pd.Series, denominator: pd.Series) -> float:
    den = float(pd.to_numeric(denominator, errors="coerce").sum())
    if den == 0:
        return math.nan
    num = float(pd.to_numeric(numerator, errors="coerce").sum())
    return 100.0 * num / den


def read_global_data() -> pd.DataFrame:
    fs_path = RAW / "faostat_fs" / "extracted" / "Food_Security_Data_E_All_Data_(Normalized).csv"
    coahd_path = RAW / "faostat_coahd" / "extracted" / "Cost_Affordability_Healthy_Diet_(CoAHD)_E_All_Data_(Normalized).csv"
    fs = pd.read_csv(fs_path, low_memory=False, encoding="utf-8-sig")
    coahd = pd.read_csv(coahd_path, low_memory=False, encoding="utf-8-sig")
    areas = [
        "World",
        "Africa",
        "Asia",
        "Europe",
        "Latin America and the Caribbean",
        "Oceania",
        "United States of America",
    ]
    indicators = {
        "moderate_or_severe_food_insecurity": "Prevalence of moderate or severe food insecurity in the total population (percent) (3-year average)",
        "severe_food_insecurity": "Prevalence of severe food insecurity in the total population (percent) (3-year average)",
        "undernourishment": "Prevalence of undernourishment (percent) (3-year average)",
    }
    records: list[dict] = []
    for key, item in indicators.items():
        subset = fs[(fs["Item"] == item) & fs["Area"].isin(areas)].copy()
        subset["period_end"] = subset["Year"].astype(str).str.extract(r"(\d{4})$")[0].astype(int)
        latest_end = int(subset["period_end"].max())
        subset = subset[subset["period_end"] == latest_end]
        for area in areas:
            rows = subset[subset["Area"] == area]
            if rows.empty:
                continue
            value_row = rows[rows["Element"] == "Value"].iloc[0]
            lower = rows.loc[rows["Element"].str.contains("Lower", na=False), "Value"]
            upper = rows.loc[rows["Element"].str.contains("Upper", na=False), "Value"]
            records.append(
                {
                    "geography": area,
                    "indicator_key": key,
                    "indicator": item,
                    "period": str(value_row["Year"]),
                    "unit": value_row["Unit"],
                    "display_value": str(value_row["Value"]),
                    "value": numeric(value_row["Value"]),
                    "lower_bound": numeric(lower.iloc[0]) if not lower.empty else math.nan,
                    "upper_bound": numeric(upper.iloc[0]) if not upper.empty else math.nan,
                    "flag": value_row["Flag"],
                    "source_id": "FAO_FS",
                }
            )

    coahd_indicators = {
        "healthy_diet_unaffordability": "Prevalence of unaffordability (PUA)",
        "people_unable_to_afford_healthy_diet": "Number of people unable to afford a healthy diet (NUA)",
    }
    for key, item in coahd_indicators.items():
        subset = coahd[(coahd["Item"] == item) & coahd["Area"].isin(areas) & (coahd["Element"] == "Value")].copy()
        latest_year = int(subset["Year"].max())
        subset = subset[subset["Year"] == latest_year]
        for _, row in subset.iterrows():
            records.append(
                {
                    "geography": row["Area"],
                    "indicator_key": key,
                    "indicator": item,
                    "period": str(row["Year"]),
                    "unit": row["Unit"],
                    "display_value": str(row["Value"]),
                    "value": numeric(row["Value"]),
                    "lower_bound": math.nan,
                    "upper_bound": math.nan,
                    "flag": row["Flag"],
                    "source_id": "FAO_COAHD",
                }
            )
    result = pd.DataFrame(records)
    result.to_csv(PROCESSED / "global_food_access_summary.csv", index=False)
    return result


def read_us_food_security() -> tuple[pd.DataFrame, dict]:
    base = RAW / "usda_food_security" / "extracted" / "foodsecurity_csv_datafiles"
    state = pd.read_csv(base / "foodsecurity-state-2024.csv", encoding="cp1252")
    state.columns = [
        "period",
        "state_abbr",
        "food_insecurity_pct",
        "food_insecurity_moe_pp",
        "very_low_food_security_pct",
        "very_low_food_security_moe_pp",
    ]
    state["period"] = state["period"].astype(str).str.replace("\u2013", "-", regex=False)
    latest = state[state["period"] == "2022-2024"].copy()
    latest.to_csv(PROCESSED / "us_food_insecurity_states_2022_2024.csv", index=False)

    households = pd.read_csv(base / "foodsecurity-all-households-2024.csv", encoding="cp1252")
    row = households[(households["Year"] == 2024) & (households["Category"] == "All households")].iloc[0]
    south = households[
        (households["Year"] == 2024)
        & (households["Category"] == "Census geographic region")
        & (households["Subcategory"] == "South")
    ].iloc[0]
    national = {
        "year": 2024,
        "households_thousands": int(row["Total"]),
        "food_secure_pct": float(row["Food secure-percent"]),
        "food_insecure_thousands": int(row["Food insecure-1,000"]),
        "food_insecure_pct": float(row["Food insecure-percent"]),
        "very_low_thousands": int(row["Very low food security-1,000"]),
        "very_low_pct": float(row["Very low food security-percent"]),
        "census_south_food_insecure_pct": float(south["Food insecure-percent"]),
        "source_id": "USDA_FOOD_SECURITY_CSV",
    }
    return latest, national


def load_sram() -> tuple[pd.DataFrame, dict]:
    base = RAW / "usda_sram" / "extracted"
    common = {"dtype": {"CensusTract20": "string"}, "low_memory": False, "encoding": "cp1252"}
    general = pd.read_csv(base / "SRAM General Tract Characteristics Data.csv", **common)
    driving = pd.read_csv(base / "SRAM Driving Distance Data.csv", **common)
    straight = pd.read_csv(base / "SRAM Straight Line Distance Data.csv", **common)

    raw_join_matches = len(set(general["CensusTract20"]) & set(driving["CensusTract20"]))
    for frame in (general, driving, straight):
        frame["GEOID20"] = frame["CensusTract20"].str.zfill(11)
    general = general.drop(columns="CensusTract20")
    driving = driving.drop(columns=["CensusTract20", "State", "County20", "County24"])
    straight = straight.drop(columns=["CensusTract20", "State", "County20", "County24"])
    merged = general.merge(driving, on="GEOID20", validate="one_to_one").merge(straight, on="GEOID20", validate="one_to_one")

    derived = {}
    for group in ("kids", "seniors", "hunv", "snap"):
        derived[f"la_{group}_mixed"] = np.where(
            merged["Urban"].eq(1),
            merged[f"DD_SRAM_la{group}1"],
            merged[f"DD_SRAM_la{group}10"],
        )
    merged = pd.concat([merged, pd.DataFrame(derived, index=merged.index)], axis=1)
    diagnostics = {
        "general_rows": len(general),
        "driving_rows": len(driving),
        "straight_rows": len(straight),
        "raw_join_matches_before_geoid_padding": raw_join_matches,
        "normalized_rows": len(merged),
        "state_count_including_dc": int(merged["State"].nunique()),
    }
    return merged, diagnostics


def aggregate_access(frame: pd.DataFrame) -> dict:
    return {
        "tract_count": int(len(frame)),
        "population": int(frame["POP2020"].sum()),
        "low_income_population": int(frame["TractLOWI"].sum()),
        "low_access_population": int(frame["DD_SRAM_LAPOP1_10"].sum()),
        "low_access_population_pct": ratio_percent(frame["DD_SRAM_LAPOP1_10"], frame["POP2020"]),
        "low_income_low_access_population": int(frame["DD_SRAM_LALOWI1_10"].sum()),
        "low_income_low_access_population_pct": ratio_percent(frame["DD_SRAM_LALOWI1_10"], frame["TractLOWI"]),
        "lila_tract_count": int(frame["DD_SRAM_LILATracts_1And10"].sum()),
        "lila_tract_pct": 100.0 * float(frame["DD_SRAM_LILATracts_1And10"].sum()) / len(frame),
        "low_access_children_pct": ratio_percent(frame["la_kids_mixed"], frame["TractKids"]),
        "low_access_seniors_pct": ratio_percent(frame["la_seniors_mixed"], frame["TractSeniors"]),
        "low_access_no_vehicle_housing_units_pct": ratio_percent(frame["la_hunv_mixed"], frame["TractHUNV"]),
        "low_access_snap_housing_units_pct": ratio_percent(frame["la_snap_mixed"], frame["TractSNAP"]),
    }


def build_state_and_alabama_outputs(sram: pd.DataFrame, state_food: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict]:
    state_rows = []
    for name, frame in sram.groupby("State", sort=True):
        state_rows.append({"state": name, "state_abbr": STATE_ABBR.get(name, ""), **aggregate_access(frame)})
    states = pd.DataFrame(state_rows)
    states = states.merge(state_food, on="state_abbr", how="left", validate="one_to_one")
    states.to_csv(PROCESSED / "us_state_retail_access_summary.csv", index=False)

    southeast = states[states["state"].isin(SOUTHEAST)].copy()
    for column, rank_name in [
        ("food_insecurity_pct", "food_insecurity_rank_high_to_low"),
        ("low_access_population_pct", "low_access_population_rank_high_to_low"),
        ("low_income_low_access_population_pct", "low_income_low_access_rank_high_to_low"),
        ("lila_tract_pct", "lila_tract_share_rank_high_to_low"),
    ]:
        southeast[rank_name] = southeast[column].rank(method="min", ascending=False).astype("Int64")
    southeast = southeast.sort_values("food_insecurity_pct", ascending=False)
    southeast.to_csv(PROCESSED / "southeast_state_comparison.csv", index=False)

    alabama = sram[sram["State"] == "Alabama"].copy()
    for numerator, denominator, output in [
        ("DD_SRAM_LAPOP1_10", "POP2020", "low_access_population_pct"),
        ("DD_SRAM_LALOWI1_10", "TractLOWI", "low_income_low_access_population_pct"),
        ("la_kids_mixed", "TractKids", "low_access_children_pct"),
        ("la_seniors_mixed", "TractSeniors", "low_access_seniors_pct"),
        ("la_hunv_mixed", "TractHUNV", "low_access_no_vehicle_housing_units_pct"),
        ("la_snap_mixed", "TractSNAP", "low_access_snap_housing_units_pct"),
    ]:
        alabama[output] = np.where(alabama[denominator] > 0, 100.0 * alabama[numerator] / alabama[denominator], np.nan)

    eligible = alabama["DD_SRAM_LILATracts_1And10"].eq(1) & ~alabama["GroupQuartersFlag"].eq(1)
    alabama["priority_rank_by_affected_low_income_count"] = pd.NA
    alabama.loc[eligible, "priority_rank_by_affected_low_income_count"] = (
        alabama.loc[eligible, "DD_SRAM_LALOWI1_10"].rank(method="min", ascending=False).astype("Int64")
    )
    tract_columns = [
        "GEOID20", "County20", "County24", "Urban", "POP2020", "GroupQuartersFlag",
        "PCTGQTRS", "LowIncomeTracts", "PovertyRate", "MedianFamilyIncome", "TractLOWI",
        "TractKids", "TractSeniors", "TractHUNV", "TractSNAP", "DD_SRAM_LILATracts_1And10",
        "DD_SRAM_LAPOP1_10", "DD_SRAM_LALOWI1_10", "la_kids_mixed", "la_seniors_mixed",
        "la_hunv_mixed", "la_snap_mixed", "low_access_population_pct",
        "low_income_low_access_population_pct", "low_access_children_pct",
        "low_access_seniors_pct", "low_access_no_vehicle_housing_units_pct",
        "low_access_snap_housing_units_pct", "priority_rank_by_affected_low_income_count",
    ]
    tracts = alabama[tract_columns].sort_values(
        ["priority_rank_by_affected_low_income_count", "DD_SRAM_LALOWI1_10"],
        na_position="last",
    )
    tracts.to_csv(PROCESSED / "alabama_tract_food_access.csv", index=False)

    county_rows = []
    for county, frame in alabama.groupby("County24", sort=True):
        county_rows.append({"county": county, **aggregate_access(frame)})
    counties = pd.DataFrame(county_rows)
    counties["rank_by_affected_low_income_count"] = counties["low_income_low_access_population"].rank(method="min", ascending=False).astype(int)
    counties["rank_by_low_income_low_access_pct"] = counties["low_income_low_access_population_pct"].rank(method="min", ascending=False).astype(int)
    counties = counties.sort_values("rank_by_affected_low_income_count")
    counties.to_csv(PROCESSED / "alabama_county_food_access.csv", index=False)

    regional = {
        "United States": aggregate_access(sram),
        "Project-defined Southeast": aggregate_access(sram[sram["State"].isin(SOUTHEAST)]),
        "Alabama": aggregate_access(alabama),
    }
    return states, southeast, counties, regional


def build_sensitivity(sram: pd.DataFrame) -> pd.DataFrame:
    definitions = [
        ("Driving", "0.5 urban / 10 rural", "DD_SRAM_LAPOP05_10", "DD_SRAM_LALOWI05_10", "DD_SRAM_LILATracts_halfAnd10"),
        ("Driving", "1 urban / 10 rural", "DD_SRAM_LAPOP1_10", "DD_SRAM_LALOWI1_10", "DD_SRAM_LILATracts_1And10"),
        ("Driving", "1 urban / 20 rural", "DD_SRAM_LAPOP1_20", "DD_SRAM_LALOWI1_20", "DD_SRAM_LILATracts_1And20"),
        ("Straight line", "1 urban / 10 rural", "SD_SRAM_LAPOP1_10", "SD_SRAM_LALOWI1_10", "SD_SRAM_LILATracts_1And10"),
    ]
    geographies = {
        "United States": sram,
        "Project-defined Southeast": sram[sram["State"].isin(SOUTHEAST)],
        "Alabama": sram[sram["State"] == "Alabama"],
    }
    records = []
    for geography, frame in geographies.items():
        for method, threshold, pop_col, lowi_col, flag_col in definitions:
            records.append(
                {
                    "geography": geography,
                    "distance_method": method,
                    "threshold": threshold,
                    "low_access_population": int(frame[pop_col].sum()),
                    "low_access_population_pct": ratio_percent(frame[pop_col], frame["POP2020"]),
                    "low_income_low_access_population": int(frame[lowi_col].sum()),
                    "low_income_low_access_population_pct": ratio_percent(frame[lowi_col], frame["TractLOWI"]),
                    "lila_tract_count": int(frame[flag_col].sum()),
                    "lila_tract_pct": 100.0 * float(frame[flag_col].sum()) / len(frame),
                }
            )
    result = pd.DataFrame(records)
    result.to_csv(RESULTS / "sensitivity_analysis.csv", index=False)
    return result


def build_qa(sram: pd.DataFrame, diagnostics: dict, state_food: pd.DataFrame) -> pd.DataFrame:
    checks = []

    def add(check: str, status: str, observed, expected: str, note: str = "") -> None:
        checks.append({"check": check, "status": status, "observed": observed, "expected": expected, "note": note})

    add("SRAM normalized row count", "PASS" if len(sram) == 84119 else "REVIEW", len(sram), "84,119")
    add("SRAM geography coverage", "PASS" if sram["State"].nunique() == 51 else "FAIL", sram["State"].nunique(), "50 states plus D.C.")
    add("SRAM duplicate GEOID", "PASS" if sram["GEOID20"].duplicated().sum() == 0 else "FAIL", int(sram["GEOID20"].duplicated().sum()), "0")
    add(
        "GEOID normalization impact",
        "PASS",
        diagnostics["normalized_rows"] - diagnostics["raw_join_matches_before_geoid_padding"],
        "Document and repair leading-zero loss",
        "General characteristics dropped leading zeros for state FIPS codes below 10; zfill(11) restored matches.",
    )
    add("Latest state food-security rows", "PASS" if len(state_food) == 52 else "REVIEW", len(state_food), "U.S., 50 states, and D.C. (52 rows)")
    for numerator, denominator in [
        ("DD_SRAM_LAPOP1_10", "POP2020"),
        ("DD_SRAM_LALOWI1_10", "TractLOWI"),
        ("la_kids_mixed", "TractKids"),
        ("la_seniors_mixed", "TractSeniors"),
        ("la_hunv_mixed", "TractHUNV"),
        ("la_snap_mixed", "TractSNAP"),
    ]:
        violations = int((sram[numerator] > sram[denominator]).sum())
        add(f"{numerator} does not exceed {denominator}", "PASS" if violations == 0 else "FAIL", violations, "0")
    primary_missing = int(sram[["DD_SRAM_LAPOP1_10", "DD_SRAM_LALOWI1_10", "DD_SRAM_LILATracts_1And10"]].isna().any(axis=1).sum())
    add(
        "Primary measure completeness",
        "PASS" if primary_missing == 0 else "REVIEW",
        primary_missing,
        "0 or documented source-data exceptions",
        "Fourteen Suffolk County, New York tracts lack low-income denominators; one zero-population Massachusetts tract lacks the LILA flag. Alabama and the project-defined Southeast are complete.",
    )

    shp = shapefile.Reader(str(RAW / "census_geometry" / "extracted" / "cb_2020_01_tract_500k.shp"))
    shape_geoids = {record["GEOID"] for record in shp.records()}
    al_geoids = set(sram.loc[sram["State"] == "Alabama", "GEOID20"])
    add("Alabama geometry join coverage", "PASS" if al_geoids == shape_geoids else "FAIL", len(al_geoids & shape_geoids), f"{len(al_geoids)}")

    qa = pd.DataFrame(checks)
    qa.to_csv(RESULTS / "qa_results.csv", index=False)
    return qa


def build_dataset_assessment() -> pd.DataFrame:
    rows = [
        ["FAO_FS", "Global and national food-insecurity context", "Global/region/country", "Current through 2023-2025 for core FIES indicators", "KEEP - context only", "Not comparable to tract retailer access; no U.S. state detail."],
        ["FAO_COAHD", "Economic access to a healthy diet", "Global/region/country", "July 2026 release; indicators through 2025", "KEEP - context only", "National and regional estimates; no U.S. state or tract detail."],
        ["USDA_FOOD_SECURITY_CSV", "U.S. household food insecurity outcome", "National/state", "2024 annual; 2022-2024 state average", "KEEP - outcome benchmark", "State margins of error are material; no official tract outcome."],
        ["USDA_SRAM_2025", "Retailer proximity and low-income/low-access burden", "2020 census tract", "SNAP retailers June 2025; ACS 2020-2024", "KEEP - primary local dataset", "Measures proximity to SNAP-authorized retailers, not price, quality, inventory, transit, or household food insecurity."],
        ["CENSUS_TRACTS_AL_2020", "Alabama mapping geometry", "2020 census tract", "2020", "KEEP - mapping support", "Geometry only; must join on an 11-digit text GEOID."],
        ["USDA_LRAM_2019", "Large-supermarket retailer-universe sensitivity", "2010 census tract", "2019 retailer list", "OPTIONAL NEXT CRAWL", "Different retailer universe and tract base; use as a sensitivity comparison, not a time series."],
        ["USDA_FOOD_ENVIRONMENT_ATLAS", "County-level price, store, assistance, and environment context", "County/state", "Mixed vintages", "ADD ONLY FOR A DECLARED GAP", "Do not add broadly; retain only variables with a specific analytical purpose."],
        ["SUBSTATE_FOOD_INSECURITY_OUTCOME", "County/tract food-insecurity outcome", "County or smaller", "No directly comparable official tract series identified", "GAP - evaluate modeled source", "Needed only if the team wants to explain local food insecurity rather than local retailer access."],
    ]
    frame = pd.DataFrame(rows, columns=["source_id", "analytical_purpose", "grain", "vintage", "recommendation", "limitation"])
    frame.to_csv(RESULTS / "dataset_assessment.csv", index=False)
    return frame


def build_variable_dictionary() -> pd.DataFrame:
    rows = [
        ["GEOID20", "USDA/Census", "11-digit 2020 census tract identifier", "text", "Leading zeros restored with zfill(11)."],
        ["DD_SRAM_LAPOP1_10", "USDA SRAM", "Population beyond 1 driving mile in urban tracts or 10 driving miles in rural tracts", "people", "Primary overall retailer-access count."],
        ["DD_SRAM_LALOWI1_10", "USDA SRAM", "Low-income population beyond the primary driving-distance threshold", "people", "Primary affected low-income count."],
        ["DD_SRAM_LILATracts_1And10", "USDA SRAM", "Official low-income and low-access tract flag at the primary driving-distance threshold", "0/1", "Primary tract classification."],
        ["low_access_population_pct", "Derived", "Sum of low-access population divided by sum of 2020 population", "percent", "Never average tract percentages."],
        ["low_income_low_access_population_pct", "Derived", "Sum of low-income low-access population divided by sum of low-income population", "percent", "Never average tract percentages."],
        ["la_kids_mixed", "Derived from USDA SRAM", "Children beyond 1 mile in urban tracts or 10 miles in rural tracts", "people", "Primary-threshold subgroup count."],
        ["la_seniors_mixed", "Derived from USDA SRAM", "Adults age 65+ beyond 1 mile in urban tracts or 10 miles in rural tracts", "people", "Primary-threshold subgroup count."],
        ["la_hunv_mixed", "Derived from USDA SRAM", "No-vehicle occupied housing units beyond 1 mile in urban tracts or 10 miles in rural tracts", "housing units", "Housing-unit denominator; not a population rate."],
        ["la_snap_mixed", "Derived from USDA SRAM", "SNAP-recipient occupied housing units beyond 1 mile in urban tracts or 10 miles in rural tracts", "housing units", "Housing-unit denominator; not a population rate."],
        ["food_insecurity_pct", "USDA CPS-FSS", "Households food insecure at some time during the three-year period", "percent of households", "State estimate with margin of error."],
        ["moderate_or_severe_food_insecurity", "FAOSTAT FIES", "Population experiencing moderate or severe food insecurity", "percent of population", "Three-year average with confidence bounds."],
        ["healthy_diet_unaffordability", "FAOSTAT CoAHD", "Population unable to afford a healthy diet", "percent of population", "Economic-access indicator."],
    ]
    frame = pd.DataFrame(rows, columns=["field", "source", "definition", "unit", "processing_note"])
    frame.to_csv(METADATA / "variable_dictionary.csv", index=False)
    return frame


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        Path(r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf"),
        Path(r"C:\Windows\Fonts\calibrib.ttf" if bold else r"C:\Windows\Fonts\calibri.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


def text_width(draw: ImageDraw.ImageDraw, text: str, face) -> int:
    box = draw.textbbox((0, 0), text, font=face)
    return box[2] - box[0]


def save_bar_chart(
    rows: list[dict],
    output: Path,
    title: str,
    subtitle: str,
    source_note: str,
    max_value: float,
    reference_value: float | None = None,
    reference_label: str = "U.S.",
    error_key: str | None = None,
) -> None:
    width, height = 1600, 980
    image = Image.new("RGB", (width, height), COLORS["white"])
    draw = ImageDraw.Draw(image)
    draw.text((85, 55), title, font=font(38, True), fill=COLORS["navy"])
    draw.text((85, 108), subtitle, font=font(21), fill=COLORS["gray"])
    x0, x1 = 365, 1470
    y0, gap, bar_h = 205, 66, 34
    if max_value <= 25:
        axis_max, tick_step = 25.0, 5.0
    elif max_value <= 40:
        axis_max, tick_step = 40.0, 10.0
    else:
        tick_step = 10.0
        axis_max = math.ceil(max_value / tick_step) * tick_step
    for tick in np.arange(0, axis_max + 0.1, tick_step):
        x = x0 + (x1 - x0) * tick / axis_max
        draw.line((x, y0 - 25, x, y0 + gap * len(rows) - 15), fill=COLORS["grid"], width=1)
        label = f"{tick:.0f}%"
        draw.text((x - text_width(draw, label, font(16)) / 2, y0 + gap * len(rows) - 2), label, font=font(16), fill=COLORS["gray"])
    if reference_value is not None:
        x = x0 + (x1 - x0) * reference_value / axis_max
        draw.line((x, y0 - 28, x, y0 + gap * len(rows) - 20), fill=COLORS["gold"], width=4)
        draw.text((x + 8, y0 - 46), f"{reference_label}: {reference_value:.1f}%", font=font(16, True), fill="#7A5A00")
    for index, row in enumerate(rows):
        y = y0 + index * gap
        label = row["label"]
        value = float(row["value"])
        draw.text((330 - text_width(draw, label, font(21, row.get("highlight", False))), y), label, font=font(21, row.get("highlight", False)), fill=COLORS["navy"])
        color = COLORS["blue"] if row.get("highlight") else COLORS["mid_blue"]
        end = x0 + (x1 - x0) * value / axis_max
        draw.rounded_rectangle((x0, y, end, y + bar_h), radius=8, fill=color)
        if error_key and row.get(error_key) is not None:
            error = float(row[error_key])
            low = x0 + (x1 - x0) * max(0, value - error) / axis_max
            high = x0 + (x1 - x0) * min(axis_max, value + error) / axis_max
            cy = y + bar_h / 2
            draw.line((low, cy, high, cy), fill=COLORS["navy"], width=3)
            draw.line((low, cy - 7, low, cy + 7), fill=COLORS["navy"], width=3)
            draw.line((high, cy - 7, high, cy + 7), fill=COLORS["navy"], width=3)
        value_label = f"{value:.1f}%"
        draw.text((min(end + 12, x1 - 55), y + 3), value_label, font=font(18, True), fill=COLORS["navy"])
    draw.text((85, height - 60), source_note, font=font(16), fill=COLORS["gray"])
    image.save(output, quality=95)


def save_global_chart(global_data: pd.DataFrame) -> None:
    areas = ["Africa", "World", "Oceania", "Latin America and the Caribbean", "Asia", "United States of America", "Europe"]
    panels = [
        ("moderate_or_severe_food_insecurity", "Moderate or severe food insecurity", "2023-2025 average"),
        ("healthy_diet_unaffordability", "Unable to afford a healthy diet", "2025"),
    ]
    image = Image.new("RGB", (1900, 1050), COLORS["white"])
    draw = ImageDraw.Draw(image)
    draw.text((85, 48), "Global food-access indicators", font=font(40, True), fill=COLORS["navy"])
    draw.text((85, 103), "Separate population measures; percentages should not be interpreted as the same construct.", font=font(21), fill=COLORS["gray"])
    for panel_index, (key, heading, period) in enumerate(panels):
        left = 70 + panel_index * 925
        draw.rounded_rectangle((left, 165, left + 865, 925), radius=18, fill="#F7F9FC", outline=COLORS["grid"], width=2)
        draw.text((left + 35, 195), heading, font=font(27, True), fill=COLORS["navy"])
        draw.text((left + 35, 232), period, font=font(18), fill=COLORS["gray"])
        data = global_data[global_data["indicator_key"] == key].set_index("geography")
        max_value = 75.0
        x0, x1 = left + 305, left + 825
        y0, gap = 300, 80
        for index, area in enumerate(areas):
            if area not in data.index:
                continue
            value = float(data.loc[area, "value"])
            y = y0 + index * gap
            label = "United States" if area == "United States of America" else area.replace("Latin America and the Caribbean", "Latin America + Caribbean")
            face = font(18, area in ("World", "United States of America"))
            draw.text((x0 - 18 - text_width(draw, label, face), y + 4), label, font=face, fill=COLORS["navy"])
            end = x0 + (x1 - x0) * value / max_value
            color = COLORS["blue"] if area == "United States of America" else (COLORS["gold"] if area == "World" else COLORS["mid_blue"])
            draw.rounded_rectangle((x0, y, end, y + 30), radius=7, fill=color)
            draw.text((min(end + 8, x1 - 42), y + 3), f"{value:.1f}%", font=font(16, True), fill=COLORS["navy"])
        for tick in (0, 25, 50, 75):
            x = x0 + (x1 - x0) * tick / max_value
            draw.text((x - 12, 875), f"{tick}%", font=font(14), fill=COLORS["gray"])
    draw.text((85, 992), "Source: FAOSTAT Suite of Food Security Indicators and Cost and Affordability of a Healthy Diet, retrieved August 22, 2026.", font=font(16), fill=COLORS["gray"])
    image.save(FIGURES / "global_food_access.png", quality=95)


def save_subgroup_chart(regional: dict) -> None:
    metrics = [
        ("Children", "low_access_children_pct"),
        ("Adults 65+", "low_access_seniors_pct"),
        ("No-vehicle housing units", "low_access_no_vehicle_housing_units_pct"),
        ("SNAP housing units", "low_access_snap_housing_units_pct"),
    ]
    geographies = ["Alabama", "Project-defined Southeast", "United States"]
    colors = [COLORS["blue"], COLORS["mid_blue"], COLORS["gold"]]
    image = Image.new("RGB", (1700, 1020), COLORS["white"])
    draw = ImageDraw.Draw(image)
    draw.text((80, 50), "Primary-threshold subgroup access", font=font(38, True), fill=COLORS["navy"])
    draw.text((80, 103), "Driving distance: 1 mile urban / 10 miles rural. Population and housing-unit denominators are kept separate.", font=font(20), fill=COLORS["gray"])
    x0, x1 = 480, 1580
    y0, group_gap, bar_gap = 220, 190, 44
    max_value = 25.0
    for tick in range(0, 26, 5):
        x = x0 + (x1 - x0) * tick / max_value
        draw.line((x, 180, x, 930), fill=COLORS["grid"], width=1)
        draw.text((x - 12, 940), f"{tick}%", font=font(16), fill=COLORS["gray"])
    for metric_index, (label, key) in enumerate(metrics):
        y = y0 + metric_index * group_gap
        draw.text((80, y + 35), label, font=font(23, True), fill=COLORS["navy"])
        for geo_index, geography in enumerate(geographies):
            value = regional[geography][key]
            bar_y = y + geo_index * bar_gap
            end = x0 + (x1 - x0) * value / max_value
            draw.text((330, bar_y + 3), geography.replace("Project-defined ", "SE "), font=font(16), fill=COLORS["gray"])
            draw.rounded_rectangle((x0, bar_y, end, bar_y + 28), radius=6, fill=colors[geo_index])
            draw.text((end + 8, bar_y + 3), f"{value:.1f}%", font=font(16, True), fill=COLORS["navy"])
    draw.text((80, 985), "Source: USDA ERS 2025 SNAP-authorized Retailer Access Map. Derived mixed urban/rural threshold counts.", font=font(16), fill=COLORS["gray"])
    image.save(FIGURES / "alabama_subgroup_access.png", quality=95)


def save_alabama_map(tracts: pd.DataFrame) -> None:
    data = tracts.set_index("GEOID20")
    reader = shapefile.Reader(str(RAW / "census_geometry" / "extracted" / "cb_2020_01_tract_500k.shp"))
    min_x, min_y, max_x, max_y = reader.bbox
    width, height = 1450, 1780
    image = Image.new("RGB", (width, height), COLORS["white"])
    draw = ImageDraw.Draw(image)
    draw.text((70, 45), "Alabama low-income population beyond the primary access threshold", font=font(34, True), fill=COLORS["navy"])
    draw.text((70, 94), "Share of each tract's low-income population beyond 1 driving mile urban / 10 driving miles rural", font=font(20), fill=COLORS["gray"])
    map_box = (80, 165, 1120, 1640)
    map_w = map_box[2] - map_box[0]
    map_h = map_box[3] - map_box[1]
    scale = min(map_w / (max_x - min_x), map_h / (max_y - min_y))
    x_offset = map_box[0] + (map_w - (max_x - min_x) * scale) / 2
    y_offset = map_box[1] + (map_h - (max_y - min_y) * scale) / 2
    bins = [0, 10, 20, 30, 40, 1000]
    fills = ["#EEF2F6", "#DCEAF7", "#A9CBEA", "#6FA8D8", "#2E74B5"]

    def color(value: float) -> str:
        if pd.isna(value):
            return "#F4F4F4"
        for idx in range(len(bins) - 1):
            if bins[idx] <= value < bins[idx + 1]:
                return fills[idx]
        return fills[-1]

    for shape_record in reader.iterShapeRecords():
        record = shape_record.record.as_dict()
        geoid = record["GEOID"]
        share = float(data.loc[geoid, "low_income_low_access_population_pct"]) if geoid in data.index else math.nan
        lila = bool(data.loc[geoid, "DD_SRAM_LILATracts_1And10"] == 1) if geoid in data.index else False
        points = shape_record.shape.points
        parts = list(shape_record.shape.parts) + [len(points)]
        for start, end in zip(parts[:-1], parts[1:]):
            polygon = [
                (
                    x_offset + (x - min_x) * scale,
                    y_offset + (max_y - y) * scale,
                )
                for x, y in points[start:end]
            ]
            draw.polygon(polygon, fill=color(share), outline="#FFFFFF")
            if lila:
                draw.line(polygon + [polygon[0]], fill=COLORS["navy"], width=2)

    legend_x, legend_y = 1160, 320
    draw.text((legend_x, legend_y - 65), "Low-income people\nbeyond threshold", font=font(20, True), fill=COLORS["navy"], spacing=5)
    labels = ["0-<10%", "10-<20%", "20-<30%", "30-<40%", "40%+"]
    for idx, label in enumerate(labels):
        y = legend_y + idx * 58
        draw.rectangle((legend_x, y, legend_x + 42, y + 32), fill=fills[idx], outline=COLORS["grid"])
        draw.text((legend_x + 55, y + 4), label, font=font(18), fill=COLORS["navy"])
    draw.line((legend_x, legend_y + 350, legend_x + 42, legend_y + 350), fill=COLORS["navy"], width=4)
    draw.text((legend_x + 55, legend_y + 338), "Official LILA tract", font=font(18), fill=COLORS["navy"])
    draw.text((70, 1700), "Sources: USDA ERS 2025 SRAM; U.S. Census Bureau 2020 cartographic tract boundaries.", font=font(16), fill=COLORS["gray"])
    image.save(FIGURES / "alabama_tract_food_access_map.png", quality=95)


def build_figures(global_data: pd.DataFrame, southeast: pd.DataFrame, regional: dict, tracts: pd.DataFrame) -> None:
    save_global_chart(global_data)
    food_rows = [
        {
            "label": row.state_abbr,
            "value": row.food_insecurity_pct,
            "moe": row.food_insecurity_moe_pp,
            "highlight": row.state_abbr == "AL",
        }
        for row in southeast.sort_values("food_insecurity_pct", ascending=False).itertuples()
    ]
    us_food = float(pd.read_csv(PROCESSED / "us_food_insecurity_states_2022_2024.csv").query("state_abbr == 'U.S.'")["food_insecurity_pct"].iloc[0])
    save_bar_chart(
        food_rows,
        FIGURES / "southeast_food_insecurity.png",
        "Household food insecurity in the project-defined Southeast",
        "Average 2022-2024; error bars show USDA margins of error.",
        "Source: USDA ERS, Food Security in the United States data files.",
        max_value=24,
        reference_value=us_food,
        error_key="moe",
    )
    access_rows = [
        {
            "label": row.state_abbr,
            "value": row.low_income_low_access_population_pct,
            "highlight": row.state_abbr == "AL",
        }
        for row in southeast.sort_values("low_income_low_access_population_pct", ascending=False).itertuples()
    ]
    save_bar_chart(
        access_rows,
        FIGURES / "southeast_retail_access.png",
        "Low-income population beyond the primary retailer-access threshold",
        "Driving distance: 1 mile urban / 10 miles rural; population-weighted state results.",
        "Source: USDA ERS 2025 SNAP-authorized Retailer Access Map.",
        max_value=36,
        reference_value=regional["United States"]["low_income_low_access_population_pct"],
    )
    save_subgroup_chart(regional)
    save_alabama_map(tracts)


def build_findings(
    global_data: pd.DataFrame,
    national_food: dict,
    state_food: pd.DataFrame,
    southeast: pd.DataFrame,
    counties: pd.DataFrame,
    regional: dict,
    tracts: pd.DataFrame,
    sensitivity: pd.DataFrame,
    qa: pd.DataFrame,
) -> dict:
    global_index = global_data.set_index(["indicator_key", "geography"])

    def global_value(key: str, geography: str) -> float:
        return float(global_index.loc[(key, geography), "value"])

    al_food = state_food[state_food["state_abbr"] == "AL"].iloc[0]
    us_food = state_food[state_food["state_abbr"] == "U.S."].iloc[0]
    al_state = southeast[southeast["state_abbr"] == "AL"].iloc[0]
    top_food = southeast.sort_values("food_insecurity_pct", ascending=False).iloc[0]
    top_access = southeast.sort_values("low_income_low_access_population_pct", ascending=False).iloc[0]
    top_tracts = tracts.dropna(subset=["priority_rank_by_affected_low_income_count"]).sort_values("priority_rank_by_affected_low_income_count").head(10)
    primary_sensitivity = sensitivity[
        (sensitivity["geography"] == "Alabama")
        & (sensitivity["distance_method"] == "Driving")
        & (sensitivity["threshold"] == "1 urban / 10 rural")
    ].iloc[0]
    straight_sensitivity = sensitivity[
        (sensitivity["geography"] == "Alabama")
        & (sensitivity["distance_method"] == "Straight line")
        & (sensitivity["threshold"] == "1 urban / 10 rural")
    ].iloc[0]
    findings = {
        "as_of": "2026-08-22",
        "global": {
            "moderate_or_severe_food_insecurity_world_pct_2023_2025": global_value("moderate_or_severe_food_insecurity", "World"),
            "moderate_or_severe_food_insecurity_us_pct_2023_2025": global_value("moderate_or_severe_food_insecurity", "United States of America"),
            "severe_food_insecurity_world_pct_2023_2025": global_value("severe_food_insecurity", "World"),
            "healthy_diet_unaffordability_world_pct_2025": global_value("healthy_diet_unaffordability", "World"),
            "healthy_diet_unaffordability_world_millions_2025": global_value("people_unable_to_afford_healthy_diet", "World"),
            "highest_regional_moderate_or_severe_pct": {
                "region": "Africa",
                "value": global_value("moderate_or_severe_food_insecurity", "Africa"),
            },
        },
        "united_states": {
            **national_food,
            "state_average_2022_2024_food_insecurity_pct": float(us_food["food_insecurity_pct"]),
            "state_average_2022_2024_food_insecurity_moe_pp": float(us_food["food_insecurity_moe_pp"]),
            **regional["United States"],
        },
        "southeast": {
            "states": list(SOUTHEAST.values()),
            "highest_food_insecurity_state": {"state": top_food["state"], "pct": float(top_food["food_insecurity_pct"])},
            "highest_low_income_low_access_state": {"state": top_access["state"], "pct": float(top_access["low_income_low_access_population_pct"])},
            **regional["Project-defined Southeast"],
        },
        "alabama": {
            "food_insecurity_pct_2022_2024": float(al_food["food_insecurity_pct"]),
            "food_insecurity_moe_pp": float(al_food["food_insecurity_moe_pp"]),
            "food_insecurity_rank_high_to_low_among_10": int(al_state["food_insecurity_rank_high_to_low"]),
            **regional["Alabama"],
            "top_counties_by_affected_low_income_count": counties.head(10)[["county", "low_income_low_access_population", "low_income_low_access_population_pct"]].to_dict("records"),
            "top_lila_tracts_by_affected_low_income_count_excluding_high_group_quarters": top_tracts[["GEOID20", "County24", "DD_SRAM_LALOWI1_10", "low_income_low_access_population_pct", "PovertyRate"]].to_dict("records"),
            "driving_vs_straight_line_low_income_low_access_pct": {
                "driving": float(primary_sensitivity["low_income_low_access_population_pct"]),
                "straight_line": float(straight_sensitivity["low_income_low_access_population_pct"]),
            },
        },
        "sufficiency": {
            "primary_dataset": "USDA ERS 2025 SRAM driving-distance data",
            "primary_measure_retained": bool((qa["status"] == "FAIL").sum() == 0),
            "qa_pass_count": int((qa["status"] == "PASS").sum()),
            "qa_review_count": int((qa["status"] == "REVIEW").sum()),
            "qa_fail_count": int((qa["status"] == "FAIL").sum()),
            "known_limit": "Retailer proximity does not measure affordability, food quality, inventory, transit, or household food insecurity.",
        },
    }
    with (RESULTS / "key_findings.json").open("w", encoding="utf-8") as stream:
        json.dump(findings, stream, indent=2, ensure_ascii=False)
    return findings


def main() -> None:
    ensure_dirs()
    global_data = read_global_data()
    state_food, national_food = read_us_food_security()
    sram, diagnostics = load_sram()
    states, southeast, counties, regional = build_state_and_alabama_outputs(sram, state_food)
    tracts = pd.read_csv(PROCESSED / "alabama_tract_food_access.csv", dtype={"GEOID20": "string"})
    sensitivity = build_sensitivity(sram)
    qa = build_qa(sram, diagnostics, state_food)
    build_dataset_assessment()
    build_variable_dictionary()
    build_figures(global_data, southeast, regional, tracts)
    findings = build_findings(global_data, national_food, state_food, southeast, counties, regional, tracts, sensitivity, qa)
    print(json.dumps({
        "processed_files": len(list(PROCESSED.glob("*.csv"))),
        "figures": len(list(FIGURES.glob("*.png"))),
        "qa": qa["status"].value_counts().to_dict(),
        "alabama": findings["alabama"],
    }, indent=2, default=str))


if __name__ == "__main__":
    main()

