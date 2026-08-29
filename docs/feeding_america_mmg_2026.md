# Feeding America Map the Meal Gap 2026 integration

## Decision

Retain selected Alabama county and state fields from the Feeding America Map the Meal Gap 2026 request package as a separate modeled food-insecurity and food-cost outcome layer. Do not combine these measures with USDA household food insecurity or tract retailer proximity.

## Source and version

- Publisher: Feeding America National Organization.
- Official report: https://www.feedingamerica.org/research/map-the-meal-gap/overall-executive-summary
- Methodology: https://www.feedingamerica.org/research/map-the-meal-gap/how-we-got-the-map-data
- Data request page: https://www.feedingamerica.org/research/map-the-meal-gap/by-county
- Received archive: `MMG2026_Data_To_Share.zip` on August 29, 2026.
- Archive SHA-256: `88b6d839860121c295ece955a2aa88bfa856c4ee452ae05403c168c3975d492a`.
- Primary workbook: `MMG2026_2024_Data_To_Share.xlsx`, updated July 28, 2026.
- Observation year: 2024.
- Recommended citation from the workbook: Ribar, D. C., Harris, V., Dewey, A., Dawes, S., Hilvers, J., and Engelhard, E. (2026). Map the Meal Gap: An Analysis of Local Food Insecurity and Food Costs in the United States in 2024. Feeding America National Organization.

## Appropriate repository scope

The archive contains national files from data years 2009 through 2024, an overview document, and a county-revision notice. The active repository adds only:

- the latest 2024 Alabama county extract;
- the latest 2024 Alabama state extract;
- source provenance and the archive hash;
- validation and reconciliation checks; and
- report and workbook updates.

The raw request package is copied into the ignored raw-data directory for local reproducibility. The archive does not state an explicit redistribution license, so the raw package is not committed to GitHub. Historical files are not added to the active trend analysis. The archive states that 2023 county overall and child estimates were corrected because the original release used 2022 rather than 2023 Bureau of Labor Statistics county unemployment rates.

## Retained measures

The county extract retains the county FIPS key, overall and child modeled rates and counts, income-threshold shares, the meal-cost and food-budget-shortfall measures, the market-basket imputation flag, the 2023 Rural-Urban Continuum Code, and source ID. The state extract also retains senior and older-adult rates and counts.

Race and ethnicity fields are excluded from the active output because the project decision keeps those analyses outside the current scope. Blank source values are not converted to zero.

## Validation

- 67 Alabama county rows.
- 67 unique five-digit FIPS values beginning with `01`.
- One Alabama state row for observation year 2024.
- All retained rate fields fall between 0 and 1 before percent formatting.
- 22 counties have imputed market-basket data.
- County food-insecure counts sum to 883,710 people; the Alabama state estimate is 919,160, a difference of 35,450.
- County food-insecure child counts sum to 271,010; the Alabama state estimate is 276,640.

The differences are expected. Feeding America documents that state estimates aggregate congressional-district estimates, while county estimates are produced with the county model.

## Interpretation

The 17.8% Alabama Map the Meal Gap rate is a modeled estimate of individuals living in food-insecure households in 2024. The 12.1% USDA Alabama estimate is a 2022-2024 household survey estimate. The 20.2% retailer-access result is the share of low-income people beyond the selected driving-distance threshold. They use different units, denominators, methods, and meanings and remain separate throughout the analysis.
