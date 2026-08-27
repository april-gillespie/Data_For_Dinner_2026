# Methodology

## Scope

This analysis reports facts at four levels: global, United States, a ten-state project-defined Southeast, and Alabama. Food allergies, race and gender demographic analysis, and straight-line distance metrics are outside the active analysis.

## Study period

The original frozen pull was retrieved August 22, 2026, Central Time. A Feeding America Map the Meal Gap archive obtained by Sandra Kopecky from the Feeding America Research Team on August 25, 2026 is now registered as an additional project source and remains in staged intake until its supplied ZIP is locally inventoried and validated. Observation periods differ by source: FAOSTAT core indicators use 2023-2025 averages, USDA household data uses 2024 nationally and 2022-2024 for state averages, retailer access uses retailers as of June 2025 with 2020 Census and 2020-2024 ACS inputs, Alabama geometry uses 2020 tracts, and Map the Meal Gap 2026 reflects 2024 observations. Retrieval date is not treated as the observation date.

## Measures

### Global

FAOSTAT provides population-level prevalence of moderate or severe food insecurity, severe food insecurity, undernourishment, and inability to afford a healthy diet. The latest period is selected separately for each indicator and geography.

### United States and states

USDA Economic Research Service household food-security files provide the 2024 national annual estimate and 2022–2024 state averages. State margins of error are retained. State ranks are descriptive; overlapping uncertainty intervals mean small differences should not be treated as definitive ordering.

### Feeding America local food insecurity

Feeding America's Map the Meal Gap produces modeled local estimates of food insecurity for the overall population, children, older adults, seniors, select income levels, and select races/ethnicities. It also estimates program eligibility, food budget shortfall, and local meal cost. Map the Meal Gap 2026 was published July 28, 2026 and reflects 2024 data.

These measures are outcomes or modeled local estimates and are conceptually distinct from USDA retailer-proximity measures. They may be compared as related dimensions of food access, but they must not be presented as interchangeable or combined into a single score without a separately documented method decision.

The archive supplied to Sandra includes 2024 data, a 2019-2023 package, and earlier annual files. Feeding America stated that 2023 county overall and child estimates were revised; any 2023 county analysis must use the corrected archive values and retain the associated revision documentation. Senior and older-adult estimates require a separate method note because Feeding America states that their estimation methods differ from other subpopulations.

### Tract retailer access

The primary local measure is the USDA 2025 SNAP-authorized Retailer Access Map network-distance threshold:

- urban tract: more than 1 driving mile from the nearest SNAP-authorized retailer;
- rural tract: more than 10 driving miles from the nearest SNAP-authorized retailer.

Counts are aggregated to state, project-region, county, and Alabama tract levels. The principal burden measure is the share of low-income residents beyond the threshold. Low-income/low-access tract flags and subgroup access shares are reported separately.

## Subgroups

The SRAM road-network file provides counts for children, seniors, occupied housing units without a vehicle, and occupied housing units receiving SNAP. The pipeline applies the urban 1-mile and rural 10-mile columns consistently. Housing-unit measures are not compared directly to population measures. SNAP-receiving occupied housing units are used as a household-need proxy, not as a count of people.

Any future Feeding America subgroup analysis must preserve that source's own population definitions and denominators rather than assuming they match SRAM subgroup fields.

## Geography

The project-defined Southeast is AL, AR, FL, GA, KY, LA, MS, NC, SC, and TN. Alabama mapping uses 2020 Census cartographic tract boundaries. All tract identifiers are normalized to 11-character text.

## Data repair and validation

The SRAM general-characteristics file imports tract identifiers as numbers and therefore loses leading zeros for states with FIPS codes below 10. The pipeline restores every key with `zfill(11)` before joining. This repair restored 15,636 tract matches, including Alabama and Arkansas. QA confirms 84,119 unique tracts, all 50 states plus the District of Columbia, no duplicate GEOIDs, and full Alabama geometry coverage.

Fifteen national source rows require review: fourteen Suffolk County, New York tracts lack low-income denominators and one zero-population Massachusetts tract lacks the primary LILA flag. Alabama and all ten project states are complete. The provisional national low-income burden excludes the missing low-income denominators.

The Feeding America archive is not promoted into publication outputs until `src/ingest_feeding_america.py` has produced a file inventory, archive/file hashes have been recorded, exact retained variables and denominators have been documented, and the corrected 2023 county records have been identified.

## Sensitivity

The primary road-network result is compared with:

- a stricter 0.5-mile urban / 10-mile rural threshold;
- a 1-mile urban / 20-mile rural threshold.

Straight-line distance is excluded because it does not follow road travel and produced implausibly influential outliers for this study. It is not imported, analyzed, or published.

The final Alabama primary estimate is 20.2% of low-income residents beyond the selected threshold. The stricter urban threshold produces 35.9%, while the 20-mile rural threshold produces 19.6%. The urban threshold materially affects the estimated burden. Final outputs must state the selected road-network threshold and reconcile to the primary value before publication.

## Interpretation boundaries

- Household food insecurity is an economic and experiential outcome; retailer proximity is a physical-access proxy.
- Feeding America Map the Meal Gap provides modeled local food-insecurity estimates; it does not directly measure retailer distance.
- SRAM covers SNAP-authorized retailers and excludes farmers markets and delivery routes from its listed retailer universe.
- Proximity does not measure price, quality, nutrition, inventory, transit, disability access, store hours, or household food insecurity.
- The current data does not measure food abundance or food-supply volume.
- Race and gender are not analyzed in the current scope.
- FAOSTAT population measures should not be numerically compared as if they were USDA household, Feeding America local, or tract-access measures.
- The analysis is descriptive. It does not make causal, medical, or policy-effect claims.

See `docs/limitations.md` for the appendix-ready list of known blind spots and future-work requirements. See `docs/feeding_america_source.md` for Feeding America provenance and intake requirements.

## Official sources

- [FAOSTAT Suite of Food Security Indicators](https://data.fao.org/catalog/dataset/955d6564-40a9-48b4-b51b-f19d65bb3539)
- [USDA ERS Food Security in the United States](https://www.ers.usda.gov/topics/food-nutrition-assistance/food-security-in-the-us/key-statistics-graphics)
- [USDA ERS SRAM download](https://www.ers.usda.gov/data-products/food-access-research-atlas/download-the-data)
- [USDA ERS SRAM reference guide](https://www.ers.usda.gov/data-products/food-access-research-atlas/documentation/snap-authorized-retailer-access-map-reference-guide)
- [USDA ERS SRAM methods](https://www.ers.usda.gov/data-products/food-access-research-atlas/documentation/snap-authorized-retailer-access-map-data-sources-and-technical-methods)
- [U.S. Census Bureau Alabama tract geometry](https://www2.census.gov/geo/tiger/GENZ2020/shp/cb_2020_01_tract_500k.zip)
- [Feeding America Map the Meal Gap 2026](https://www.feedingamerica.org/research/map-the-meal-gap/overall-executive-summary)
- [Feeding America Map the Meal Gap methodology](https://www.feedingamerica.org/research/map-the-meal-gap/how-we-got-the-map-data)
