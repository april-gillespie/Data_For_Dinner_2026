# Recommended next crawl: food-allergy feasibility

## Recommendation

Run a separate feasibility crawl before adding allergies to the food-access analysis. No single public official source identified in this review directly links diagnosed allergy prevalence, household food insecurity, retail product availability and price, and tract geography. Combining the available sources immediately would imply joins and comparability that the data do not support.

## Proposed source sequence

1. **Standardize scope with the FDA's nine major allergens.** Use milk, egg, fish, crustacean shellfish, tree nuts, peanuts, wheat, soybeans, and sesame as the primary taxonomy. Preserve fruit and chocolate only as explicitly defined exploratory categories; they are not part of the FDA nine-major-allergen list.
2. **Measure diagnosed prevalence with the 2024 National Health Interview Survey.** The CDC/NCHS 2024 public-use files support national adult and child estimates and selected demographic or urbanization comparisons. Public-use geography does not support a reliable tract-level Alabama join.
3. **Test product-label extraction with USDA FoodData Central branded foods.** Ingredients, brand owner, category, and GTIN/UPC can support a labeled-product inventory. Allergen status would require a validated parsing rule for ingredient and “Contains” text; the database is not a local store inventory or price source.
4. **Use openFDA food-enforcement data only for recall events.** Search recall reasons for undeclared allergens and retain event date, status, distribution pattern, and state when available. Recall events do not estimate allergy prevalence or product availability.
5. **Gate local availability and price.** Do not claim “allergen-safe food access” until a retailer source supplies store-level inventory, price, product identifiers, dates, and coverage for Alabama or the project region. Document licensing and API limits before collection.

## Feasibility decision

Proceed to an allergy-access analysis only if the team can obtain a product-by-store-by-date inventory with price and a defensible mapping from products to the FDA taxonomy. Otherwise, present prevalence, product-label coverage, and recalls as separate descriptive modules or keep allergies as future work.

## Official starting points

- [FDA food allergies](https://www.fda.gov/food/nutrition-food-labeling-and-critical-foods/food-allergies)
- [FDA sesame as the ninth major allergen](https://www.fda.gov/food/food-allergies/faster-act-sesame-ninth-major-food-allergen)
- [CDC/NCHS 2024 adult food-allergy estimates](https://www.cdc.gov/nchs/products/databriefs/db545.htm)
- [CDC/NCHS 2024 child food-allergy estimates](https://www.cdc.gov/nchs/products/databriefs/db546.htm)
- [CDC/NCHS 2024 NHIS files and documentation](https://www.cdc.gov/nchs/nhis/documentation/2024-nhis.html)
- [USDA FoodData Central data dictionary](https://fdc.nal.usda.gov/portal-data/external/dataDictionary)
- [openFDA food-enforcement API](https://open.fda.gov/apis/food/enforcement/)

## Reusable crawl prompt

> Conduct an official-source-only feasibility crawl for food-allergy access in Alabama and the project-defined Southeast (AL, AR, FL, GA, KY, LA, MS, NC, SC, TN). Keep this separate from the current food-access analysis until joinability is proven. Use the FDA nine major allergens—milk, egg, fish, crustacean shellfish, tree nuts, peanuts, wheat, soybeans, and sesame—as the primary taxonomy. Treat fruit and chocolate only as explicitly defined exploratory categories. For each candidate dataset, record publisher, exact dataset and table, URL/API endpoint, release and observation dates, population or product universe, geography, unit of analysis, allergen fields, price/inventory fields, identifiers, access/licensing limits, update frequency, missingness, and proposed joins. Prioritize CDC/NCHS 2024 NHIS for diagnosed prevalence, USDA FoodData Central branded foods for a pilot of ingredient/Contains-text classification, and openFDA food-enforcement data for undeclared-allergen recall events. Do not treat recalls as prevalence or FoodData Central as store inventory. Do not make causal or medical claims and do not collect personal health information. Sanity-check denominators, duplicate records, changing labels, geography, dates, and taxonomy. Deliver (1) a source inventory, (2) a field-level data dictionary, (3) small reproducible pilot extracts, (4) QA findings, (5) a joinability matrix, and (6) a proceed/pause recommendation. Proceed to local allergen-safe access only if a product-by-store-by-date source with price and defensible coverage is available; otherwise recommend separate descriptive modules and identify the exact missing data.

