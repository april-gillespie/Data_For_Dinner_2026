# Data for Dinner 2026

## Project status

The food-access analysis is complete and quality checked. The primary local measure uses road-network distance. Straight-line distance is excluded from the active analysis and all published results. Feeding America Map the Meal Gap 2026 is included as a separate modeled county and state outcome layer for observation year 2024. Sandra Kopecky's contributed workbook is now the prevailing team story workbook for presentation development. The validated analysis tables remain the audit source for exact published claims. The team plans to record the final presentation and submit the project during the weekend ending September 13, 2026.

## Research question

What does current official data show about food security and access to food globally, in the United States, across the project-defined Southeast, and in Alabama?

Food insecurity is a household condition in which access to adequate food is limited or uncertain because of insufficient money or other resources. Food access is the ability to reach and obtain food. The local analysis measures proximity to SNAP-authorized retailers and does not treat proximity as a complete measure of food insecurity.

## Scope

The active analysis includes global and U.S. food-insecurity context, a ten-state comparison, Alabama tract-level retailer access, and a separate Alabama county and state Map the Meal Gap outcome layer. The project-defined Southeast is Alabama, Arkansas, Florida, Georgia, Kentucky, Louisiana, Mississippi, North Carolina, South Carolina, and Tennessee. This is a project convention, not a claim that it is the only official regional definition.

The active analysis excludes:

- food allergies and allergen-specific commodity analysis;
- race and gender demographic analysis;
- straight-line distance metrics;
- causal claims about retailer proximity and food insecurity; and
- retailer-level price, product quality, inventory, transit, and household-level local food-insecurity outcomes.

Exploratory allergen files remain available for future feasibility work, but they are not inputs to the active analysis. See [data/README.md](data/README.md) and [docs/allergy_next_crawl.md](docs/allergy_next_crawl.md).

## Study period and source vintages

The core frozen pull was retrieved August 22, 2026, Central Time. The Feeding America request package was received August 29, 2026. The sources do not share one observation period:

- FAOSTAT core food-insecurity indicators use 2023-2025 averages, with some affordability series through 2025.
- USDA household food-security data use the 2024 national estimate and 2022-2024 state averages.
- USDA retailer access uses SNAP-authorized retailers as of June 2025, 2020 Census population, and 2020-2024 ACS inputs.
- Alabama map geometry uses 2020 Census tracts.
- Feeding America Map the Meal Gap 2026 reports modeled county and state estimates for observation year 2024; its latest workbook was updated July 28, 2026.

Results are compared only where units, denominators, geography, and periods support the comparison. Retrieval date is not treated as the observation date.

## Analytical design

- Global context: FAOSTAT food-insecurity and healthy-diet-affordability indicators.
- U.S. and state outcomes: USDA ERS household food-security estimates.
- Local physical access: USDA ERS 2025 SNAP-authorized Retailer Access Map, using more than 1 driving mile for urban tracts and more than 10 driving miles for rural tracts.
- Alabama mapping: U.S. Census Bureau 2020 tract geometry.
- Alabama county and state outcome context: Feeding America Map the Meal Gap 2026 modeled individual estimates and localized meal-cost measures for 2024.
- Household need proxy: occupied housing units receiving SNAP, reported with its matching housing-unit denominator.
- Evolving team story: Sandra Kopecky's contributed workbook organizes the global, U.S., regional, Southeast, Alabama county, and Alabama regional narrative. Its driver labels are treated as hypotheses until direct supporting sources are attached.

These layers answer related but different questions. Global population indicators, U.S. household food insecurity, modeled individual food insecurity, and tract retailer proximity are reported separately and are not combined into one score.

## Method decisions

- The primary result uses the road-network threshold of 1 mile for urban tracts and 10 miles for rural tracts.
- Straight-line distance is excluded because it does not represent road travel and produced implausibly influential outliers for this study.
- Sensitivity checks vary the road-network threshold only: 0.5 mile urban and 10 miles rural, plus 1 mile urban and 20 miles rural.
- Tract GEOIDs are stored as 11-character text. The pipeline restores leading zeros before every join.
- State margins of error remain attached to household food-insecurity estimates.

## Factual highlights

- FAOSTAT estimates 26.8% of the world population experienced moderate or severe food insecurity in 2023-2025. The corresponding U.S. estimate is 10.7%.
- USDA estimates 13.7% of U.S. households were food insecure in 2024.
- Among the ten project states, 2022-2024 household food-insecurity estimates range from 11.8% in North Carolina to 19.4% in Arkansas. Alabama is 12.1%, with a 2.23 percentage-point margin of error.
- In Alabama, 20.2% of low-income residents are beyond the primary retailer-access threshold. Alabama has 151 low-income/low-access tracts, or 10.5% of its tracts.
- Alabama's low-income low-access share is slightly below the provisional U.S. estimate of 21.2%, while its share of tracts flagged low-income/low-access is above the U.S. share of 7.5%.
- Feeding America estimates that 17.8% of Alabama residents, or 919,160 people, experienced food insecurity in 2024. The modeled child rate is 24.4%, or 276,640 children.
- Across Alabama counties, the modeled overall rate ranges from 13.1% in Shelby County to 24.8% in Greene County. These county estimates are not tract-level measures and are not combined with the retailer-proximity metric.

## Sensitivity checkpoint

The final Alabama headline is 20.2% of low-income residents beyond the primary threshold. Under the stricter 0.5-mile urban threshold, the estimate is 35.9%. Under the 20-mile rural threshold, it is 19.6%. The urban threshold materially affects the burden estimate, so every final chart, table, and narrative must state the selected threshold.

## Visualization priority

The final story should distinguish the presence of food resources from the ability to reach and afford food. The current repository measures food insecurity, healthy-diet affordability, and retailer proximity. It does not yet contain a validated food-supply-volume measure, so a food-abundance claim or map should be added only after that measure, unit, date range, and geographic coverage are approved.

## Repository policy

Only reviewed, reproducible, publication-ready files belong in the GitHub repository. Raw downloads, local previews, caches, exploratory allergen outputs, and partial drafts remain ignored. A new dataset is published only after its source, vintage, geography, unit, denominator, license, processing steps, and QA status are documented.

The Feeding America source gate is now complete. The repository includes selected Alabama county and state extracts, a source hash, field definitions, validation checks, and a reconciliation note. The request-only raw archive remains ignored because the package does not state an explicit redistribution license. See [docs/feeding_america_mmg_2026.md](docs/feeding_america_mmg_2026.md).

Sandra Kopecky's contributed workbook is preserved byte for byte under `data/contributed/sandra_kopecky/` and is credited in the project roles, source manifest, report, charter, and workbook guide. It is the prevailing team synthesis for the evolving story. See [docs/sandra_kopecky_story_workbook.md](docs/sandra_kopecky_story_workbook.md) for its role and review boundaries.

## Repository structure

```text
data/
  contributed/     credited team-created story workbooks
  metadata/        source manifest and variable dictionary
  processed/       analysis-ready CSV outputs
docs/              methods, decisions, limitations, and future-work notes
figures/           reviewed charts and Alabama tract map
reports/           team report, PDF, and analysis workbook
results/           QA, sensitivity, assessment, and findings outputs
src/               acquisition and analysis scripts
```

Raw source files are not committed because they are large, reproducibly downloaded from official publishers, or supplied through a request-only workflow. The Feeding America archive is represented by its SHA-256 hash and selected reviewed extracts.

## Reproduce

```powershell
python -m pip install -r requirements.txt
python src/acquire_data.py
python src/process_feeding_america_mmg.py --archive "C:\path\to\MMG2026_Data_To_Share.zip"
python src/analyze_food_access.py
```

The acquisition script preserves existing downloads and writes SHA-256 hashes to `data/metadata/source_manifest.csv`. The analysis script repairs source GEOIDs to 11-character text before joining, writes processed tables and QA results, and regenerates all figures.

## Reports

- `reports/Data_for_Dinner_Food_Access_Analysis.docx`
- `reports/Data_for_Dinner_Food_Access_Analysis.pdf`
- `reports/Data_for_Dinner_Food_Access_Analysis.xlsx`

## Prevailing team story workbook

- `data/contributed/sandra_kopecky/WomenInData Data Stats and Summary - Story.xlsx`, created by Sandra Kopecky and preserved as submitted.

## Supporting documentation

- [Methodology](docs/methodology.md)
- [August 25 decisions](docs/decisions_2026-08-25.md)
- [Known limitations and blind spots](docs/limitations.md)
- [Sandra Kopecky story workbook](docs/sandra_kopecky_story_workbook.md)
- [Allergy feasibility note](docs/allergy_next_crawl.md)

## Project roles

Roles are maintained in the supporting document [docs/project_roles.md](docs/project_roles.md) so readers encounter the project content before team assignments.
