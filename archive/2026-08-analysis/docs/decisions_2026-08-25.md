# Decisions from August 25, 2026

This record captures the meeting decisions that affect the published repository. It does not reproduce every discussion item or logistical action.

## Approved analytical decisions

- Keep food security and food access as distinct concepts.
- Use USDA road-network distance as the local physical-access measure: more than 1 mile for urban tracts and more than 10 miles for rural tracts.
- Retain the official USDA low-access tract rule of at least 500 people or 33 percent of the tract population beyond the selected threshold. The 30 percent wording in the meeting notes is treated as shorthand, not as the published definition. See the [USDA ERS SRAM reference guide](https://www.ers.usda.gov/data-products/food-access-research-atlas/documentation/snap-authorized-retailer-access-map-reference-guide).
- Exclude straight-line distance from the analysis, results, workbook, and report.
- Test sensitivity with alternate road-network thresholds only.
- Exclude allergen-specific analysis from the active scope while documenting that exploratory allergen work is available for a future feasibility study.
- Exclude race and gender demographic analysis from the current scope.
- Treat SNAP-receiving occupied housing units as a household-need proxy, with the matching housing-unit denominator.
- Preserve tract and ZIP-like geographic identifiers as text so leading zeros are not lost.
- Place limitations and blind spots in supporting documentation and report appendices.

## Repository and delivery decisions

- Publish only finalized, reviewed files.
- Target final recording and submission for the weekend ending September 13, 2026.
- Prioritize a visual story that contrasts available food resources with actual access, but do not label a measure as food abundance until its definition and data source are approved.

## Feeding America data decision, completed August 29

The Feeding America Map the Meal Gap 2026 request package is now validated and integrated as a separate Alabama county and state outcome layer. The 2024 label is the observation year. Values are modeled estimates for individuals, children, seniors, and older adults, plus localized food-cost measures. They are not household survey rates and are not tract retailer-access measures.

The completed gate records:

1. Feeding America as publisher, its official data request page, and the received archive hash;
2. observation year 2024 and file update date July 28, 2026;
3. modeled individual counts and rates, with the appropriate population denominator for each field;
4. county and state geographic grains, with five-digit county FIPS identifiers stored as text;
5. a raw-package access note: the archive contains no explicit redistribution license, so it is not committed;
6. separate interpretation from USDA household food insecurity and USDA retailer proximity;
7. all 67 Alabama county rows, unique FIPS values, valid rate ranges, and one Alabama state row; and
8. the documented 35,450-person difference between the state estimate and the sum of county estimates. Feeding America states that state estimates aggregate congressional-district results, so equality is not expected.

## Validation checkpoint

The primary Alabama result remains 20.2% of low-income residents beyond the 1-mile urban and 10-mile rural road-network threshold. The alternate road-network estimates are 35.9% under the 0.5-mile urban threshold and 19.6% under the 20-mile rural threshold. Final deliverables must use the same primary value and state the threshold.

## Team story workbook decision, August 29

Sandra Kopecky's `WomenInData Data Stats and Summary - Story.xlsx` is accepted as the prevailing team story workbook and presentation-development source. Sandra receives explicit credit in the repository, report, charter, project roles, source manifest, and analysis workbook guide.

The file is preserved unchanged so its authorship and original structure remain intact. Its global, U.S., Southeast, Alabama county, and Alabama regional sections guide the evolving story. Exact published values still reconcile to the validated repository tables. Driver labels, causal language, static county rankings, and regional summaries remain exploratory until their calculations and direct sources are documented.
