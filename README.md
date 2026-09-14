# Data for Dinner 2026

Women in Data Datathon 2026. Track: Eat. Final presentation: September 13, 2026.

<p align="center">
  <img src="assets/women-in-data-logo.png" alt="Women in Data" width="520">
</p>

Data for Dinner explores food insecurity from the globe to the United States, the Southeast, and Alabama. The project connects regional food insecurity patterns with the challenges families face in obtaining affordable, nourishing food, and proposes practical actions for local communities.

## Project links

| Resource | Open |
| --- | --- |
| Final presentation, 27 slides | [Read the presentation](presentation/DataForDinnerTeam_WiDDatathon2026_Presentation_Final_13Sept2026.pdf) |
| Tableau Public dashboard | [Explore the dashboard](https://public.tableau.com/shared/NX9Y4P32D?%3Adisplay_count=n&%3Aorigin=viz_share_link) |
| Final video | [Video home](video/README.md), recording pending |
| Supporting files | [Research workbook and presentation outline](supporting/README.md) |

The final presentation is the source of truth for this project. It takes precedence over supporting workbooks and earlier documentation when they differ. See [source priority and reconciliation](docs/source_priority.md).

## The problem

Food insecurity impact families & diminishes quality of life. Families face an uneven menu of limited access, unaffordability, and undernourishment. We need community-driven solutions that deliver equitable food and nourishment for all.

The final project focuses on local communities and policy makers: families, farmers and home growers, farmers markets, fishers, and town, county, state, and federal government. See presentation slides 4 and 6.

## How we approached it

The team used FAOSTAT food security indicators for global context and Feeding America for U.S. and Alabama context. The presentation describes batch downloads, merged datasets, Excel analysis, cleanup of aggregation differences, MapChart visualizations, and a Tableau Public dashboard. Collaboration used GitHub, Google Drive, Google Meet, and Microsoft Teams. See slides 8 and 9.

**Scope note:** During the project, we narrowed our focus from food access to food insecurity as local data limitations became clearer.

## Key findings

| Topic | Presentation result | Slide |
| --- | --- | --- |
| Global context | Africa is reported at **57.4%** for the chart category labeled moderate insecurity and 21.1% for severe insecurity. | 12 |
| U.S. regions | The South is reported at **15.5%**, compared with the Northeast at 11.4%, Midwest at 12.3% in the slide text, and West at 12.6%. | 15 |
| Southeast | The presentation reports **15.8%** compared with a U.S. average of 12.9%. | 17 |
| Alabama | County comparisons show disparities in low access and low income. The separate low-income/low-access ranking begins with Shelby at **36.70%**, Madison at **35.30%**, and Lee at **32.70%**. | 19 and 20 |

These are the values and labels reported in the final presentation. Their measure definitions and source differences are recorded in the [final project summary](docs/final_project.md) and [reconciliation notes](docs/source_priority.md). The county low-income/low-access ranking is a different measure from a food insecurity rate.

## Community solutions and future work

The team proposes support for food pantries and shelters, small neighborhood pantries for shelf-stable staples, community buses serving as fresh-food pantries, and local farmers and fishers. These are proposed interventions from slide 22.

Future work would investigate how food allergy constraints affect affordability, access, and nutrition, with expanded data discovery and research relevant to Alabama resources. The final project does not report a completed analysis of allergy impacts. See slide 24.

## Team

The following credits reproduce slide 3 of the final presentation.

| Team member | Background shown | Project roles shown |
| --- | --- | --- |
| Sharon Brooks | Data Governance Analyst | Team Lead; Project Manager |
| April Gillespie | Technical Marketing Engineer | Researcher; Data Scientist; GitHub Manager |
| Sandra Kopecky | IT Specialist | Data Discovery; Data Analyst; Insights Manager |
| Toni Randell | IT Data Analyst | Dashboarding; Data Analyst |

## Repository guide

```text
presentation/   final PDF and slide guide
video/          final recording home
supporting/     research and presentation-planning files
assets/         Women in Data logo and supplied QR images
docs/          final summary, source priority, and artifact manifest
tools/         final package verification
archive/       preserved earlier analysis and repository documentation
```

The [archive](archive/README.md) preserves earlier analysis, code, data, and figures for provenance.

Source links are collected in the [final project summary](docs/final_project.md#sources). The [artifact manifest](docs/artifact_manifest.json) records the five supplied files retained in the published package and their SHA-256 hashes. See the [validation record](docs/validation.md) for checks and remaining limitations.

## For technical reviewers

To check the supplied file hashes and repository links after cloning, run:

```sh
python tools/verify_final_package.py
```
