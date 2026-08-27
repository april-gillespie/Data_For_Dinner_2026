# Data directory

Only reviewed metadata and processed outputs are included in this repository.

## Included

- `metadata/source_manifest.csv` records official sources, vintages, retrieval timestamps, local source paths, file sizes, and hashes.
- `metadata/variable_dictionary.csv` records retained fields, units, definitions, and processing notes.
- `processed/*.csv` contains analysis-ready outputs produced by `src/analyze_food_access.py`.

## Excluded from the active analysis

Food-allergy and gluten exploration is available in the local project workspace for possible future research, but it is not a finalized input to the current food-access analysis. It is excluded from active variables, processed tables, figures, findings, and reports. The feasibility criteria are documented in `docs/allergy_next_crawl.md`.

Raw downloads, partial extracts, and exploratory outputs are not committed. New data is added only after its source, vintage, geography, unit, denominator, license, processing steps, and QA status are documented.
