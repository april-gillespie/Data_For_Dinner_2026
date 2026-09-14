import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const root = process.cwd();
const manifestPath = path.join(root, "faostat_datasets_E_2026-08-19.json");
const schemaPath = path.join(root, "faostat_zip_schemas_2026-08-19.json");
const outputDir = path.join(root, "outputs", "faostat-data-dictionary-2026-08-19");
const outputPath = path.join(outputDir, "FAOSTAT_Site_Wide_Data_Dictionary_2026-08-19.xlsx");
const previewDir = path.join(outputDir, "previews");

const manifest = JSON.parse(await fs.readFile(manifestPath, "utf8"));
const schemaPayload = JSON.parse(await fs.readFile(schemaPath, "utf8"));
const datasets = manifest.Datasets.Dataset;
const schemaByCode = new Map(schemaPayload.datasets.map((row) => [row.dataset_code, row]));

const sourceManifestUrl = "https://bulks-faostat.fao.org/production/datasets_E.json";
const faostatHomeUrl = "https://www.fao.org/faostat/en/";
const apiAnnouncementUrl = "https://www.fao.org/statistics/highlights-archive/highlights-detail/faostat-launches-a-new-api-developer-portal-to-make-data-access-easier/en";
const caliperUrl = "https://www.fao.org/statistics/caliper/classifications/en";
const methodsUrl = "https://www.fao.org/statistics/methods-and-standards/agriculture/en";

const COLORS = {
  navy: "#164B74",
  blue: "#2F80B7",
  paleBlue: "#EAF4FA",
  green: "#5A8F3D",
  paleGreen: "#EDF5E8",
  amber: "#D99B2B",
  paleAmber: "#FFF4DB",
  archive: "#8A5A44",
  paleArchive: "#F4E9E4",
  ink: "#23313D",
  muted: "#60717E",
  line: "#D5E0E7",
  white: "#FFFFFF",
};

function splitDatasetName(fullName) {
  const index = fullName.indexOf(":");
  if (index < 0) return { group: "Unclassified", name: fullName };
  return { group: fullName.slice(0, index).trim(), name: fullName.slice(index + 1).trim() };
}

function parseSizeKb(value) {
  const match = String(value ?? "").match(/[\d.]+/);
  return match ? Number(match[0]) : null;
}

function statusFor(group) {
  return group === "Discontinued archives and data series" ? "Archive / discontinued" : "Current catalog";
}

function normalizedConcept(column) {
  return column
    .replace(/ Code(?: \([^)]*\))?$/i, "")
    .replace(/\s+/g, " ")
    .trim();
}

const definitions = {
  "Activity": "Activity category used to disaggregate the observation.",
  "Area": "FAOSTAT reporting geography label; may represent a country, territory, region, or special aggregate supported by the dataset.",
  "Breakdown Variable": "Survey breakdown dimension used to segment the reported indicator.",
  "Breadown by Sex of the Household Head": "Sex-of-household-head breakdown label. The misspelling is preserved from the source CSV header.",
  "Census Year": "Reference year of the agricultural census observation.",
  "Cost Category": "Agricultural research expenditure cost category.",
  "Currency": "Currency label associated with the reported exchange-rate observation.",
  "Degree": "Researcher education or degree category.",
  "Donor": "Donor geography or organization providing the development flow.",
  "Element": "Statistical measure or operation applied to the dimension combination. Interpret Value together with Element and Unit.",
  "Factor": "Primary factor category used in the food-value-chain dataset.",
  "Flag": "Data-status, estimation, or provenance symbol. Decode with the dataset's companion Flags CSV when supplied.",
  "Food Group": "Food-group category used to classify dietary observations.",
  "Food Value": "Food-value-chain category used in value-share observations.",
  "Geographic Level": "Survey or indicator geographic aggregation level.",
  "Indicator": "Named indicator whose observation is reported.",
  "Industry": "Industry category used in food-value-chain observations.",
  "Institution": "Institutional sector or institution category.",
  "Item": "Dataset-specific subject, commodity, product, or indicator item. Decode with the dataset's ItemCodes CSV when supplied.",
  "Months": "Month or period label for subannual observations.",
  "Note": "Optional record-level explanatory note supplied with the observation.",
  "Partner Country": "Partner geography in a bilateral trade observation.",
  "Partner Countries": "Partner geography in a bilateral trade observation.",
  "Population Age Group": "Age-group category used to disaggregate an indicator.",
  "Purpose": "Purpose category used to classify development flows.",
  "Qualifier": "Qualifier category that refines a rural-livelihood indicator.",
  "Recipient Country": "Recipient geography of a development flow or food-aid shipment.",
  "Release": "Named publication or release version for the reported observation.",
  "Reporter Country": "Reporting geography in a bilateral trade observation.",
  "Reporter Countries": "Reporting geography in a bilateral trade observation.",
  "Sex": "Sex category used to disaggregate an indicator.",
  "Source": "Source category or originating data source associated with the observation.",
  "Survey": "Survey identifier or survey label from which the statistics were derived.",
  "Unit": "Measurement unit for Value; must be interpreted with Element or Indicator.",
  "Value": "Reported numeric observation for the full combination of dimensions in the row.",
  "WCA Round": "World Census of Agriculture programme round.",
  "Year": "Reference year of the observation.",
};

function fieldRole(column) {
  if (column === "Value") return "Observation value";
  if (column === "Unit") return "Measure metadata";
  if (column === "Flag" || column === "Note") return "Provenance / quality";
  if (column.includes("Code")) return "Dimension code";
  if (column === "Year" || column === "Months" || column === "Census Year" || column === "WCA Round") return "Time / reference period";
  return "Dimension label";
}

function suggestedType(column) {
  if (column === "Value") return "Decimal number";
  if (column === "Year" || column === "Census Year") return "Integer";
  if (column.includes("Code")) return "Text identifier";
  return "Text";
}

function definitionFor(column) {
  if (column === "Area Code (M49)" || column.includes("Country Code (M49)")) {
    return "United Nations M49 geography code; store as text to preserve leading zeroes.";
  }
  if (column === "Item Code (CPC)") return "Central Product Classification code supplied for the item; store as text.";
  if (column === "Item Code (FBS)") return "Food Balance Sheets classification code supplied for the item; store as text.";
  if (column === "Item Code (SDG)" || column === "Sex Code (SDG)" || column === "Activity Code (SDG)") {
    return "SDG-aligned code supplied for the corresponding dimension; store as text.";
  }
  if (column.includes("Code")) {
    const concept = normalizedConcept(column);
    return `Dataset-specific identifier for ${concept}. Store as text and decode with the matching companion lookup when supplied.`;
  }
  return definitions[column] ?? definitions[normalizedConcept(column)] ?? `Source-system label for the ${normalizedConcept(column)} dimension.`;
}

const lookupTokens = [
  ["Reporter Country", "ReporterCountries"],
  ["Partner Country", "PartnerCountries"],
  ["Population Age Group", "PopulationAgeGroups"],
  ["Geographic Level", "GeographicLevels"],
  ["Cost Category", "CostCategorys"],
  ["Breakdown Variable", "Breakdown"],
  ["Area", "AreaCodes"],
  ["Item", "ItemCodes"],
  ["Element", "Elements"],
  ["Flag", "Flags"],
  ["Source", "Sources"],
  ["Indicator", "Indicators"],
  ["Sex", "Sex"],
  ["Activity", "Activities"],
  ["Purpose", "Purposes"],
  ["Qualifier", "Qualifiers"],
  ["Survey", "Surveys"],
  ["Institution", "Institutions"],
  ["Degree", "Degrees"],
  ["Release", "Releases"],
  ["Currency", "Currencys"],
];

function lookupFor(column, companions) {
  const concept = normalizedConcept(column);
  for (const [prefix, token] of lookupTokens) {
    if (concept.startsWith(prefix)) {
      const match = companions.find((name) => name.toLowerCase().includes(token.toLowerCase()));
      if (match) return match;
    }
  }
  return "Not supplied as a companion CSV";
}

function inferCompanionType(filename) {
  const match = filename.match(/_E_([^/]+)\.csv$/i);
  return match ? match[1] : "Lookup / metadata";
}

const records = datasets.map((dataset) => {
  const parsed = splitDatasetName(dataset.DatasetName);
  const schema = schemaByCode.get(dataset.DatasetCode);
  return {
    ...dataset,
    group: parsed.group,
    shortName: parsed.name,
    status: statusFor(parsed.group),
    schema,
  };
});

const variantMap = new Map();
for (const record of records) {
  const key = record.schema.columns.join("\u241F");
  if (!variantMap.has(key)) variantMap.set(key, []);
  variantMap.get(key).push(record.DatasetCode);
}
const variants = [...variantMap.entries()]
  .map(([key, codes]) => ({ key, codes, columns: key.split("\u241F") }))
  .sort((a, b) => b.codes.length - a.codes.length || a.key.localeCompare(b.key));
variants.forEach((variant, index) => (variant.id = `V${String(index + 1).padStart(2, "0")}`));
const variantIdByKey = new Map(variants.map((variant) => [variant.key, variant.id]));

const catalogRows = records.map((record) => [
  record.status,
  record.group,
  record.DatasetCode,
  record.shortName,
  record.Topic ?? "Not supplied in manifest",
  new Date(record.DateUpdate),
  Number(record.FileRows),
  parseSizeKb(record.FileSize),
  record.FileType,
  record.CompressionFormat,
  record.schema.main_csv,
  record.schema.columns.length,
  record.schema.companion_csvs.length,
  variantIdByKey.get(record.schema.columns.join("\u241F")),
  record.FileLocation,
  `${faostatHomeUrl}#data/${record.DatasetCode}`,
  record.Contact ?? "Not supplied",
  record.Email ?? "Not supplied",
]);

const detailRows = records.map((record) => [
  record.group,
  record.DatasetCode,
  record.shortName,
  record.Topic ?? "Not supplied in manifest",
  record.DatasetDescription ?? "Not supplied in manifest",
  record.Contact ?? "Not supplied",
  record.Email ?? "Not supplied",
  record.FileLocation,
]);

const fieldRows = [];
for (const record of records) {
  record.schema.columns.forEach((column, index) => {
    fieldRows.push([
      record.group,
      record.DatasetCode,
      record.shortName,
      index + 1,
      column,
      fieldRole(column),
      suggestedType(column),
      definitionFor(column),
      lookupFor(column, record.schema.companion_csvs),
      "Not declared by the bulk-file manifest",
      "Exact normalized CSV header",
    ]);
  });
}

const fileRows = [];
for (const record of records) {
  fileRows.push([
    record.group,
    record.DatasetCode,
    record.shortName,
    "Observation file",
    "Normalized long-format data",
    record.schema.main_csv,
    record.FileLocation,
  ]);
  for (const filename of record.schema.companion_csvs) {
    fileRows.push([
      record.group,
      record.DatasetCode,
      record.shortName,
      "Companion lookup",
      inferCompanionType(filename),
      filename,
      record.FileLocation,
    ]);
  }
}

const correctionRows = [
  ["Scope", "A site-wide dictionary", "The draft mostly catalogs one Food Balances dataset and then adds platform capabilities and possible reports.", "Use the official manifest as the dataset spine; keep capabilities and use cases separate.", "Official bulk manifest + exact headers"],
  ["Dataset inventory", "Top-level groups only", "The current English bulk manifest contains 69 datasets across 20 group labels.", "List every dataset code and name, not just broad group headings.", sourceManifestUrl],
  ["Archive coverage", "Archive series are mixed into other discussion or omitted", "Seven records are explicitly grouped as Discontinued archives and data series.", "Label them as archive/discontinued and keep them separate from current-catalog datasets.", sourceManifestUrl],
  ["Food Balances coverage", "Four Food Balances domains", "The manifest lists five: CB, CBH, FBS, FBSH, and SCL.", "Add historical commodity balances (CBH) and retain exact codes.", sourceManifestUrl],
  ["Universal dimensions", "Area × Element × Item × Year is the platform model", "That pattern is common but not universal. Trade matrices add reporter/partner; investment flows add donor/recipient/purpose; surveys and gender add specialized dimensions.", "Define the grain separately for each dataset from its exact header.", "Field Dictionary sheet"],
  ["Bulk output fields", "Domain / Domain Code are listed as standard fields", "The 69 normalized bulk headers do not include Domain or Domain Code columns; dataset identity is carried by the selected ZIP/dataset code.", "Treat dataset code as file-level metadata, not an asserted row column.", "Field Dictionary sheet"],
  ["Items", "A prose list of food commodities represents available items", "The list is partial, domain-specific, and difficult to audit. Item systems vary, including CPC, FBS, SDG, and dataset-specific identifiers.", "Use each ZIP's official ItemCodes companion CSV; do not hand-maintain a universal item list.", "File Inventory sheet"],
  ["Areas", "More than 245 countries and territories implies one universal Area list", "Coverage and supported aggregates vary by dataset; some datasets use survey geography or donor/recipient/reporter/partner dimensions.", "Use dataset-specific companion geography lists and preserve M49 as text.", sourceManifestUrl],
  ["Years", "2010–2023 is presented as a website year range", "That range is specific to the observed FBS selector and is neither site-wide nor safely permanent.", "Derive minimum and maximum periods from each observation file when doing analysis; do not hard-code a site-wide year range.", "Exact headers + manifest topic/description"],
  ["Definitions", "Short interpretations are supplied without field-level provenance", "Many terms are valid, but exact definitions belong to dataset metadata and companion lists.", "Keep a standardized field definition and link to the dataset's official metadata source.", "Dataset Details + Sources sheets"],
  ["API authentication", "Personal access token authentication is stated as a capability", "The cited FAO launch announcement describes the API features but does not substantiate that specific authentication claim.", "Remove the claim unless the current developer-portal documentation is cited directly.", apiAnnouncementUrl],
  ["Capabilities vs. data", "Query builder, Power Query, rankings, reports, R/Python, and MCP are mixed into the dictionary", "These describe access channels or products, not datasets, fields, or code lists.", "Put access channels in a separate methods note; keep the dictionary focused on datasets and schemas.", faostatHomeUrl],
  ["Interpretation", "Food Balances are availability/accounting, not intake", "This caution is correct and should remain.", "Retain it prominently when FBS/SUA data are used.", `${faostatHomeUrl}#data/FBS`],
  ["Units", "Values can be compared after selecting item and year", "Values are not comparable without Element/Indicator and Unit, and sometimes Source, Release, Month, or other dimensions.", "Define each dataset's row grain and require Unit in analytical keys.", "Field Dictionary sheet"],
];

const sourceRows = [
  ["FAOSTAT English bulk-download manifest", sourceManifestUrl, "Authoritative dataset code/name, topic, description, update date, row count, size, and ZIP location used for this workbook.", new Date("2026-08-19")],
  ["FAOSTAT homepage", faostatHomeUrl, "Platform scope and links to data exploration, bulk downloads, selected indicators, rankings, and the developer portal.", new Date("2026-08-19")],
  ["FAO API Developer Portal announcement", apiAnnouncementUrl, "Official summary of API capabilities: all domains, dimensions, metadata/codes, query builder, and JSON/CSV outputs.", new Date("2026-08-19")],
  ["FAO Caliper classifications", caliperUrl, "Official classification catalog, including the FAOSTAT Commodity List and related international classifications.", new Date("2026-08-19")],
  ["FAO methods and standards — agriculture", methodsUrl, "Official context on FAOSTAT commodity classifications and the transition toward CPC expanded for agriculture.", new Date("2026-08-19")],
  ["Normalized ZIP central directories and CSV headers", sourceManifestUrl, "Exact main CSV headers and companion CSV filenames were read from every manifest ZIP using byte-range requests; no observation files were copied into the workbook.", new Date("2026-08-19")],
];

const groups = [...new Set(records.map((record) => record.group))].sort((a, b) => a.localeCompare(b));

const workbook = Workbook.create();
const overview = workbook.worksheets.add("Overview");
const groupSummary = workbook.worksheets.add("Group Summary");
const catalog = workbook.worksheets.add("Dataset Catalog");
const details = workbook.worksheets.add("Dataset Details");
const fields = workbook.worksheets.add("Field Dictionary");
const files = workbook.worksheets.add("File Inventory");
const schemaVariants = workbook.worksheets.add("Schema Variants");
const corrections = workbook.worksheets.add("Draft Corrections");
const sources = workbook.worksheets.add("Sources");

function titleBand(sheet, endColumn, title, subtitle) {
  sheet.mergeCells(`A1:${endColumn}1`);
  sheet.getRange("A1").values = [[title]];
  sheet.getRange(`A1:${endColumn}1`).format = {
    fill: COLORS.navy,
    font: { bold: true, color: COLORS.white, size: 18 },
    verticalAlignment: "center",
  };
  sheet.getRange("A1").format.rowHeight = 32;
  sheet.mergeCells(`A2:${endColumn}2`);
  sheet.getRange("A2").values = [[subtitle]];
  sheet.getRange(`A2:${endColumn}2`).format = {
    fill: COLORS.paleBlue,
    font: { color: COLORS.ink, italic: true, size: 10 },
    wrapText: true,
    verticalAlignment: "center",
  };
  sheet.getRange("A2").format.rowHeight = 30;
  sheet.showGridLines = false;
}

function styleTableHeader(range) {
  range.format = {
    fill: COLORS.blue,
    font: { bold: true, color: COLORS.white },
    wrapText: true,
    verticalAlignment: "center",
    borders: { preset: "outside", style: "thin", color: COLORS.navy },
  };
  range.format.rowHeight = 32;
}

function addTable(sheet, range, name) {
  const table = sheet.tables.add(range, true, name);
  table.style = "TableStyleMedium2";
  table.showBandedRows = true;
  table.showFilterButton = true;
  return table;
}

titleBand(overview, "J", "FAOSTAT Site-Wide Data Dictionary", "Verified against the English bulk-download manifest and all 69 normalized ZIP schemas on 2026-08-19");
overview.getRange("A4:B4").values = [["Coverage metric", "Value"]];
styleTableHeader(overview.getRange("A4:B4"));
overview.getRange("A5:A12").values = [
  ["Datasets"],
  ["Catalog groups"],
  ["Current-catalog datasets"],
  ["Archive / discontinued datasets"],
  ["Published observation rows"],
  ["Exact source fields cataloged"],
  ["Distinct normalized schemas"],
  ["Companion lookup files"],
];
overview.getRange("B5:B12").formulas = [
  [`=COUNTA('Dataset Catalog'!$C$5:$C$${4 + catalogRows.length})`],
  [`=COUNTA('Group Summary'!$A$5:$A$${4 + groups.length})`],
  [`=COUNTIF('Dataset Catalog'!$A$5:$A$${4 + catalogRows.length},"Current catalog")`],
  [`=COUNTIF('Dataset Catalog'!$A$5:$A$${4 + catalogRows.length},"Archive / discontinued")`],
  [`=SUM('Dataset Catalog'!$G$5:$G$${4 + catalogRows.length})`],
  [`=COUNTA('Field Dictionary'!$B$5:$B$${4 + fieldRows.length})`],
  [`=COUNTA('Schema Variants'!$A$5:$A$${4 + variants.length})`],
  [`=COUNTIF('File Inventory'!$D$5:$D$${4 + fileRows.length},"Companion lookup")`],
];
overview.getRange("A5:B12").format.borders = { preset: "inside", style: "thin", color: COLORS.line };
overview.getRange("B5:B12").format.numberFormat = "#,##0";
overview.getRange("B5:B12").format.font = { bold: true, color: COLORS.navy };
overview.getRange("D4:J4").merge();
overview.getRange("D4").values = [["What this workbook is"]];
overview.getRange("D4:J4").format = { fill: COLORS.green, font: { bold: true, color: COLORS.white } };
overview.getRange("D5:J8").merge();
overview.getRange("D5").values = [["A reproducible catalog of every dataset in FAOSTAT's current English bulk manifest, each dataset's exact normalized CSV columns, and every companion lookup filename supplied in its ZIP. It inventories structure and metadata; it does not duplicate hundreds of millions of observation values or hand-maintain changing item and area lists."]];
overview.getRange("D5:J8").format = { fill: COLORS.paleGreen, font: { color: COLORS.ink }, wrapText: true, verticalAlignment: "top", borders: { preset: "outside", style: "thin", color: COLORS.green } };
overview.getRange("D10:J10").merge();
overview.getRange("D10").values = [["How to read FAOSTAT"]];
overview.getRange("D10:J10").format = { fill: COLORS.blue, font: { bold: true, color: COLORS.white } };
overview.getRange("D11:J14").merge();
overview.getRange("D11").values = [["Dataset code → dataset-specific dimensions and code lists → observation rows. Area × Element × Item × Year is common, but not universal. Bilateral trade, development flows, surveys, gender, and census datasets add specialized dimensions. Always interpret Value with the full row grain, especially Element or Indicator and Unit."]];
overview.getRange("D11:J14").format = { fill: COLORS.paleBlue, font: { color: COLORS.ink }, wrapText: true, verticalAlignment: "top", borders: { preset: "outside", style: "thin", color: COLORS.blue } };
overview.getRange("A15:J15").merge();
overview.getRange("A15").values = [["Recommended workflow"]];
overview.getRange("A15:J15").format = { fill: COLORS.amber, font: { bold: true, color: COLORS.white } };
overview.getRange("A16:J19").merge();
overview.getRange("A16").values = [["1) Choose a dataset in Dataset Catalog.  2) Inspect its exact row fields in Field Dictionary.  3) Use File Inventory to locate official area/item/element/flag and specialized code lists inside the ZIP.  4) Read Dataset Details before interpreting the measure.  5) Derive actual year coverage and dimension members from the selected data file at analysis time."]];
overview.getRange("A16:J19").format = { fill: COLORS.paleAmber, wrapText: true, verticalAlignment: "top", borders: { preset: "outside", style: "thin", color: COLORS.amber } };
overview.getRange("A21:J21").merge();
overview.getRange("A21").values = [["Important boundary"]];
overview.getRange("A21:J21").format = { fill: COLORS.archive, font: { bold: true, color: COLORS.white } };
overview.getRange("A22:J25").merge();
overview.getRange("A22").values = [["The bulk manifest is the authoritative inventory used here. Website features such as selected indicators, rankings, reports, query builders, API tooling, and analytical briefs are access or presentation products, not additional bulk datasets unless they appear in the manifest. The catalog changes over time; refresh it from the source URL shown on the Sources sheet."]];
overview.getRange("A22:J25").format = { fill: COLORS.paleArchive, wrapText: true, verticalAlignment: "top", borders: { preset: "outside", style: "thin", color: COLORS.archive } };
overview.getRange("A4:B12").format.columnWidth = 24;
overview.getRange("A1:A25").format.columnWidth = 30;
overview.getRange("B1:B25").format.columnWidth = 18;
overview.getRange("C1:C25").format.columnWidth = 3;
overview.getRange("D1:J25").format.columnWidth = 14;
overview.freezePanes.freezeRows(2);

titleBand(groupSummary, "E", "FAOSTAT Catalog Groups", "Counts are formula-driven from Dataset Catalog; archive status follows the manifest's explicit archive group");
groupSummary.getRange("A4:E4").values = [["Group", "Datasets", "Current catalog", "Archive / discontinued", "Published rows"]];
styleTableHeader(groupSummary.getRange("A4:E4"));
groupSummary.getRange(`A5:A${4 + groups.length}`).values = groups.map((group) => [group]);
for (let index = 0; index < groups.length; index += 1) {
  const row = 5 + index;
  groupSummary.getRange(`B${row}:E${row}`).formulas = [[
    `=COUNTIF('Dataset Catalog'!$B$5:$B$${4 + catalogRows.length},A${row})`,
    `=COUNTIFS('Dataset Catalog'!$B$5:$B$${4 + catalogRows.length},A${row},'Dataset Catalog'!$A$5:$A$${4 + catalogRows.length},"Current catalog")`,
    `=COUNTIFS('Dataset Catalog'!$B$5:$B$${4 + catalogRows.length},A${row},'Dataset Catalog'!$A$5:$A$${4 + catalogRows.length},"Archive / discontinued")`,
    `=SUMIF('Dataset Catalog'!$B$5:$B$${4 + catalogRows.length},A${row},'Dataset Catalog'!$G$5:$G$${4 + catalogRows.length})`,
  ]];
}
addTable(groupSummary, `A4:E${4 + groups.length}`, "GroupSummaryTable");
groupSummary.getRange(`B5:E${4 + groups.length}`).format.numberFormat = "#,##0";
groupSummary.getRange(`A1:A${4 + groups.length}`).format.columnWidth = 44;
groupSummary.getRange(`B1:E${4 + groups.length}`).format.columnWidth = 20;
groupSummary.freezePanes.freezeRows(4);

titleBand(catalog, "R", "Dataset Catalog", "One row per dataset in the official FAOSTAT English bulk-download manifest");
const catalogHeaders = ["Status", "Group", "Dataset Code", "Dataset", "Topic / coverage", "Last Updated", "Published Rows", "ZIP Size (KB)", "File Type", "Compression", "Main Normalized CSV", "Field Count", "Companion Files", "Schema Variant", "Bulk ZIP URL", "FAOSTAT UI URL", "Contact", "Email"];
catalog.getRange("A4:R4").values = [catalogHeaders];
styleTableHeader(catalog.getRange("A4:R4"));
catalog.getRange(`A5:R${4 + catalogRows.length}`).values = catalogRows;
addTable(catalog, `A4:R${4 + catalogRows.length}`, "DatasetCatalogTable");
catalog.getRange(`F5:F${4 + catalogRows.length}`).format.numberFormat = "yyyy-mm-dd";
catalog.getRange(`G5:H${4 + catalogRows.length}`).format.numberFormat = "#,##0";
catalog.getRange(`A5:A${4 + catalogRows.length}`).conditionalFormats.add("containsText", { text: "Archive", format: { fill: COLORS.paleArchive, font: { color: COLORS.archive, bold: true } } });
catalog.getRange(`A5:A${4 + catalogRows.length}`).conditionalFormats.add("containsText", { text: "Current", format: { fill: COLORS.paleGreen, font: { color: COLORS.green } } });
catalog.getRange(`A5:R${4 + catalogRows.length}`).format.verticalAlignment = "top";
catalog.getRange(`D5:E${4 + catalogRows.length}`).format.wrapText = true;
catalog.getRange(`A1:A${4 + catalogRows.length}`).format.columnWidth = 23;
catalog.getRange(`B1:B${4 + catalogRows.length}`).format.columnWidth = 34;
catalog.getRange(`C1:C${4 + catalogRows.length}`).format.columnWidth = 13;
catalog.getRange(`D1:D${4 + catalogRows.length}`).format.columnWidth = 38;
catalog.getRange(`E1:E${4 + catalogRows.length}`).format.columnWidth = 60;
catalog.getRange(`F1:N${4 + catalogRows.length}`).format.columnWidth = 16;
catalog.getRange(`K1:K${4 + catalogRows.length}`).format.columnWidth = 48;
catalog.getRange(`O1:P${4 + catalogRows.length}`).format.columnWidth = 48;
catalog.getRange(`Q1:Q${4 + catalogRows.length}`).format.columnWidth = 52;
catalog.getRange(`R1:R${4 + catalogRows.length}`).format.columnWidth = 30;
catalog.freezePanes.freezeRows(4);
catalog.freezePanes.freezeColumns(3);

titleBand(details, "H", "Dataset Details", "Manifest topic and description preserved verbatim as structured metadata; see Sources for provenance");
const detailHeaders = ["Group", "Dataset Code", "Dataset", "Topic / coverage", "Full Dataset Description", "Contact", "Email", "Bulk ZIP URL"];
details.getRange("A4:H4").values = [detailHeaders];
styleTableHeader(details.getRange("A4:H4"));
details.getRange(`A5:H${4 + detailRows.length}`).values = detailRows;
addTable(details, `A4:H${4 + detailRows.length}`, "DatasetDetailsTable");
details.getRange(`A5:H${4 + detailRows.length}`).format.wrapText = true;
details.getRange(`A5:H${4 + detailRows.length}`).format.verticalAlignment = "top";
details.getRange(`A1:A${4 + detailRows.length}`).format.columnWidth = 34;
details.getRange(`B1:B${4 + detailRows.length}`).format.columnWidth = 13;
details.getRange(`C1:C${4 + detailRows.length}`).format.columnWidth = 40;
details.getRange(`D1:D${4 + detailRows.length}`).format.columnWidth = 72;
details.getRange(`E1:E${4 + detailRows.length}`).format.columnWidth = 96;
details.getRange(`F1:F${4 + detailRows.length}`).format.columnWidth = 52;
details.getRange(`G1:G${4 + detailRows.length}`).format.columnWidth = 32;
details.getRange(`H1:H${4 + detailRows.length}`).format.columnWidth = 54;
details.getRange(`A5:H${4 + detailRows.length}`).format.autofitRows();
details.freezePanes.freezeRows(4);
details.freezePanes.freezeColumns(2);

titleBand(fields, "K", "Field Dictionary", "Every exact column in every normalized dataset CSV; definitions standardize structural meaning without replacing domain metadata");
const fieldHeaders = ["Group", "Dataset Code", "Dataset", "Ordinal", "Exact Source Column", "Semantic Role", "Suggested Type", "Definition", "Official Lookup in ZIP", "Nullability", "Source Method"];
fields.getRange("A4:K4").values = [fieldHeaders];
styleTableHeader(fields.getRange("A4:K4"));
fields.getRange(`A5:K${4 + fieldRows.length}`).values = fieldRows;
addTable(fields, `A4:K${4 + fieldRows.length}`, "FieldDictionaryTable");
fields.getRange(`D5:D${4 + fieldRows.length}`).format.numberFormat = "0";
fields.getRange(`A5:K${4 + fieldRows.length}`).format.verticalAlignment = "top";
fields.getRange(`H5:K${4 + fieldRows.length}`).format.wrapText = true;
fields.getRange(`A1:A${4 + fieldRows.length}`).format.columnWidth = 34;
fields.getRange(`B1:B${4 + fieldRows.length}`).format.columnWidth = 13;
fields.getRange(`C1:C${4 + fieldRows.length}`).format.columnWidth = 38;
fields.getRange(`D1:D${4 + fieldRows.length}`).format.columnWidth = 9;
fields.getRange(`E1:E${4 + fieldRows.length}`).format.columnWidth = 34;
fields.getRange(`F1:G${4 + fieldRows.length}`).format.columnWidth = 22;
fields.getRange(`H1:H${4 + fieldRows.length}`).format.columnWidth = 62;
fields.getRange(`I1:I${4 + fieldRows.length}`).format.columnWidth = 54;
fields.getRange(`J1:K${4 + fieldRows.length}`).format.columnWidth = 30;
fields.freezePanes.freezeRows(4);
fields.freezePanes.freezeColumns(3);

titleBand(files, "G", "ZIP File Inventory", "Main normalized observation file and every companion lookup CSV supplied for each dataset");
const fileHeaders = ["Group", "Dataset Code", "Dataset", "Entry Role", "Lookup / Content Type", "ZIP Entry Filename", "Bulk ZIP URL"];
files.getRange("A4:G4").values = [fileHeaders];
styleTableHeader(files.getRange("A4:G4"));
files.getRange(`A5:G${4 + fileRows.length}`).values = fileRows;
addTable(files, `A4:G${4 + fileRows.length}`, "FileInventoryTable");
files.getRange(`A5:G${4 + fileRows.length}`).format.verticalAlignment = "top";
files.getRange(`A1:A${4 + fileRows.length}`).format.columnWidth = 34;
files.getRange(`B1:B${4 + fileRows.length}`).format.columnWidth = 13;
files.getRange(`C1:C${4 + fileRows.length}`).format.columnWidth = 38;
files.getRange(`D1:E${4 + fileRows.length}`).format.columnWidth = 24;
files.getRange(`F1:F${4 + fileRows.length}`).format.columnWidth = 68;
files.getRange(`G1:G${4 + fileRows.length}`).format.columnWidth = 58;
files.freezePanes.freezeRows(4);
files.freezePanes.freezeColumns(2);

titleBand(schemaVariants, "E", "Normalized Schema Variants", "Distinct column sequences observed across the 69 normalized bulk files");
const variantHeaders = ["Variant", "Dataset Count", "Dataset Codes", "Column Count", "Exact Column Sequence"];
schemaVariants.getRange("A4:E4").values = [variantHeaders];
styleTableHeader(schemaVariants.getRange("A4:E4"));
const variantRows = variants.map((variant) => [variant.id, variant.codes.length, variant.codes.join(", "), variant.columns.length, variant.columns.join(" | ")]);
schemaVariants.getRange(`A5:E${4 + variantRows.length}`).values = variantRows;
addTable(schemaVariants, `A4:E${4 + variantRows.length}`, "SchemaVariantsTable");
schemaVariants.getRange(`A5:E${4 + variantRows.length}`).format.wrapText = true;
schemaVariants.getRange(`B5:D${4 + variantRows.length}`).format.numberFormat = "#,##0";
schemaVariants.getRange(`A1:A${4 + variantRows.length}`).format.columnWidth = 12;
schemaVariants.getRange(`B1:B${4 + variantRows.length}`).format.columnWidth = 16;
schemaVariants.getRange(`C1:C${4 + variantRows.length}`).format.columnWidth = 36;
schemaVariants.getRange(`D1:D${4 + variantRows.length}`).format.columnWidth = 15;
schemaVariants.getRange(`E1:E${4 + variantRows.length}`).format.columnWidth = 110;
schemaVariants.getRange(`A5:E${4 + variantRows.length}`).format.autofitRows();
schemaVariants.freezePanes.freezeRows(4);

titleBand(corrections, "E", "Corrections to the AI Draft", "Audit of the user-provided narrative against the official manifest and delivered bulk schemas");
const correctionHeaders = ["Issue", "Draft Position", "Verified Finding", "Recommended Correction", "Evidence"];
corrections.getRange("A4:E4").values = [correctionHeaders];
styleTableHeader(corrections.getRange("A4:E4"));
corrections.getRange(`A5:E${4 + correctionRows.length}`).values = correctionRows;
addTable(corrections, `A4:E${4 + correctionRows.length}`, "DraftCorrectionsTable");
corrections.getRange(`A5:E${4 + correctionRows.length}`).format.wrapText = true;
corrections.getRange(`A5:E${4 + correctionRows.length}`).format.verticalAlignment = "top";
corrections.getRange(`A1:A${4 + correctionRows.length}`).format.columnWidth = 24;
corrections.getRange(`B1:D${4 + correctionRows.length}`).format.columnWidth = 58;
corrections.getRange(`E1:E${4 + correctionRows.length}`).format.columnWidth = 52;
corrections.getRange(`A5:E${4 + correctionRows.length}`).format.autofitRows();
corrections.freezePanes.freezeRows(4);

titleBand(sources, "D", "Sources and Method", "Primary official sources and the extraction boundary for this workbook");
const sourceHeaders = ["Source", "URL", "How Used", "Accessed"];
sources.getRange("A4:D4").values = [sourceHeaders];
styleTableHeader(sources.getRange("A4:D4"));
sources.getRange(`A5:D${4 + sourceRows.length}`).values = sourceRows;
addTable(sources, `A4:D${4 + sourceRows.length}`, "SourcesTable");
sources.getRange(`D5:D${4 + sourceRows.length}`).format.numberFormat = "yyyy-mm-dd";
sources.getRange(`A5:D${4 + sourceRows.length}`).format.wrapText = true;
sources.getRange(`A5:D${4 + sourceRows.length}`).format.verticalAlignment = "top";
sources.getRange(`A1:A${4 + sourceRows.length}`).format.columnWidth = 40;
sources.getRange(`B1:B${4 + sourceRows.length}`).format.columnWidth = 82;
sources.getRange(`C1:C${4 + sourceRows.length}`).format.columnWidth = 78;
sources.getRange(`D1:D${4 + sourceRows.length}`).format.columnWidth = 14;
sources.getRange(`A5:D${4 + sourceRows.length}`).format.autofitRows();
sources.freezePanes.freezeRows(4);

await fs.mkdir(previewDir, { recursive: true });
const renderTargets = [
  ["Overview", "A1:J25"],
  ["Group Summary", `A1:E${Math.min(4 + groups.length, 25)}`],
  ["Dataset Catalog", "A1:J14"],
  ["Dataset Details", "A1:H10"],
  ["Field Dictionary", "A1:K16"],
  ["File Inventory", "A1:G16"],
  ["Schema Variants", `A1:E${Math.min(4 + variantRows.length, 16)}`],
  ["Draft Corrections", `A1:E${4 + correctionRows.length}`],
  ["Sources", `A1:D${4 + sourceRows.length}`],
];
for (const [sheetName, range] of renderTargets) {
  const preview = await workbook.render({ sheetName, range, scale: 1, format: "png" });
  const safeName = sheetName.toLowerCase().replace(/[^a-z0-9]+/g, "-");
  await fs.writeFile(path.join(previewDir, `${safeName}.png`), new Uint8Array(await preview.arrayBuffer()));
}

const inspectOverview = await workbook.inspect({ kind: "table", range: "Overview!A1:J25", include: "values,formulas", tableMaxRows: 25, tableMaxCols: 10, maxChars: 10000 });
console.log("OVERVIEW_INSPECT");
console.log(inspectOverview.ndjson);
const inspectCatalog = await workbook.inspect({ kind: "table", range: "Dataset Catalog!A1:R10", include: "values,formulas", tableMaxRows: 10, tableMaxCols: 18, maxChars: 10000 });
console.log("CATALOG_INSPECT");
console.log(inspectCatalog.ndjson);
const errors = await workbook.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A", options: { useRegex: true, maxResults: 300 }, summary: "final formula error scan", maxChars: 10000 });
console.log("ERROR_SCAN");
console.log(errors.ndjson);

await fs.mkdir(outputDir, { recursive: true });
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);
console.log(JSON.stringify({ outputPath, previewDir, datasetCount: records.length, groupCount: groups.length, fieldRows: fieldRows.length, fileRows: fileRows.length, schemaVariants: variants.length }, null, 2));
