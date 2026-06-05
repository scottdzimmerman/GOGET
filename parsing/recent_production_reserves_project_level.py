"""
recent_production_reserves_project_level.py

Migrated from Colab notebook: Recent Production and Reseves - Summarize Project Level (clean).ipynb
Auto-converted to a Python script. Colab-specific lines
(drive.mount, google.colab imports, shell/magic commands) have been
commented out and flagged; pip installs moved to ../requirements.txt.
"""

# # This is a script for parsing GOGET data, summarizing production data by most recent year, and applying conversions to the reserves

# Load in libs, define timestamp, define DB

# ===== Cell 1 =====
# import libraries

# import pandas for manipulation
import pandas as pd

# mount google drive
# [colab-only removed] from google.colab import drive
# [colab drive mount removed] drive.mount('/content/drive')

# Library needed to connect to the database
from sqlalchemy import create_engine, text
import psycopg2

# ===== Cell 2 =====
# name export path
export_gen_path = "/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/GOGET Iterations/Alternative Formats of GOGET/"
export_qc_path = '/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/QC/QC Output Dump/'
# import conversion factors
conversion_factors = pd.read_csv('/content/drive/MyDrive/GOGET q1 2026/GOGET oil & gas extraction sites conversion factors for QC  2026 01 30 1633 - Conversion factors.csv')

# make timestamp
from datetime import datetime
now = datetime.now()
timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")

print('this runs qc output will all be timestamped: ' + timestamp)

# ===== Cell 3 =====
# connect to db
# Set up database pull via URL from the data team.
# (URL updated 2025-07-07 by Maisie to reflect new follower database location)
DATABASE_URL = 'postgres://readonly:p8973ecd68569dabd2e8d1bc7bd5446d35a0d457487e0a783c83de2ec8a1043cc@ec2-54-243-187-12.compute-1.amazonaws.com:5432/d3o895iig4poii'

if DATABASE_URL.startswith('postgres:'):
    DATABASE_URL = DATABASE_URL.replace('postgres:', 'postgresql:')

# Connect to the database
engine = create_engine(DATABASE_URL)
conn = engine.connect()

# Load in relevant data

# ===== Cell 4 =====
# function to convert sql tables to dataframes
def get_sql_table(table_name):
   df = pd.read_sql(table_name,conn)
   return df

   # load GOGET table
goget_project = get_sql_table("goget_project")

# TODO: load in "plant" and "country" then merge those onto GOGET PROJECT
# temp workaround
# merge country from GOGET interface
# load in recent goget CSV
GOGET_folder = '/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/GOGET Iterations/Snapshots of GOGET main data set/'
GOGET_download = GOGET_folder + 'all-fields-2026-02-03T213445.csv'
GOGET_download = pd.read_csv(GOGET_download)

# Prep data

# ===== Cell 5 =====
# keep just "Country/Area" and "Unit ID" column
GOGET_countries = GOGET_download[['Country/Area', 'Unit ID']]

GOGET_download_with_prod = GOGET_download.copy()

# rename "Unit ID" as project_id
GOGET_countries = GOGET_countries.rename(columns={'Unit ID': 'project_id'})

# strip the "L" from the project_id
GOGET_countries['project_id'] = GOGET_countries['project_id'].str.replace('L', '')

# merge namePrefix from goget_project onto reserves_production using project_id
reserves_production = get_sql_table("reserves_production")
reserves_production['project_id'] = reserves_production['project_id'].astype(str)
goget_project['project_id'] = goget_project['project_id'].astype(str)

# First, merge with goget_project to get 'namePrefix'
reserves_production_merged = reserves_production.merge(goget_project[["project_id", "namePrefix"]], on="project_id", how="left")

# Then, merge the result with GOGET_countries to get 'Country/Area'
reserves_production_merged = reserves_production_merged.merge(GOGET_countries[['project_id', 'Country/Area']], on="project_id", how="left")

# # Production data

# ===== Cell 6 =====
# pull recent production in, filtering by all and specific fuel

# Filter for rows where productionReserves is 'production' or 'production design capacity'
production_df = reserves_production_merged[reserves_production_merged['productionReserves'].isin(['production', 'production design capacity'])].copy() #added pdc of 2026 01 23

# Sort by project_id, fuelDesc, and year in descending order to get the most recent year first
production_df = production_df.sort_values(by=['project_id', 'fuelDesc', 'year'], ascending=[True, True, False])

# Drop duplicate project_id and fuelDesc combinations, keeping the first row (which is the most recent year)
recent_production_byfuel_df = production_df.drop_duplicates(subset=['project_id', 'fuelDesc'])

# Drop duplicates so any fuel counts - use this for recent status
recent_production_overall_df = recent_production_byfuel_df.drop_duplicates(subset=['project_id'])

# rename year to prodyear
recent_production_byfuel_df = recent_production_byfuel_df.rename(columns={'year': 'prodyear'})
recent_production_overall_df = recent_production_overall_df.rename(columns={'year': 'prodyear'})

# Select the desired columns
recent_production_byfuel_df = recent_production_byfuel_df[['project_id', 'namePrefix', 'fuelDesc', 'prodyear', 'quantity', 'quantityUnit','Country/Area']]
recent_production_overall_df = recent_production_overall_df[['project_id', 'namePrefix', 'prodyear', 'quantity', 'quantityUnit','Country/Area']]

display(recent_production_overall_df.head())

# Convert production data

# ===== Cell 7 =====
#Convert to common units (million bbl and million cubic meters)

# combine 'fuelDesc' and 'quantityUnit' as "Fuel_quantity" in recent_production_byfuel_df
recent_production_byfuel_df['Fuel_quantity'] = recent_production_byfuel_df['fuelDesc'] + ' ' + recent_production_byfuel_df['quantityUnit']

# unique fuel_quanity to make sure all are on conversion sheet
unique_fuel_quantity = recent_production_byfuel_df['Fuel_quantity'].unique()

# compare conversion factors "Fuel description + Units (original)" to unique_fuel_quantity looking for missing entries
missing_entries = []
for entry in unique_fuel_quantity:
    if entry not in conversion_factors['Fuel description + Units (original)'].values:
        missing_entries.append(entry)
        print(f"Missing entry: {entry}") # Print missing entries as they are found

# After the loop, check if any entries were missing
if not missing_entries:
    print("No missing entries found.")

# ===== Cell 8 =====
# Apply conversion factors and add new columns

# Ensure conversion_factors has unique 'Fuel description + Units (original)' before merging
# This assumes that for duplicate 'Fuel description + Units (original)', the 'Conversion factor' and 'Common units' are identical or we want to pick one arbitrarily.
# Given the earlier output, they appear to be identical.
unique_conversion_factors = conversion_factors.drop_duplicates(subset=['Fuel description + Units (original)'], keep='first')

recent_production_byfuel_converted_df = recent_production_byfuel_df.merge(
    unique_conversion_factors[['Fuel description + Units (original)', 'Conversion factor', 'Common units']],
    left_on='Fuel_quantity',
    right_on='Fuel description + Units (original)',
    how='left'
)

# Apply the conversion factor to the quantity
recent_production_byfuel_converted_df['quantity_converted'] = recent_production_byfuel_converted_df['quantity'] * recent_production_byfuel_converted_df['Conversion factor']

# Select and rename the desired columns
recent_production_byfuel_converted_df = recent_production_byfuel_converted_df[[
    'project_id',
    'namePrefix',
    'Country/Area',
    'fuelDesc',
    'prodyear',
    'quantity',
    'quantityUnit',
    'quantity_converted',
    'Common units'
]]

# ===== Cell 9 =====
# when "Common units" = "million m³/y" multiply by .00588 new "shared unit" column
recent_production_byfuel_converted_df.loc[recent_production_byfuel_converted_df['Common units'] == 'million m³/y', 'shared unit (million boe/y)'] = recent_production_byfuel_converted_df['quantity_converted'] * .00588

# when common units = million bbl/y or million boe/y, put that value in shared unit column
recent_production_byfuel_converted_df.loc[recent_production_byfuel_converted_df['Common units'].isin(['million bbl/y', 'shared unit (million boe/y)']), 'shared unit (million boe/y)'] = recent_production_byfuel_converted_df['quantity_converted']

# sort recent_production_byfuel_converted_df by shared unit (million boe/y) in ascending order
recent_production_byfuel_converted_df = recent_production_byfuel_converted_df.sort_values(by=['shared unit (million boe/y)'], ascending=[False])

# ===== Cell 10 =====
# group recent_production_byfuel_converted_df by project id, summing shared unit (million boe/) amd taking the average prodyear
grouped_prod = recent_production_byfuel_converted_df.groupby(['project_id','namePrefix', 'Country/Area'], as_index=False).agg({
    'shared unit (million boe/y)': 'sum',
    'prodyear': 'mean'
})

# if shared unit (million boe/y) > 1 add "makeWIKI" column and "True" to it
grouped_prod.loc[grouped_prod['shared unit (million boe/y)'] > 1, 'makeWIKI'] = True
grouped_prod.loc[grouped_prod['shared unit (million boe/y)'] <= 1, 'makeWIKI'] = False

# sort by shared unit
grouped_prod = grouped_prod.sort_values(by=['shared unit (million boe/y)'], ascending=[False])

# strip the L from Unit ID in GOGET_download_with_prod before merging
GOGET_download_with_prod['Unit ID'] = GOGET_download_with_prod['Unit ID'].str.replace('L', '')

# Define columns to be merged from grouped_prod
merge_cols = ['project_id', 'prodyear', 'shared unit (million boe/y)', 'makeWIKI']

# Identify columns in GOGET_download_with_prod that would be duplicated by the merge
duplicate_cols = [col for col in merge_cols if col in GOGET_download_with_prod.columns and col != 'project_id']

# Drop identified duplicate columns before merging
if duplicate_cols:
    GOGET_download_with_prod = GOGET_download_with_prod.drop(columns=duplicate_cols)


GOGET_download_with_prod = GOGET_download_with_prod.merge(grouped_prod[merge_cols], left_on='Unit ID', right_on='project_id', how='left')
display(GOGET_download_with_prod.head())

# # Reserve data

# ===== Cell 11 =====
# pull recent reserves in, filtering by all and specific fuel

# Filter for rows where productionReserves is 'reserves'
reserves_df = reserves_production_merged[reserves_production_merged['productionReserves'].isin(['reserves'])].copy()

# Sort by project_id, fuelDesc, and year in descending order to get the most recent year first
reserves_df = reserves_df.sort_values(by=['project_id', 'fuelDesc', 'year'], ascending=[True, True, False])

# ===== Cell 12 =====
# Drop duplicate project_id and fuelDesc combinations, keeping the first row (which is the most recent year)
recent_reserve_byfuel_df = reserves_df .drop_duplicates(subset=['project_id', 'reserveClassification','fuelDesc'])

# Drop duplicates so any fuel counts - use this for recent status
recent_reserves_overall_df = recent_reserve_byfuel_df.drop_duplicates(subset=['project_id'])

# rename year to prodyear
recent_reserves_overall_df = recent_reserves_overall_df.rename(columns={'year': 'reseryear'})
recent_reserve_byfuel_df = recent_reserve_byfuel_df.rename(columns={'year': 'reseryear'})

# Select the desired columns
recent_reserves_overall_df = recent_reserves_overall_df[['project_id', 'namePrefix', 'fuelDesc', 'reseryear', 'quantity', 'quantityUnit','Country/Area','reserveClassification']]
recent_reserve_byfuel_df = recent_reserve_byfuel_df[['project_id', 'namePrefix', 'fuelDesc', 'reseryear', 'quantity', 'quantityUnit','Country/Area','reserveClassification']]

display(recent_reserve_byfuel_df.head())

# ===== Cell 13 =====
# combine 'fuelDesc' and 'quantityUnit' as 'Fuel_quantity' in recent_reserve_byfuel_df
recent_reserve_byfuel_df['Fuel_quantity'] = recent_reserve_byfuel_df['fuelDesc'] + ' ' + recent_reserve_byfuel_df['quantityUnit']

# unique fuel_quanity to make sure all are on conversion sheet
unique_reserve_fuel_quantity = recent_reserve_byfuel_df['Fuel_quantity'].unique()

# compare conversion factors 'Fuel description + Units (original)' to unique_reserve_fuel_quantity looking for missing entries
missing_reserve_entries = []
for entry in unique_reserve_fuel_quantity:
    if entry not in conversion_factors['Fuel description + Units (original)'].values:
        missing_reserve_entries.append(entry)
        print(f"Missing reserve entry: {entry}") # Print missing entries as they are found

# After the loop, check if any entries were missing
if not missing_reserve_entries:
    print("No missing reserve entries found.")

# Apply conversion factors and add new columns to reserves
recent_reserve_byfuel_converted_df = recent_reserve_byfuel_df.merge(
    unique_conversion_factors[['Fuel description + Units (original)', 'Conversion factor', 'Common units']],
    left_on='Fuel_quantity',
    right_on='Fuel description + Units (original)',
    how='left'
)

# Apply the conversion factor to the quantity
recent_reserve_byfuel_converted_df['quantity_converted'] = recent_reserve_byfuel_converted_df['quantity'] * recent_reserve_byfuel_converted_df['Conversion factor']

# when "Common units" = "million m³" multiply by .00588 new "shared unit" column
recent_reserve_byfuel_converted_df.loc[recent_reserve_byfuel_converted_df['Common units'] == 'million m³', 'shared unit (million boe)'] = recent_reserve_byfuel_converted_df['quantity_converted'] * .00588

# when common units = million bbl or million boe, put that value in shared unit column
recent_reserve_byfuel_converted_df.loc[recent_reserve_byfuel_converted_df['Common units'].isin(['million bbl', 'shared unit (million boe)']), 'shared unit (million boe)'] = recent_reserve_byfuel_converted_df['quantity_converted']

# Select and rename the desired columns for reserves
recent_reserve_byfuel_converted_df = recent_reserve_byfuel_converted_df[[
    'project_id',
    'namePrefix',
    'Country/Area',
    'fuelDesc',
    'reseryear',
    'quantity',
    'quantityUnit',
    'reserveClassification',
    'quantity_converted',
    'Common units',
    'shared unit (million boe)'
]]

# sort by shared unit (million boe)
recent_reserve_byfuel_converted_df = recent_reserve_byfuel_converted_df.sort_values(by=['shared unit (million boe)'], ascending=[False])
display(recent_reserve_byfuel_converted_df.head())

# # reserve harmozination (not for export functions)

# ===== Cell 14 =====
# import rf sheet
rf_sheet = pd.read_csv(export_qc_path + 'recent_reserve_byfuel_converted_df 2026-01-30_22-36-42 - rf sheet.csv')

# filter recent_reserve_byfuel_converted_df for rows where reserveClassification is listed in rf_sheet "description"
in_place_recent = recent_reserve_byfuel_converted_df[recent_reserve_byfuel_converted_df['reserveClassification'].isin(rf_sheet['description'])].copy()

# for in_place_recent, create country specifc id by joining Country/Area - fuelDesc - reserveClassification
in_place_recent['country_specific_id'] = in_place_recent['Country/Area'] + ' - ' + in_place_recent['fuelDesc'] + ' - ' + in_place_recent['reserveClassification']

# matching on "Combo" in rf_sheet bring over Recovery Factor from rf_sheet to in_place_recent
in_place_recent = in_place_recent.merge(rf_sheet[['Combo', 'Recovery Factor']], left_on='country_specific_id', right_on='Combo', how='left')

# Clean and convert 'Recovery Factor' to numeric
in_place_recent['Recovery Factor'] = in_place_recent['Recovery Factor'].str.replace('%', '', regex=False).astype(float) / 100

# apply Recovery Factor to shared unit (million boe) value creating "estimated recoverable"
in_place_recent['estimated recoverable (RF applied to in-place)'] = in_place_recent['shared unit (million boe)'] * in_place_recent['Recovery Factor']

# tag all rows where estimated recoverable (1P_2P, 3P_2P) > 0 as "converted from 1p to 2p, 3P to 2p"
in_place_recent['conversion type'] = in_place_recent.apply(lambda row: f"RF applied (Recovery Factor: {row['Recovery Factor']:.2f})" if row['estimated recoverable (RF applied to in-place)'] > 0 else 'not converted', axis=1)

# rename estimated recoverable (RF applied to in-place)
in_place_recent['estimated recoverable'] = in_place_recent['estimated recoverable (RF applied to in-place)']

# drop columns
in_place_recent = in_place_recent.drop(columns=['Combo', 'country_specific_id', 'Recovery Factor','estimated recoverable (RF applied to in-place)'])

in_place_recent

# ===== Cell 15 =====
# import 1P2P3P sheet
p1p2p3p_sheet = pd.read_csv(export_qc_path + 'recent_reserve_byfuel_converted_df 2026-01-30_22-36-42 - Clean 2p conversion.csv')

# filter recent_reserve_byfuel_converted_df for rows where reserveClassification is listed in p1p2p3p "reserveClassification"
closeto1p2p3p = recent_reserve_byfuel_converted_df[recent_reserve_byfuel_converted_df['reserveClassification'].isin(p1p2p3p_sheet['reserveClassification'])].copy()

# map p1p2p3p_sheet Conversion_factor to closeto1p2p3p on reserveClassification
closeto1p2p3p = closeto1p2p3p.merge(p1p2p3p_sheet[['reserveClassification', 'Conversion_factor']], left_on='reserveClassification', right_on='reserveClassification', how='left')

# apply Recovery Factor to shared unit (million boe) value creating "estimated recoverable"
closeto1p2p3p['estimated recoverable (1P_2P, 3P_2P)'] = closeto1p2p3p['shared unit (million boe)'] * closeto1p2p3p['Conversion_factor']

# tag all rows where estimated recoverable (1P_2P, 3P_2P) > 0 as "converted from 1p to 2p, 3P to 2p"
closeto1p2p3p['conversion type'] = closeto1p2p3p.apply(lambda row: f"converted from 1p to 2p, 3P to 2p (Conversion Factor: {row['Conversion_factor']:.2f})"  if row['estimated recoverable (1P_2P, 3P_2P)'] > 0 else 'not converted', axis=1)

# rename estimated recoverable (RF applied to in-place)
closeto1p2p3p['estimated recoverable'] = closeto1p2p3p['estimated recoverable (1P_2P, 3P_2P)']

# drop columns
closeto1p2p3p = closeto1p2p3p.drop(columns=['Conversion_factor', 'estimated recoverable (1P_2P, 3P_2P)'])

closeto1p2p3p

# ===== Cell 16 =====
# join closeto1p2p3p and in_place_recent
in_place_and1p2p3p = pd.concat([in_place_recent, closeto1p2p3p])

# # create project level summaries - failed method

# Prep data

# ===== Cell 17 =====
production_consolidation_df = GOGET_download_with_prod.copy()

# Fill NaN values in 'Project/Complex' with an empty string
production_consolidation_df['Project/Complex'] = production_consolidation_df['Project/Complex'].fillna('')

# Fill NaN values in 'Unit Name' with an empty string
production_consolidation_df['Unit Name'] = production_consolidation_df['Unit Name'].fillna('')

# Convert 'shared unit (million boe/y)' to numeric, coercing errors to NaN
production_consolidation_df['shared unit (million boe/y)'] = pd.to_numeric(production_consolidation_df['shared unit (million boe/y)'], errors='coerce')

print("Data preparation for consolidation complete. Displaying the first few rows and data types:")
display(production_consolidation_df.head())
display(production_consolidation_df[['Project/Complex', 'Unit Name', 'shared unit (million boe/y)']].dtypes)

# find project level production

# ===== Cell 18 =====
project_level_production_df = production_consolidation_df[
    (production_consolidation_df['Project/Complex'] == production_consolidation_df['Unit Name']) &
    (production_consolidation_df['Project/Complex'] != '')
].copy()
project_level_production_df['production_type'] = 'project level production'

# Initialize a set to keep track of all Unit IDs that have been accounted for
accounted_unit_ids = set(project_level_production_df['Unit ID'].unique())

# The remaining_production_df is effectively production_consolidation_df minus project-level entries
# We will filter this later based on accounted_unit_ids

print("Identified project-level production. Displaying first few rows of project_level_production_df:")
display(project_level_production_df.head())

# calculated production that should be summed to the project level - failed method

# ===== Cell 19 =====
# Create a DataFrame of units that are potential candidates for summing (excluding already accounted units)
multi_unit_candidates_df = production_consolidation_df[
    (~production_consolidation_df['Unit ID'].isin(accounted_unit_ids)) &
    (production_consolidation_df['Project/Complex'] != '') &
    (production_consolidation_df['Project/Complex'] != production_consolidation_df['Unit Name']) &
    (production_consolidation_df['shared unit (million boe/y)'].notna())
].copy()

# Get the project_ids that correspond to multi-unit projects from the candidates
# A project is considered multi-unit if the same Project/Complex appears with more than one unique Unit ID
multi_unit_project_complexes = multi_unit_candidates_df.groupby('Project/Complex')['Unit ID'].nunique()
multi_unit_project_complexes = multi_unit_project_complexes[multi_unit_project_complexes > 1].index

# Filter the DataFrame to only include rows that belong to these identified multi-unit Project/Complexes
summed_units_production_source_df = multi_unit_candidates_df[
    multi_unit_candidates_df['Project/Complex'].isin(multi_unit_project_complexes)
].copy()

# Group by 'Project/Complex' to sum production and average year
summed_units_production_df = summed_units_production_source_df.groupby(['Project/Complex', 'Country/Area'], as_index=False).agg({
    'shared unit (million boe/y)': 'sum',
    'prodyear': 'mean'
})

# Rename 'Project/Complex' to 'namePrefix' and create 'project_id' from it (as it's a project-level aggregation)
summed_units_production_df = summed_units_production_df.rename(columns={'Project/Complex': 'namePrefix'})
summed_units_production_df['project_id'] = 'SUM_' + summed_units_production_df['namePrefix'].str.replace(' ', '_')

# Recalculate makeWIKI based on the summed production
summed_units_production_df['makeWIKI'] = summed_units_production_df['shared unit (million boe/y)'] > 1
summed_units_production_df['production_type'] = 'summed units production'

# Add the Unit IDs that contributed to these summed projects to the accounted_unit_ids set
accounted_unit_ids.update(summed_units_production_source_df['Unit ID'].unique())

print("Identified and summed multi-unit projects. Displaying first few rows of summed_units_production_df:")
display(summed_units_production_df.head())

# calculate field only level production

# ===== Cell 20 =====
# The remaining units are those that have not been accounted for yet
unit_level_production_df = production_consolidation_df[
    (~production_consolidation_df['Unit ID'].isin(accounted_unit_ids)) &
    (production_consolidation_df['shared unit (million boe/y)'].notna())
].copy()

unit_level_production_df['production_type'] = 'unit level production'
unit_level_production_df = unit_level_production_df.rename(columns={'Unit Name': 'namePrefix'})

# Select and reorder columns to be consistent with other DFs
unit_level_production_df = unit_level_production_df[[
    'project_id',
    'namePrefix',
    'Country/Area',
    'shared unit (million boe/y)',
    'prodyear',
    'makeWIKI',
    'production_type'
]]

print("Identified unit-level production. Displaying first few rows of unit_level_production_df:")
display(unit_level_production_df.head())

# Combine 3 types (project, summed project, field)

# ===== Cell 21 =====
final_production_df = pd.concat([
    project_level_production_df[[
        'project_id',
        'Project/Complex',
        'Country/Area',
        'shared unit (million boe/y)',
        'prodyear',
        'makeWIKI',
        'production_type'
    ]].rename(columns={'Project/Complex': 'namePrefix'}),
    summed_units_production_df[[
        'project_id',
        'namePrefix',
        'Country/Area',
        'shared unit (million boe/y)',
        'prodyear',
        'makeWIKI',
        'production_type'
    ]],
    unit_level_production_df[[
        'project_id',
        'namePrefix',
        'Country/Area',
        'shared unit (million boe/y)',
        'prodyear',
        'makeWIKI',
        'production_type'
    ]]
])

print("Combined all production categories into a single DataFrame. Displaying the first few rows:")
display(final_production_df.head())
print("Displaying the last few rows:")
display(final_production_df.tail())
print("Displaying value counts for 'production_type':")
display(final_production_df['production_type'].value_counts())

# # Combine project and field level production - current approach

# ===== Cell 22 =====
df = GOGET_download_with_prod.copy()

#filter DF for only 2023-2025 production
df = df[df['prodyear'].between(2020, 2025)]
df = df[df['Status'] == 'operating']
df['Project/Complex'] = df['Project/Complex'].fillna('')
df['Unit Name'] = df['Unit Name'].fillna('')
df['shared unit (million boe/y)'] = pd.to_numeric(
    df['shared unit (million boe/y)'], errors='coerce'
)

# ===== Cell 23 =====
results = []

project_level_count = 0
aggregated_count = 0

# Process unit-only entries (those without a Project/Complex) once before the loop
unit_only_df = df[
    (df['Project/Complex'] == '') &
    (df['shared unit (million boe/y)'].notna())
].copy()

unit_only_df['namePrefix'] = unit_only_df['Unit Name']
unit_only_df['production_type'] = 'unit only production'
# Append these to results
for _, row in unit_only_df.iterrows():
    results.append({
        'project_id': row['project_id'],
        'namePrefix': row['namePrefix'],
        'Country/Area': row['Country/Area'],
        'shared unit (million boe/y)': row['shared unit (million boe/y)'],
        'prodyear': row['prodyear'],
        'makeWIKI': row['makeWIKI'],
        'production_type': row['production_type']
    })

# Get Unit IDs that have been processed as 'unit only' to exclude from further processing
accounted_for_unit_ids = set(unit_only_df['Unit ID'].unique())

for project, group in df.groupby('Project/Complex'):
    # Skip groups where Project/Complex is empty, as they are handled by unit_only_df
    if project == '':
        continue

    # Filter out units that were already accounted for in unit_only_df
    group = group[~group['Unit ID'].isin(accounted_for_unit_ids)]

    # Project-level production: same-name rule
    project_level = group[
        (group['Project/Complex'] == group['Unit Name']) &
        (group['shared unit (million boe/y)'].notna())
    ]

    if not project_level.empty:
        project_level_count += 1

        for _, row in project_level.iterrows():
            results.append({
                'project_id': row['project_id'],
                'namePrefix': project,
                'Country/Area': row['Country/Area'],
                'shared unit (million boe/y)': row['shared unit (million boe/y)'],
                'prodyear': row['prodyear'],
                'makeWIKI': row['makeWIKI'],
                'production_type': 'project level production'
            })
            # Add Unit IDs from project_level to accounted_for_unit_ids
            accounted_for_unit_ids.add(row['Unit ID'])

    else:
        # Aggregate lower-level units if no project-level entry for this Project/Complex
        lower_level = group[
            (group['Project/Complex'] != group['Unit Name']) &
            (group['shared unit (million boe/y)'].notna())
        ]

        # Filter out units that are already accounted for by project_level_production_df
        lower_level = lower_level[~lower_level['Unit ID'].isin(accounted_for_unit_ids)]

        if not lower_level.empty:
            aggregated_count += 1

            for country, cgroup in lower_level.groupby('Country/Area'):
                results.append({
                    'project_id': f"SUM_{project.replace(' ', '_')}",
                    'namePrefix': project,
                    'Country/Area': country,
                    'shared unit (million boe/y)': cgroup['shared unit (million boe/y)'].sum(),
                    'prodyear': cgroup['prodyear'].mean(),
                    'makeWIKI': cgroup['shared unit (million boe/y)'].sum() > 1,
                    'production_type': 'aggregated unit production'
                })
                # Add Unit IDs from this aggregated group to accounted_for_unit_ids
                accounted_for_unit_ids.update(cgroup['Unit ID'].unique())

# Convert results to DataFrame
final_production_df_old_method = pd.DataFrame(results)

print(f"Project-level entries: {project_level_count}")
print(f"Aggregated entries: {aggregated_count}")
print(f'unit only production: {len(unit_only_df)}')
display(final_production_df_old_method.head())

# ===== Cell 24 =====

final_production_df_old_method.to_csv(export_qc_path + f'{timestamp} final_production_df_old_method.csv')
