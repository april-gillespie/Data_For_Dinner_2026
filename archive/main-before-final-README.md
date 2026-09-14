# Data for Dinner 2026

Women in Data 2026 Datathon | **What's Cooking?**

## Project Status

**Current phase:** TBD



## Datathon

The 2026 Women in Data datathon challenges teams to use open food-system data to investigate meaningful real-world problems and develop practical, evidence-based solutions.

**Theme:** What's Cooking?  
**Selected track:** Eat  
**Project period:** August–September 2026  
**Final submission:** September 15, 2026

### Evaluation Areas

- Depth of Analysis — 35%
- Practical Application — 30%
- Presentation Quality — 25%
- Originality & Innovation — 10%

## Working Problem Statement


## Working Research Question


## Research Process and Plan Evolution

The project follows an iterative research process rather than treating the initial plan as fixed:

1. Define the question, scope, candidate datasets, and proposed measures.
2. Acquire and inspect the actual source data.
3. Validate identifiers, denominators, completeness, geography, and measurement definitions.
4. Run the proposed analysis and sensitivity checks.
5. Revisit the plan using evidence from implementation.
6. Update definitions, source status, scope, and documentation before the next stage of analysis.

### Guiding principle

**More data is not automatically better.** Sources are retained only when they answer a defined analytical question, have sufficiently clear geography and denominators, and add information not already supplied by the retained dataset stack.

## Data Sources

| Source | Role | Status |
|---|---|---|
| FAOSTAT Suite of Food Security Indicators | Global food-insecurity context | Analyzed |
| FAOSTAT Cost and Affordability of a Healthy Diet | Global affordability context | Analyzed |
| USDA Household Food Security estimates | U.S. and state outcome context | Analyzed |
| USDA 2025 SNAP-authorized Retailer Access Map | Primary Alabama and Southeast physical-access analysis | Analyzed / proposed primary source |
| 2020 Census tract geometry | Alabama tract mapping | Analyzed |
| USDA Food Environment Atlas | Optional county-level gap filling | Deferred unless a specific analytical gap is identified |
| Allergy / gluten exploration | Separate exploratory work | Archived / outside active scope |

## Methodology

The analysis is built around methodological rigor, reproducibility, and explicit interpretation boundaries.

### Source selection

Datasets are evaluated for:

- construct fit to the research question
- geographic coverage and compatible spatial units
- stable join keys
- documented vintage and source provenance
- acceptable completeness
- clear denominators and units
- analytical value beyond already retained sources

### Data preparation and validation

- Preserve frozen raw-data snapshots and source metadata.
- Record source URLs, retrieval dates, vintages, filenames, and checksums where practical.
- Store geographic identifiers such as FIPS and GEOID values as text so leading zeros are preserved.
- Test for duplicate keys, missingness, range violations, denominator inconsistencies, and geographic coverage before analysis.
- Standardize processed data without overwriting the original source files.

### Aggregation and interpretation

- Recalculate county and state rates from summed numerators and denominators rather than averaging tract percentages.
- Preserve margins of error for survey-based state food-insecurity estimates.
- Keep measures with different populations, units, or meanings analytically separate.
- Distinguish **low-income individuals** from **low-income/low-access tracts** because the underlying USDA definitions are not interchangeable.
- Use descriptive language and avoid unsupported causal claims.
- Run sensitivity analyses when methodological choices materially affect the result.

## Current Analysis


## Preliminary Findings

## Scope Boundaries

## Practical Application / Proposed Solution

*TBD after team review of the validated analysis and final problem framing.*

The solution should follow from the evidence rather than being selected before the analysis is complete.

## Deliverables

The repository is structured to preserve both the analysis and the final datathon submission.

- [ ] Core source discovery and evaluation
- [ ] Initial data acquisition and validation
- [ ] Alabama pilot and tract-key validation
- [ ] Initial state and Alabama analysis
- [ ] Sensitivity checks
- [ ] Initial figures and maps
- [ ] Final team-approved problem statement and scope
- [ ] Final analysis notebook(s) / reproducible pipeline
- [ ] Final figures / visualizations
- [ ] IEEE-style paper
- [ ] Final presentation / slide deck
- [ ] Project recording / presentation video
- [ ] Final project documentation and repository review

## Repository Structure

```text
Data_For_Dinner_2026/
├── README.md
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
├── src/
├── figures/
├── presentation/
├── docs/
└── results/
```

Folders will be populated as project artifacts are finalized.

## Project Timeline

### Week 1 — Explore, Define, and Validate

### Week 2 — Refine and Analyze

### Week 3 — Develop and Validate

### Week 4 — Finalize and Present

## Limitations


## Final Presentation

*TBD*

## Recording

*TBD*

## Conclusions

*TBD after final team review and completion of the analysis.*
