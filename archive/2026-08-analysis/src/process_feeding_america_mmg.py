"""Validate and extract the Feeding America Map the Meal Gap 2026 archive.

The original request-only archive is copied into the ignored raw-data area. The
repository receives only selected Alabama outputs, provenance, and validation
results. Race and ethnicity fields are intentionally excluded from this active
analysis because they remain outside the agreed project scope.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = "2026-08-29"
RAW_DIR = ROOT / "data" / "raw" / SNAPSHOT / "feeding_america_mmg"
CANONICAL_ARCHIVE = RAW_DIR / "MMG2026_Data_To_Share.zip"
PROCESSED = ROOT / "data" / "processed"
RESULTS = ROOT / "results"
MANIFEST = ROOT / "data" / "metadata" / "source_manifest.csv"

SOURCE_ID = "FEEDING_AMERICA_MMG_2026"
REQUEST_URL = "https://www.feedingamerica.org/research/map-the-meal-gap/by-county"
EXPECTED_ARCHIVE_SHA256 = "88b6d839860121c295ece955a2aa88bfa856c4ee452ae05403c168c3975d492a"
LATEST_WORKBOOK = "MMG2026_2024_Data_To_Share.xlsx"
CORRECTED_HISTORY_WORKBOOK = "MMG2025_2019-2023_Data_To_Share_v2.xlsx"
REVISION_NOTE = "MMG_2025_County_Revisions_Detail.pdf"

MANIFEST_FIELDS = [
    "source_id",
    "publisher",
    "dataset",
    "url",
    "geography",
    "vintage",
    "retrieved_at_utc",
    "local_path",
    "bytes",
    "sha256",
    "status",
    "relative_path",
    "extract_to",
    "access_notes",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_members(bundle: zipfile.ZipFile) -> list[str]:
    names = []
    root = Path("archive-root").resolve()
    for member in bundle.infolist():
        target = (root / member.filename).resolve()
        if root not in target.parents and target != root:
            raise ValueError(f"Unsafe archive member: {member.filename}")
        if member.flag_bits & 0x1:
            raise ValueError(f"Encrypted archive member: {member.filename}")
        names.append(member.filename)
    required = {LATEST_WORKBOOK, CORRECTED_HISTORY_WORKBOOK, REVISION_NOTE}
    missing = required - set(names)
    if missing:
        raise ValueError(f"Archive is missing required files: {sorted(missing)}")
    return names


def read_sheet(bundle: zipfile.ZipFile, workbook_name: str, sheet_name: str) -> pd.DataFrame:
    with bundle.open(workbook_name) as stream:
        workbook_bytes = io.BytesIO(stream.read())
    return pd.read_excel(workbook_bytes, sheet_name=sheet_name, engine="openpyxl")


def normalize_counties(frame: pd.DataFrame) -> pd.DataFrame:
    renamed = frame.rename(
        columns={
            "FIPS": "county_fips",
            "State": "state_abbr",
            "County, State": "county",
            "Year": "observation_year",
            "Overall Food Insecurity Rate": "overall_food_insecurity_rate",
            "# of Food Insecure Persons Overall": "food_insecure_persons",
            "% FI ≤ SNAP Threshold": "food_insecure_at_or_below_snap_threshold_rate",
            "% FI > SNAP Threshold": "food_insecure_above_snap_threshold_rate",
            "Child Food Insecurity Rate": "child_food_insecurity_rate",
            "# of Food Insecure Children": "food_insecure_children",
            "Imputed Market Basket Data": "market_basket_data_imputed",
            "Cost Per Meal": "cost_per_meal_usd",
            "Weighted weekly $ needed by FI": "weekly_food_budget_shortfall_per_food_insecure_person_usd",
            "Weighted Annual Food Budget Shortfall": "annual_food_budget_shortfall_usd",
            "Rural-Urban Continuum Code (2023)": "rural_urban_continuum_code_2023",
        }
    )
    columns = [
        "county_fips",
        "state_abbr",
        "county",
        "observation_year",
        "overall_food_insecurity_rate",
        "food_insecure_persons",
        "food_insecure_at_or_below_snap_threshold_rate",
        "food_insecure_above_snap_threshold_rate",
        "child_food_insecurity_rate",
        "food_insecure_children",
        "market_basket_data_imputed",
        "cost_per_meal_usd",
        "weekly_food_budget_shortfall_per_food_insecure_person_usd",
        "annual_food_budget_shortfall_usd",
        "rural_urban_continuum_code_2023",
    ]
    missing = [column for column in columns if column not in renamed.columns]
    if missing:
        raise ValueError(f"County sheet is missing expected columns: {missing}")
    result = renamed.loc[renamed["state_abbr"].eq("AL"), columns].copy()
    result["county_fips"] = result["county_fips"].astype("Int64").astype("string").str.zfill(5)
    result["market_basket_data_imputed"] = (
        result["market_basket_data_imputed"].fillna("").astype(str).str.strip().str.lower().eq("imputed")
    )
    result["source_id"] = SOURCE_ID
    return result.sort_values("county_fips").reset_index(drop=True)


def normalize_state(frame: pd.DataFrame) -> pd.DataFrame:
    renamed = frame.rename(
        columns={
            "FIPS": "state_fips",
            "State Name": "state_name",
            "State": "state_abbr",
            "Year": "observation_year",
            "Overall Food Insecurity Rate": "overall_food_insecurity_rate",
            "# of Food Insecure Persons Overall": "food_insecure_persons",
            "% FI ≤ SNAP Threshold": "food_insecure_at_or_below_snap_threshold_rate",
            "% FI > SNAP Threshold": "food_insecure_above_snap_threshold_rate",
            "Child Food Insecurity Rate": "child_food_insecurity_rate",
            "# of Food Insecure Children": "food_insecure_children",
            "Senior Food Insecurity Rate": "senior_food_insecurity_rate",
            "# of Food Insecure Seniors": "food_insecure_seniors",
            "Older Adult Food Insecurity Rate": "older_adult_food_insecurity_rate",
            "# of Food Insecure Older Adults": "food_insecure_older_adults",
            "Cost Per Meal": "cost_per_meal_usd",
            "Weighted weekly $ needed by FI": "weekly_food_budget_shortfall_per_food_insecure_person_usd",
            "Weighted Annual Food Budget Shortfall": "annual_food_budget_shortfall_usd",
        }
    )
    columns = [
        "state_fips",
        "state_name",
        "state_abbr",
        "observation_year",
        "overall_food_insecurity_rate",
        "food_insecure_persons",
        "food_insecure_at_or_below_snap_threshold_rate",
        "food_insecure_above_snap_threshold_rate",
        "child_food_insecurity_rate",
        "food_insecure_children",
        "senior_food_insecurity_rate",
        "food_insecure_seniors",
        "older_adult_food_insecurity_rate",
        "food_insecure_older_adults",
        "cost_per_meal_usd",
        "weekly_food_budget_shortfall_per_food_insecure_person_usd",
        "annual_food_budget_shortfall_usd",
    ]
    missing = [column for column in columns if column not in renamed.columns]
    if missing:
        raise ValueError(f"State sheet is missing expected columns: {missing}")
    result = renamed.loc[renamed["state_abbr"].eq("AL"), columns].copy()
    result["state_fips"] = result["state_fips"].astype("Int64").astype("string").str.zfill(2)
    result["source_id"] = SOURCE_ID
    return result.reset_index(drop=True)


def validate_outputs(counties: pd.DataFrame, state: pd.DataFrame) -> dict:
    rate_columns = [
        "overall_food_insecurity_rate",
        "food_insecure_at_or_below_snap_threshold_rate",
        "food_insecure_above_snap_threshold_rate",
        "child_food_insecurity_rate",
    ]
    state_rate_columns = rate_columns + ["senior_food_insecurity_rate", "older_adult_food_insecurity_rate"]
    checks = {
        "county_rows": len(counties),
        "county_fips_unique": not counties["county_fips"].duplicated().any(),
        "county_fips_valid": bool(counties["county_fips"].str.fullmatch(r"01\d{3}").all()),
        "county_years": sorted(int(value) for value in counties["observation_year"].dropna().unique()),
        "county_rates_in_unit_interval": bool(counties[rate_columns].apply(lambda s: s.between(0, 1) | s.isna()).all().all()),
        "state_rows": len(state),
        "state_rates_in_unit_interval": bool(state[state_rate_columns].apply(lambda s: s.between(0, 1) | s.isna()).all().all()),
        "county_food_insecure_persons_sum": int(counties["food_insecure_persons"].sum()),
        "state_food_insecure_persons": int(state.iloc[0]["food_insecure_persons"]),
        "county_child_food_insecure_sum": int(counties["food_insecure_children"].sum()),
        "state_child_food_insecure": int(state.iloc[0]["food_insecure_children"]),
        "imputed_market_basket_counties": int(counties["market_basket_data_imputed"].sum()),
    }
    blocking = [
        checks["county_rows"] == 67,
        checks["county_fips_unique"],
        checks["county_fips_valid"],
        checks["county_years"] == [2024],
        checks["county_rates_in_unit_interval"],
        checks["state_rows"] == 1,
        checks["state_rates_in_unit_interval"],
    ]
    if not all(blocking):
        raise ValueError(f"Map the Meal Gap validation failed: {checks}")
    return checks


def update_manifest(archive: Path, archive_hash: str) -> None:
    rows: list[dict[str, str]] = []
    if MANIFEST.exists():
        with MANIFEST.open(newline="", encoding="utf-8-sig") as stream:
            rows = [dict(row) for row in csv.DictReader(stream) if row.get("source_id") != SOURCE_ID]
    retrieved = datetime.fromtimestamp(archive.stat().st_mtime, timezone.utc).replace(microsecond=0).isoformat()
    rows.append(
        {
            "source_id": SOURCE_ID,
            "publisher": "Feeding America National Organization",
            "dataset": "Map the Meal Gap 2026: local food insecurity and food costs in 2024",
            "url": REQUEST_URL,
            "geography": "U.S. county, congressional district, and state; Alabama county and state extracts retained",
            "vintage": "2024 observation year; file updated 2026-07-28; corrected 2023 county estimates included",
            "retrieved_at_utc": retrieved,
            "local_path": archive.relative_to(ROOT).as_posix(),
            "bytes": str(archive.stat().st_size),
            "sha256": archive_hash,
            "status": "user_provided_validated",
            "relative_path": "feeding_america_mmg/MMG2026_Data_To_Share.zip",
            "extract_to": "",
            "access_notes": "Official request workflow; no explicit redistribution license in archive. Raw package excluded from GitHub; selected Alabama extracts, metadata, and citations published.",
        }
    )
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    with MANIFEST.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=MANIFEST_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, required=True, help="Feeding America MMG2026_Data_To_Share.zip")
    args = parser.parse_args()
    source = args.archive.expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(source)

    archive_hash = sha256(source)
    if archive_hash != EXPECTED_ARCHIVE_SHA256:
        raise ValueError(f"Unexpected archive SHA-256: {archive_hash}")

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    if source != CANONICAL_ARCHIVE.resolve():
        shutil.copy2(source, CANONICAL_ARCHIVE)
    archive = CANONICAL_ARCHIVE

    with zipfile.ZipFile(archive) as bundle:
        members = validate_members(bundle)
        counties = normalize_counties(read_sheet(bundle, LATEST_WORKBOOK, "County"))
        state = normalize_state(read_sheet(bundle, LATEST_WORKBOOK, "State"))

    checks = validate_outputs(counties, state)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    RESULTS.mkdir(parents=True, exist_ok=True)
    counties.to_csv(PROCESSED / "alabama_county_food_insecurity_2024.csv", index=False)
    state.to_csv(PROCESSED / "alabama_state_food_insecurity_2024.csv", index=False)
    with (RESULTS / "feeding_america_mmg_validation.json").open("w", encoding="utf-8") as stream:
        json.dump(
            {
                "source_id": SOURCE_ID,
                "archive_sha256": archive_hash,
                "archive_members": members,
                "checks": checks,
                "note": "County sums are not expected to equal state estimates because Feeding America state estimates aggregate congressional district results.",
            },
            stream,
            indent=2,
        )
    update_manifest(archive, archive_hash)
    print(json.dumps(checks, indent=2))


if __name__ == "__main__":
    main()
