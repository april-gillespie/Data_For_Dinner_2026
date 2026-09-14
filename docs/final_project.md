# Final project summary

This is a text companion to the [September 13, 2026 final presentation](../presentation/DataForDinnerTeam_WiDDatathon2026_Presentation_Final_13Sept2026.pdf). Page numbers below refer to that PDF. The presentation controls the final project narrative and reported values.

## Focus and audience

Data for Dinner selected the Eat track of the Women in Data 2026 Datathon. The final focus is food insecurity across the globe, the United States, the Southeast, and Alabama. The problem statement connects family wellbeing with limited access, unaffordability, and undernourishment, and calls for community action to improve equitable food and nourishment. See pages 2 and 4.

The intended stakeholders are families, farmers and home growers, farmers markets, local fishers, and policy makers at town, county, state, and federal levels. See page 6.

## Sources and workflow

The presentation identifies FAOSTAT food security indicators for global context and Feeding America for U.S. and Alabama context. Its global dimensions include severe food insecurity, the category labeled moderate food insecurity, undernourishment, and prevalence of unaffordability across Africa, Asia, Europe, Latin America and the Caribbean, Oceania, the United States, and the world. See page 8.

The workflow uses batch downloads, merged datasets, Excel analysis, cleanup when data did not align with aggregations, MapChart geographic visualizations, and a Tableau Public dashboard. GitHub, Google Drive, Google Meet, and Microsoft Teams supported collaboration. See page 9.

The project shifted from an initial emphasis on food access toward food insecurity because local data were not consistently available. The team also deferred analysis of food allergy impacts when the available data lacked the necessary detail. See page 10.

## Findings as presented

The following tables transcribe selected values from the final slides. They are a record of the presentation, not a new calculation or a replacement statistical release. The slides do not consistently specify observation periods and denominators for every displayed value. No missing year or denominator has been inferred from an older report. See [reconciliation notes](source_priority.md).

### Global context

Page 12 presents four dimensions: moderate insecurity, severe insecurity, unaffordability, and undernourishment. It emphasizes unequal distribution and the effect of poverty and other factors.

| Geography | Slide category | Reported value | Page |
| --- | --- | --- | --- |
| Africa | Moderate insecurity | 57.4% | 12 |
| Africa | Severe insecurity | 21.1% | 12 |

The category names above follow the slide. They should not be combined or redefined without checking the underlying indicator definition.

### United States and Southeast

Page 14 introduces the USDA definition of food insecurity as a household economic and social condition of limited or uncertain access to adequate food. Pages 15 and 17 present regional comparisons.

| Comparison | Reported value | Page |
| --- | --- | --- |
| South | 15.5% | 15 |
| Northeast | 11.4% | 15 |
| Midwest, slide body text | 12.3% | 15 |
| West | 12.6% | 15 |
| Southeast | 15.8% | 17 |
| U.S. average shown for the Southeast comparison | 12.9% | 17 |
| Arkansas | 19.4% | 17 |
| Kentucky | 18.8% | 17 |
| Louisiana, Mississippi, Texas, and Oklahoma | 17% as grouped in the slide text | 17 |

The Southeast map on page 17 includes Texas and Oklahoma. The repository follows the geography shown in the final presentation rather than imposing the earlier ten-state analysis definition. The 12.9% comparison is retained as the slide reports it; the supporting workbook calculates its corresponding U.S. summary as an unweighted average of 50 state values and the District of Columbia. It is not documented there as a population-weighted national estimate.

The presentation discusses poverty, rural geography, retailer networks, transportation barriers, demographic vulnerabilities, climate variation affecting crops, and policy gaps as factors relevant to families. These are the factors discussed by the team, not newly estimated causal effects.

### Alabama county comparisons

Page 19 compares low access and low income against total population. Page 20 contains a separate table headed Low-Income Low-Access. Preserve that measure label when citing its ranking.

| Rank | County | Low-income low-access value shown | Page |
| --- | --- | --- | --- |
| 1 | Shelby | 36.70% | 20 |
| 2 | Madison | 35.30% | 20 |
| 3 | Lee | 32.70% | 20 |
| 4 | Macon | 31.10% | 20 |
| 5 | Jefferson | 30.80% | 20 |
| 6 | Montgomery | 25.40% | 20 |
| 7 | Tuscaloosa | 25.10% | 20 |
| 8 | Baldwin | 23.90% | 20 |
| 9 | Calhoun | 21.90% | 20 |
| 10 | Morgan | 21.70% | 20 |

This county table is not a ranking of household or modeled individual food insecurity rates. The final presentation discusses county differences in relation to poverty, rural conditions, transportation, and economic constraints. Its geographic visualizations and driver descriptions are preserved in the original PDF.

## Proposed community action

Page 22 proposes support for local food pantries and shelters, small neighborhood pantries offering shelf-stable staples, community buses serving as fresh-food pantries, and farmers and fishers. The presentation describes these as practical ideas that use existing community resources and can be adapted to rural and urban settings. It does not present measured outcomes from implementing them.

## Future work

Page 24 proposes further research into how food allergy constraints affect affordability, access, and nutrition, with expanded data discovery and attention to Alabama resources and local crops. The food examples in the slide belong to this future research discussion. The team did not complete an analysis of allergy impacts on food insecurity.

## Conclusions

Page 26 emphasizes food insecurity across geographic scales, the vulnerability associated with economic shocks and limited food-system resilience, rural isolation and retail constraints, and the value of layered geographic analysis for identifying practical community action.

The [video home](../video/README.md) is ready for the final recording.

## Sources

These are the source links printed in the final presentation. Their presence records the attribution used by the team; the final packaging work did not rerun the source acquisition or certify every slide calculation against a new data release.

- [FAOSTAT Suite of Food Security Indicators](https://www.fao.org/faostat/en/#data/FS), pages 8 and 12.
- [Feeding America Map the Meal Gap](https://map.feedingamerica.org/), page 8 and U.S./Alabama slide footers.
- [Feeding America U.S. overall population view for 2024](https://map.feedingamerica.org/county/2024/overall/), page 8.
- [Feeding America Alabama overall population view for 2024](https://map.feedingamerica.org/county/2024/overall/alabama), page 8.
- [MapChart](https://www.mapchart.net/usa.html), geographic visualization tool credited on pages 9 and 14 to 20.
- [Final Tableau dashboard](https://public.tableau.com/shared/NX9Y4P32D?%3Adisplay_count=n&%3Aorigin=viz_share_link), destination of the page 27 QR code.
