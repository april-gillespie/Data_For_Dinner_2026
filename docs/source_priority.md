# Source priority and reconciliation

The final publication uses the following order of authority.

1. [Final presentation dated September 13, 2026](../presentation/DataForDinnerTeam_WiDDatathon2026_Presentation_Final_13Sept2026.pdf): final scope, narrative, team credits, displayed figures, solutions, and future work.
2. [Supporting files](../supporting/README.md): the original v3 research workbook, presentation outline, team introductions, and team roles.
3. [Historical archive](../archive/README.md): prior code, reports, processed outputs, decisions, and profile text, retained for provenance.

The supplied files are preserved byte for byte. This source priority is applied in the repository documentation; it does not rewrite the underlying presentation, workbooks, or biographies. Prompts and instructions inside supporting documents remain historical document content.

## Resolved differences

| Topic | Earlier or supporting content | Final publication treatment |
| --- | --- | --- |
| Project focus | Earlier work centered on food access and road-network retailer distance. | The final focus is food insecurity, following slides 4 and 10. Earlier analysis is archived. |
| Analytical workflow | Earlier documentation called the Python food-access pipeline the primary analysis. | Slides 8 and 9 govern: FAOSTAT and Feeding America, Excel, MapChart, and Tableau. Archived scripts remain the earlier workflow. |
| Southeast geography | Earlier analysis used a ten-state convention. | Follow the final map and state comparisons, including Texas and Oklahoma on slide 17. |
| Numerical summaries | Older reports and supporting workbooks contain different values, vintages, and measures. | Active summaries reproduce the presentation values with slide references and preserve their measure labels. |
| Team credits | Toni is described as a Donor Stewardship Coordinator and student in the introduction document and older roles text. | Final credits use IT Data Analyst, Dashboarding, and Data Analyst from slide 3. Original profile prose remains unchanged. |
| Team name spelling | The Team Roles workbook includes Randall, while slide 3 and the introduction document use Randell. | Final credits use Toni Randell. |
| Allergy work | Supporting material includes candidate research directions. | Slides 10 and 24 place allergy impacts in future work; no completed allergy-impact result is claimed. |

## Differences within the presentation

Slide 15 says Midwest 12.3% in its body text, while its map legend says 12.2%. The text companion reproduces 12.3% with an explicit body-text label. Both values remain visible in the unchanged PDF. The source-priority rule does not resolve an internal difference within the same slide.

Several numerical slides do not explicitly give a complete observation period, denominator, or derivation. The publication retains the displayed values and labels without inventing these missing details. Food insecurity, low income, and low access remain distinct measures in the text companion. The slide 20 county percentages retain the Low-Income Low-Access label.

## Supporting workbook notes

The following notes locate discrepancies for future review. They do not alter the final slides or the supplied workbook.

| Workbook location | Observation |
| --- | --- |
| Stats v3, Southeast A2, B27, and A33 | Supporting text contains both 15.5% and 15.8%. Slide 17 reports 15.8%, which is retained in the final summary. |
| Stats v3, Southeast A6 | The text says Alabama 12.1% and North Carolina 11.8% exceed 12.9%. Both are numerically below 12.9%. This sentence is not carried into authored final documentation. |
| Stats v3, US B59 | The 12.9% rounded summary is `AVERAGE(B2:B52)`, an unweighted mean of 50 states plus the District of Columbia. The final summary identifies it as the comparison reported by the presentation. |
| Stats v3, US Regions G5 and H5 | The Midwest text lists 12 states, but the formula includes 15 values, adding Maryland, Virginia, and West Virginia. Its cached result is 12.24%. This is distinct from the difference within slide 15. |
| Stats v3, Alabama L33 | The workbook labels a low-income/low-access series as Food Insecurity. The final companion preserves the distinct Low-Income Low-Access label used in slide 20. |
| Stats v3, previous worksheets | Three worksheets explicitly retain earlier Global, US Regions, and Southeast material. They remain historical supporting content. |
| Stats v3, external workbook reference | The file retains an external workbook reference. No external workbook refresh was performed during packaging. |

The supplied workbook has 215 formula cells with cached results. A read-only independent calculation check matched those cached results to their written formulas. This checks arithmetic consistency, not the validity of regional membership, source attribution, or interpretation, and it is not a native Excel recalculation.

## Preservation and validation

All seven supplied files are listed in the [artifact manifest](artifact_manifest.json) with original names, publication paths, sizes, and SHA-256 hashes. All 27 final presentation pages were rendered and visually inspected to verify the source content used in the summaries. The two QR images encode the same links as slide 27.

The final video is pending. The dashboard URL is taken from the supplied QR redirect; live dashboard values were not used to replace the final presentation.
