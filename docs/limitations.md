# Known limitations and blind spots

These limits apply to the current descriptive analysis and should remain in final appendices and presentation notes.

## Construct limits

- Household food insecurity is an economic and experiential outcome. Retailer proximity is a physical-access proxy. They are not interchangeable.
- Proximity does not measure food price, product quality, nutrition, inventory, store hours, disability access, transit service, food banks, delivery, or online purchasing.
- The analysis does not measure household food insecurity at the Alabama tract level. Map the Meal Gap adds modeled individual estimates at county and state levels only.
- The current data does not quantify food abundance or supply volume. It cannot support a claim that an area has abundant food without another validated measure.

## Coverage limits

- The retailer data covers SNAP-authorized retailers. It does not represent every food outlet.
- State household estimates include material margins of error. Small rank differences should not be treated as definitive.
- Fourteen Suffolk County, New York tracts lack low-income denominators, and one zero-population Massachusetts tract lacks the primary tract flag. Alabama and the ten project states are complete.
- Source vintages differ. Retailer locations, population, ACS inputs, household estimates, and map geometry do not all describe the same year.
- Map the Meal Gap county and state estimates use different geographic models. Alabama county counts sum to 883,710 people, while the state estimate is 919,160; the 35,450-person difference is retained and documented rather than forced to reconcile.
- Map the Meal Gap rates are modeled approximations. Race and ethnicity fields were excluded from this active scope, and missing or suppressed subpopulation values should not be interpreted as zero.
- The Feeding America request archive contains no explicit redistribution license. The raw package remains outside GitHub; only selected Alabama extracts, hashes, definitions, and citations are published.

## Scope limits

- Food allergies, race, and gender are excluded from the current analysis.
- Children, adults age 65 or older, no-vehicle occupied housing units, and SNAP-receiving occupied housing units are reported only where the source provides matching denominators.
- Straight-line distance is excluded. Sensitivity analysis varies road-network thresholds only.
- Results are descriptive and do not establish causes, medical effects, or policy effects.

## Future work

- Define and validate a food-supply or resource-availability measure before building the planned abundance-versus-access visualization.
- If a future analysis uses the historical Map the Meal Gap files, apply the documented methodology breaks and the corrected 2023 county estimates before interpreting trends.
- Revisit allergen access only if product-by-store-by-date inventory and price data with defensible geographic coverage becomes available.
