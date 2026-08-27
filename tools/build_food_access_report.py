from __future__ import annotations

import csv
import json
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from PIL import Image

import create_project_charter as base


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reports" / "Data_for_Dinner_Food_Access_Analysis.docx"
REPORT_ASSETS = ROOT / "reports" / ".assets"

NAVY = "12304F"
BLUE = "3A7EBB"
PALE_BLUE = "E9F2FA"
GREEN = "4C7A5B"
PALE_GREEN = "EAF3EC"
AMBER = "D89A2B"
PALE_AMBER = "FFF3D8"
RED = "A94B45"
PALE_RED = "F8E8E6"
INK = "172B44"
MUTED = "68778D"
LINE = "D5DFE9"
WHITE = "FFFFFF"


def read_csv(relative_path: str) -> list[dict[str, str]]:
    with (ROOT / relative_path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def pct(value: float | str, digits: int = 1) -> str:
    return f"{float(value):.{digits}f}%"


def num(value: float | str) -> str:
    return f"{float(value):,.0f}"


def set_repeat_table_header(row):
    base.set_repeat_table_header(row)


def add_rule(paragraph, color=LINE, size=8):
    p_pr = paragraph._p.get_or_add_pPr()
    p_bdr = p_pr.find(qn("w:pBdr"))
    if p_bdr is None:
        p_bdr = OxmlElement("w:pBdr")
        p_pr.append(p_bdr)
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), str(size))
    bottom.set(qn("w:space"), "5")
    bottom.set(qn("w:color"), color)
    p_bdr.append(bottom)


def report_image(relative_path: str) -> Path:
    source = ROOT / relative_path
    REPORT_ASSETS.mkdir(parents=True, exist_ok=True)
    target = REPORT_ASSETS / source.name
    image = Image.open(source).convert("RGB")
    if source.name == "alabama_tract_food_access_map.png":
        image.thumbnail((800, 1000), Image.Resampling.LANCZOS)
        colors = 64
    else:
        image.thumbnail((1000, 1200), Image.Resampling.LANCZOS)
        colors = 96
    image.convert("P", palette=Image.Palette.ADAPTIVE, colors=colors).save(target, optimize=True)
    return target


def add_picture(doc: Document, relative_path: str, alt_text: str, caption: str, width=6.45):
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.space_before = Pt(4)
    paragraph.paragraph_format.space_after = Pt(3)
    shape = paragraph.add_run().add_picture(str(report_image(relative_path)), width=Inches(width))
    doc_pr = shape._inline.docPr
    doc_pr.set("descr", alt_text)
    doc_pr.set("title", caption.split(".", 1)[0])
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.space_after = Pt(8)
    run = cap.add_run(caption)
    base.set_font(run, size=9, color=MUTED, italic=True)
    return shape


def add_fact_list(doc: Document, items: list[str]):
    for item in items:
        p = base.add_list_item(doc, item)
        p.paragraph_format.space_after = Pt(4)


def add_section_intro(doc: Document, text: str):
    p = base.add_body(doc, text, after=8)
    p.paragraph_format.keep_with_next = True
    return p


def add_small_note(doc: Document, text: str):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(7)
    r = p.add_run(text)
    base.set_font(r, size=8.5, color=MUTED, italic=True)
    return p


def add_prompt_box(doc: Document, text: str):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = base.WD_TABLE_ALIGNMENT.LEFT
    table.autofit = False
    cell = table.cell(0, 0)
    base.set_cell_shading(cell, "F4F7FA")
    base.set_cell_margins(cell, top=180, start=220, bottom=180, end=220)
    cell.width = Inches(6.5)
    cell.text = ""
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.05
    r = p.add_run(text)
    base.set_font(r, name="Aptos", size=9.2, color=INK)
    base.set_table_borders(table, color=BLUE, size=9)
    set_repeat_table_header(table.rows[0])
    return table


def configure_document(doc: Document):
    section = doc.sections[0]
    section.top_margin = Inches(0.75)
    section.bottom_margin = Inches(0.7)
    section.left_margin = Inches(1.0)
    section.right_margin = Inches(1.0)

    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = "Aptos"
    normal._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), "Aptos")
    normal._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"), "Aptos")
    normal.font.size = Pt(10.2)
    normal.font.color.rgb = RGBColor.from_string(INK)
    normal.paragraph_format.space_after = Pt(5)
    normal.paragraph_format.line_spacing = 1.06

    for style_name, size, color in (("Title", 29, NAVY), ("Heading 1", 19, NAVY), ("Heading 2", 13.5, BLUE), ("Heading 3", 11.5, GREEN)):
        style = styles[style_name]
        style.font.name = "Aptos Display"
        style._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), "Aptos Display")
        style._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"), "Aptos Display")
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = RGBColor.from_string(color)
        style.paragraph_format.keep_with_next = True
        style.paragraph_format.space_before = Pt(10 if style_name != "Heading 1" else 4)
        style.paragraph_format.space_after = Pt(5)

    if "Report Subtitle" not in styles:
        subtitle = styles.add_style("Report Subtitle", WD_STYLE_TYPE.PARAGRAPH)
    else:
        subtitle = styles["Report Subtitle"]
    subtitle.font.name = "Aptos"
    subtitle.font.size = Pt(15)
    subtitle.font.color.rgb = RGBColor.from_string(BLUE)
    subtitle.paragraph_format.space_after = Pt(18)

    header = section.header
    hp = header.paragraphs[0]
    hp.text = "DATA FOR DINNER 2026  /  FOOD ACCESS"
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    base.set_font(hp.runs[0], name="Aptos", size=8, color=MUTED, bold=True)
    add_rule(hp, color=LINE, size=6)

    footer = section.footer
    fp = footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = fp.add_run("Data for Dinner 2026  •  August 22, 2026  •  ")
    base.set_font(r, name="Aptos", size=8, color=MUTED)
    base.add_field(fp, "PAGE")

    doc.core_properties.title = "Food Access: Global to Alabama"
    doc.core_properties.subject = "Official-data pull, factual analysis, dataset sufficiency, and next allergy crawl"
    doc.core_properties.author = "Data for Dinner 2026 team"
    doc.core_properties.keywords = "food access; food insecurity; Alabama; Southeast; FAOSTAT; USDA SRAM"
    base.set_update_fields(doc)


def build_document() -> Path:
    global_rows = read_csv("data/processed/global_food_access_summary.csv")
    se_rows = read_csv("data/processed/southeast_state_comparison.csv")
    county_rows = read_csv("data/processed/alabama_county_food_access.csv")
    tract_rows = read_csv("data/processed/alabama_tract_food_access.csv")
    sensitivity_rows = read_csv("results/sensitivity_analysis.csv")
    qa_rows = read_csv("results/qa_results.csv")
    assessment_rows = read_csv("results/dataset_assessment.csv")
    manifest_rows = read_csv("data/metadata/source_manifest.csv")
    findings = json.loads((ROOT / "results" / "key_findings.json").read_text(encoding="utf-8"))

    alabama = findings["alabama"]
    united_states = findings["united_states"]

    def global_value(geography: str, key: str) -> str:
        row = next(item for item in global_rows if item["geography"] == geography and item["indicator_key"] == key)
        return row["display_value"]

    doc = Document()
    configure_document(doc)
    base.add_numbering_definitions(doc)

    # Cover
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(38)
    r = p.add_run("DATA FOR DINNER 2026")
    base.set_font(r, name="Aptos", size=10, color=GREEN, bold=True)
    add_rule(p, color=GREEN, size=14)

    title = doc.add_paragraph(style="Title")
    title.paragraph_format.space_before = Pt(38)
    title.paragraph_format.space_after = Pt(10)
    title.add_run("Food Access:\nGlobal to Alabama")

    subtitle = doc.add_paragraph(style="Report Subtitle")
    subtitle.add_run("Official-data pull, factual analysis, dataset sufficiency, and next-crawl recommendation")

    base.add_callout(doc, "SCOPE", "Global to United States to project-defined Southeast to Alabama. Food allergies, race and gender demographic analysis, and straight-line distance are outside the active analysis.", accent=BLUE)

    meta = doc.add_table(rows=4, cols=2)
    meta.style = "Table Grid"
    set_repeat_table_header(meta.rows[0])
    rows = [
        ("Prepared by", "Data for Dinner 2026 project team"),
        ("Frozen pull", "August 22, 2026 (Central Time)"),
        ("Primary local source", "USDA ERS 2025 SNAP-authorized Retailer Access Map"),
        ("Project region", "AL, AR, FL, GA, KY, LA, MS, NC, SC, TN"),
    ]
    for i, (label, value) in enumerate(rows):
        base.set_cell_shading(meta.rows[i].cells[0], PALE_BLUE)
        base.set_cell_text(meta.rows[i].cells[0], label, bold=True, color=NAVY, size=9.5)
        base.set_cell_text(meta.rows[i].cells[1], value, size=9.5)
        base.set_row_cant_split(meta.rows[i])
    base.set_table_geometry(meta, [2200, 7160])
    base.set_table_borders(meta, color=LINE)
    add_small_note(doc, "Prepared as a factual checkpoint. The report does not assign causes, make causal claims, or combine unlike access measures into one score.")
    base.add_page_break(doc)

    # Executive summary
    base.add_heading(doc, "Executive summary", 1)
    add_section_intro(doc, "The pull supports the current main question. The primary local dataset is sufficient for Alabama and the ten-state comparison, provided the distance method and measurement boundaries remain explicit.")

    base.add_heading(doc, "Key facts", 2)
    add_fact_list(doc, [
        f"Global: FAOSTAT estimates {global_value('World', 'moderate_or_severe_food_insecurity')}% of the world population experienced moderate or severe food insecurity in 2023–2025. The U.S. FAOSTAT estimate is {global_value('United States of America', 'moderate_or_severe_food_insecurity')}%.",
        "United States: USDA estimates 13.7% of U.S. households were food insecure in 2024, representing 18.34 million households. Very low food security affected 5.4%, or 7.20 million households.",
        "Project-defined Southeast: 2022–2024 state household estimates range from 11.8% in North Carolina to 19.4% in Arkansas. Alabama is 12.1% ± 2.23 percentage points and ranks ninth of ten from high to low.",
        f"Alabama: {pct(alabama['low_income_low_access_population_pct'])} of low-income residents, or {num(alabama['low_income_low_access_population'])} people, are beyond the primary retailer-access threshold.",
        f"Alabama: {num(alabama['lila_tract_count'])} tracts, or {pct(alabama['lila_tract_pct'])}, are flagged low-income/low-access. The provisional U.S. share is {pct(united_states['lila_tract_pct'])}.",
        f"Sensitivity: Alabama's low-income burden is {pct(alabama['driving_threshold_low_income_low_access_pct']['1_urban_10_rural'])} at the primary threshold, {pct(alabama['driving_threshold_low_income_low_access_pct']['0.5_urban_10_rural'])} at 0.5 mile urban / 10 miles rural, and {pct(alabama['driving_threshold_low_income_low_access_pct']['1_urban_20_rural'])} at 1 mile urban / 20 miles rural.",
    ])

    base.add_heading(doc, "Decisions from this pull", 2)
    decision_rows = [
        ("Primary local dataset", "Retain USDA 2025 SRAM", "Complete for Alabama and the ten project states; supports tract, population, low-income, and subgroup measures."),
        ("Global and U.S. context", "Retain as separate layers", "FAOSTAT population indicators and USDA household estimates answer different questions from retailer proximity."),
        ("More datasets", "Add only against a declared gap", "Avoid a broad crawl that mixes vintages and measures without an analytical purpose."),
        ("Distance method", "Road network only", "Straight-line distance is excluded because it does not represent road travel and produced implausibly influential outliers for this study."),
        ("Allergies", "Pause integration; run feasibility crawl", "No single official public source links prevalence, tract food insecurity, store inventory, price, and allergens."),
    ]
    base.add_table(doc, ["Decision area", "Recommendation", "Reason"], decision_rows, [2080, 2560, 4720], font_size=8.8)
    base.add_callout(doc, "COMPARABILITY", "Global population indicators, U.S. household food insecurity, and tract retailer proximity have different universes, units, and meanings. They are reported side by side, not as one numeric scale.", accent=RED)
    base.add_page_break(doc)

    # Data pull
    base.add_heading(doc, "1. Data selected and captured", 1)
    add_section_intro(doc, "All retained sources are official, publicly downloadable, and frozen with URLs, file sizes, retrieval timestamps, and SHA-256 hashes. Raw files are reproducibly downloaded; processed tables and metadata are stored with the analysis.")
    source_rows = []
    for row in manifest_rows:
        source_rows.append((row["source_id"], row["dataset"], row["geography"], row["vintage"]))
    base.add_table(doc, ["Source ID", "Dataset", "Geography", "Vintage"], source_rows, [1500, 3000, 1800, 3060], font_size=8.3)

    base.add_heading(doc, "Selection rules", 2)
    add_fact_list(doc, [
        "Use the latest official release available on the pull date; retain observation dates separately from retrieval dates.",
        "Keep a measure only when its unit, denominator, geography, and join key are clear.",
        "Use the 1-mile urban / 10-mile rural driving-distance threshold as the primary local measure because it matches the agreed plan and follows the road network.",
        "Preserve uncertainty for state household estimates and vary only road-network thresholds in sensitivity output.",
        "Exclude straight-line distance from imported analysis fields, results, workbook tables, and report findings.",
        "Do not average tract percentages. Aggregate numerators and denominators, then calculate the rate.",
    ])
    base.add_heading(doc, "Capture package", 2)
    base.add_table(doc, ["Artifact", "Contents"], [
        ("Source manifest", "Official URL, geography, vintage, retrieval time, bytes, SHA-256, local path."),
        ("Processed CSVs", "Global summary, all state outcomes, all state retailer access, ten-state comparison, Alabama counties, all Alabama tracts."),
        ("Results", "QA checks, sensitivity analysis, dataset sufficiency assessment, key findings."),
        ("Figures", "Five reviewed charts/maps with source notes and consistent styling."),
        ("Team files and reproducibility", "This report in DOCX/PDF, a filterable workbook with 12 sheets, acquisition and analysis scripts, a dependency list, and methods documentation."),
    ], [2300, 7060], font_size=9)

    # Global
    base.add_heading(doc, "2. Global access to food", 1)
    add_section_intro(doc, "FAOSTAT provides population-level indicators for food insecurity, undernourishment, and affordability of a healthy diet. Values below are the latest selected period for each series.")
    add_picture(doc, "figures/global_food_access.png", "Grouped horizontal bars comparing latest moderate or severe food insecurity and healthy-diet unaffordability for the world, major regions, and the United States.", "Figure 1. Global food-access indicators from FAOSTAT. Series have different concepts but the same population-percent unit.", width=6.1)
    global_table = []
    for geography in ("World", "Africa", "Asia", "Europe", "Latin America and the Caribbean", "Oceania", "United States of America"):
        global_table.append((
            geography.replace("United States of America", "United States"),
            global_value(geography, "moderate_or_severe_food_insecurity") + "%",
            global_value(geography, "severe_food_insecurity") + "%",
            global_value(geography, "undernourishment") + "%",
            global_value(geography, "healthy_diet_unaffordability") + "%",
        ))
    base.add_table(doc, ["Geography", "Moderate/severe FI", "Severe FI", "Undernourished", "Unable to afford healthy diet"], global_table, [2500, 1650, 1350, 1550, 2310], font_size=8.5)
    add_small_note(doc, "Periods: food-insecurity and undernourishment indicators use 2023–2025; healthy-diet unaffordability uses 2025. “<2.5” is preserved as published.")

    base.add_heading(doc, "What stands out", 2)
    add_fact_list(doc, [
        "Africa has the highest selected moderate/severe food-insecurity estimate (57.4%), severe estimate (21.1%), undernourishment estimate (20.1%), and healthy-diet unaffordability estimate (66.6%).",
        "The world estimates are 26.8% moderate/severe food insecurity, 9.8% severe food insecurity, 8.1% undernourishment, and 32.7% unable to afford a healthy diet.",
        "The United States is below the world estimate on every selected FAOSTAT indicator: 10.7%, 1.1%, less than 2.5%, and 4.5%, respectively.",
    ])
    base.add_page_break(doc)

    # U.S.
    base.add_heading(doc, "3. United States access to food", 1)
    add_section_intro(doc, "\u00a0The U.S. section separates household food insecurity from physical proximity to SNAP-authorized retailers.")
    base.add_heading(doc, "Household food security, 2024", 2)
    us_rows = [
        ("Food secure", "86.3%", "115.58 million households"),
        ("Food insecure", "13.7%", "18.34 million households"),
        ("Very low food security", "5.4%", "7.20 million households"),
    ]
    base.add_table(doc, ["Status", "Share", "Households"], us_rows, [3500, 1800, 4060], font_size=9.5)

    base.add_heading(doc, "Retailer access, primary threshold", 2)
    retail_rows = [
        ("Population beyond threshold", num(united_states["low_access_population"]), pct(united_states["low_access_population_pct"])),
        ("Low-income population beyond threshold", num(united_states["low_income_low_access_population"]), pct(united_states["low_income_low_access_population_pct"])),
        ("Low-income/low-access tracts", num(united_states["lila_tract_count"]), pct(united_states["lila_tract_pct"])),
        ("Children beyond threshold", "N/A", pct(united_states["low_access_children_pct"])),
        ("Adults 65+ beyond threshold", "N/A", pct(united_states["low_access_seniors_pct"])),
        ("No-vehicle occupied units beyond threshold", "N/A", pct(united_states["low_access_no_vehicle_housing_units_pct"])),
        ("SNAP occupied units beyond threshold", "N/A", pct(united_states["low_access_snap_housing_units_pct"])),
    ]
    base.add_table(doc, ["Measure", "Count", "Share of matching denominator"], retail_rows, [4300, 2200, 2860], font_size=9)
    add_small_note(doc, "Primary threshold: more than 1 driving mile in urban tracts or 10 driving miles in rural tracts. The national low-income share is provisional because fourteen New York tracts lack low-income denominators.")
    base.add_callout(doc, "BOUNDARY", "Household food insecurity is an outcome reported for households. SRAM retailer access is a tract-based proximity measure reported for people or housing units. A household can experience either, both, or neither.", accent=RED)
    base.add_page_break(doc)

    # Southeast outcome
    base.add_heading(doc, "4. Project-defined Southeast", 1)
    add_section_intro(doc, "The ten-state comparison uses the same state set throughout: Alabama, Arkansas, Florida, Georgia, Kentucky, Louisiana, Mississippi, North Carolina, South Carolina, and Tennessee.")
    add_picture(doc, "figures/southeast_food_insecurity.png", "Horizontal bar chart of 2022 to 2024 household food insecurity estimates for ten Southeast states with USDA margins of error and a United States reference line.", "Figure 2. Household food insecurity in the project-defined Southeast, 2022–2024 average.", width=6.1)
    se_outcome_rows = []
    for row in sorted(se_rows, key=lambda item: float(item["food_insecurity_pct"]), reverse=True):
        se_outcome_rows.append((row["state_abbr"], pct(row["food_insecurity_pct"]), f"± {float(row['food_insecurity_moe_pp']):.2f}", pct(row["very_low_food_security_pct"]), row["food_insecurity_rank_high_to_low"]))
    base.add_table(doc, ["State", "Food insecure", "MOE (points)", "Very low", "Rank high→low"], se_outcome_rows, [1700, 2100, 2000, 1800, 1760], font_size=8.8)
    add_small_note(doc, "Margins of error are material. Small rank differences are descriptive, especially where intervals overlap.")
    base.add_page_break(doc)

    # Southeast access
    base.add_heading(doc, "5. Southeast retailer access", 1)
    add_picture(doc, "figures/southeast_retail_access.png", "Horizontal bar chart of the share of low-income residents beyond the driving-distance retailer-access threshold in ten Southeast states, with Alabama highlighted and a United States reference line.", "Figure 3. Low-income population beyond the primary retailer-access threshold.", width=5.9)
    se_access_rows = []
    for row in sorted(se_rows, key=lambda item: float(item["low_income_low_access_population_pct"]), reverse=True):
        se_access_rows.append((row["state_abbr"], pct(row["low_income_low_access_population_pct"]), pct(row["low_access_population_pct"]), pct(row["lila_tract_pct"]), row["low_income_low_access_rank_high_to_low"]))
    base.add_table(doc, ["State", "Low-income burden", "All-population burden", "LILA tract share", "Rank high→low"], se_access_rows, [1500, 2200, 2100, 1900, 1660], font_size=8.8)
    base.add_heading(doc, "What stands out", 2)
    add_fact_list(doc, [
        "Georgia (31.6%) and Florida (31.6%) have the highest low-income retailer-access shares in the ten-state set; Mississippi is lowest at 16.9%.",
        "Alabama is 20.2%, eighth-highest of ten, and 0.9 percentage points below the provisional U.S. estimate of 21.2%.",
        "Household food-insecurity ordering and retailer-access ordering differ. Arkansas ranks first on the household outcome and sixth on retailer access; Georgia ranks fifth and first, respectively.",
    ])
    base.add_page_break(doc)

    # Alabama
    base.add_heading(doc, "6. Alabama access to food", 1)
    add_section_intro(doc, "Alabama has complete primary fields for all 1,436 2020 census tracts and complete joins to the selected Census tract geometry.")
    base.add_table(doc, ["Measure", "Count", "Share"], [
        ("2020 population", num(alabama["population"]), "N/A"),
        ("Low-income population", num(alabama["low_income_population"]), "N/A"),
        ("Population beyond primary threshold", num(alabama["low_access_population"]), pct(alabama["low_access_population_pct"])),
        ("Low-income population beyond threshold", num(alabama["low_income_low_access_population"]), pct(alabama["low_income_low_access_population_pct"])),
        ("Low-income/low-access tracts", num(alabama["lila_tract_count"]), pct(alabama["lila_tract_pct"])),
    ], [4700, 2400, 2260], font_size=9.5)
    add_picture(doc, "figures/alabama_tract_food_access_map.png", "Choropleth map of Alabama census tracts shaded by the percentage of low-income residents beyond the one mile urban or ten mile rural driving-distance threshold, with no-data tracts identified separately.", "Figure 4. Alabama low-income retailer-access burden by census tract.", width=4.5)
    add_small_note(doc, "Dark shading indicates a larger share of the tract's low-income population beyond the threshold; the map does not show household food-insecurity prevalence.")

    # Counties
    base.add_heading(doc, "7. Alabama county and tract detail", 1)
    add_section_intro(doc, "Counties below are ordered by the count of affected low-income residents, not by rate. This favors places where the absolute number is largest.")
    county_table = []
    for row in county_rows[:10]:
        county_table.append((row["county"].replace(" County", ""), num(row["low_income_low_access_population"]), pct(row["low_income_low_access_population_pct"]), num(row["lila_tract_count"]), pct(row["lila_tract_pct"])))
    base.add_table(doc, ["County", "Affected low-income residents", "Low-income burden", "LILA tracts", "LILA tract share"], county_table, [2100, 2200, 1900, 1400, 1760], font_size=8.8)
    base.add_heading(doc, "Highest affected counts", 2)
    add_fact_list(doc, [
        "Jefferson County: 133,014 affected low-income residents; 30.8% of its low-income population.",
        "Madison County: 106,257; 35.3%.",
        "Shelby County: 68,184; 36.7%.",
        "Baldwin County: 42,834; 23.9%.",
        "Mobile County: 39,741; 15.8%.",
    ])
    add_small_note(doc, "A high count and a high rate answer different questions. The workbook contains all 67 counties and both rankings.")

    base.add_heading(doc, "Top LILA tracts by affected low-income count", 2)
    tract_table = []
    qualifying = [row for row in tract_rows if float(row["DD_SRAM_LILATracts_1And10"] or 0) == 1 and float(row["GroupQuartersFlag"] or 0) != 1]
    qualifying.sort(key=lambda item: float(item["DD_SRAM_LALOWI1_10"] or 0), reverse=True)
    for row in qualifying[:8]:
        tract_table.append((row["GEOID20"], row["County24"].replace(" County", ""), num(row["DD_SRAM_LALOWI1_10"]), pct(row["low_income_low_access_population_pct"]), pct(row["PovertyRate"])))
    base.add_table(doc, ["GEOID", "County", "Affected low-income", "Low-income burden", "Poverty rate"], tract_table, [1800, 2000, 2000, 1800, 1760], font_size=8.5)
    base.add_page_break(doc)

    # Subgroups
    heading = base.add_heading(doc, "8. Subgroup access results", 1)
    heading.paragraph_format.page_break_before = True
    add_picture(doc, "figures/alabama_subgroup_access.png", "Horizontal comparison of Alabama and United States retailer-access shares for the total population, low-income population, children, seniors, no-vehicle occupied housing units, and SNAP occupied housing units.", "Figure 5. Primary-threshold retailer access by population or housing-unit subgroup.")
    subgroup_rows = [
        ("All population", pct(alabama["low_access_population_pct"]), pct(united_states["low_access_population_pct"]), "People"),
        ("Low-income population", pct(alabama["low_income_low_access_population_pct"]), pct(united_states["low_income_low_access_population_pct"]), "Low-income people"),
        ("Children", pct(alabama["low_access_children_pct"]), pct(united_states["low_access_children_pct"]), "Children"),
        ("Adults 65+", pct(alabama["low_access_seniors_pct"]), pct(united_states["low_access_seniors_pct"]), "Adults 65+"),
        ("No-vehicle occupied units", pct(alabama["low_access_no_vehicle_housing_units_pct"]), pct(united_states["low_access_no_vehicle_housing_units_pct"]), "Housing units"),
        ("SNAP occupied units", pct(alabama["low_access_snap_housing_units_pct"]), pct(united_states["low_access_snap_housing_units_pct"]), "Housing units"),
    ]
    base.add_table(doc, ["Group", "Alabama", "United States", "Denominator"], subgroup_rows, [3300, 1600, 1800, 2660], font_size=9.2)
    base.add_heading(doc, "What stands out", 2)
    add_fact_list(doc, [
        "Alabama is below the provisional U.S. share for all people, low-income people, children, and seniors.",
        "Alabama is above the U.S. share for no-vehicle occupied units (12.6% versus 8.9%) and SNAP occupied units (12.5% versus 11.1%).",
        "The no-vehicle and SNAP figures use housing-unit denominators; they should not be numerically pooled with population shares.",
    ])
    base.add_page_break(doc)

    # Sensitivity + QA
    base.add_heading(doc, "9. Sensitivity and sanity checks", 1)
    base.add_heading(doc, "Alabama road-network sensitivity", 2)
    al_sensitivity = [row for row in sensitivity_rows if row["geography"] == "Alabama"]
    sens_table = []
    for row in al_sensitivity:
        sens_table.append((row["threshold"], pct(row["low_access_population_pct"]), pct(row["low_income_low_access_population_pct"]), pct(row["lila_tract_pct"])))
    base.add_table(doc, ["Road-network threshold", "All population", "Low-income population", "LILA tracts"], sens_table, [3100, 1900, 2360, 2000], font_size=8.8)
    add_fact_list(doc, [
        "Changing the urban threshold from 1.0 mile to 0.5 mile raises Alabama's low-income burden from 20.2% to 35.9%.",
        "Changing the rural threshold from 10 to 20 miles lowers the low-income burden only slightly, from 20.2% to 19.6%.",
        "Straight-line distance is excluded from the study and is not treated as a sensitivity result.",
        "Recommendation: retain the road-network 1/10 threshold and label it on every table, chart, and spoken finding.",
    ])

    base.add_heading(doc, "QA result", 2)
    status_counts = {}
    for row in qa_rows:
        status_counts[row["status"]] = status_counts.get(row["status"], 0) + 1
    base.add_callout(doc, "QA STATUS", f"{status_counts.get('PASS', 0)} PASS  •  {status_counts.get('REVIEW', 0)} REVIEW  •  {status_counts.get('FAIL', 0)} FAIL", accent=GREEN)
    qa_table = []
    for row in qa_rows:
        qa_table.append((row["status"], row["check"], row["observed"], row["note"] or "N/A"))
    base.add_table(doc, ["Status", "Check", "Observed", "Note"], qa_table, [1100, 3100, 1500, 3660], font_size=7.2)
    add_small_note(doc, "The one reviewed exception consists of fourteen Suffolk County, New York tracts without low-income denominators and one zero-population Massachusetts tract without a LILA flag. Alabama and the ten project states are complete.")
    base.add_page_break(doc)

    # Data sufficiency
    base.add_heading(doc, "10. What is available and whether to change datasets", 1)
    assessment_table = []
    for row in assessment_rows:
        assessment_table.append((row["source_id"], row["grain"], row["recommendation"], row["limitation"]))
    base.add_table(doc, ["Source / gap", "Grain", "Recommendation", "Main limitation"], assessment_table, [1850, 1800, 2400, 3310], font_size=7.6)

    base.add_heading(doc, "Recommendation", 2)
    base.add_callout(doc, "RETAIN THE CURRENT CORE", "USDA SRAM is sufficient for the primary Alabama and Southeast physical-access question. FAOSTAT and USDA household estimates are sufficient as separate factual context and outcome benchmarks.", accent=GREEN)
    add_fact_list(doc, [
        "Do not replace SRAM with the 2019 Large Retailer Access Map. The retailer universe and tract base differ; use LRAM only as a labeled sensitivity comparison.",
        "Do not add the full Food Environment Atlas by default. Add a small, predeclared variable set only if the team decides to examine price, assistance, store environment, or another explicit county-level gap.",
        "If the team wants a local food-insecurity outcome, evaluate a modeled county or tract source separately and document that it is not directly comparable to the official state household series.",
        "Hold the 2024 Feeding America Alabama data until the source file, direct citation, field definitions, denominator, geography, license, and Alabama reconciliation are documented.",
        "Preserve the current frozen pull. Refresh only with a new dated snapshot and a change log.",
    ])

    base.add_heading(doc, "Known blind spots", 2)
    add_fact_list(doc, [
        "SRAM does not measure food price, product quality, nutrition, inventory, store hours, transit, disability access, online purchasing, or household food insecurity.",
        "The listed retailer universe is SNAP-authorized retailers as of June 2025 and excludes farmers markets and delivery routes.",
        "Observation periods differ across layers. This is a cross-source snapshot, not a synchronized time series.",
        "The current data does not quantify food abundance or supply volume. That visual requires an approved measure and source.",
        "Race and gender demographic analysis is outside the current scope.",
    ])
    # Allergy
    base.add_heading(doc, "11. Recommended next crawl for food allergies", 1)
    add_section_intro(doc, "Keep allergies outside the active analysis until feasibility is demonstrated. The public official sources identified here describe different parts of the problem and do not form a direct tract-level access dataset.")
    allergy_rows = [
        ("Taxonomy", "FDA nine major allergens", "Milk, egg, fish, crustacean shellfish, tree nuts, peanuts, wheat, soybeans, sesame.", "Scope control; not prevalence or availability."),
        ("Diagnosed prevalence", "CDC/NCHS 2024 NHIS", "National adult/child estimates and selected demographic/urbanization comparisons.", "Public-use geography does not support a reliable tract-level Alabama join."),
        ("Product labels", "USDA FoodData Central branded foods", "Ingredients, brand owner, category, GTIN/UPC; pilot text classification.", "Not store inventory or price; allergen parsing requires validation."),
        ("Recall events", "openFDA food enforcement", "Reason, report date, status, distribution pattern, state when available.", "Events are not prevalence or product availability."),
        ("Local availability and price", "Retailer inventory source", "Product × store × date × price, with stable product identifiers.", "Not present in the official public sources reviewed; licensing/API gate."),
    ]
    base.add_table(doc, ["Module", "Starting source", "What it can support", "Boundary"], allergy_rows, [1600, 2100, 3000, 2660], font_size=8.2)

    base.add_heading(doc, "Proceed / pause rule", 2)
    base.add_callout(doc, "PROCEED ONLY IF", "A product-by-store-by-date source with price, defensible geographic coverage, stable product identifiers, and a validated FDA-allergen mapping is available. Otherwise, keep prevalence, product-label coverage, and recall events as separate descriptive modules or future work.", accent=AMBER)
    base.add_heading(doc, "Recommended crawl sequence", 2)
    add_fact_list(doc, [
        "Lock the FDA nine-major-allergen taxonomy. Keep fruit and chocolate only as separately defined exploratory categories.",
        "Profile 2024 NHIS prevalence fields, denominators, demographic detail, and public-use geography.",
        "Pilot FoodData Central ingredient/Contains-text classification on a small sample and manually validate false positives and false negatives.",
        "Pull openFDA enforcement records for undeclared-allergen events; deduplicate and keep recall geography and dates.",
        "Search for a retailer inventory-and-price source only after the first four modules are documented; stop if product/store/date joins cannot be proven.",
    ])
    base.add_page_break(doc)

    # Prompt
    base.add_heading(doc, "12. Reusable prompt for the allergy crawl", 1)
    prompt = (
        "Conduct an official-source-only feasibility crawl for food-allergy access in Alabama and the project-defined Southeast "
        "(AL, AR, FL, GA, KY, LA, MS, NC, SC, TN). Keep this separate from the current food-access analysis until joinability "
        "is proven. Use the FDA nine major allergens, including milk, egg, fish, crustacean shellfish, tree nuts, peanuts, wheat, soybeans, "
        "and sesame, as the primary taxonomy. Treat fruit and chocolate only as explicitly defined exploratory categories. For each "
        "candidate dataset, record publisher, exact dataset and table, URL/API endpoint, release and observation dates, population "
        "or product universe, geography, unit of analysis, allergen fields, price/inventory fields, identifiers, access/licensing limits, "
        "update frequency, missingness, and proposed joins. Prioritize CDC/NCHS 2024 NHIS for diagnosed prevalence, USDA FoodData "
        "Central branded foods for a pilot of ingredient/Contains-text classification, and openFDA food-enforcement data for "
        "undeclared-allergen recall events. Do not treat recalls as prevalence or FoodData Central as store inventory. Do not make "
        "causal or medical claims and do not collect personal health information. Sanity-check denominators, duplicate records, "
        "changing labels, geography, dates, and taxonomy. Deliver (1) a source inventory, (2) a field-level data dictionary, (3) small "
        "reproducible pilot extracts, (4) QA findings, (5) a joinability matrix, and (6) a proceed/pause recommendation. Proceed to "
        "local allergen-safe access only if a product-by-store-by-date source with price and defensible coverage is available; otherwise "
        "recommend separate descriptive modules and identify the exact missing data."
    )
    add_prompt_box(doc, prompt)
    base.add_heading(doc, "Expected output contract", 2)
    base.add_table(doc, ["Output", "Acceptance check"], [
        ("Source inventory", "Every row has an official owner, direct URL/API endpoint, vintage, geography, grain, and access terms."),
        ("Field dictionary", "Denominators, identifier formats, allergen text fields, and missing-value conventions are explicit."),
        ("Pilot extracts", "Small, reproducible, dated, hashed, and free of personal health information."),
        ("QA report", "Duplicates, denominators, taxonomy, date ranges, geography, and label parsing are tested."),
        ("Joinability matrix", "Every proposed join lists cardinality, expected match rate, temporal alignment, and failure conditions."),
        ("Decision", "Proceed/pause is tied to product-by-store-by-date inventory and price coverage, not project novelty."),
    ], [2500, 6860], font_size=8.8)
    base.add_page_break(doc)

    # Methods and limitations
    base.add_heading(doc, "Appendix A. Processing and validation details", 1)
    base.add_heading(doc, "Tract key repair", 2)
    base.add_body(doc, "The SRAM general-characteristics CSV stores CensusTract20 without leading zeros when imported as a number. Distance files preserve 11 digits. Normalizing every tract key to text with zfill(11) restored 15,636 joins, including all Alabama and Arkansas tracts. The pipeline then verified 84,119 unique U.S. tracts, 50 states plus the District of Columbia, and zero duplicate GEOIDs.")
    base.add_heading(doc, "Aggregation", 2)
    add_fact_list(doc, [
        "Overall burden = sum of people beyond the selected threshold ÷ sum of 2020 population.",
        "Low-income burden = sum of low-income people beyond the selected threshold ÷ sum of low-income population.",
        "Subgroup shares use their matching child, senior, no-vehicle housing-unit, or SNAP housing-unit denominator.",
        "LILA tract share = flagged tracts ÷ all tracts in the geography.",
    ])
    base.add_heading(doc, "Interpretation limits", 2)
    add_fact_list(doc, [
        "Descriptive comparisons do not establish causes or policy effects.",
        "State household margins of error should accompany estimates; ranks are descriptive.",
        "Physical proximity is one dimension of food access and cannot be read as product availability or affordability.",
        "Straight-line distance is excluded; road-network thresholds must be disclosed.",
        "The current data does not quantify food abundance or supply volume.",
        "Race and gender demographic analysis is outside the current scope.",
        "The national low-income retailer-access estimate is provisional because of fourteen missing New York denominators. Alabama and the project region are unaffected.",
    ])

    base.add_heading(doc, "Appendix B. Files delivered", 1)
    base.add_table(doc, ["Path", "Purpose"], [
        ("reports/Data_for_Dinner_Food_Access_Analysis.docx", "Editable team report."),
        ("reports/Data_for_Dinner_Food_Access_Analysis.pdf", "Fixed-layout report."),
        ("reports/Data_for_Dinner_Food_Access_Analysis.xlsx", "Filterable source, data, sensitivity, QA, and metadata workbook."),
        ("data/processed/*.csv", "Analysis-ready tables at global, state, county, and tract levels."),
        ("data/metadata/*.csv", "Source manifest and analysis variable dictionary."),
        ("results/*.csv / *.json", "QA, sensitivity, sufficiency assessment, and key findings."),
        ("src/*.py", "Reproducible acquisition and analysis."),
        ("docs/*.md", "Methods and allergy next-crawl documentation."),
    ], [4200, 5160], font_size=8.6)
    base.add_page_break(doc)

    # Sources
    heading = base.add_heading(doc, "Appendix C. Official sources", 1)
    heading.paragraph_format.page_break_before = True
    sources = [
        ("FAOSTAT Suite of Food Security Indicators", "Food and Agriculture Organization of the United Nations", "https://data.fao.org/catalog/dataset/955d6564-40a9-48b4-b51b-f19d65bb3539", "Global, regional, and national food-security indicators."),
        ("FAOSTAT Cost and Affordability of a Healthy Diet", "Food and Agriculture Organization of the United Nations", "https://bulks-faostat.fao.org/production/Cost_Affordability_Healthy_Diet_(CoAHD)_E_All_Data_(Normalized).zip", "Healthy-diet affordability indicators through 2025."),
        ("Household Food Security in the United States in 2024", "USDA Economic Research Service", "https://ers.usda.gov/sites/default/files/_laserfiche/publications/113623/ERR-358.pdf", "2024 national and 2022–2024 state household estimates."),
        ("Food Security in the U.S.: Key Statistics & Graphics", "USDA Economic Research Service", "https://www.ers.usda.gov/topics/food-nutrition-assistance/food-security-in-the-us/key-statistics-graphics", "Official national summary and definitions."),
        ("Food Access Research Atlas - Download the Data", "USDA Economic Research Service", "https://www.ers.usda.gov/data-products/food-access-research-atlas/download-the-data", "Official 2025 SRAM download and release information."),
        ("SRAM Reference Guide", "USDA Economic Research Service", "https://www.ers.usda.gov/data-products/food-access-research-atlas/documentation/snap-authorized-retailer-access-map-reference-guide", "Variables, thresholds, and retailer universe."),
        ("SRAM Data Sources and Technical Methods", "USDA Economic Research Service", "https://www.ers.usda.gov/data-products/food-access-research-atlas/documentation/snap-authorized-retailer-access-map-data-sources-and-technical-methods", "STARS, Census, LandScan, ACS, distance, and method details."),
        ("2020 Alabama Census Tract Boundaries", "U.S. Census Bureau", "https://www2.census.gov/geo/tiger/GENZ2020/shp/cb_2020_01_tract_500k.zip", "Mapping geometry."),
        ("Food Allergies", "U.S. Food and Drug Administration", "https://www.fda.gov/food/nutrition-food-labeling-and-critical-foods/food-allergies", "FDA major-allergen taxonomy and labeling context."),
        ("2024 Adult Food-Allergy Estimates", "CDC National Center for Health Statistics", "https://www.cdc.gov/nchs/products/databriefs/db545.htm", "Diagnosed adult prevalence."),
        ("2024 Child Food-Allergy Estimates", "CDC National Center for Health Statistics", "https://www.cdc.gov/nchs/products/databriefs/db546.htm", "Diagnosed child prevalence."),
        ("FoodData Central Data Dictionary", "USDA Agricultural Research Service", "https://fdc.nal.usda.gov/portal-data/external/dataDictionary", "Branded-food product fields and ingredients."),
        ("openFDA Food Enforcement API", "U.S. Food and Drug Administration", "https://open.fda.gov/apis/food/enforcement/", "Food recall enforcement events."),
    ]
    for index, (title_text, organization, url, note) in enumerate(sources, start=1):
        base.add_source_item(doc, index, title_text, organization, url, note)

    base.add_heading(doc, "Appendix D. Final factual checkpoint", 1)
    checkpoint_rows = [
        ("Main question answered without allergies", "Yes"),
        ("Global, U.S., Southeast, Alabama facts reported", "Yes"),
        ("Primary measure sufficient for project geography", "Yes"),
        ("Subgroup denominators clear", "Yes"),
        ("Road-network sensitivity disclosed", "Yes"),
        ("Straight-line result excluded", "Yes"),
        ("Source hashes and retrieval dates captured", "Yes"),
        ("Blocking QA failures", "None"),
        ("Allergy integration", "Paused pending feasibility gate"),
    ]
    base.add_table(doc, ["Check", "Result"], checkpoint_rows, [6600, 2760], font_size=9.2)

    roles_heading = base.add_heading(doc, "Appendix E. Project roles", 1)
    roles_heading.paragraph_format.page_break_before = True
    base.add_body(doc, "Roles are placed at the end so readers encounter the project question, methods, evidence, and limitations first.")
    base.add_table(doc, ["Team member", "Primary responsibilities"], [
        ("Sharon Brooks", "Team lead and project management, meeting coordination, and review of the repository framework."),
        ("Sandra Kopecky", "Data and database work, source review, and use of the approved dataset for analysis."),
        ("April Gillespie", "Repository management, analysis, technical implementation, documentation updates, and integration of validated team data."),
        ("Shared", "Review definitions and final numbers, record the presentation, and submit during the weekend ending September 13, 2026."),
    ], [2500, 6860], font_size=9.0)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUTPUT)
    return OUTPUT


if __name__ == "__main__":
    result = build_document()
    print(result)
