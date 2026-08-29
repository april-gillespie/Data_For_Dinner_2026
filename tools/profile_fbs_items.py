from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd


BASE = Path(r"C:\Users\athen\OneDrive\Documents\Data for Dinner\FAOSTAT_A-S_E")
FBS = BASE / "FoodBalanceSheets_E_All_Data_(Normalized).csv"
OUT = Path(__file__).resolve().parents[1] / "fbs_item_profile.json"


def main() -> None:
    items: set[tuple[int, str]] = set()
    years: set[int] = set()
    areas: set[tuple[int, str]] = set()
    rows = 0
    for chunk in pd.read_csv(
        FBS,
        usecols=["Area Code", "Area", "Item Code", "Item", "Element Code", "Year"],
        chunksize=300_000,
        low_memory=False,
    ):
        rows += len(chunk)
        country = chunk[chunk["Area Code"] < 5000]
        areas.update((int(code), str(name)) for code, name in country[["Area Code", "Area"]].drop_duplicates().itertuples(index=False, name=None))
        years.update(int(year) for year in country["Year"].dropna().unique())
        kcal = country[country["Element Code"] == 664]
        items.update((int(code), str(name)) for code, name in kcal[["Item Code", "Item"]].drop_duplicates().itertuples(index=False, name=None))

    pattern = re.compile(
        r"wheat|barley|rye|triticale|oats|rice|maize|millet|sorghum|buckwheat|quinoa|cassava|potato|yam|root|pulses|cereal|grand total",
        re.I,
    )
    candidates = [{"item_code": code, "item": name} for code, name in sorted(items) if pattern.search(name)]
    payload = {
        "rows_scanned": rows,
        "country_area_count": len(areas),
        "years": sorted(years),
        "kcal_item_count": len(items),
        "candidate_items": candidates,
    }
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
