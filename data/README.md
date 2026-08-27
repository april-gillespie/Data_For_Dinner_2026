# Data directory

Only reviewed metadata and processed outputs are included in this repository.

## Included

- `metadata/source_manifest.csv` records official sources, vintages, retrieval timestamps, local source paths, file sizes, hashes, and source status.
- `metadata/variable_dictionary.csv` records retained fields, units, definitions, and processing notes.
- `processed/*.csv` contains analysis-ready outputs produced by `src/analyze_food_access.py`.

## Feeding America source received August 25, 2026

Sandra obtained the official Feeding America Map the Meal Gap archive directly from the Feeding America Research Team. The archive includes the 2026 release using 2024 data, the 2025 package covering 2019-2023, and older annual files. Feeding America also noted that 2023 county overall and child estimates were revised and that the corrected values are included in the supplied archive.

The source is now registered in the project and documented in `docs/feeding_america_source.md`. Because the emailed Qualtrics download is not committed to GitHub, the archive must be placed in `data/raw/2026-08-25/feeding_america/` before ingestion. Run `python src/ingest_feeding_america.py` to extract and inventory the archive before any Feeding America fields are promoted into `processed/` outputs.

Feeding America data is treated as an official local food-insecurity outcome source, distinct from USDA retailer-proximity measures. It must not be merged into a composite score without an explicitly documented analytical decision.

## Excluded from the active analysis

Food-allergy and gluten exploration is available in the local project workspace for possible future research, but it is not a finalized input to the current food-access analysis. It is excluded from active variables, processed tables, figures, findings, and reports. The feasibility criteria are documented in `docs/allergy_next_crawl.md`.

Raw downloads, partial extracts, and exploratory outputs are not committed. New data is added to publication outputs only after its source, vintage, geography, unit, denominator, license/usage conditions, processing steps, and QA status are documented.
