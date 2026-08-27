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
- Keep roles in supporting material at the bottom of the main project documentation.
- Target final recording and submission for the weekend ending September 13, 2026.
- Prioritize a visual story that contrasts available food resources with actual access, but do not label a measure as food abundance until its definition and data source are approved.

## Feeding America data update

The previously deferred Feeding America item now has direct provenance. Sandra Kopecky obtained the official Map the Meal Gap archive from the Feeding America Research Team on August 25, 2026. Feeding America stated that the archive contains 2024 data for the 2026 release, a package covering 2019-2023, and earlier annual files. They also stated that 2023 county overall and child estimates were revised and corrected in the supplied archive.

The source is therefore accepted into project intake and registered in the source manifest. It is not yet promoted into publication outputs because the emailed Qualtrics ZIP must still be locally downloaded, hashed, extracted, inventoried, and mapped to exact variables and denominators. `src/ingest_feeding_america.py` provides that intake workflow, and `docs/feeding_america_source.md` records the provenance and interpretation rules.

Before publication use, confirm:

1. exact file names and schemas inside the supplied archive;
2. which fields correspond to overall, child, senior/older-adult, income, race/ethnicity, meal-cost, and food-budget-shortfall measures;
3. the population universe and denominator for every retained field;
4. geographic grain and identifier format;
5. permitted use and redistribution terms in the supplied documentation;
6. use of the corrected 2023 county overall and child values rather than superseded copies;
7. comparability boundaries with USDA household and retailer-access measures; and
8. reconciliation of Alabama and selected county values against Feeding America's published outputs.

## Validation checkpoint

The primary Alabama retailer-access result remains 20.2% of low-income residents beyond the 1-mile urban and 10-mile rural road-network threshold. The alternate road-network estimates are 35.9% under the 0.5-mile urban threshold and 19.6% under the 20-mile rural threshold. Feeding America food-insecurity estimates are a separate outcome layer and must not be substituted for or blended into this retailer-access metric.
