# Data directory

Only reviewed metadata and processed outputs are included in this repository.

## Included

- `metadata/source_manifest.csv` records official sources, vintages, retrieval timestamps, local source paths, file sizes, and hashes.
- `metadata/variable_dictionary.csv` records retained fields, units, definitions, and processing notes.
- `processed/*.csv` contains analysis-ready outputs produced by `src/analyze_food_access.py`.
- `processed/alabama_county_food_insecurity_2024.csv` and `processed/alabama_state_food_insecurity_2024.csv` contain the selected Alabama fields from the validated Feeding America request package. Race and ethnicity fields remain excluded from the active scope.
- `contributed/sandra_kopecky/WomenInData Data Stats and Summary - Story.xlsx` is Sandra Kopecky's prevailing team story workbook. It is preserved unchanged and credited by name. It organizes the evolving narrative while the validated processed tables remain the audit source for exact claims.

## Contributor workbook review boundary

Sandra's workbook is an accepted team synthesis rather than a new official publisher source. The repository records its SHA-256 hash, seven-sheet structure, authorship metadata, and review notes. Narrative driver labels and static regional summaries require direct citations or reproducible calculations before they become final causal or policy claims.

## Excluded from the active analysis

Food-allergy and gluten exploration is available in the local project workspace for possible future research, but it is not a finalized input to the current food-access analysis. It is excluded from active variables, processed tables, figures, findings, and reports. The feasibility criteria are documented in `docs/allergy_next_crawl.md`.

Raw downloads, request-only source packages, partial extracts, and exploratory outputs are not committed. New data is added only after its source, vintage, geography, unit, denominator, access terms, processing steps, and QA status are documented. The Feeding America package did not include an explicit redistribution license, so the raw archive remains ignored while selected Alabama extracts and provenance are published.
