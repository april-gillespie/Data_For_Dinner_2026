# Data for Dinner 2026

## Project status

The food-access analysis is complete and quality checked. The primary local measure uses road-network distance. Straight-line distance is excluded from the active analysis and all published results. An official Feeding America Map the Meal Gap archive obtained by Sandra Kopecky is now registered as an additional staged source and is being held outside publication outputs until its ZIP is locally inventoried and validated. The team plans to record the final presentation and submit the project during the weekend ending September 13, 2026.

## Research question

What does current official data show about food security and access to food globally, in the United States, across the project-defined Southeast, and in Alabama?

Food insecurity is a household condition in which access to adequate food is limited or uncertain because of insufficient money or other resources. Food access is the ability to reach and obtain food. The local analysis measures proximity to SNAP-authorized retailers and does not treat proximity as a complete measure of food insecurity.

## Scope

The active analysis includes global and U.S. food-insecurity context, a ten-state comparison, and Alabama tract-level retailer access. The project-defined Southeast is Alabama, Arkansas, Florida, Georgia, Kentucky, Louisiana, Mississippi, North Carolina, South Carolina, and Tennessee. This is a project convention, not a claim that it is the only official regional definition.

The active analysis excludes:

- food allergies and allergen-specific commodity analysis;
- race and gender demographic analysis;
- straight-line distance metrics;
- causal claims about retailer proximity and food insecurity; and
- food price, product quality, inventory, transit, and household-level local food-insecurity outcomes.

Exploratory allergen files remain available for future feasibility work, but they are not inputs to the active analysis. See [data/README.md](data/README.md) and [docs/allergy_next_crawl.md](docs/allergy_next_crawl.md).

## Study period and source vintages

The original frozen pull was retrieved August 22, 2026, Central Time. Feeding America's archive was obtained August 25, 2026 and is tracked separately as staged intake. The sources do not share one observation period:

- FAOSTAT core food-insecurity indicators use 2023-2025 averages, with some affordability series through 2025.
- USDA household food-security data use the 2024 national estimate and 2022-2024 state averages.
- USDA retailer access uses SNAP-authorized retailers as of June 2025, 2020 Census population, and 2020-2024 ACS inputs.
- Alabama map geometry uses 2020 Census tracts.
- Feeding America Map the Meal Gap 2026 reflects 2024 data; the supplied archive also includes 2019-2023 and older annual files.

Results are compared only where units, denominators, geography, and periods support the comparison. Retrieval date is not treated as the observation date.

## Analytical design

- Global context: FAOSTAT food-insecurity and healthy-diet-affordability indicators.
- U.S. and state outcomes: USDA ERS household food-security estimates.
- Local physical access: USDA ERS 2025 SNAP-authorized Retailer Access Map, using more than 1 driving mile for urban tracts and more than 10 driving miles for rural tracts.
- Alabama mapping: U.S. Census Bureau 2020 tract geometry.
- Household need proxy: occupied housing units receiving SNAP, reported with its matching housing-unit denominator.
- Staged local outcome layer: Feeding America Map the Meal Gap modeled local food-insecurity estimates, pending archive inventory, variable mapping, denominator checks, and QA.

These layers answer related but different questions. Global population indicators, U.S. household food insecurity, Feeding America modeled local outcomes, and tract retailer proximity are reported separately and are not combined into one score.

## Method decisions

- The primary result uses the road-network threshold of 1 mile for urban tracts and 10 miles for rural tracts.
- Straight-line distance is excluded because it does not represent road travel and produced implausibly influential outliers for this study.
- Sensitivity checks vary the road-network threshold only: 0.5 mile urban and 10 miles rural, plus 1 mile urban and 20 miles rural.
- Tract GEOIDs are stored as 11-character text. The pipeline restores leading zeros before every join.
- State margins of error remain attached to household food-insecurity estimates.
- Feeding America outcomes remain distinct from retailer-proximity measures; 2023 county analyses must use the revised Feeding America overall and child estimates supplied in the archive.

## Factual highlights

- FAOSTAT estimates 26.8% of the world population experienced moderate or severe food insecurity in 2023-2025. The corresponding U.S. estimate is 10.7%.
- USDA estimates 13.7% of U.S. households were food insecure in 2024.
- Among the ten project states, 2022-2024 household food-insecurity estimates range from 11.8% in North Carolina to 19.4% in Arkansas. Alabama is 12.1%, with a 2.23 percentage-point margin of error.
- In Alabama, 20.2% of low-income residents are beyond the primary retailer-access threshold. Alabama has 151 low-income/low-access tracts, or 10.5% of its tracts.
- Alabama's low-income low-access share is slightly below the provisional U.S. estimate of 21.2%, while its share of tracts flagged low-income/low-access is above the U.S. share of 7.5%.

Feeding America values are not yet included in these headline figures because the supplied ZIP has not been inventoried in the project workspace.

## Sensitivity checkpoint

The final Alabama retailer-access headline is 20.2% of low-income residents beyond the primary threshold. Under the stricter 0.5-mile urban threshold, the estimate is 35.9%. Under the 20-mile rural threshold, it is 19.6%. The urban threshold materially affects the burden estimate, so every final chart, table, and narrative must state the selected threshold.

## Visualization priority

The final story should distinguish the presence of food resources from the ability to reach and afford food. The current repository measures food insecurity, healthy-diet affordability, and retailer proximity. Feeding America offers a stronger future county-level outcome layer once validated. The repository does not yet contain a validated food-supply-volume measure, so a food-abundance claim or map should be added only after that measure, unit, date range, and geographic coverage are approved.

## Repository policy

Only reviewed, reproducible, publication-ready files belong in the GitHub repository. Raw downloads, local previews, caches, exploratory allergen outputs, and partial drafts remain ignored. A new dataset is published only after its source, vintage, geography, unit, denominator, license/usage conditions, processing steps, and QA status are documented.

Sandra's Feeding America source now has direct provenance and is registered in the source manifest. It remains staged rather than publication-ready because the emailed archive must still be downloaded locally, hashed, extracted, inventoried, and mapped to exact variables and denominators. See [docs/feeding_america_source.md](docs/feeding_america_source.md).

## Repository structure

```text
data/
  metadata/        source manifest, variable dictionary, source inventories
  processed/       analysis-ready CSV outputs
docs/              methods, decisions, limitations, and source notes
figures/           reviewed charts and Alabama tract map
reports/           team report, PDF, and analysis workbook
results/           QA, sensitivity, assessment, and findings outputs
src/               acquisition, intake, and analysis scripts
```

Raw source files are not committed because they are large and/or supplied directly by official publishers.

## Reproduce

```powershell
python -m pip install -r requirements.txt
python src/acquire_data.py
python src/ingest_feeding_america.py   # after saving the supplied ZIP locally
python src/analyze_food_access.py
```

The standard acquisition script preserves existing downloads and writes SHA-256 hashes to `data/metadata/source_manifest.csv`. The Feeding America intake script hashes, safely extracts, and inventories the supplied archive before any fields are promoted into processed data. The analysis script repairs source GEOIDs to 11-character text before joining, writes processed tables and QA results, and regenerates all figures.

## Reports

- `reports/Data_for_Dinner_Food_Access_Analysis.docx`
- `reports/Data_for_Dinner_Food_Access_Analysis.pdf`
- `reports/Data_for_Dinner_Food_Access_Analysis.xlsx`

## Supporting documentation

- [Methodology](docs/methodology.md)
- [August 25 decisions](docs/decisions_2026-08-25.md)
- [Feeding America source and intake](docs/feeding_america_source.md)
- [Known limitations and blind spots](docs/limitations.md)
- [Allergy feasibility note](docs/allergy_next_crawl.md)

## Project roles

Roles are maintained in the supporting document [docs/project_roles.md](docs/project_roles.md) so readers encounter the project content before team assignments.
