# Data For Dinner Team 2026

This project is a submission of the 2026 Women in Data (WiD) What's Cooking Datathon. Data For Dinner explores food insecurity from the globe to the United States, the Southeast, and Alabama. The project connects regional food insecurity patterns with the challenges families face in obtaining affordable, nourishing food, and proposes practical actions for local communities.

<p align="center">
  <img src="assets/women-in-data-logo.png" alt="Women in Data" width="220">
</p>

**Track:** Eat  
**Final presentation:** September 13, 2026

## Project links

| Resource | Open |
| --- | --- |
| Data for Dinner Team WiD Datathon 2026 Video Submission | [Download the recording](https://github.com/april-gillespie/Data_For_Dinner_2026/raw/refs/heads/main/video/Data_for_Dinner_2026.mp4) |
| Presentation | [Review the presentation](presentation/DataForDinnerTeam_WiDDatathon2026_Presentation_Final_13Sept2026.pdf) |
| Tableau Public dashboard | [Explore the dashboard](https://public.tableau.com/shared/NX9Y4P32D?%3Adisplay_count=n&%3Aorigin=viz_share_link) |
| Research workbook | [Download the Excel workbook](data/WomenInData_Data_Stats_and_Summary_v3.xlsx) |
| Video guide and captions | [Recording details, original captions, and transcript](video/README.md) |

[![Data For Dinner presentation video](assets/video-poster.jpg)](https://github.com/april-gillespie/Data_For_Dinner_2026/raw/refs/heads/main/video/Data_for_Dinner_2026.mp4)

## The problem

The United States Department of Agriculture (USDA) defines food insecurity as a household-level economic and social condition of limited or uncertain access to adequate food. Food-secure households have consistent access throughout the year to adequate food for active, healthy living for all household members. Food-insecure households lack that access at some time during the year.

Food insecurity impacts families and diminishes quality of life. Families face an uneven menu of limited access, unaffordability, and undernourishment. We need community-driven solutions that deliver equitable food and nourishment for all.

The stakeholders are  local communities and policy makers: families, farmers and home growers, farmers markets, fishers, and town, county, state, and federal government.

![United States food insecurity definition and map](assets/slide-14-us-food-insecurity.png)

## How we approached it

The team used datasets from FAOSTAT and Feeding America for food security indicators for global context and Feeding America for U.S. and Alabama context. The presentation describes batch downloads, merged datasets, Excel analysis, cleanup of aggregation differences, MapChart visualizations, and a Tableau Public dashboard. Collaboration used GitHub, Google Drive, Google Meet, and Microsoft Teams.

**Scope note:** During the project, we shifted our focus from food access to food insecurity due to local data limitations.

## Key findings

The figures below follow the final presentation. See the [review notes](docs/review.md#data-and-presentation-notes) for differences between the slides, workbook, and dashboard, including measure definitions and the U.S. comparison average.

### Global context

- Globally, millions experience moderate and severe food insecurity due to poverty and various other factors.
- The global charts compare percentages across regions; they do not establish which regions have the largest numbers of affected people.
- Slide 12 reports Africa at **57.4%** for the category labeled moderate insecurity and **21.1%** for severe insecurity.
- Despite global baselines, the distribution of food remains uneven, leaving entire populations without food and nourishment.

![Global food insecurity, affordability, and nourishment charts](assets/slide-12-global-food-insecurity.png)

### United States

- Regional differences create pockets of heightened vulnerability.
- Slide 15 reports the South at **15.5%**, compared with the Northeast at 11.4%, the Midwest at 12.3% in the slide text, and the West at 12.6%. The Midwest map legend shows 12.2%, while the live dashboard shows 12.1%. See the [review notes](docs/review.md#data-and-presentation-notes).

![United States food insecurity by region](assets/slide-15-us-food-insecurity-by-region.png)

### Southeast

- Regional differences create pockets of heightened vulnerability.
- Slide 17 reports Southeast food insecurity at **15.8%**, compared with **12.9%** for the U.S. comparison. The workbook calculates 12.9% as an unweighted average of 50 states plus the District of Columbia, rather than a population-weighted national estimate.

![US Southeast food insecurity](assets/slide-17-southeast-food-insecurity.png)

### Alabama

Alabama faces significant disparities in low access and low income, with some counties experiencing extreme levels of both.

The county ranking below uses the slide label **Low-Income Low-Access**. It is a different measure from a food insecurity rate.

![Alabama highest counties for low income and low access](assets/slide-20-alabama-highest-counties.png)

## Community solutions

The team proposes practical community actions that use existing infrastructure. Their costs and outcomes were not evaluated in this project:

- Support local food pantries
- Support local shelters
- Establish small neighborhood pantries for shelf-stable staples, similar to little libraries
- Use small community buses as fresh-food pantries
- Support local farmers and fishers

## Future work

Food allergy impact analysis for food insecurity requires:

- Continued research
- Expanded data discovery
- Deeper insights into:
  - Affordability
  - Access
  - Nutrition

Alabama food resources to consider include:

- Seafood
  - Shellfish allergy
- Crops
  - Peanuts, ranking third in the nation
  - Sweet potatoes
  - Soybeans
  - Corn
  - Pecans
  - Wheat

Future analysis should consider food allergy constraints and local crop availability. The project does not report a completed analysis of allergy impacts.

## Key takeaways

- Food insecurity is a multi-scale systems challenge that becomes clearer when analyzed through integrated, data-driven geospatial methods.
- Structural instability, economic shocks, and limited food-system resilience create widespread vulnerability.
- Rural isolation and limited food-retail infrastructure intensify insecurity.
- Findings highlight the value of layered geospatial analysis for identifying actionable intervention points and support a practical framework of low-cost, scalable solutions.

## Team

<img width="755" height="413" alt="Data For Dinner team" src="https://github.com/user-attachments/assets/942d08a9-e598-4a4b-9eda-b804b2a06966" />

| Team member | Professional Role | Project roles shown |
| --- | --- | --- |
| Sharon Brooks | [Data Governance Analyst](https://www.linkedin.com/in/sharonbrooks1618) | Team Lead; Project Manager |
| April Gillespie | [Technical Marketing Engineer](https://www.linkedin.com/in/april-ee) | Researcher; Data Scientist; GitHub Manager |
| Sandra Kopecky | [IT Specialist](https://www.linkedin.com/in/sandrakopecky) | Data Discovery; Data Analyst; Insights Manager |
| Toni Randell | [IT Data Analyst](https://www.linkedin.com/in/tonitheanalyst) | Dashboarding; Data Analyst; Video Editor |

## Sources and review

- [FAOSTAT Suite of Food Security Indicators](https://www.fao.org/faostat/en/#data/FS), cited in slides 8 and 12.
- [Feeding America Map the Meal Gap](https://map.feedingamerica.org/), cited in the U.S. and Alabama slides.
- [MapChart](https://www.mapchart.net/usa.html), used for the geographic visuals.
- [Publication review](docs/review.md), covering the video cleanup, file checks, and remaining data differences.

To verify the published media, file hashes, captions, and local links, run `python tools/verify_publication.py` after cloning the repository.
