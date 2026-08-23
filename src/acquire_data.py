"""Acquire and freeze the official source files used by the food-access analysis.

The script is intentionally conservative: existing files are preserved unless
``--force`` is supplied. Every downloaded file is hashed into a source manifest.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import shutil
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = "2026-08-22"
RAW = ROOT / "data" / "raw" / SNAPSHOT
MANIFEST = ROOT / "data" / "metadata" / "source_manifest.csv"

SOURCES = [
    {
        "source_id": "FAO_FS",
        "publisher": "Food and Agriculture Organization of the United Nations",
        "dataset": "FAOSTAT Suite of Food Security Indicators",
        "url": "https://bulks-faostat.fao.org/production/Food_Security_Data_E_All_Data_(Normalized).zip",
        "relative_path": "faostat_fs/Food_Security_Data_E_All_Data_Normalized.zip",
        "extract_to": "faostat_fs/extracted",
        "geography": "Global, regional, and national",
        "vintage": "Current bulk release retrieved 2026-08-22",
    },
    {
        "source_id": "FAO_COAHD",
        "publisher": "Food and Agriculture Organization of the United Nations",
        "dataset": "FAOSTAT Cost and Affordability of a Healthy Diet",
        "url": "https://bulks-faostat.fao.org/production/Cost_Affordability_Healthy_Diet_(CoAHD)_E_All_Data_(Normalized).zip",
        "relative_path": "faostat_coahd/Cost_Affordability_Healthy_Diet_CoAHD_E_All_Data_Normalized.zip",
        "extract_to": "faostat_coahd/extracted",
        "geography": "Global, regional, and national",
        "vintage": "July 2026 SOFI release",
    },
    {
        "source_id": "USDA_SRAM_2025",
        "publisher": "U.S. Department of Agriculture, Economic Research Service",
        "dataset": "2025 SNAP-authorized Retailer Access Map",
        "url": "https://www.ers.usda.gov/media/29395/2025-snap-authorized-retailer-access-map-sram-data.zip?v=25213",
        "relative_path": "usda_sram/2025_SRAM_data.zip",
        "extract_to": "usda_sram/extracted",
        "geography": "2020 U.S. census tracts",
        "vintage": "Retailers as of June 2025; released 2026-07-27",
    },
    {
        "source_id": "USDA_FOOD_SECURITY_CSV",
        "publisher": "U.S. Department of Agriculture, Economic Research Service",
        "dataset": "Food Security in the United States data files",
        "url": "https://www.ers.usda.gov/media/799/food-security-csv-data-files.zip",
        "relative_path": "usda_food_security/food_security_csv_data_files.zip",
        "extract_to": "usda_food_security/extracted",
        "geography": "United States and states",
        "vintage": "2024 annual; 2022-2024 state average",
    },
    {
        "source_id": "USDA_ERR_358",
        "publisher": "U.S. Department of Agriculture, Economic Research Service",
        "dataset": "Household Food Security in the United States in 2024 (ERR-358)",
        "url": "https://ers.usda.gov/sites/default/files/_laserfiche/publications/113623/ERR-358.pdf",
        "relative_path": "usda_food_security/ERR-358.pdf",
        "extract_to": "",
        "geography": "United States and states",
        "vintage": "Published 2025; state estimates average 2022-2024",
    },
    {
        "source_id": "CENSUS_TRACTS_AL_2020",
        "publisher": "U.S. Census Bureau",
        "dataset": "2020 Alabama cartographic census tract boundaries, 1:500,000",
        "url": "https://www2.census.gov/geo/tiger/GENZ2020/shp/cb_2020_01_tract_500k.zip",
        "relative_path": "census_geometry/cb_2020_01_tract_500k.zip",
        "extract_to": "census_geometry/extracted",
        "geography": "Alabama 2020 census tracts",
        "vintage": "2020",
    },
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def download(url: str, destination: Path, force: bool) -> str:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and not force:
        return "preserved_existing"
    request = urllib.request.Request(url, headers={"User-Agent": "Data-for-Dinner/2026"})
    temporary = destination.with_suffix(destination.suffix + ".partial")
    with urllib.request.urlopen(request, timeout=180) as response, temporary.open("wb") as output:
        shutil.copyfileobj(response, output)
    temporary.replace(destination)
    return "downloaded"


def extract(archive: Path, destination: Path, force: bool) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    if any(destination.iterdir()) and not force:
        return
    with zipfile.ZipFile(archive) as bundle:
        for member in bundle.infolist():
            target = (destination / member.filename).resolve()
            if destination.resolve() not in target.parents and target != destination.resolve():
                raise ValueError(f"Unsafe archive member: {member.filename}")
        bundle.extractall(destination)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="replace existing raw snapshots")
    args = parser.parse_args()
    retrieved = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    rows = []
    for source in SOURCES:
        local_path = RAW / source["relative_path"]
        status = download(source["url"], local_path, args.force)
        if source["extract_to"]:
            extract(local_path, RAW / source["extract_to"], args.force)
        rows.append(
            {
                **source,
                "retrieved_at_utc": retrieved,
                "local_path": local_path.relative_to(ROOT).as_posix(),
                "bytes": local_path.stat().st_size,
                "sha256": sha256(local_path),
                "status": status,
            }
        )

    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    fields = [
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
    ]
    with MANIFEST.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {MANIFEST.relative_to(ROOT)} with {len(rows)} sources")


if __name__ == "__main__":
    main()

