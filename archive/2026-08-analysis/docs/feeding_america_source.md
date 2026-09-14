# Feeding America Map the Meal Gap source

## Provenance

On August 25, 2026, the Feeding America Research Team responded to Sandra Kopecky with an official Map the Meal Gap data archive. The archive link was forwarded to April Gillespie on August 25, 2026.

Feeding America described the archive as containing:

- `MMG2026_2024_Data_To_Share` for 2024 observations released in Map the Meal Gap 2026;
- `MMG2025_2019-2023_Data_ToShare` for 2019-2023 observations; and
- individual files for earlier years.

Feeding America also stated that its 2023 county overall and child estimates were revised. The corrected values are included in the supplied archive, with revision details in `MMG_2025_County_Revisions_Detail`.

## Official interpretation guidance

The project must use Feeding America's report and methodology alongside the data. Map the Meal Gap 2026 was published July 28, 2026 and reflects 2024 data. Feeding America estimates local food insecurity for the overall population, children, older adults, seniors, selected income levels, and selected races/ethnicities. It also estimates program eligibility, food budget shortfall, and local meal cost.

Food-insecurity estimates are modeled local outcomes. They are analytically different from the USDA SNAP-authorized Retailer Access Map used elsewhere in this project, which measures physical retailer proximity. The two sources may be compared as related dimensions of access but must not be described as measuring the same thing.

## Intake status

The source has been accepted into project intake, but the emailed ZIP is not stored in GitHub. Before Feeding America variables are used in publication outputs:

1. place `MMG2026_Data_To_Share.zip` in `data/raw/2026-08-25/feeding_america/`;
2. run `python src/ingest_feeding_america.py` to extract and inventory the archive;
3. verify Alabama, Southeast, and national geographies and identifiers;
4. identify the exact columns and denominators for overall, child, senior/older-adult, income, race/ethnicity, meal-cost, and food-budget-shortfall measures that are in scope;
5. confirm that 2023 county analyses use the revised records rather than any superseded local copy;
6. document retained variables in `data/metadata/variable_dictionary.csv`;
7. add QA checks before promotion into `data/processed/`, figures, findings, or reports.

## Current analytical opportunity

This source can strengthen the project's U.S. and Alabama story because it supplies modeled county-level food-insecurity outcomes and 2024 local estimates. It can be used to test whether counties with higher modeled food insecurity also show greater retailer-access burden, while keeping outcome and proximity measures conceptually separate.

Senior and older-adult measures are potentially useful because Feeding America explicitly publishes estimates for those populations, but the latest technical documentation notes that their estimation methodology differs from other subpopulations. Any senior-hunger analysis therefore requires its own method note and denominator check.

## Official references

- Map the Meal Gap 2026 report: https://www.feedingamerica.org/research/map-the-meal-gap/overall-executive-summary
- Map the Meal Gap methodology: https://www.feedingamerica.org/research/map-the-meal-gap/how-we-got-the-map-data
- Interactive map: https://map.feedingamerica.org/
- Data request page: https://www.feedingamerica.org/research/map-the-meal-gap/overall-executive-summary

## Usage note

Feeding America invited recipients to share resulting papers, visualizations, or assets with its Research Team. Before final submission, preserve source attribution and check the supplied files or accompanying documentation for any additional usage language that should appear in the report or repository.
