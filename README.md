# Data for Dinner 2026

Women in Data 2026 Datathon | **What's Cooking?**

## Project Status

**Current phase:** Validated core analysis and scope refinement

Initial exploration has progressed into a defined food-access analysis centered on Alabama. Core datasets have been acquired and validated, the first analysis and sensitivity checks are complete, and the team is reviewing the resulting scope, definitions, and methodological decisions before proceeding to final analysis and presentation development.

This repository preserves both the analytical work and the decisions that shaped it. The project plan is treated as a working research document: assumptions and proposed methods are tested against the actual data, then revised when implementation reveals a better definition, limitation, or analytical boundary.

## Team

### Sharon Brooks — Team Lead / Project Manager
**Background:** Senior Data Governance Business Analyst  
**Contributions:**
- Team leadership and project management
- Dashboarding
- Data analysis using Excel and SQL
- Presentation and slide deck development

### Sandra Kopecky — Data / Database Analysis
**Background:** IT Specialist / Product Owner and adjunct professor. Career experience includes programming, analysis, database programming, and database administration.  
**Contributions:**
- SQL and database expertise
- Python
- Data analysis
- Academic and technical perspective

### April Gillespie — Data Analysis / Technical Development
**Background:** Customer Technical Advocate / Technical Marketing Engineer with an electrical engineering background.  
**Contributions:**
- Data discovery, source evaluation, and dataset sufficiency assessment
- Python, SQL/SQLite, and DuckDB
- Data cleaning, normalization, validation, and reproducible processing
- Data provenance and quality-assurance workflows
- Analytical interpretation and methodological review
- Translating findings into practical, evidence-based recommendations

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

Food insecurity is broader than physical proximity to food retailers. This project uses official food-insecurity estimates for context while examining geographic and transportation-related retailer access as a measurable local dimension of food access in Alabama.

The analysis deliberately keeps unlike measures separate. Population-level FAOSTAT indicators, household food-insecurity estimates, and census-tract retailer-access measures describe different constructs and are not combined into a single score.

## Working Research Question

**Which Alabama census tracts have the greatest combined burden of low income and limited access to SNAP-authorized food retailers, and how does Alabama compare with the selected Southeast states and the United States?**

This remains a working question until final team approval.

## Research Process and Plan Evolution

The project follows an iterative research process rather than treating the initial plan as fixed:

1. Define the question, scope, candidate datasets, and proposed measures.
2. Acquire and inspect the actual source data.
3. Validate identifiers, denominators, completeness, geography, and measurement definitions.
4. Run the proposed analysis and sensitivity checks.
5. Revisit the plan using evidence from implementation.
6. Update definitions, source status, scope, and documentation before the next stage of analysis.

The first data pull confirmed that USDA's 2025 SNAP-authorized Retailer Access Map can support the Alabama and Southeast physical-access analysis. It also exposed distinctions that needed to be made explicit, including the difference between household food insecurity, low-income individual access measures, and low-income/low-access tract classifications.

The project documentation was updated after the initial analysis so that the written plan reflects what the data actually support rather than preserving assumptions that were only provisional at the planning stage.

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

The core analysis currently moves from broad context to increasingly local detail:

1. Global food-insecurity and healthy-diet affordability context from FAOSTAT.
2. U.S. household food-security context from USDA.
3. Comparison across a project-defined Southeast region: Alabama, Arkansas, Florida, Georgia, Kentucky, Louisiana, Mississippi, North Carolina, South Carolina, and Tennessee.
4. Alabama census-tract retailer-access analysis using the USDA 2025 SNAP-authorized Retailer Access Map.
5. Alabama county and tract detail.
6. Selected subgroup access measures, including children, older adults, no-vehicle occupied units, and SNAP-receiving occupied units.
7. Sensitivity testing of distance definitions and measurement choices.

## Preliminary Findings

These findings are descriptive and remain subject to team review and final source reconciliation.

- Alabama's 2022–2024 household food-insecurity estimate is **12.1% ± 2.23 percentage points**.
- **20.2% of Alabama's low-income population** is beyond the primary 1-mile urban / 10-mile rural driving-distance threshold to a SNAP-authorized retailer.
- **151 Alabama census tracts, or 10.5%,** are flagged low-income/low-access under the selected USDA tract definition.
- The distance method materially affects the result: Alabama's low-income burden is **20.2% using driving distance** versus **8.6% using straight-line distance**.
- Household food-insecurity rankings and retailer-access rankings do not move together consistently, reinforcing that the measures capture different dimensions of the broader food-access problem.

## Scope Boundaries

The current project does **not** treat retailer proximity as a complete measure of food access.

The primary retailer-access dataset does not directly measure:

- food price or affordability
- product quality or nutritional quality
- store inventory or hours
- public-transit access
- disability or individual mobility constraints
- food-bank access
- online purchasing or delivery
- household food insecurity itself

Food allergies and pesticide analysis are outside the active scope. Existing exploratory work is preserved separately rather than being forced into the current analysis without a defensible data connection.

## Practical Application / Proposed Solution

*TBD after team review of the validated analysis and final problem framing.*

The solution should follow from the evidence rather than being selected before the analysis is complete.

## Deliverables

The repository is structured to preserve both the analysis and the final datathon submission.

- [x] Core source discovery and evaluation
- [x] Initial data acquisition and validation
- [x] Alabama pilot and tract-key validation
- [x] Initial state and Alabama analysis
- [x] Sensitivity checks
- [x] Initial figures and maps
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
- Explore FAOSTAT and relevant official datasets
- Select the Eat track
- Identify candidate questions
- Define an initial problem statement and data plan
- Test the plan against the actual source data
- Validate the core Alabama retailer-access dataset
- Revise documentation based on findings from implementation

### Week 2 — Refine and Analyze
- Finalize team-approved scope and research question
- Freeze the retained dataset stack
- Complete reproducible analysis and QA
- Refine Alabama and Southeast comparisons
- Select the findings that materially contribute to the final story

### Week 3 — Develop and Validate
- Develop the practical application or proposed solution from the evidence
- Finalize visualizations
- Reconcile figures, source notes, methods, and written findings
- Draft and review the paper and presentation narrative

### Week 4 — Finalize and Present
- Finalize analysis and proposed solution
- Complete presentation materials
- Rehearse the seven-minute narrative
- Record the presentation video
- Complete final source and repository review
- Prepare final submission

## Limitations

- The analysis is descriptive and does not establish causal relationships.
- Data sources use different observation periods and should not be interpreted as a synchronized time series.
- Household food insecurity, population-level indicators, and tract-level retailer proximity use different units and populations.
- The SNAP-authorized retailer universe includes multiple retailer types and should not be described as equivalent to healthy grocery access.
- Geographic proximity is only one dimension of food access.
- National retailer-access estimates contain a small number of missing low-income denominators outside the project region; Alabama and the selected Southeast states are complete for the primary fields used here.

## Final Presentation

*TBD*

## Recording

*TBD*

## Conclusions

*TBD after final team review and completion of the analysis.*
