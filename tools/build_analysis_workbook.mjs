import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const root = process.cwd();
const outputDir = path.join(root, "reports");
const previewDir = path.join(root, "qa", "workbook");
const outputPath = path.join(outputDir, "Data_for_Dinner_Food_Access_Analysis.xlsx");

function parseCsv(text) {
  const rows = [];
  let row = [];
  let field = "";
  let quoted = false;
  for (let i = 0; i < text.length; i += 1) {
    const char = text[i];
    if (quoted) {
      if (char === '"' && text[i + 1] === '"') {
        field += '"';
        i += 1;
      } else if (char === '"') {
        quoted = false;
      } else {
        field += char;
      }
    } else if (char === '"') {
      quoted = true;
    } else if (char === ",") {
      row.push(field);
      field = "";
    } else if (char === "\n") {
      row.push(field.replace(/\r$/, ""));
      rows.push(row);
      row = [];
      field = "";
    } else {
      field += char;
    }
  }
  if (field.length || row.length) {
    row.push(field.replace(/\r$/, ""));
    rows.push(row);
  }
  return rows;
}

function coerce(value, header) {
  if (value === "") return null;
  if (/^(GEOID20|source_id|state|state_abbr|county|County24|geography|indicator_key|indicator|period|unit|display_value|flag|publisher|dataset|url|vintage|retrieved_at_utc|sha256|analytical_purpose|grain|recommendation|limitation|check|status|expected|note|distance_method|threshold|field|source|definition|processing_note)$/i.test(header)) return value;
  const number = Number(value);
  return Number.isFinite(number) ? number : value;
}

async function readCsv(relativePath, selectHeaders = null, filter = null) {
  const matrix = parseCsv(await fs.readFile(path.join(root, relativePath), "utf8"));
  const headers = matrix[0];
  const indexes = (selectHeaders ?? headers).map((header) => headers.indexOf(header));
  if (indexes.some((index) => index < 0)) throw new Error(`Missing selected header in ${relativePath}`);
  const outputHeaders = selectHeaders ?? headers;
  const records = matrix.slice(1).filter((values) => values.length > 1).map((values) => Object.fromEntries(headers.map((header, index) => [header, values[index] ?? ""])));
  const kept = filter ? records.filter(filter) : records;
  return {
    headers: outputHeaders,
    rows: kept.map((record) => outputHeaders.map((header) => coerce(record[header], header))),
  };
}

const globalData = await readCsv("data/processed/global_food_access_summary.csv", ["geography", "indicator", "period", "unit", "display_value", "value", "lower_bound", "upper_bound", "source_id"]);
const usStates = await readCsv("data/processed/us_food_insecurity_states_2022_2024.csv");
const retailStates = await readCsv("data/processed/us_state_retail_access_summary.csv", ["state", "state_abbr", "tract_count", "population", "low_income_population", "low_access_population", "low_access_population_pct", "low_income_low_access_population", "low_income_low_access_population_pct", "lila_tract_count", "lila_tract_pct"]);
const southeast = await readCsv("data/processed/southeast_state_comparison.csv", ["state", "state_abbr", "food_insecurity_pct", "food_insecurity_moe_pp", "very_low_food_security_pct", "low_access_population_pct", "low_income_low_access_population_pct", "lila_tract_pct", "low_access_children_pct", "low_access_seniors_pct", "low_access_no_vehicle_housing_units_pct", "low_access_snap_housing_units_pct", "food_insecurity_rank_high_to_low", "low_income_low_access_rank_high_to_low"]);
const counties = await readCsv("data/processed/alabama_county_food_access.csv");
const tracts = await readCsv("data/processed/alabama_tract_food_access.csv", ["GEOID20", "County24", "Urban", "POP2020", "PovertyRate", "TractLOWI", "DD_SRAM_LILATracts_1And10", "DD_SRAM_LAPOP1_10", "DD_SRAM_LALOWI1_10", "low_access_population_pct", "low_income_low_access_population_pct", "low_access_children_pct", "low_access_seniors_pct", "low_access_no_vehicle_housing_units_pct", "low_access_snap_housing_units_pct", "priority_rank_by_affected_low_income_count"]);
const sensitivity = await readCsv("results/sensitivity_analysis.csv");
const qa = await readCsv("results/qa_results.csv");
const assessment = await readCsv("results/dataset_assessment.csv");
const variables = await readCsv("data/metadata/variable_dictionary.csv");
const sources = await readCsv("data/metadata/source_manifest.csv", ["source_id", "publisher", "dataset", "url", "geography", "vintage", "retrieved_at_utc", "bytes", "sha256"]);

const COLORS = {
  navy: "#12304F",
  blue: "#3A7EBB",
  paleBlue: "#E9F2FA",
  green: "#4C7A5B",
  paleGreen: "#EAF3EC",
  amber: "#D89A2B",
  paleAmber: "#FFF3D8",
  red: "#A94B45",
  paleRed: "#F8E8E6",
  ink: "#172B44",
  muted: "#68778D",
  line: "#D5DFE9",
  white: "#FFFFFF",
};

const workbook = Workbook.create();

function titleBand(sheet, endColumn, title, subtitle) {
  sheet.mergeCells(`A1:${endColumn}1`);
  sheet.getRange("A1").values = [[title]];
  sheet.getRange(`A1:${endColumn}1`).format = { fill: COLORS.navy, font: { bold: true, color: COLORS.white, size: 18 }, verticalAlignment: "center" };
  sheet.getRange("A1").format.rowHeight = 34;
  sheet.mergeCells(`A2:${endColumn}2`);
  sheet.getRange("A2").values = [[subtitle]];
  sheet.getRange(`A2:${endColumn}2`).format = { fill: COLORS.paleBlue, font: { color: COLORS.ink, italic: true, size: 10 }, wrapText: true, verticalAlignment: "center" };
  sheet.getRange("A2").format.rowHeight = 30;
  sheet.showGridLines = false;
}

function styleHeader(range) {
  range.format = { fill: COLORS.blue, font: { bold: true, color: COLORS.white }, wrapText: true, verticalAlignment: "center", borders: { preset: "outside", style: "thin", color: COLORS.navy } };
  range.format.rowHeight = 34;
}

function addDataSheet(name, title, subtitle, data, endColumn, tableName, widths = {}) {
  const sheet = workbook.worksheets.add(name);
  titleBand(sheet, endColumn, title, subtitle);
  sheet.getRange(`A4:${endColumn}4`).values = [data.headers];
  styleHeader(sheet.getRange(`A4:${endColumn}4`));
  if (data.rows.length) sheet.getRange(`A5:${endColumn}${4 + data.rows.length}`).values = data.rows;
  const table = sheet.tables.add(`A4:${endColumn}${4 + data.rows.length}`, true, tableName);
  table.style = "TableStyleMedium2";
  table.showBandedRows = true;
  table.showFilterButton = true;
  sheet.getRange(`A5:${endColumn}${4 + data.rows.length}`).format.verticalAlignment = "top";
  for (const [column, width] of Object.entries(widths)) sheet.getRange(`${column}1:${column}${4 + data.rows.length}`).format.columnWidth = width;
  sheet.freezePanes.freezeRows(4);
  return sheet;
}

const summary = workbook.worksheets.add("Summary");
titleBand(summary, "J", "Data for Dinner — food-access analysis", "Global → United States → project-defined Southeast → Alabama | frozen pull: 2026-08-22");
summary.getRange("A4:J4").merge();
summary.getRange("A4").values = [["Key facts"]];
summary.getRange("A4:J4").format = { fill: COLORS.green, font: { bold: true, color: COLORS.white, size: 12 } };
summary.getRange("A6:B6").values = [["Measure", "Value"]];
styleHeader(summary.getRange("A6:B6"));
summary.getRange("A7:A14").values = [["World moderate/severe food insecurity (2023–2025)"], ["U.S. households food insecure (2024)"], ["Alabama households food insecure (2022–2024)"], ["Alabama low-income residents beyond 1/10-mile threshold"], ["Alabama LILA tracts"], ["Alabama LILA tract share"], ["QA checks passed"], ["QA checks failed"]];
summary.getRange("B7:B14").formulas = [["=INDEX(Global!$F:$F,MATCH(1,(Global!$A:$A=\"World\")*(Global!$B:$B=\"Prevalence of moderate or severe food insecurity in the total population (percent) (3-year average)\"),0))"], ["=13.7"], ["=INDEX(Southeast!$C:$C,MATCH(\"AL\",Southeast!$B:$B,0))"], ["=INDEX(Southeast!$G:$G,MATCH(\"AL\",Southeast!$B:$B,0))"], ["=151"], ["=10.5153203343"], ["=COUNTIF(QA!$B:$B,\"PASS\")"], ["=COUNTIF(QA!$B:$B,\"FAIL\")"]];
summary.getRange("B7:B10").format.numberFormat = "0.0%";
summary.getRange("B7:B10").formulas = [["=26.8/100"], ["=13.7/100"], ["=INDEX(Southeast!$C:$C,MATCH(\"AL\",Southeast!$B:$B,0))/100"], ["=INDEX(Southeast!$G:$G,MATCH(\"AL\",Southeast!$B:$B,0))/100"]];
summary.getRange("B11").format.numberFormat = "#,##0";
summary.getRange("B12").format.numberFormat = "0.0%";
summary.getRange("B12").formulas = [["=10.5153203343/100"]];
summary.getRange("B13:B14").format.numberFormat = "0";
summary.getRange("A7:B14").format.borders = { preset: "inside", style: "thin", color: COLORS.line };
summary.getRange("B7:B14").format.font = { bold: true, color: COLORS.navy };
summary.getRange("D6:J6").merge();
summary.getRange("D6").values = [["What stands out"]];
summary.getRange("D6:J6").format = { fill: COLORS.blue, font: { bold: true, color: COLORS.white } };
summary.getRange("D7:J12").merge();
summary.getRange("D7").values = [["Alabama is ninth-highest of the ten project states on the USDA household estimate (12.1% ± 2.23 points) and eighth-highest on the low-income retailer-access burden (20.2%). Its burden is just below the provisional U.S. result of 21.2%, but 10.5% of Alabama tracts are flagged low-income/low-access versus 7.5% nationally. Network distance produces a much higher burden than straight-line distance, so the method is part of the result."]];
summary.getRange("D7:J12").format = { fill: COLORS.paleBlue, wrapText: true, verticalAlignment: "top", borders: { preset: "outside", style: "thin", color: COLORS.blue } };
summary.getRange("A16:J16").merge();
summary.getRange("A16").values = [["Decision"]];
summary.getRange("A16:J16").format = { fill: COLORS.amber, font: { bold: true, color: COLORS.white } };
summary.getRange("A17:J21").merge();
summary.getRange("A17").values = [["Retain USDA SRAM as the primary local dataset. It is complete for Alabama and all ten project states and supports clear population and subgroup denominators. Keep FAOSTAT and USDA household estimates as separate context/outcome layers. Do not add a broad county atlas unless the team declares a specific gap. Run allergies as a separately gated feasibility crawl."]];
summary.getRange("A17:J21").format = { fill: COLORS.paleAmber, wrapText: true, verticalAlignment: "top", borders: { preset: "outside", style: "thin", color: COLORS.amber } };
summary.getRange("A23:J23").merge();
summary.getRange("A23").values = [["Comparability boundary"]];
summary.getRange("A23:J23").format = { fill: COLORS.red, font: { bold: true, color: COLORS.white } };
summary.getRange("A24:J27").merge();
summary.getRange("A24").values = [["FAOSTAT population indicators, USDA household food insecurity, and tract-level SNAP-retailer proximity have different universes, units, and meanings. The workbook keeps them on separate sheets and does not compute a combined score."]];
summary.getRange("A24:J27").format = { fill: COLORS.paleRed, wrapText: true, verticalAlignment: "top", borders: { preset: "outside", style: "thin", color: COLORS.red } };
summary.getRange("A1:A27").format.columnWidth = 51;
summary.getRange("B1:B27").format.columnWidth = 18;
summary.getRange("C1:C27").format.columnWidth = 3;
summary.getRange("D1:J27").format.columnWidth = 15;
summary.freezePanes.freezeRows(2);

const globalSheet = addDataSheet("Global", "Global food-access indicators", "Latest selected FAOSTAT values; do not compare these population measures as if they were USDA household or tract measures", globalData, "I", "GlobalIndicators", { A: 24, B: 64, C: 15, D: 12, E: 14, F: 12, G: 12, H: 12, I: 14 });
globalSheet.getRange(`F5:H${4 + globalData.rows.length}`).format.numberFormat = "0.0";

const usSheet = addDataSheet("US States", "U.S. and state household food insecurity", "USDA ERS 2022–2024 state averages; margins of error are percentage points", usStates, "F", "USStateFoodSecurity", { A: 28, B: 14, C: 18, D: 19, E: 22, F: 21 });
usSheet.getRange(`C5:F${4 + usStates.rows.length}`).format.numberFormat = "0.0";

const retailSheet = addDataSheet("Retail by State", "U.S. state retailer-access summary", "USDA 2025 SRAM, driving distance: 1 mile urban / 10 miles rural", retailStates, "K", "RetailStateSummary", { A: 24, B: 10, C: 12, D: 15, E: 18, F: 18, G: 16, H: 22, I: 22, J: 16, K: 14 });
retailSheet.getRange(`C5:F${4 + retailStates.rows.length}`).format.numberFormat = "#,##0";
retailSheet.getRange(`G5:G${4 + retailStates.rows.length}`).format.numberFormat = "0.0";
retailSheet.getRange(`H5:H${4 + retailStates.rows.length}`).format.numberFormat = "#,##0";
retailSheet.getRange(`I5:I${4 + retailStates.rows.length}`).format.numberFormat = "0.0";
retailSheet.getRange(`J5:J${4 + retailStates.rows.length}`).format.numberFormat = "#,##0";
retailSheet.getRange(`K5:K${4 + retailStates.rows.length}`).format.numberFormat = "0.0";

const seSheet = addDataSheet("Southeast", "Project-defined Southeast comparison", "AL, AR, FL, GA, KY, LA, MS, NC, SC, TN; outcome and proximity columns remain distinct", southeast, "N", "SoutheastComparison", { A: 22, B: 9, C: 18, D: 18, E: 18, F: 18, G: 22, H: 15, I: 17, J: 17, K: 22, L: 20, M: 16, N: 20 });
seSheet.getRange(`C5:L${4 + southeast.rows.length}`).format.numberFormat = "0.0";
seSheet.getRange(`M5:N${4 + southeast.rows.length}`).format.numberFormat = "0";
seSheet.getRange(`A5:N${4 + southeast.rows.length}`).conditionalFormats.add("custom", { formula: "=$B5=\"AL\"", format: { fill: "#DCEBFA", font: { bold: true, color: COLORS.navy } } });

const countySheet = addDataSheet("Alabama Counties", "Alabama county retailer-access summary", "Sorted by the number of low-income residents beyond the 1-mile urban / 10-mile rural network threshold", counties, "P", "AlabamaCounties", { A: 24, B: 11, C: 14, D: 18, E: 19, F: 18, G: 18, H: 22, I: 22, J: 14, K: 14, L: 17, M: 17, N: 20, O: 20, P: 16 });
countySheet.getRange(`B5:E${4 + counties.rows.length}`).format.numberFormat = "#,##0";
countySheet.getRange(`F5:F${4 + counties.rows.length}`).format.numberFormat = "0.0";
countySheet.getRange(`G5:G${4 + counties.rows.length}`).format.numberFormat = "#,##0";
countySheet.getRange(`H5:H${4 + counties.rows.length}`).format.numberFormat = "0.0";
countySheet.getRange(`I5:I${4 + counties.rows.length}`).format.numberFormat = "#,##0";
countySheet.getRange(`J5:N${4 + counties.rows.length}`).format.numberFormat = "0.0";
countySheet.getRange(`O5:P${4 + counties.rows.length}`).format.numberFormat = "0";

const tractSheet = addDataSheet("Alabama Tracts", "Alabama tract retailer-access detail", "All 1,436 tracts; identifiers are stored as 11-character text and high-group-quarters flags remain available in processed data", tracts, "P", "AlabamaTracts", { A: 15, B: 24, C: 9, D: 12, E: 13, F: 14, G: 17, H: 18, I: 22, J: 18, K: 22, L: 18, M: 18, N: 22, O: 20, P: 15 });
tractSheet.getRange(`A5:A${4 + tracts.rows.length}`).format.numberFormat = "@";
tractSheet.getRange(`D5:D${4 + tracts.rows.length}`).format.numberFormat = "#,##0";
tractSheet.getRange(`E5:E${4 + tracts.rows.length}`).format.numberFormat = "0.0";
tractSheet.getRange(`F5:I${4 + tracts.rows.length}`).format.numberFormat = "#,##0";
tractSheet.getRange(`J5:O${4 + tracts.rows.length}`).format.numberFormat = "0.0";

const sensSheet = addDataSheet("Sensitivity", "Distance and threshold sensitivity", "The primary result is the driving-distance 1-mile urban / 10-mile rural row", sensitivity, "I", "SensitivityResults", { A: 28, B: 16, C: 24, D: 20, E: 20, F: 25, G: 25, H: 16, I: 16 });
sensSheet.getRange(`D5:D${4 + sensitivity.rows.length}`).format.numberFormat = "#,##0";
sensSheet.getRange(`E5:E${4 + sensitivity.rows.length}`).format.numberFormat = "0.0";
sensSheet.getRange(`F5:F${4 + sensitivity.rows.length}`).format.numberFormat = "#,##0";
sensSheet.getRange(`G5:G${4 + sensitivity.rows.length}`).format.numberFormat = "0.0";
sensSheet.getRange(`H5:H${4 + sensitivity.rows.length}`).format.numberFormat = "#,##0";
sensSheet.getRange(`I5:I${4 + sensitivity.rows.length}`).format.numberFormat = "0.0";
sensSheet.getRange(`A5:I${4 + sensitivity.rows.length}`).conditionalFormats.add("custom", { formula: "=AND($B5=\"Driving\",$C5=\"1 urban / 10 rural\")", format: { fill: COLORS.paleGreen, font: { bold: true, color: COLORS.green } } });

const qaSheet = addDataSheet("QA", "Quality-assurance results", "No blocking failures; one reviewed source exception is outside Alabama and the project-defined Southeast", qa, "E", "QAResults", { A: 39, B: 13, C: 20, D: 36, E: 86 });
qaSheet.getRange(`B5:B${4 + qa.rows.length}`).conditionalFormats.add("containsText", { text: "PASS", format: { fill: COLORS.paleGreen, font: { bold: true, color: COLORS.green } } });
qaSheet.getRange(`B5:B${4 + qa.rows.length}`).conditionalFormats.add("containsText", { text: "REVIEW", format: { fill: COLORS.paleAmber, font: { bold: true, color: COLORS.amber } } });
qaSheet.getRange(`B5:B${4 + qa.rows.length}`).conditionalFormats.add("containsText", { text: "FAIL", format: { fill: COLORS.paleRed, font: { bold: true, color: COLORS.red } } });
qaSheet.getRange(`A5:E${4 + qa.rows.length}`).format.wrapText = true;

const assessSheet = addDataSheet("Assessment", "Dataset sufficiency and change recommendations", "KEEP the primary local dataset; add other data only against a declared analytical gap", assessment, "F", "DatasetAssessment", { A: 28, B: 52, C: 26, D: 31, E: 30, F: 72 });
assessSheet.getRange(`A5:F${4 + assessment.rows.length}`).format.wrapText = true;

const variableSheet = addDataSheet("Variables", "Analysis variable dictionary", "Source definitions and processing notes for retained fields", variables, "E", "VariableDictionary", { A: 32, B: 23, C: 76, D: 16, E: 68 });
variableSheet.getRange(`A5:E${4 + variables.rows.length}`).format.wrapText = true;

const sourceSheet = addDataSheet("Sources", "Frozen official-source manifest", "URLs, observation vintages, retrieval timestamps, file sizes, and SHA-256 hashes", sources, "I", "SourceManifest", { A: 20, B: 38, C: 50, D: 82, E: 28, F: 39, G: 27, H: 16, I: 68 });
sourceSheet.getRange(`A5:I${4 + sources.rows.length}`).format.wrapText = true;
sourceSheet.getRange(`G5:G${4 + sources.rows.length}`).format.numberFormat = "yyyy-mm-dd hh:mm";
sourceSheet.getRange(`H5:H${4 + sources.rows.length}`).format.numberFormat = "#,##0";

await fs.mkdir(previewDir, { recursive: true });
const renderTargets = [
  ["Summary", "A1:J27"],
  ["Global", "A1:I16"],
  ["US States", "A1:F16"],
  ["Retail by State", "A1:K14"],
  ["Southeast", "A1:N14"],
  ["Alabama Counties", "A1:P14"],
  ["Alabama Tracts", "A1:P14"],
  ["Sensitivity", "A1:I16"],
  ["QA", `A1:E${4 + qa.rows.length}`],
  ["Assessment", `A1:F${4 + assessment.rows.length}`],
  ["Variables", `A1:E${4 + variables.rows.length}`],
  ["Sources", `A1:I${4 + sources.rows.length}`],
];
for (const [sheetName, range] of renderTargets) {
  const preview = await workbook.render({ sheetName, range, scale: 1, format: "png" });
  const safe = sheetName.toLowerCase().replace(/[^a-z0-9]+/g, "-");
  await fs.writeFile(path.join(previewDir, `${safe}.png`), new Uint8Array(await preview.arrayBuffer()));
}

const summaryInspect = await workbook.inspect({ kind: "table", range: "Summary!A1:J27", include: "values,formulas", tableMaxRows: 27, tableMaxCols: 10, maxChars: 12000 });
const southeastInspect = await workbook.inspect({ kind: "table", range: "Southeast!A1:N14", include: "values,formulas", tableMaxRows: 14, tableMaxCols: 14, maxChars: 12000 });
const errors = await workbook.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A", options: { useRegex: true, maxResults: 300 }, summary: "final formula error scan", maxChars: 12000 });
await fs.mkdir(outputDir, { recursive: true });
await fs.writeFile(path.join(previewDir, "summary.inspect.ndjson"), summaryInspect.ndjson);
await fs.writeFile(path.join(previewDir, "southeast.inspect.ndjson"), southeastInspect.ndjson);
await fs.writeFile(path.join(previewDir, "errors.inspect.ndjson"), errors.ndjson);

const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);
console.log(JSON.stringify({ outputPath, previewDir, sheets: renderTargets.length, formulaErrorScan: errors.ndjson }, null, 2));

