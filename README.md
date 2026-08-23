# Data for Dinner 2026

## Team

- Sharon Brooks — team lead / project management
- Sandra Kopecky — data and database
- April Gillespie — analysis and technical implementation

## Research question

What does current official data show about access to food globally, in the United States, across the project-defined Southeast, and in Alabama?

The active analysis intentionally excludes food allergies. Allergy data is treated as a separate feasibility crawl so that prevalence, labeling, product availability, recall events, and retailer access are not combined before their units and joins are validated.

## Geographic scope

The project-defined Southeast is Alabama, Arkansas, Florida, Georgia, Kentucky, Louisiana, Mississippi, North Carolina, South Carolina, and Tennessee. This is a project convention, not a claim that it is the only official regional definition.

## Current analytical design

- Global context: FAOSTAT food-insecurity and healthy-diet-affordability indicators.
- U.S. and state outcomes: USDA ERS household food-security estimates.
- Local physical access: USDA ERS 2025 SNAP-authorized Retailer Access Map (SRAM), using the network-distance threshold of 1 mile for urban tracts and 10 miles for rural tracts.
- Alabama mapping: U.S. Census Bureau 2020 tract geometry.

These layers answer related but different questions. Global population indicators, U.S. household food insecurity, and tract retailer proximity are reported separately and are not treated as a single comparable metric.

## Factual highlights

- FAOSTAT estimates 26.8% of the world population experienced moderate or severe food insecurity in 2023–2025; the corresponding U.S. estimate is 10.7%.
- USDA estimates 13.7% of U.S. households were food insecure in 2024.
- Among the ten project states, 2022–2024 household food-insecurity estimates range from 11.8% in North Carolina to 19.4% in Arkansas. Alabama is 12.1% with a 2.23 percentage-point margin of error.
- In Alabama, 20.2% of low-income residents are beyond the primary SRAM retailer-access threshold. Alabama has 151 low-income/low-access tracts, or 10.5% of its tracts.
- Alabama's low-income low-access share is slightly below the provisional U.S. estimate of 21.2%, while its share of tracts flagged low-income/low-access is above the U.S. share of 7.5%.
- Driving distance gives a materially higher Alabama burden than straight-line distance (20.2% versus 8.6% of low-income residents), so the distance method must remain visible in every report.

## Repository structure

```text
data/
  metadata/        source manifest and variable dictionary
  processed/       analysis-ready CSV outputs
docs/              methodology and allergy-crawl recommendation
figures/           reviewed charts and Alabama tract map
reports/           team report, PDF, and analysis workbook
results/           QA, sensitivity, assessment, and findings outputs
src/               acquisition and analysis scripts
```

Raw source files are not committed because they are large and reproducibly downloaded from official publishers.

## Reproduce

```powershell
python -m pip install -r requirements.txt
python src/acquire_data.py
python src/analyze_food_access.py
```

The acquisition script preserves existing downloads and writes SHA-256 hashes to `data/metadata/source_manifest.csv`. The analysis script repairs source GEOIDs to 11-character text before joining, writes processed tables and QA results, and regenerates all figures.

## Reports

- `reports/Data_for_Dinner_Food_Access_Analysis.docx`
- `reports/Data_for_Dinner_Food_Access_Analysis.pdf`
- `reports/Data_for_Dinner_Food_Access_Analysis.xlsx`

## Source dates

The frozen pull was retrieved August 22, 2026 (Central Time). The SRAM retailer list is June 2025, household food-security data are 2024 annual and 2022–2024 state averages, and FAOSTAT core indicators extend through 2023–2025 or 2025 depending on the series.

## Status

Analysis complete and quality checked. The primary dataset is retained for the current question. Food allergies remain a separately gated next crawl.

