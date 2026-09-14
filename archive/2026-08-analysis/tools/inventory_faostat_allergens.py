from __future__ import annotations

import csv
import io
import json
import re
import zipfile
from collections import defaultdict
from pathlib import Path

import pandas as pd


ROOTS = [
    Path(r"C:\Users\athen\OneDrive\Documents\Data for Dinner\FAOSTAT_A-S_E"),
    Path(r"C:\Users\athen\OneDrive\Documents\Data for Dinner\FAOSTAT_T-Z_E"),
]
WORKSPACE = Path(__file__).resolve().parents[1]
FBS_MAIN = ROOTS[0] / "FoodBalanceSheets_E_All_Data_(Normalized).csv"
OUT = WORKSPACE / "faostat_allergen_inventory.json"

MAIN_DIMENSION_SPECS = {
    "Food_Aid_Shipments_WFP_E_All_Data_(Normalized).zip": ("Item Code", "Item"),
    "Food_and_Diet_Individual_Quantitative_Dietary_Data_E_All_Data_(Normalized).zip": (
        "Food Group Code",
        "Food Group",
    ),
    "Household_Consumption_and_Expenditure_Surveys_Food_and_Diet_E_All_Data_(Normalized).zip": (
        "Food Group Code",
        "Food Group",
    ),
    "Individual_Quantitative_Dietary_Data_Food_and_Diet_E_All_Data_(Normalized).zip": (
        "Food Group Code",
        "Food Group",
    ),
    "Minimum_Dietary_Diversity_for_Women_(MDD-W)_Food_and_Diet_E_All_Data_(Normalized).zip": (
        "Food Group Code",
        "Food Group",
    ),
    "Supply_Utilization_Accounts_Food_and_Diet_E_All_Data_(Normalized).zip": (
        "Food Group Code",
        "Food Group",
    ),
}


# FDA major-nine categories plus the additional EU declaration categories.
# Sulphites are searched as an additive/chemical name, not inferred from foods
# that sometimes contain them.
PATTERNS = {
    "Cereals containing gluten": re.compile(
        r"\b(wheat|barley|rye|oats?|triticale|spelt|meslin|kamut)\b", re.I
    ),
    "Milk": re.compile(
        r"\b(milk|cheese|butter|ghee|cream|whey|yogh?urt|casein|curd|lactose)\b", re.I
    ),
    "Eggs": re.compile(r"\b(eggs?|albumin)\b", re.I),
    "Fish": re.compile(
        r"\b(fish|fishes|tuna|salmon|sardines?|herring|cod|mackerel|anchov(?:y|ies)|trout|eel|tilapia|carp|catfish|flounder)\b",
        re.I,
    ),
    "Crustaceans": re.compile(
        r"\b(crustaceans?|shrimps?|prawns?|lobsters?|crabs?|crayfish)\b", re.I
    ),
    "Tree nuts": re.compile(
        r"\b(almonds?|hazelnuts?|filberts?|walnuts?|cashew nuts?|pecans?|brazil nuts?|pistachios?|macadamias?|chestnuts?|pine nuts?|treenuts?|nuts and products)\b",
        re.I,
    ),
    "Peanuts": re.compile(r"\b(peanuts?|groundnuts?)\b", re.I),
    "Soybeans": re.compile(r"\b(soybeans?|soyabeans?|soya beans?|soy|soya)\b", re.I),
    "Sesame": re.compile(r"\b(sesame|sesameseed)\b", re.I),
    "Celery": re.compile(r"\bcelery\b", re.I),
    "Mustard": re.compile(r"\b(mustard|mustardseed)\b", re.I),
    "Lupin": re.compile(r"\blupins?\b", re.I),
    "Molluscs": re.compile(
        r"\b(molluscs?|mussels?|oysters?|clams?|scallops?|squids?|octopus|cuttlefish|snails?|cephalopods?)\b",
        re.I,
    ),
    "Sulphur dioxide and sulphites": re.compile(
        r"\b(sulphur dioxide|sulfur dioxide|sulphites?|sulfites?)\b", re.I
    ),
}


def dataset_name(zip_path: Path) -> str:
    return zip_path.name.removesuffix("_All_Data_(Normalized).zip")


def add_record(store: dict, dataset: str, code: str, item: str, source_file: str) -> None:
    clean_item = item.strip()
    if not clean_item:
        return
    for category, pattern in PATTERNS.items():
        if pattern.search(clean_item):
            key = (category, clean_item)
            store[key]["codes"].add(str(code).strip())
            store[key]["datasets"].add(dataset)
            store[key]["source_files"].add(source_file)


def scan_item_code_files(store: dict) -> tuple[int, int]:
    zip_count = 0
    item_file_count = 0
    for root in ROOTS:
        for zip_path in sorted(root.glob("*.zip")):
            zip_count += 1
            with zipfile.ZipFile(zip_path) as archive:
                item_files = [name for name in archive.namelist() if name.endswith("ItemCodes.csv")]
                for member in item_files:
                    item_file_count += 1
                    raw = archive.read(member).decode("utf-8-sig", errors="replace")
                    reader = csv.DictReader(io.StringIO(raw))
                    if not reader.fieldnames or "Item" not in reader.fieldnames:
                        continue
                    code_field = "Item Code" if "Item Code" in reader.fieldnames else reader.fieldnames[0]
                    for row in reader:
                        add_record(
                            store,
                            dataset_name(zip_path),
                            row.get(code_field, ""),
                            row.get("Item", ""),
                            str(zip_path),
                        )
    return zip_count, item_file_count


def scan_fbs_main(store: dict) -> int:
    # The current FBS ItemCodes companion file contains only a header, so derive
    # its distinct item/code pairs from the observation file.
    pairs = set()
    for chunk in pd.read_csv(
        FBS_MAIN,
        usecols=["Item Code", "Item"],
        chunksize=400_000,
        low_memory=False,
    ):
        pairs.update(chunk.drop_duplicates().itertuples(index=False, name=None))
    for code, item in pairs:
        add_record(store, "FoodBalanceSheets_E", str(code), str(item), str(FBS_MAIN))
    return len(pairs)


def scan_main_dimensions(store: dict) -> dict[str, int]:
    pair_counts = {}
    root = ROOTS[0]
    for archive_name, (code_col, value_col) in MAIN_DIMENSION_SPECS.items():
        zip_path = root / archive_name
        if not zip_path.exists():
            continue
        pairs = set()
        with zipfile.ZipFile(zip_path) as archive:
            main_member = next(
                name for name in archive.namelist() if name.endswith("All_Data_(Normalized).csv")
            )
            with archive.open(main_member) as source:
                for chunk in pd.read_csv(
                    source,
                    usecols=[code_col, value_col],
                    chunksize=300_000,
                    low_memory=False,
                    encoding="utf-8",
                    encoding_errors="replace",
                ):
                    pairs.update(chunk.drop_duplicates().itertuples(index=False, name=None))
        dataset = dataset_name(zip_path)
        for code, item in pairs:
            add_record(store, dataset, str(code), str(item), str(zip_path))
        pair_counts[dataset] = len(pairs)
    return pair_counts


def main() -> None:
    store = defaultdict(lambda: {"codes": set(), "datasets": set(), "source_files": set()})
    zip_count, item_file_count = scan_item_code_files(store)
    fbs_pair_count = scan_fbs_main(store)
    main_dimension_pair_counts = scan_main_dimensions(store)

    rows = []
    for (category, item), values in sorted(store.items()):
        rows.append(
            {
                "allergen_group": category,
                "item": item,
                "item_codes": sorted(values["codes"]),
                "datasets": sorted(values["datasets"]),
                "source_files": sorted(values["source_files"]),
            }
        )
    counts = defaultdict(int)
    for row in rows:
        counts[row["allergen_group"]] += 1

    result = {
        "scope": {
            "zip_archives_scanned": zip_count,
            "item_code_files_scanned": item_file_count,
            "fbs_distinct_item_code_pairs_scanned": fbs_pair_count,
            "main_dimension_pair_counts": main_dimension_pair_counts,
        },
        "candidate_counts": dict(sorted(counts.items())),
        "candidates": rows,
    }
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(result["scope"], indent=2))
    print(json.dumps(result["candidate_counts"], indent=2))


if __name__ == "__main__":
    main()
