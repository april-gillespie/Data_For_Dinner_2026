from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


BASE = Path(r"C:\Users\athen\OneDrive\Documents\Data for Dinner\FAOSTAT_A-S_E")
ROOT = Path(__file__).resolve().parents[1]
FBS_PATH = BASE / "FoodBalanceSheets_E_All_Data_(Normalized).csv"
QCL_PATH = BASE / "Production_Crops_Livestock_E_All_Data_(Normalized).csv"
CAHD_PATH = BASE / "Cost_Affordability_Healthy_Diet_(CoAHD)_E_All_Data_(Normalized).csv"
OUT = ROOT / "gluten_trend_analysis.json"
WORLD_AREA_CODE = 5000
# FAOSTAT publishes "China" as an aggregate of mainland China, Hong Kong,
# Macao and Taiwan. Exclude it from country comparisons to avoid duplicating
# the constituent areas, which are also present in these files.
EXCLUDED_COMPOSITE_AREA_CODES = {351}


FBS_GROUPS = {
    2511: "strict_gluten",  # Wheat and products
    2513: "strict_gluten",  # Barley and products
    2515: "strict_gluten",  # Rye and products
    2516: "oats_separate",
    2514: "gf_core",  # Maize and products
    2517: "gf_core",  # Millet and products
    2518: "gf_core",  # Sorghum and products
    2807: "gf_core",  # Rice and products
    2531: "gf_core",  # Potatoes and products
    2532: "gf_core",  # Cassava and products
    2533: "gf_core",  # Sweet potatoes
    2534: "gf_core",  # Roots, Other
    2535: "gf_core",  # Yams
    2911: "pulses_separate",
    2901: "grand_total",
    2905: "cereal_total",
    2501: "population",
}

QCL_ITEMS = {
    15: "Wheat",
    44: "Barley",
    71: "Rye",
    97: "Triticale",
    75: "Oats",
    56: "Maize",
    27: "Rice",
    79: "Millet",
    83: "Sorghum",
    89: "Buckwheat",
    92: "Quinoa",
    125: "Cassava",
    116: "Potatoes",
    122: "Sweet potatoes",
    137: "Yams",
    1726: "Pulses; Total",
}


def finite(value):
    if value is None or (isinstance(value, float) and not np.isfinite(value)):
        return None
    if isinstance(value, (np.integer, int)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        return float(value)
    return value


def frame_records(frame: pd.DataFrame, columns: list[str], n: int = 10) -> list[dict]:
    result = []
    for row in frame.head(n)[columns].to_dict(orient="records"):
        result.append({key: finite(value) for key, value in row.items()})
    return result


def load_fbs() -> tuple[pd.DataFrame, dict]:
    usecols = [
        "Area Code",
        "Area",
        "Item Code",
        "Item",
        "Element Code",
        "Element",
        "Year",
        "Unit",
        "Value",
        "Flag",
    ]
    selected = []
    scanned = 0
    for chunk in pd.read_csv(FBS_PATH, usecols=usecols, chunksize=300_000, low_memory=False):
        scanned += len(chunk)
        country_or_world = (
            ((chunk["Area Code"] < WORLD_AREA_CODE) & ~chunk["Area Code"].isin(EXCLUDED_COMPOSITE_AREA_CODES))
            | (chunk["Area Code"] == WORLD_AREA_CODE)
        )
        chunk = chunk[country_or_world & chunk["Item Code"].isin(FBS_GROUPS)]
        chunk = chunk[
            ((chunk["Element Code"] == 664) & (chunk["Item Code"] != 2501))
            | ((chunk["Element Code"] == 511) & (chunk["Item Code"] == 2501))
            | (
                chunk["Element Code"].isin([5301, 5511, 5611])
                & chunk["Item Code"].isin([code for code, group in FBS_GROUPS.items() if group in {"strict_gluten", "gf_core", "oats_separate"}])
            )
        ]
        if not chunk.empty:
            selected.append(chunk)
    fbs = pd.concat(selected, ignore_index=True)
    fbs["Value"] = pd.to_numeric(fbs["Value"], errors="coerce")
    fbs["group"] = fbs["Item Code"].map(FBS_GROUPS)

    energy = fbs[fbs["Element Code"] == 664].copy()
    grouped_energy = (
        energy.groupby(["Area Code", "Area", "Year", "group"], observed=True)["Value"]
        .sum(min_count=1)
        .unstack("group")
        .reset_index()
    )
    for column in ["strict_gluten", "oats_separate", "gf_core", "pulses_separate"]:
        if column not in grouped_energy:
            grouped_energy[column] = 0.0
        grouped_energy[column] = grouped_energy[column].fillna(0.0)

    population = (
        fbs[(fbs["Element Code"] == 511) & (fbs["group"] == "population")]
        .groupby(["Area Code", "Area", "Year"], observed=True)["Value"]
        .sum(min_count=1)
        .rename("population_thousand")
        .reset_index()
    )
    metrics = grouped_energy.merge(population, on=["Area Code", "Area", "Year"], how="left")

    detail = energy[energy["group"] == "gf_core"].copy()
    detail_sum = detail.groupby(["Area Code", "Area", "Year", "Item Code"], observed=True)["Value"].sum().rename("item_kcal").reset_index()
    detail_sum["gf_total"] = detail_sum.groupby(["Area Code", "Year"])["item_kcal"].transform("sum")
    detail_sum["share_sq"] = np.where(detail_sum["gf_total"] > 0, (detail_sum["item_kcal"] / detail_sum["gf_total"]) ** 2, np.nan)
    diversity = (
        1 - detail_sum.groupby(["Area Code", "Area", "Year"], observed=True)["share_sq"].sum(min_count=1)
    ).rename("gf_diversity").reset_index()
    metrics = metrics.merge(diversity, on=["Area Code", "Area", "Year"], how="left")

    quantities = fbs[fbs["Element Code"].isin([5301, 5511, 5611])].copy()
    element_names = {5301: "domestic_supply_t", 5511: "production_t", 5611: "imports_t"}
    quantities["measure"] = quantities["Element Code"].map(element_names)
    quantity_pivot = (
        quantities.groupby(["Area Code", "Area", "Year", "group", "measure"], observed=True)["Value"]
        .sum(min_count=1)
        .unstack(["group", "measure"])
    )
    quantity_pivot.columns = [f"{group}_{measure}" for group, measure in quantity_pivot.columns]
    metrics = metrics.merge(quantity_pivot.reset_index(), on=["Area Code", "Area", "Year"], how="left")

    metrics["gluten_share_total_pct"] = 100 * metrics["strict_gluten"] / metrics["grand_total"]
    metrics["gluten_share_cereal_pct"] = 100 * metrics["strict_gluten"] / metrics["cereal_total"]
    metrics["gf_core_share_total_pct"] = 100 * metrics["gf_core"] / metrics["grand_total"]
    metrics["gf_to_gluten_ratio"] = metrics["gf_core"] / metrics["strict_gluten"].replace(0, np.nan)
    metrics["gf_import_dependency_pct"] = 100 * metrics.get("gf_core_imports_t", np.nan) / metrics.get("gf_core_domestic_supply_t", np.nan)
    metrics["gluten_import_dependency_pct"] = 100 * metrics.get("strict_gluten_imports_t", np.nan) / metrics.get("strict_gluten_domestic_supply_t", np.nan)

    weighted_columns = ["strict_gluten", "oats_separate", "gf_core", "pulses_separate", "grand_total", "cereal_total"]
    # Prefer FAOSTAT's published World observations over summing countries.
    # This avoids duplicated composite entities and historical boundary issues.
    world = metrics[metrics["Area Code"] == WORLD_AREA_CODE].copy()
    if not world.empty:
        global_trend = world[["Year", "population_thousand", *weighted_columns]].rename(
            columns={"Year": "year", "population_thousand": "population_thousand_world"}
        )
        for column in weighted_columns:
            global_trend = global_trend.rename(columns={column: f"{column}_kcal_cap_day"})
        global_trend["population_billion"] = global_trend["population_thousand_world"] / 1_000_000
        global_trend["gluten_share_total_pct"] = 100 * global_trend["strict_gluten_kcal_cap_day"] / global_trend["grand_total_kcal_cap_day"]
        global_trend["gluten_share_cereal_pct"] = 100 * global_trend["strict_gluten_kcal_cap_day"] / global_trend["cereal_total_kcal_cap_day"]
        global_trend["gf_core_share_total_pct"] = 100 * global_trend["gf_core_kcal_cap_day"] / global_trend["grand_total_kcal_cap_day"]
        global_trend = global_trend.sort_values("year")
    else:
        global_rows = []
        countries = metrics[metrics["Area Code"] < WORLD_AREA_CODE]
        for year, group in countries.groupby("Year"):
            valid_pop = group["population_thousand"].notna() & (group["population_thousand"] > 0)
            base = group[valid_pop]
            row = {"year": int(year), "population_billion": base["population_thousand"].sum() / 1_000_000}
            for column in weighted_columns:
                valid = base[column].notna()
                row[f"{column}_kcal_cap_day"] = np.average(base.loc[valid, column], weights=base.loc[valid, "population_thousand"]) if valid.any() else np.nan
            row["gluten_share_total_pct"] = 100 * row["strict_gluten_kcal_cap_day"] / row["grand_total_kcal_cap_day"]
            row["gluten_share_cereal_pct"] = 100 * row["strict_gluten_kcal_cap_day"] / row["cereal_total_kcal_cap_day"]
            row["gf_core_share_total_pct"] = 100 * row["gf_core_kcal_cap_day"] / row["grand_total_kcal_cap_day"]
            global_rows.append(row)
        global_trend = pd.DataFrame(global_rows).sort_values("year")

    selected_flags = energy[energy["group"].isin(["strict_gluten", "gf_core", "oats_separate", "pulses_separate"])]
    flag_counts = selected_flags["Flag"].fillna("blank").value_counts(dropna=False).to_dict()
    diagnostics = {
        "rows_scanned": scanned,
        "selected_rows": len(fbs),
        "country_areas": int(metrics.loc[metrics["Area Code"] < WORLD_AREA_CODE, "Area Code"].nunique()),
        "year_min": int(metrics["Year"].min()),
        "year_max": int(metrics["Year"].max()),
        "selected_energy_flag_counts": {str(key): int(value) for key, value in flag_counts.items()},
    }
    return metrics, {"global_trend": global_trend, "diagnostics": diagnostics}


def load_qcl() -> tuple[pd.DataFrame, dict]:
    usecols = ["Area Code", "Area", "Item Code", "Item", "Element", "Year", "Unit", "Value", "Flag"]
    selected = []
    scanned = 0
    for chunk in pd.read_csv(QCL_PATH, usecols=usecols, chunksize=300_000, low_memory=False):
        scanned += len(chunk)
        chunk = chunk[
            (chunk["Area Code"] == WORLD_AREA_CODE)
            & chunk["Item Code"].isin(QCL_ITEMS)
            & chunk["Element"].isin(["Production", "Area harvested"])
        ]
        if not chunk.empty:
            selected.append(chunk)
    qcl = pd.concat(selected, ignore_index=True)
    qcl["Value"] = pd.to_numeric(qcl["Value"], errors="coerce")
    qcl["analysis_item"] = qcl["Item Code"].map(QCL_ITEMS)
    production = qcl[(qcl["Element"] == "Production") & (qcl["Unit"] == "t")]
    global_production = (
        production.groupby(["Year", "analysis_item"], observed=True)["Value"]
        .sum(min_count=1)
        .unstack("analysis_item")
        .sort_index()
    )
    rows = []
    for item in QCL_ITEMS.values():
        if item not in global_production:
            continue
        series = global_production[item].dropna()
        if series.empty:
            continue
        first_year = int(series.index.min())
        last_year = int(series.index.max())
        first_value = float(series.loc[first_year])
        last_value = float(series.loc[last_year])
        years = last_year - first_year
        cagr = ((last_value / first_value) ** (1 / years) - 1) * 100 if years > 0 and first_value > 0 and last_value > 0 else np.nan
        row = {
            "item": item,
            "first_year": first_year,
            "last_year": last_year,
            "first_million_t": first_value / 1_000_000,
            "last_million_t": last_value / 1_000_000,
            "total_change_pct": (last_value / first_value - 1) * 100 if first_value else np.nan,
            "cagr_pct": cagr,
        }
        for year in [1961, 2000, 2010, 2024]:
            row[f"production_{year}_million_t"] = float(series.loc[year]) / 1_000_000 if year in series.index else np.nan
        rows.append(row)
    crop_trends = pd.DataFrame(rows).sort_values("last_million_t", ascending=False)
    latest_year = int(production["Year"].max())
    latest_flags = production[production["Year"] == latest_year]["Flag"].fillna("blank").value_counts().to_dict()
    diagnostics = {
        "rows_scanned": scanned,
        "selected_rows": len(qcl),
        "production_year_min": int(production["Year"].min()),
        "production_year_max": latest_year,
        "latest_production_flag_counts": {str(key): int(value) for key, value in latest_flags.items()},
    }
    return crop_trends, diagnostics


def load_cahd() -> pd.DataFrame:
    cahd = pd.read_csv(CAHD_PATH, low_memory=False)
    cahd["Value"] = pd.to_numeric(cahd["Value"], errors="coerce")
    return cahd[
        (cahd["Area Code"] < WORLD_AREA_CODE)
        & ~cahd["Area Code"].isin(EXCLUDED_COMPOSITE_AREA_CODES)
        & (cahd["Item Code"] == 7005)
    ][
        ["Area Code", "Area", "Year", "Value", "Unit", "Flag"]
    ].rename(columns={"Value": "unaffordability_pct"})


def summarize(metrics: pd.DataFrame, fbs_info: dict, crop_trends: pd.DataFrame, qcl_diagnostics: dict, cahd: pd.DataFrame) -> dict:
    global_trend = fbs_info["global_trend"]
    first = global_trend.iloc[0]
    last = global_trend.iloc[-1]
    global_change = {}
    for column in [
        "strict_gluten_kcal_cap_day",
        "oats_separate_kcal_cap_day",
        "gf_core_kcal_cap_day",
        "pulses_separate_kcal_cap_day",
        "grand_total_kcal_cap_day",
        "gluten_share_total_pct",
        "gluten_share_cereal_pct",
        "gf_core_share_total_pct",
    ]:
        global_change[column] = {
            str(int(first["year"])): finite(first[column]),
            str(int(last["year"])): finite(last[column]),
            "absolute_change": finite(last[column] - first[column]),
            "percent_change": finite((last[column] / first[column] - 1) * 100) if first[column] else None,
        }

    latest_year = int(metrics["Year"].max())
    latest = metrics[
        (metrics["Year"] == latest_year)
        & (metrics["Area Code"] < WORLD_AREA_CODE)
        & (metrics["population_thousand"] >= 1000)
    ].copy()
    latest = latest.replace([np.inf, -np.inf], np.nan)
    top_gluten = latest.sort_values("gluten_share_total_pct", ascending=False)
    top_gf = latest.sort_values("gf_core", ascending=False)
    low_gf = latest[latest["grand_total"] > 0].sort_values("gf_core", ascending=True)
    import_dep = latest[(latest["gf_core_domestic_supply_t"] > 0) & latest["gf_import_dependency_pct"].notna()].sort_values("gf_import_dependency_pct", ascending=False)

    wide = metrics[
        (metrics["Area Code"] < WORLD_AREA_CODE) & (metrics["population_thousand"] >= 1000)
    ].pivot(index=["Area Code", "Area"], columns="Year", values="gluten_share_total_pct")
    if 2010 in wide.columns and latest_year in wide.columns:
        change = wide[[2010, latest_year]].dropna().copy()
        change["change_pp"] = change[latest_year] - change[2010]
        change = change.reset_index()
        biggest_increases = change.sort_values("change_pp", ascending=False)
        biggest_decreases = change.sort_values("change_pp", ascending=True)
    else:
        biggest_increases = pd.DataFrame(columns=["Area", 2010, latest_year, "change_pp"])
        biggest_decreases = biggest_increases.copy()

    cahd_year = min(latest_year, int(cahd["Year"].max()))
    cahd_latest = cahd[cahd["Year"] == cahd_year][["Area Code", "unaffordability_pct"]]
    joined = latest.merge(cahd_latest, on="Area Code", how="inner")
    joined = joined[["Area", "gluten_share_total_pct", "gf_core", "gf_diversity", "unaffordability_pct", "population_thousand"]].dropna()
    pearson_gluten = joined["gluten_share_total_pct"].corr(joined["unaffordability_pct"])
    spearman_gluten = joined["gluten_share_total_pct"].rank().corr(joined["unaffordability_pct"].rank())
    pearson_gf = joined["gf_core"].corr(joined["unaffordability_pct"])
    spearman_gf = joined["gf_core"].rank().corr(joined["unaffordability_pct"].rank())
    pua_q75 = joined["unaffordability_pct"].quantile(0.75)
    gluten_q75 = joined["gluten_share_total_pct"].quantile(0.75)
    gf_q25 = joined["gf_core"].quantile(0.25)
    intersection = joined[
        (joined["unaffordability_pct"] >= pua_q75)
        & (joined["gluten_share_total_pct"] >= gluten_q75)
        & (joined["gf_core"] <= gf_q25)
    ].sort_values(["unaffordability_pct", "gluten_share_total_pct"], ascending=False)

    return {
        "definitions": {
            "strict_gluten_fbs_items": {"2511": "Wheat and products", "2513": "Barley and products", "2515": "Rye and products"},
            "oats_handling": "Oats are reported separately and excluded from both strict gluten and core gluten-free groups.",
            "gf_core_fbs_items": {
                "2514": "Maize and products",
                "2517": "Millet and products",
                "2518": "Sorghum and products",
                "2807": "Rice and products",
                "2531": "Potatoes and products",
                "2532": "Cassava and products",
                "2533": "Sweet potatoes",
                "2534": "Roots, Other",
                "2535": "Yams",
            },
            "pulses_handling": "Pulses are reported separately rather than treated as a staple substitute.",
            "country_filter": "Area Code < 5000, excluding composite China code 351; FAOSTAT World code 5000 is used only for global trends.",
        },
        "fbs_diagnostics": fbs_info["diagnostics"],
        "global_2010_to_2023": global_change,
        "latest_country_patterns": {
            "year": latest_year,
            "top_gluten_share_of_total_energy": frame_records(top_gluten, ["Area", "gluten_share_total_pct", "strict_gluten", "grand_total", "gf_core"], 10),
            "highest_gf_core_kcal_cap_day": frame_records(top_gf, ["Area", "gf_core", "gluten_share_total_pct", "gf_diversity"], 10),
            "lowest_gf_core_kcal_cap_day": frame_records(low_gf, ["Area", "gf_core", "gluten_share_total_pct", "gf_diversity"], 10),
            "highest_gf_import_dependency_population_ge_1m": frame_records(import_dep, ["Area", "gf_import_dependency_pct", "gf_core_imports_t", "gf_core_domestic_supply_t"], 10),
            "largest_gluten_share_increases_2010_to_latest": frame_records(biggest_increases, ["Area", 2010, latest_year, "change_pp"], 10),
            "largest_gluten_share_decreases_2010_to_latest": frame_records(biggest_decreases, ["Area", 2010, latest_year, "change_pp"], 10),
        },
        "cahd_context": {
            "join_year": cahd_year,
            "countries_joined": len(joined),
            "pearson_gluten_share_vs_unaffordability": finite(pearson_gluten),
            "spearman_gluten_share_vs_unaffordability": finite(spearman_gluten),
            "pearson_gf_kcal_vs_unaffordability": finite(pearson_gf),
            "spearman_gf_kcal_vs_unaffordability": finite(spearman_gf),
            "upper_quartile_unaffordability_threshold_pct": finite(pua_q75),
            "upper_quartile_gluten_share_threshold_pct": finite(gluten_q75),
            "lower_quartile_gf_kcal_threshold": finite(gf_q25),
            "three_way_descriptive_intersection": frame_records(
                intersection,
                ["Area", "unaffordability_pct", "gluten_share_total_pct", "gf_core", "gf_diversity"],
                30,
            ),
        },
        "qcl_diagnostics": qcl_diagnostics,
        "global_crop_production_trends": [
            {key: finite(value) for key, value in row.items()}
            for row in crop_trends.to_dict(orient="records")
        ],
    }


def main() -> None:
    metrics, fbs_info = load_fbs()
    crop_trends, qcl_diagnostics = load_qcl()
    cahd = load_cahd()
    result = summarize(metrics, fbs_info, crop_trends, qcl_diagnostics, cahd)
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
