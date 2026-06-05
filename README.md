# GOGET

Code for the **Global Oil and Gas Extraction Tracker (GOGET)** — a collection of
Python scripts for querying, parsing, filtering, comparing, summarizing, mapping,
and quality-checking GOGET data.

These scripts were migrated from Google Colab notebooks and converted to plain
Python (`.py`). Each script preserves its original cell order (marked with
`# ===== Cell N =====`); markdown cells were turned into comments. Colab-specific
lines (`drive.mount`, `google.colab` imports, `%magics`, `!shell` commands) were
commented out and flagged in-line, and `!pip install` lines were collected into
`requirements.txt`. The original notebook for each script is preserved under
`notebooks_original/`.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

These are standalone scripts, not an installed package — run them individually
(e.g. `python qc/goget_qc.py`).

### Credentials & external services

The notebooks ran in Colab and relied on Colab-only conveniences that were stripped
during migration. To run outside Colab you'll need to supply these yourself:

- **GEM database** — scripts in `database/` and `qc/` connect to the GEM Postgres
  database via SQLAlchemy. Connection details (host, user, password) lived in Colab
  `userdata` and are not committed; set them via environment variables.
- **Google Sheets** — scripts using `pygsheets` need a service-account JSON
  (Colab used built-in auth). See the pygsheets authentication docs.
- **Tesseract OCR** — `misc/convert_image_to_spreadsheet.py` and
  `asset_impact/extract_field_totals_brazil_powerbi.py` need the Tesseract binary
  installed on the system in addition to `pytesseract`.

## Repository layout

| Folder | Purpose |
|---|---|
| `qc/` | Quality-control application and checks |
| `database/` | Querying the GEM database and exporting to Google Sheets |
| `ownership/` | Owner/operator comparison, dedup, name matching, M&A checks |
| `compare/` | Comparing GOGET versions and external datasets |
| `parsing/` | Parsing FID, discovery, reserves & production from compiled data |
| `asset_impact/` | Parsing and merging Asset Impact data with GOGET |
| `filter_compile/` | Filtering and compiling GOGET data into single sheets |
| `summary/` | Summary sheets, dashboard data, Earth Genome files |
| `maps_viz/` | Maps and charts |
| `geo_conversion/` | Coordinate, WKT, and centroid conversions |
| `wiki/` | Wiki page / URL generation and reference-URL archiving |
| `country_specific/` | One-off country/region explorations |
| `misc/` | Image-to-spreadsheet, unit condensing, and other utilities |
| `notebooks_original/` | The original `.ipynb` source for every script |

## Script index

### `qc/` — Quality control
- **`goget_qc.py`** — Main GOGET QC application: runs an automated, user-friendly
  battery of quality-control checks against the data. *(Current version.)*
- **`goget_qc_checks_legacy.py`** — Earlier (2025-08) QC check routines: reads and
  filters data, flags unit-type/status outliers and potential duplicate names.

### `database/` — GEM database access
- **`gem_db_to_googlesheet.py`** — Query a table from the GEM database and save it
  to a Google Sheet.
- **`gem_db_query_for_qc.py`** — Query the GEM database to pull data for QC work.

### `ownership/` — Owners & operators
- **`compare_ownership_between_sheets.py`** — Compare ownership records between two
  sheets to spot differences.
- **`check_ownership_for_duplicates.py`** — QC check for duplicate ownership entries
  in GOGET.
- **`top_companies_per_county_mergers.py`** — List top owners/operators per county
  for a country, then use AI to check for mergers and acquisitions.
- **`name_matching.py`** — Fuzzy-match company/entity names to reconcile variants.

### `compare/` — Version & dataset comparison
- **`compare_two_copies_of_goget.py`** — Compare two iterations of GOGET to see
  changes within a specified range.
- **`compare_versions_missing_entries.py`** — Compare two versions of GOGET to find
  entries missing from one.
- **`compare_gov_datasets_between_years.py`** — Compare two versions of the same
  government dataset across years.
- **`compare_goget_locations_to_brazil.py`** — Compare GOGET locations against
  Brazilian government data locations.
- **`compare_urls_generated_vs_existing.py`** — Compare generated URLs against
  existing ones to catch mismatches.
- **`duplicate_locations_check.py`** — Detect duplicate locations within GOGET.

### `parsing/` — Parsing compiled data
- **`parse_fid_2022_2023.py`** — Parse 2022/2023 Final Investment Decision (FID)
  data from the compiled dataset.
- **`parse_discovery_2022_2023.py`** — Parse 2022/2023 discovery data from the
  compiled dataset.
- **`parse_fid_2024_beyond.py`** — Parse FID data for 2024 and beyond from the
  compiled dataset.
- **`reserve_harmonization.py`** — Harmonize reserve figures across sources/units.
- **`recent_production_reserves_project_level.py`** — Summarize production by most
  recent year and apply reserve conversions at the project level.

### `asset_impact/` — Asset Impact data
- **`asset_impact_data_parse_texas_2025.py`** — Parse Asset Impact data (Texas,
  California, Pennsylvania), modified for the 2025 Texas data.
- **`merge_asset_impact_with_goget.py`** — Merge Asset Impact data with GOGET data.
- **`asset_impact_us_states_2025.py`** — Process Asset Impact data across US states
  (2025 run).
- **`extract_field_totals_brazil_powerbi.py`** — Extract field totals from a Brazil
  Power BI table (OCR-based).

### `filter_compile/` — Filtering & compiling
- **`filter_and_compile_single_sheet.py`** — Filter and compile GOGET data into a
  single sheet from a recent data file.
- **`filter_compiled_for_region.py`** — Filter compiled data for a region (Latin
  American oil & gas example).
- **`filter_compiled_region_country_analysis.py`** — Filter the compiled sheet for
  region/country-level analysis.
- **`filter_data.py`** — Filter the number of GOGET fields down to a working subset.

### `summary/` — Summaries & dashboards
- **`summary_sheet_creation.py`** — Build the GOGET summary sheet *(2026-02 version)*.
- **`earthgenome_file_creation.py`** — Create the Earth Genome file, adding reserve
  and production data to the main data frame.
- **`pull_data_for_dashboards.py`** — Generate the data feeding the GOGET dashboard.

### `maps_viz/` — Maps & charts
- **`goget_maps.py`** — Generate GOGET figures and maps.
- **`violin_charts.py`** — Produce violin charts of GOGET data.
- **`distance_to_shore.py`** — Compute distance-to-shore for offshore assets.

### `geo_conversion/` — Coordinates & geometry
- **`routes_to_wkt.py`** — Convert routes exported from Google Maps to WKT.
- **`create_wkt_routes_excel.py`** — Build an Excel file of WKT routes (internal).
- **`convert_xy_pipeline_coords.py`** — Convert x/y pipeline coordinates into
  `"y, x"` strings / geometry.
- **`iran_coordinate_conversion.py`** — Convert Iran coordinates (UTM-based).
- **`california_centroid_by_field_operator.py`** — Compute centroids by field and
  operator for California.

### `wiki/` — Wiki & references
- **`create_oil_gas_wikis.py`** — Generate GOGET oil & gas field wiki pages.
- **`generate_goget_url_from_wiki_name.py`** — Build a GOGET URL from a wiki page name.
- **`archive_reference_urls.py`** — Submit reference URLs to the Internet Archive.

### `country_specific/` — One-off explorations
- **`new_mexico_exploration.py`** — Exploratory analysis of New Mexico data.
- **`argentina_api_exploration.py`** — Explore an Argentina data API.
- **`compile_california_data.py`** — Compile data from California's WellSTAR program.
- **`bc_group_wells_by_operator_field.py`** — Group British Columbia wells by
  operator and field.
- **`totalenergies_analysis.py`** — TotalEnergies-focused analysis of reserves and
  production.

### `misc/` — Utilities
- **`convert_image_to_spreadsheet.py`** — OCR an image into a spreadsheet.
- **`condense_gas_plant_units_by_status.py`** — Condense gas plant units by status.
- **`condense_lng_terminals.py`** — Condense LNG terminal records.
- **`parse_gfw_download.py`** — Parse a Global Fishing Watch (GFW) download.
- **`pe_map_parse.py`** — Parse a PE map (JSON) into structured data.
- **`time_to_start_up_briefing.py`** — Briefing-prep script (originally split from
  the GEM database QC notebook).

## Notes on migration

A number of original notebooks were intentionally **not** migrated: empty/unrelated
scraps (`Untitled*`, `Gemini Agent Test`) and older duplicates where a newer
canonical version exists (earlier `goget_qc_clean` versions, an older summary-sheet
notebook, duplicate parse/convert notebooks, and other people's copies). The raw
Colab export zip and a few loose notebooks left in the repo root are git-ignored;
delete them once you're satisfied with the migration.
