"""Stage and inventory the Feeding America Map the Meal Gap archive.

This script does not promote Feeding America fields into publication outputs.
It extracts the official archive received through the Feeding America Research
Team, hashes the source ZIP, and writes a file-level inventory so the team can
review schema, geography, vintages, and revision notes before analysis.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import zipfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ZIP = ROOT / "data" / "raw" / "2026-08-25" / "feeding_america" / "MMG2026_Data_To_Share.zip"
DEFAULT_EXTRACT = ROOT / "data" / "raw" / "2026-08-25" / "feeding_america" / "extracted"
DEFAULT_INVENTORY = ROOT / "data" / "metadata" / "feeding_america_inventory.csv"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def safe_extract(archive: Path, destination: Path, force: bool) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    if any(destination.iterdir()) and not force:
        return
    with zipfile.ZipFile(archive) as bundle:
        for member in bundle.infolist():
            target = (destination / member.filename).resolve()
            root = destination.resolve()
            if root not in target.parents and target != root:
                raise ValueError(f"Unsafe archive member: {member.filename}")
        bundle.extractall(destination)


def preview_header(path: Path) -> str:
    if path.suffix.lower() not in {".csv", ".tsv", ".txt"}:
        return ""
    try:
        with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as stream:
            first = stream.readline().strip()
        return first[:2000]
    except OSError:
        return ""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--zip", dest="zip_path", type=Path, default=DEFAULT_ZIP)
    parser.add_argument("--extract-to", type=Path, default=DEFAULT_EXTRACT)
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    archive = args.zip_path.resolve()
    if not archive.exists():
        raise FileNotFoundError(
            f"Feeding America archive not found: {archive}\n"
            "Save the ZIP received from Feeding America there or pass --zip PATH."
        )

    extract_to = args.extract_to.resolve()
    safe_extract(archive, extract_to, args.force)

    archive_hash = sha256(archive)
    inventoried_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    rows = []
    for path in sorted(p for p in extract_to.rglob("*") if p.is_file()):
        relative = path.relative_to(extract_to).as_posix()
        lower = relative.lower()
        rows.append(
            {
                "archive": archive.name,
                "archive_sha256": archive_hash,
                "inventoried_at_utc": inventoried_at,
                "relative_path": relative,
                "extension": path.suffix.lower(),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
                "possible_2023_revision_detail": "yes" if "revision" in lower and "2025" in lower else "",
                "possible_2024_data": "yes" if "2024" in lower or "mmg2026" in lower else "",
                "possible_2019_2023_data": "yes" if "2019" in lower and "2023" in lower else "",
                "header_preview": preview_header(path),
            }
        )

    args.inventory.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "archive",
        "archive_sha256",
        "inventoried_at_utc",
        "relative_path",
        "extension",
        "bytes",
        "sha256",
        "possible_2023_revision_detail",
        "possible_2024_data",
        "possible_2019_2023_data",
        "header_preview",
    ]
    with args.inventory.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Archive SHA-256: {archive_hash}")
    print(f"Inventoried {len(rows)} extracted files -> {args.inventory.relative_to(ROOT)}")
    print("Review the inventory and technical documentation before promoting fields into processed outputs.")


if __name__ == "__main__":
    main()
