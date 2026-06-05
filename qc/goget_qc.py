"""
goget_qc.py

Migrated from Colab notebook: goget_qc_clean 2026 05 20 10_43 - Current.ipynb
Auto-converted to a Python script. Colab-specific lines
(drive.mount, google.colab imports, shell/magic commands) have been
commented out and flagged; pip installs moved to ../requirements.txt.
"""

# # GOGET QC Application
#
# This notebook automates quality control checks in a user friendly manner

# ===== Cell 1 =====
# Install Dependencies - No need to edit this
# [moved to requirements.txt] !pip install pandas sqlalchemy psycopg2-binary xlsxwriter shapely

# ===== Cell 2 =====
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime
import os
import pytz
import json
import math
import zipfile
from typing import List
# [colab-only removed] from google.colab import files
# [colab-only removed] from google.colab import userdata
# [colab-only removed] from google.colab import drive
# [colab drive mount removed] drive.mount('/content/drive')


try:
    from shapely.geometry import shape, Point
    SHAPELY_AVAILABLE = True
except ImportError:
    SHAPELY_AVAILABLE = False

def _load_country_shapes(geojson_path):
    with open(geojson_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    shapes = []
    for feature in data['features']:
        name = feature['properties'].get('NAME') or feature['properties'].get('name', '')
        try:
            geom = shape(feature['geometry'])
            shapes.append((name, geom))
        except Exception:
            pass
    return shapes

def _find_closest_country(lat, lon, country_shapes):
    pt = Point(lon, lat)
    for name, geom in country_shapes:
        if geom.contains(pt):
            return name
    min_dist = float('inf')
    closest = None
    for name, geom in country_shapes:
        try:
            dist = pt.distance(geom)
            if dist < min_dist:
                min_dist = dist
                closest = name
        except Exception:
            pass
    return closest

def _names_match(db_name, geo_name):
    if pd.isna(db_name) or pd.isna(geo_name):
        return False
    a = str(db_name).strip().lower()
    b = str(geo_name).strip().lower()
    if a == b: return True
    aliases = [
        ({"united states", "united states of america", "usa", "us"}),
        ({"russia", "russian federation"}),
        ({"iran", "iran (islamic republic of)", "islamic republic of iran"}),
        ({"south korea", "republic of korea", "korea, republic of"}),
        ({"north korea", "democratic people's republic of korea", "korea, democratic people's republic of"}),
        ({"bolivia", "bolivia (plurinational state of)"}),
        ({"venezuela", "venezuela (bolivarian republic of)"}),
        ({"taiwan", "taiwan, province of china"}),
        ({"trinidad", "trinidad and tobago"}),
        ({"uk", "united kingdom", "great britain"}),
        ({"congo", "democratic republic of the congo", "dr congo", "dem. rep. congo"}),
        ({"republic of the congo", "congo-brazzaville", "congo"}),
        ({"ivory coast", "cote d'ivoire", "cote d'ivoire"}),
        ({"czech republic", "czechia"}),
        ({"myanmar", "burma"}),
        ({"laos", "lao pdr", "lao people's democratic republic"}),
        ({"vietnam", "viet nam"}),
        ({"syria", "syrian arab republic"}),
        ({"tanzania", "united republic of tanzania"}),
        ({"moldova", "republic of moldova"}),
        ({"macau", "macao"}),
        ({"palestine", "state of palestine", "west bank"}),
    ]
    for group in aliases:
        if a in group and b in group:
            return True
    return a in b or b in a

def run_qc_checks(database_url: str, output_dir: str, selected_countries: List[str] = None, qc_steps: List[str] = None, geojson_path: str = None, outlier_ratio_threshold: int = 10):
    if database_url.startswith('postgres:'):
        database_url = database_url.replace('postgres:', 'postgresql:')
    if 'cockroachlabs.cloud' in database_url:
        if '?verify-full=true' in database_url: database_url = database_url.replace('?verify-full=true', '?sslmode=require')
        elif '?sslmode=' not in database_url and '&sslmode=' not in database_url:
            database_url += '&sslmode=require' if '?' in database_url else '?sslmode=require'
    else:
        if '?verify-full=true' in database_url: database_url = database_url.replace('?verify-full=true', '?sslmode=require')

    os.makedirs(output_dir, exist_ok=True)
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
    engine = create_engine(database_url)

    def get_sql_table(table_name):
        return pd.read_sql(f"SELECT * FROM {table_name}", engine)

    print("Loading tables...")
    plant = get_sql_table("plant")
    country = get_sql_table("country")
    goget_project = get_sql_table("goget_project")

    plant = plant.rename(columns={'id': 'plant_table_id'})
    plant['plant_table_id'] = plant['plant_table_id'].astype(str)
    goget_project['project_id'] = goget_project['project_id'].astype(str)

    goget_project = goget_project.merge(plant[['plant_table_id', 'country_id', 'latitude', 'longitude']], left_on='project_id', right_on='plant_table_id', how='left')
    goget_project['country_id'] = pd.to_numeric(goget_project['country_id'], errors='coerce')
    goget_project['country_id'] = goget_project['country_id'].fillna(-1).astype('int64')
    goget_project = goget_project.merge(country[['id', 'gemName']], left_on='country_id', right_on='id', how='left')
    goget_project = goget_project.rename(columns={'gemName': 'Country/Area'})

    if selected_countries:
        goget_project = goget_project[goget_project['Country/Area'].isin(selected_countries)]

    goget_project = goget_project.drop(columns=['country_id'], errors='ignore')
    if 'id_y' in goget_project.columns: goget_project = goget_project.drop(columns=['id_y'])

    if not qc_steps: qc_steps = ["duplicates", "production", "reserves", "status", "startups", "coordinates", "wkt"]

    reserves_production = get_sql_table("reserves_production")
    reserves_production['project_id'] = reserves_production['project_id'].astype(str)
    reserves_production_merged = reserves_production.merge(
        goget_project[["project_id", "namePrefix", "Country/Area"]],
        on="project_id", how="inner"
    )

    if "wkt" in qc_steps:
        geo = get_sql_table("project_geospatial")
        geo['project_id'] = geo['project_id'].astype(str)
        goget_project_wkt = goget_project.merge(geo[['project_id', 'wkt']], on='project_id', how='left')
        goget_project_wkt_path = os.path.join(output_dir, f'goget_project_wkt_{timestamp}.xlsx')
        goget_project_wkt.to_excel(goget_project_wkt_path, index=False)
        print(f"WKT export saved to {goget_project_wkt_path}")

    if "status" in qc_steps:
        status_timeline = get_sql_table("status_timeline")
        status_timeline['unit_id'] = status_timeline['unit_id'].astype(str)
        status_timeline_filtered = status_timeline.merge(goget_project[['project_id']], left_on='unit_id', right_on='project_id', how='inner')
        status_timeline_merged = status_timeline_filtered[status_timeline.columns]
        for col in ['created', 'modified']:
            if col in status_timeline_merged.columns and pd.api.types.is_datetime64_any_dtype(status_timeline_merged[col]):
                if status_timeline_merged[col].dt.tz is not None:
                    status_timeline_merged[col] = status_timeline_merged[col].dt.tz_localize(None)
        status_out = os.path.join(output_dir, f'status_timeline_check_{timestamp}.xlsx')
        status_timeline_merged.to_excel(status_out, index=False)
        print(f"Status timeline saved to {status_out}")

    if "duplicates" in qc_steps:
        def check_exact_duplicates(df):
            duplicates = df.groupby(['productionReserves', 'fuelDesc', 'reserveClassification', 'quantity', 'quantityUnit', 'year', 'project_id']).size().reset_index(name='counts')
            return duplicates[duplicates['counts'] > 1]
        dups = check_exact_duplicates(reserves_production_merged)
        if not dups.empty:
            dups.to_csv(os.path.join(output_dir, f"duplicate_full_entries_{timestamp}.csv"), index=False)
            print(f"Duplicate entries found and saved to duplicate_full_entries_{timestamp}.csv")
        else:
            print("No duplicate production entries found.")

    if "reserves" in qc_steps:
        reserves_df = reserves_production_merged[reserves_production_merged['productionReserves'].isin(['reserves'])].copy()
        reserves_df = reserves_df.sort_values(by=['project_id', 'fuelDesc', 'year'], ascending=[True, True, False])
        def reserves_classified(df):
            return df[df['reserveClassification'].isnull() | (df['reserveClassification'] == '')]
        unclassified_reserves = reserves_classified(reserves_df)
        if not unclassified_reserves.empty:
            unclassified_reserves.to_csv(os.path.join(output_dir, f"unclassified_reserves_entries_{timestamp}.csv"), index=False)
            print(f"Unclassified reserves entries found and saved.")
        else:
            print("No unclassified reserves entries found.")
        def reserve_not_timestamped(df):
            return df[df['year'].isnull() | (df['year'] == '')]
        timestamped_reserves = reserve_not_timestamped(reserves_df)
        if not timestamped_reserves.empty:
            timestamped_reserves.to_csv(os.path.join(output_dir, f"non_timestamped_reserves_entries_{timestamp}.csv"), index=False)
            print(f"Non-timestamped reserves entries found and saved.")
        else:
            print("No non-timestamped reserves entries found.")

    if "production" in qc_steps:
        production_df = reserves_production_merged[reserves_production_merged['productionReserves'].isin(['production', 'production design capacity'])].copy()
        production_df = production_df.sort_values(by=['project_id', 'fuelDesc', 'year'], ascending=[True, True, False])

        formatting_issues = []
        current_year = datetime.now().year

        required_fields = ['project_id', 'fuelDesc', 'year', 'quantity', 'quantityUnit', 'productionReserves']
        for field in required_fields:
            if field in production_df.columns:
                missing = production_df[production_df[field].isnull() | (production_df[field].astype(str).str.strip() == '')]
                if not missing.empty:
                    flagged = missing.copy()
                    flagged['formatting_issue'] = f'Missing required field: {field}'
                    formatting_issues.append(flagged)

        if 'year' in production_df.columns:
            year_numeric = pd.to_numeric(production_df['year'], errors='coerce')
            bad_year = production_df[year_numeric.isnull() | (year_numeric < 1900) | (year_numeric > current_year + 5)].copy()
            if not bad_year.empty:
                bad_year['formatting_issue'] = 'Invalid year value'
                formatting_issues.append(bad_year)

        if 'quantity' in production_df.columns:
            qty_numeric = pd.to_numeric(production_df['quantity'], errors='coerce')
            bad_qty = production_df[qty_numeric.isnull() | (qty_numeric < 0)].copy()
            if not bad_qty.empty:
                bad_qty['formatting_issue'] = 'Quantity is missing or negative'
                formatting_issues.append(bad_qty)

        valid_prod_types = {'production', 'production design capacity'}
        if 'productionReserves' in production_df.columns:
            bad_type = production_df[~production_df['productionReserves'].str.strip().str.lower().isin(valid_prod_types)].copy()
            if not bad_type.empty:
                bad_type['formatting_issue'] = 'Unexpected productionReserves value'
                formatting_issues.append(bad_type)

        conversion_factors = get_sql_table("quantity_unit")
        unique_factors = conversion_factors.drop_duplicates(subset=['name'], keep='first')

        all_production_converted_df = production_df.copy()
        all_production_converted_df['Fuel_quantity'] = all_production_converted_df['fuelDesc'] + ' ' + all_production_converted_df['quantityUnit']
        all_production_converted_df = all_production_converted_df.merge(
            unique_factors[['name', 'conversion_factor', 'common_unit']],
            left_on='Fuel_quantity', right_on='name', how='left'
        )
        all_production_converted_df = all_production_converted_df.rename(columns={
            'conversion_factor': 'Conversion factor',
            'common_unit': 'Common units',
        })
        all_production_converted_df['quantity_converted'] = all_production_converted_df['quantity'] * all_production_converted_df['Conversion factor']
        all_production_converted_df.loc[all_production_converted_df['Common units'] == 'million m³/y', 'shared unit (million boe/y)'] = all_production_converted_df['quantity_converted'] * .00588
        all_production_converted_df.loc[all_production_converted_df['Common units'].isin(['million bbl/y', 'shared unit (million boe/y)']), 'shared unit (million boe/y)'] = all_production_converted_df['quantity_converted']
        all_production_path = os.path.join(output_dir, f'all_production_converted_{timestamp}.csv')
        all_production_converted_df.to_csv(all_production_path, index=False)
        print(f"All production entries converted and saved to all_production_converted_{timestamp}.csv")

        valid_units = {'million m³/y', 'million bbl/y', 'million boe/y'}
        if 'Common units' in all_production_converted_df.columns:
            bad_units = all_production_converted_df[
                ~all_production_converted_df['Common units'].isin(valid_units)
            ][['project_id', 'namePrefix', 'Country/Area', 'fuelDesc', 'quantityUnit', 'Common units', 'productionReserves']].copy()
            if not bad_units.empty:
                bad_units['formatting_issue'] = 'Common units not in valid set'
                formatting_issues.append(bad_units)

        if formatting_issues:
            all_issues = pd.concat(formatting_issues, ignore_index=True)
            all_issues = all_issues.drop_duplicates(subset=['project_id', 'fuelDesc', 'year', 'quantity', 'formatting_issue'])
            issues_path = os.path.join(output_dir, f'production_formatting_issues_{timestamp}.csv')
            all_issues.to_csv(issues_path, index=False)
            print(f"Production formatting issues found ({len(all_issues)} rows). Saved to production_formatting_issues_{timestamp}.csv")
        else:
            print("No production formatting issues found.")

        all_production_converted_df = all_production_converted_df[all_production_converted_df['productionReserves'] == 'production']
        most_recent_production = all_production_converted_df.sort_values(by=['project_id', 'fuelDesc', 'year'], ascending=[True, True, False]).drop_duplicates(subset=['project_id', 'fuelDesc'], keep='first')

        gas_production_boe = most_recent_production[most_recent_production['Common units'] == 'million m³/y']['shared unit (million boe/y)'].sum()
        oil_production_boe = most_recent_production[most_recent_production['Common units'] == 'million bbl/y']['shared unit (million boe/y)'].sum()

        print(f"Total country production by fuel type:")
        print(f"  Gas: {gas_production_boe:,.2f} million boe/y ")
        print(f"  Oil: {oil_production_boe:,.2f} million boe/y")
        print(f"  Total: {most_recent_production['shared unit (million boe/y)'].sum():,.2f} million boe/y")

    if "outliers" in qc_steps:
        print("Running outlier detection...")

        outlier_prod = reserves_production_merged[
            reserves_production_merged['productionReserves'] != 'reserves'
        ].copy()
        outlier_prod['Fuel_quantity'] = outlier_prod['fuelDesc'] + ' ' + outlier_prod['quantityUnit']

        conversion_factors_ol = get_sql_table("quantity_unit")
        unique_factors_ol = conversion_factors_ol.drop_duplicates(subset=['name'], keep='first')

        missing_fq = set(outlier_prod['Fuel_quantity'].unique()) - set(unique_factors_ol['name'].values)
        if missing_fq:
            print(f"  Warning: {len(missing_fq)} Fuel_quantity combos missing from conversion table: {missing_fq}")

        outlier_prod = outlier_prod.merge(
            unique_factors_ol[['name', 'conversion_factor', 'common_unit']],
            left_on='Fuel_quantity', right_on='name', how='left'
        )
        outlier_prod['quantity_converted'] = outlier_prod['quantity'] * outlier_prod['conversion_factor']
        outlier_prod['Project ID'] = 'L' + outlier_prod['project_id']

        print(f"  {outlier_prod['Country/Area'].notna().sum():,} of {len(outlier_prod):,} rows matched a country.")

        if selected_countries:
            outlier_prod = outlier_prod[outlier_prod['Country/Area'].isin(selected_countries)].copy()

        RATIO_THRESHOLD = outlier_ratio_threshold

        group_keys = ['Project ID', 'common_unit']
        group_median = (
            outlier_prod
            .groupby(group_keys)['quantity_converted']
            .transform('median')
        )
        group_size = (
            outlier_prod
            .groupby(group_keys)['quantity_converted']
            .transform('count')
        )

        eligible = (group_size >= 2) & (group_median != 0)
        ratio = outlier_prod['quantity_converted'] / group_median

        too_high = eligible & (ratio > RATIO_THRESHOLD)
        too_low  = eligible & (ratio < 1 / RATIO_THRESHOLD)

        outlier_prod['outlier_flag'] = too_high | too_low
        outlier_prod['outlier_reason'] = ''

        outlier_prod.loc[too_high, 'outlier_reason'] = (
            'Value (' + outlier_prod.loc[too_high, 'quantity_converted'].map('{:,.2f}'.format)
            + ') is ' + ratio[too_high].map('{:.1f}'.format)
            + 'x the group median ('
            + group_median[too_high].map('{:,.2f}'.format)
            + f') — exceeds {RATIO_THRESHOLD}x threshold'
        )
        outlier_prod.loc[too_low, 'outlier_reason'] = (
            'Value (' + outlier_prod.loc[too_low, 'quantity_converted'].map('{:,.2f}'.format)
            + ') is ' + ratio[too_low].map('{:.6f}'.format)
            + 'x the group median ('
            + group_median[too_low].map('{:,.2f}'.format)
            + f') — below 1/{RATIO_THRESHOLD}x threshold'
        )

        outliers = outlier_prod[outlier_prod['outlier_flag']]
        print(f"  Total rows: {len(outlier_prod):,}  |  Outliers flagged: {len(outliers):,}")

        if not outliers.empty:
            out_cols = ['Project ID', 'namePrefix', 'Country/Area', 'year',
                        'fuelDesc', 'quantity_converted', 'common_unit', 'outlier_reason']
            out_df = outliers[out_cols].rename(columns={
                'namePrefix': 'Project Name',
                'year': 'Year',
                'fuelDesc': 'Fuel Description',
                'quantity_converted': 'Quantity (converted)',
                'common_unit': 'Quantity Unit (converted)',
            }).sort_values(['Project ID', 'Quantity Unit (converted)', 'Year'])
            outliers_path = os.path.join(output_dir, f'production_outliers_{timestamp}.csv')
            out_df.to_csv(outliers_path, index=False)
            print(f"  Outliers saved to production_outliers_{timestamp}.csv")
        else:
            print("  No outliers found.")

    if "coordinates" in qc_steps and SHAPELY_AVAILABLE and geojson_path and os.path.exists(geojson_path):
        print("Running coordinate country check...")
        country_shapes = _load_country_shapes(geojson_path)
        coord_df = goget_project[['project_id', 'namePrefix', 'Country/Area', 'latitude', 'longitude']].copy()
        coord_df['latitude'] = pd.to_numeric(coord_df['latitude'], errors='coerce')
        coord_df['longitude'] = pd.to_numeric(coord_df['longitude'], errors='coerce')
        coord_valid = coord_df.dropna(subset=['latitude', 'longitude']).copy()
        if not coord_valid.empty:
            coord_valid['geo_country'] = coord_valid.apply(lambda row: _find_closest_country(row['latitude'], row['longitude'], country_shapes), axis=1)
            coord_valid['coordinates_match'] = coord_valid.apply(lambda row: _names_match(row['Country/Area'], row['geo_country']), axis=1)
            mismatched = coord_valid[~coord_valid['coordinates_match']].copy()
            if not mismatched.empty:
                mismatched.to_csv(os.path.join(output_dir, f'mismatched_coordinates_{timestamp}.csv'), index=False)
            print(f"Coordinate check done. {len(mismatched)} mismatches found.")
        else:
            print("No valid coordinates found.")

    return f"QC process completed successfully. Output saved to: {output_dir}"

# # Define hidden database URL, Conversions and outputs

# ===== Cell 3 =====
# grab hidden database URL from OnePassword as "GEM Database URL" - enter in the secrets panel
DATABASE_URL = userdata.get('DATABASE_URL')

if DATABASE_URL.startswith('postgres:'):
    DATABASE_URL = DATABASE_URL.replace('postgres:', 'postgresql:')

# name export path
QC_folder = '/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/QC/'
export_gen_path = "/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/GOGET Iterations/Alternative Formats of GOGET/"
export_qc_path = QC_folder + 'QC Output Dump/'

geojson_file = QC_folder + 'ne_110m_admin_0_countries.geojson'

# ===== Cell 4 =====
SELECTED_COUNTRIES = "Bangladesh" # @param {type:"string"}
DUPLICATES_CHECK = False # @param {type:"boolean"}
PRODUCTION_DATA = False # @param {type:"boolean"}
STATUS_TIMELINES = False # @param {type:"boolean"}
YEARLY_STARTUPS = False # @param {type:"boolean"}
COORDINATE_CHECK = True # @param {type:"boolean"}
RESERVES_CHECK = False # @param {type:"boolean"}
OUTLIER_CHECK = False # @param {type:"boolean"}
OUTLIER_RATIO_THRESHOLD = 10 # @param {type:"number"}
WKT_CHECK = False # @param {type:"boolean"}

# Ensure pandas, sqlalchemy, and text are available in this cell
import pandas as pd
from sqlalchemy import create_engine, text

# Check if DATABASE_URL is defined before using it
if 'DATABASE_URL' not in globals():
    DATABASE_URL = None # Assign None if not defined, to prevent NameError

if not DATABASE_URL:
    print("Please enter a DATABASE_URL.")
else:
    if not os.path.exists(geojson_file):
        print(f"Please upload '{geojson_file}' (needed for coordinate check)")
        uploaded = files.upload()

    qc_steps = []
    if DUPLICATES_CHECK: qc_steps.append("duplicates")
    if PRODUCTION_DATA: qc_steps.append("production")
    if STATUS_TIMELINES: qc_steps.append("status")
    if YEARLY_STARTUPS: qc_steps.append("startups")
    if COORDINATE_CHECK: qc_steps.append("coordinates")
    if RESERVES_CHECK: qc_steps.append("reserves")
    if OUTLIER_CHECK: qc_steps.append("outliers")
    if WKT_CHECK: qc_steps.append("wkt")

    countries = [c.strip() for c in SELECTED_COUNTRIES.split(",") if c.strip()]

    proceed_with_qc = True
    if countries: # Only check if specific countries were selected by the user
        try:
            temp_engine = create_engine(DATABASE_URL)
            with temp_engine.connect() as connection:
                db_countries_df = pd.read_sql(text('SELECT "gemName" FROM country'), connection)
            valid_db_country_names = set(db_countries_df['gemName'].dropna().str.strip().str.lower())

            user_selected_lower = {c.lower() for c in countries}
            if not any(user_country in valid_db_country_names for user_country in user_selected_lower):
                print("Country selected not in database")
                proceed_with_qc = False
        except Exception as e:
            print(f"Could not verify country existence due to database error: {e}")
            proceed_with_qc = False

    if proceed_with_qc:
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(export_qc_path, f"qc_outputs_{SELECTED_COUNTRIES}_{run_id}")

        try:
            result = run_qc_checks(
                database_url=DATABASE_URL,
                output_dir=output_dir,
                selected_countries=countries if countries else None,
                qc_steps=qc_steps,
                geojson_path=geojson_file,
                outlier_ratio_threshold=OUTLIER_RATIO_THRESHOLD
            )
            print(result)

            # Zip results
            zip_name = os.path.join(export_qc_path, f"qc_results_{SELECTED_COUNTRIES}_{run_id}.zip")
            with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files_in_dir in os.walk(output_dir):
                    for file in files_in_dir:
                        file_path = os.path.join(root, file)
                        zipf.write(file_path, os.path.relpath(file_path, output_dir))

            print(f"Results zipped to {zip_name}.")

        except Exception as e:
            print(f"An error occurred: {e}")
