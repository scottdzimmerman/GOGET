"""
asset_impact_us_states_2025.py

Migrated from Colab notebook: 2025 Asset Impact US States 2025 12 10.ipynb
Auto-converted to a Python script. Colab-specific lines
(drive.mount, google.colab imports, shell/magic commands) have been
commented out and flagged; pip installs moved to ../requirements.txt.
"""

# ===== Cell 1 =====
# mount google drive
# [colab-only removed] from google.colab import drive
# [colab drive mount removed] drive.mount('/content/drive')

# ===== Cell 2 =====
# import libraries
import pandas as pd
import numpy as np

# import fuzzy match
# [moved to requirements.txt] !pip install fuzzywuzzy
# [moved to requirements.txt] !pip install python-Levenshtein
from fuzzywuzzy import process

# ===== Cell 3 =====
# name file path
AI_Folder = '/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/Data sets & reports (O&G)/O&G global materials/Asset Impact Data/2025 Data'
US_file = AI_Folder + '/GEM-AI 2025 6 US states OG data.parquet'

# ===== Cell 4 =====
# code from daan to open parquet
import pyarrow.parquet as pq

import os

# Folder that contains the Parquet file (fill this in)

location = AI_Folder
file_path = os.path.join(
    location,
    "GEM-AI 2025 6 US states OG data.parquet",

)

# Read the Parquet file
table = pq.read_table(file_path)
df = table.to_pandas()

# ===== Cell 5 =====
# load in wyoming and ohio data as well
WyomingOhioSup = AI_Folder + '/GEM-AI 2025 Ohio Wyoming Update.parquet'
table = pq.read_table(WyomingOhioSup)
WyomingOhioSup_df = table.to_pandas()

# bring in new ohio and wyoming data
df = df[~df['state'].isin(['ohio', 'wyoming'])]
df = pd.concat([df, WyomingOhioSup_df], ignore_index=True)
print(f'DataFrame updated with Ohio and Wyoming data from WyomingOhioSup_df. New row count: {len(df)}')

# ===== Cell 6 =====
# check unique states included
unique_states_list = df['state'].unique()
unique_states_str = ', '.join(unique_states_list)
print('Unique states are: ')
print(unique_states_str)

# check unique columns included
unique_columns = df.columns
print('Unique columns are: ')
print(unique_columns)

# ===== Cell 7 =====
# filter down to 2024 data
key_year = 2024
AIkeyyear = df[df['year'] == key_year]

# ===== Cell 8 =====
# check data density (is not blank) per state for each attribute in given year (2024 here)
density_data = []
for state in unique_states_list:
  state_df = AIkeyyear[AIkeyyear['state'] == state]
  # Avoid division by zero for empty state_df
  if len(state_df) == 0:
    for column in unique_columns:
      density_data.append({"State": state, "Column": column, "Density": 0.0})
    continue

  for column in unique_columns:
    density = state_df[column].count() / len(state_df)
    density_data.append({"State": state, "Column": column, "Density": density})

import pandas as pd
density_df = pd.DataFrame(density_data)
display(density_df)

# ===== Cell 9 =====
for state in unique_states_list:
  state_df = AIkeyyear[AIkeyyear['state'] == state]
  print(f'{state} has {len(state_df)} rows')
  # show state dfs names
  print(f'data frame for {state} has been created.')

# As of last run 2025 01 21:
# texas has 155212 rows
# data frame for texas has been created.
# new_mexico has 65990 rows
# data frame for new_mexico has been created.
# california has 54978 rows
# data frame for california has been created.
# pennsylvania has 86110 rows
# data frame for pennsylvania has been created.
# ohio has 36484 rows
# data frame for ohio has been created.
# wyoming has 30561 rows
# data frame for wyoming has been created.

# ===== Cell 10 =====
# calacuate the dry_gas_vol, gross_gas_vol, oil_and_condensate_vol, and ngl_vol for each states

premerge_totals_data = []

for state in unique_states_list:
  state_df = AIkeyyear[AIkeyyear['state'] == state]
  dry_gas_vol_sum = state_df['dry_gas_vol'].sum()
  gross_gas_vol_sum = state_df['gross_gas_vol'].sum()
  oil_and_condensate_vol_sum = state_df['oil_and_condensate_vol'].sum()
  ngl_vol_sum = state_df['ngl_vol'].sum()

  premerge_totals_data.append({
      'State': state,
      'Dry Gas Volume Total': dry_gas_vol_sum,
      'Gross Gas Volume Total': gross_gas_vol_sum,
      'Oil and Condensate Volume Total': oil_and_condensate_vol_sum,
      'NGL Volume Total': ngl_vol_sum
  })

premerge_totals_df = pd.DataFrame(premerge_totals_data)
display(premerge_totals_df)

# Gas volumes are listed in million cubic meters/y, liquids in million bbl/y

# ===== Cell 11 =====
# save out density_df
density_df.to_csv(f'{AI_Folder}/density_{key_year}.csv', index=False)
print(f'saved density_{key_year}.csv')

# ===== Cell 12 =====
# check texas offshore
Texas = AIkeyyear[AIkeyyear['state'] == 'texas']
Texas_offshore = Texas[Texas['field_terrain'] == 'Offshore']

# save to output
Texas_offshore.to_csv(f'{AI_Folder}/texas_offshore_{key_year}.csv', index=False)

# # Wyoming
# Wyoming was not updated in the 2025 GOGET release. Data is currently at the Field Name + County + Operator (n=205)

# ===== Cell 13 =====
# Install fuzzywuzzy if not already installed
# [moved to requirements.txt] !pip install fuzzywuzzy
# [moved to requirements.txt] !pip install python-Levenshtein

from fuzzywuzzy import process
import numpy as np

# ===== Cell 14 =====
# group wyoming df by field_name + operator_name
wyoming_df = AIkeyyear[AIkeyyear['state'] == 'wyoming']

# title case operator and field name
wyoming_df_capitalized = wyoming_df.copy()
wyoming_df_capitalized['operator_name'] = wyoming_df['operator_name'].str.title()
wyoming_df_capitalized['field_name'] = wyoming_df['field_name'].str.title()
wyoming_df_capitalized['formation_name'] = wyoming_df['formation_name'].str.title()

# Convert longitude and latitude to numeric, coercing errors to NaN
wyoming_df_capitalized['longitude'] = pd.to_numeric(wyoming_df_capitalized['longitude'], errors='coerce')
wyoming_df_capitalized['latitude'] = pd.to_numeric(wyoming_df_capitalized['latitude'], errors='coerce')

# fill in "formation not assigned" when formation_name = null
wyoming_df_capitalized['formation_name'] = wyoming_df_capitalized['formation_name'].fillna('Formation not assigned')
wyoming_df_capitalized['field_name'] = wyoming_df_capitalized['field_name'].fillna('Field not assigned')

# Replace "wc" in field_name with "Wild cat"
wyoming_df_capitalized['field_name'] = wyoming_df_capitalized['field_name'].str.replace('WC', 'Wild cat')

print("data cleaned")

# ===== Cell 15 =====
# group by operator + field
wyoming_df_grouped_field = wyoming_df_capitalized.groupby(['field_name', 'operator_name']).agg({
    'well_no': lambda x: '; '.join(x.astype(str).unique()),
    'longitude': 'mean',
    'latitude': 'mean',
    'gross_gas_vol': 'sum',
    'dry_gas_vol': 'sum',
    'oil_and_condensate_vol': 'sum',
    'ngl_vol': 'sum',
    'formation_name': lambda x: '; '.join(x.astype(str).unique()), # Include formation_name in aggregation
    'resource_type': lambda x: '; '.join(x.astype(str).unique()) # Include resource_type in aggregation
}).reset_index()

# count grouped rows
print(f'Wyoming has {len(wyoming_df_grouped_field)} rows when grouped by field + operator')
# print count of first not assinged entries
print(f'Wyoming has {len(wyoming_df_grouped_field[wyoming_df_grouped_field["field_name"] == "Field not assigned"])} rows with "Field not assigned"')

# ===== Cell 16 =====
# group wyoming df by field_name + operator_name
wyoming_df_grouped_formation = wyoming_df_capitalized.groupby(['formation_name', 'operator_name']).agg({
    'well_no': lambda x: '; '.join(x.astype(str).unique()),
    'longitude': 'mean',
    'latitude': 'mean',
    'gross_gas_vol': 'sum',
    'dry_gas_vol': 'sum',
    'oil_and_condensate_vol': 'sum',
    'ngl_vol': 'sum',
    'resource_type': lambda x: '; '.join(x.astype(str).unique()) # Include resource_type in aggregation
}).reset_index()

# count grouped rows
print(f'Wyoming has {len(wyoming_df_grouped_formation)} rows when grouped by formation + operator')

# print count of "Formation not assigned" entries
print(f'Wyoming has {len(wyoming_df_grouped_formation[wyoming_df_grouped_formation["formation_name"] == "Formation not assigned"])} rows with "Formation not assigned"')

# ===== Cell 17 =====
# check totals in formation grouping
WY_dry_gas_vol_sum = wyoming_df_grouped_formation['dry_gas_vol'].sum()
WY_gross_gas_vol_sum = wyoming_df_grouped_formation['gross_gas_vol'].sum()
WY_oil_and_condensate_vol_sum = wyoming_df_grouped_formation['oil_and_condensate_vol'].sum()
WY_ngl_vol_sum = wyoming_df_grouped_formation['ngl_vol'].sum()

print(f'formation grouped dry gas sum = {WY_dry_gas_vol_sum}')
print(f'formation grouped gross gas sum = {WY_gross_gas_vol_sum}')
print(f'formation grouped oil and condensate sum = {WY_oil_and_condensate_vol_sum}')
print(f'formation grouped ngl sum = {WY_ngl_vol_sum}')

# ===== Cell 18 =====
# check totals in field grouping
WY_dry_gas_vol_sum = wyoming_df_grouped_field['dry_gas_vol'].sum()
WY_gross_gas_vol_sum = wyoming_df_grouped_field['gross_gas_vol'].sum()
WY_oil_and_condensate_vol_sum = wyoming_df_grouped_field['oil_and_condensate_vol'].sum()
WY_ngl_vol_sum = wyoming_df_grouped_field['ngl_vol'].sum()

print(f'field grouped dry gas sum= {WY_dry_gas_vol_sum}')
print(f'field grouped gross gas sum = {WY_gross_gas_vol_sum}')
print(f'field grouped oil and condensate sum = {WY_oil_and_condensate_vol_sum}')
print(f'field grouped ngl sum = {WY_ngl_vol_sum}')


# ===== Cell 19 =====
# pull in GEM Entity IDs for top 95% operators
WY_top_op = pd.read_csv(f'{AI_Folder}/wyoming_grouped_formation_2024 - Unique Operators.csv')

# pull in field discovery years from GOGET
WY_GOGET_Folder = '/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/Data sets & reports (O&G)/O&G country materials/United States (GOGET O&G)/Wyoming (GOGET)/'
WY_disco_years = pd.read_csv(WY_GOGET_Folder + 'GOGET WY 2025 12 12 - GOGET fields discovery year.csv')

# ===== Cell 20 =====
# merge Entity ID based on Operator	in WY_top_op and operator_name in wyoming_df_grouped_formation
wyoming_df_grouped_formation_plusID = wyoming_df_grouped_formation.merge(WY_top_op, left_on='operator_name', right_on='Operator', how='left')
wyoming_df_grouped_field_plusID = wyoming_df_grouped_field.merge(WY_top_op, left_on='operator_name', right_on='Operator', how='left')

# drop columns from wyoming_df_grouped_formation
WY_Form_ID = wyoming_df_grouped_formation_plusID.drop(columns=['Operator', 'Production','Percent here','Percentage of Wyoming Gas Production by Company (2023), per PAW', 'Percentage of Wyoming Oil Production by Company (2023)'])
WY_Field_ID = wyoming_df_grouped_field_plusID.drop(columns=['Operator', 'Production','Percent here','Percentage of Wyoming Gas Production by Company (2023), per PAW', 'Percentage of Wyoming Oil Production by Company (2023)'])

# ===== Cell 21 =====
# drop rows where Entity ID is null
WY_Form_ID_noNull = WY_Form_ID.dropna(subset=['Entity ID']).copy()
WY_Field_ID_noNull = WY_Field_ID.dropna(subset=['Entity ID']).copy()

# print row count pre and post drop formation and field
print(f'Formation grouped has {len(wyoming_df_grouped_formation)} rows')
print(f'Formation groups with only top ops has {len(WY_Form_ID_noNull)} rows')
print(f'Field grouped has {len(wyoming_df_grouped_field)} rows')
print(f'Field groups with only top ops has {len(WY_Field_ID_noNull)} rows')

# ===== Cell 22 =====
# calcuate sums for gross_gas, dry gas, oil and cond, NGL in new dataframe for formations
filter_WY_dry_gas_vol_sum = WY_Form_ID_noNull['dry_gas_vol'].sum()
filter_WY_gross_gas_vol_sum = WY_Form_ID_noNull['gross_gas_vol'].sum()
filter_WY_oil_and_condensate_vol_sum = WY_Form_ID_noNull['oil_and_condensate_vol'].sum()
filter_WY_ngl_vol_sum = WY_Form_ID_noNull['ngl_vol'].sum()

# print sums
print(f'WY_Form_ID_noNull_sum dry_gas_vol = {filter_WY_dry_gas_vol_sum}')
print(f'WY_Form_ID_noNull_sum gross_gas_vol = {filter_WY_gross_gas_vol_sum}')
print(f'WY_Form_ID_noNull_sum oil_and_condensate_vol = {filter_WY_oil_and_condensate_vol_sum}')
print(f'WY_Form_ID_noNull_sum ngl_vol = {filter_WY_ngl_vol_sum}')

# ===== Cell 23 =====
# calcuate sums for gross_gas, dry gas, oil and cond, NGL in new dataframe for fields
filter_WY_dry_gas_vol_sum = WY_Field_ID_noNull['dry_gas_vol'].sum()
filter_WY_gross_gas_vol_sum = WY_Field_ID_noNull['gross_gas_vol'].sum()
filter_WY_oil_and_condensate_vol_sum = WY_Field_ID_noNull['oil_and_condensate_vol'].sum()
filter_WY_ngl_vol_sum = WY_Field_ID_noNull['ngl_vol'].sum()

# print sums
print(f'WY_Field_ID_noNull dry_gas_vol = {filter_WY_dry_gas_vol_sum}')
print(f'WY_Field_ID_noNull gross_gas_vol = {filter_WY_gross_gas_vol_sum}')
print(f'WY_Field_ID_noNull oil_and_condensate_vol = {filter_WY_oil_and_condensate_vol_sum}')
print(f'WY_Field_ID_noNull ngl_vol = {filter_WY_ngl_vol_sum}')

# ===== Cell 24 =====
# set row for choosing field or formation
row_choice = 'field' # User can change select 'formation' and 'field'

if row_choice == 'formation':
    df_to_use = WY_Form_ID_noNull
    name_col = 'formation_name'
    project_complex_col = 'formation_name'
elif row_choice == 'field':
    df_to_use = WY_Field_ID_noNull
    name_col = 'field_name'
    project_complex_col = 'formation_name'
else:
    raise ValueError("Invalid row_choice. Must be 'formation' or 'field'.")

choice = df_to_use

print(f'choice is {row_choice}')
choice.head()

# ===== Cell 25 =====
# Map resource type : Unconventional; Conventional, Conventional; Unconventional and Unconventional = "Unconventional". Conventional = Conventional
choice['resource_type'] = choice['resource_type'].replace({
    'Unconventional; Conventional': 'Unconventional',
    'Conventional; Unconventional': 'Unconventional',
    'Conventional': 'Conventional'
})

# ===== Cell 26 =====
import numpy as np

conditions = [
    (choice['dry_gas_vol'] > 0) & (choice['oil_and_condensate_vol'] > 0),
    (choice['dry_gas_vol'] == 0) & (choice['oil_and_condensate_vol'] > 0),
    (choice['dry_gas_vol'] > 0) & (choice['oil_and_condensate_vol'] == 0)
]

choices = ['oil and gas', 'oil', 'gas']

choice['fuel_type'] = np.select(conditions, choices, default=None)

# ===== Cell 27 =====
# merge discovery year on to choice based on field name
choice = choice.merge(WY_disco_years, left_on='field_name', right_on='Unit Name', how='left')

# drop columns from wyoming_df_grouped_formation
choice = choice.drop(columns=['Unit Name'])

# ===== Cell 28 =====
# format for GOGET bulk upload
# create asset name
choice.loc[:, 'name'] = choice[name_col] + ' - ' + choice['operator_name']

# add unit type
choice.loc[:, 'unit_type'] = "asset"

# add project/complex
choice.loc[:, 'project_complex'] = choice[project_complex_col]

# add coordinate accuracy
choice.loc[:, 'coordinate_accuracy'] = "exact"

# add operator source
choice.loc[:, 'operator_source'] = "WOGCC_Op_2025"

# add location source
choice.loc[:, 'location_source'] = "WOGCC_Loc_2025; WOGCC_Prod_2024"

# add resource source
choice.loc[:, 'resource_type_source'] = "WOGCC_Prod_2024"

# add discovery year source
choice.loc[:, 'discovery_year_source'] = "WOGCC_Prod_2024"

# replace "Wc" in name with "Wildcat"
choice['name'] = choice['name'].str.replace('Wc', 'Wildcat')

# ===== Cell 29 =====
choice.columns

# ===== Cell 30 =====
print(f'Number of rows in choice before deduplication: {len(choice)}')
choice.drop_duplicates(inplace=True)
print(f'Number of rows in choice after deduplication: {len(choice)}')

# ===== Cell 31 =====
# add total production column
choice['total_hydrocarbons_production'] = (choice['dry_gas_vol']*0.005883) + choice['oil_and_condensate_vol'] + choice['ngl_vol']

# show sum of total hydrocarbon
total_hydrocarbons_production = choice['total_hydrocarbons_production'].sum()
print(f'total hydrocarbon production = {total_hydrocarbons_production}')

# ===== Cell 32 =====
# set column order
# if choice = field, columns are 'name', 'unit_type', 'fuel_type', 'project_complex', 'longitude', 'latitude','coordinate_accuracy', 'location_source', 'operator_name', 'operator_source', 'Entity ID', 'resource_type', 'resource_type_source','Discovery year','discovery_year_source','well_no', 'total_hydrocarbons_production'
if row_choice == 'field': WY_Clean = choice[['name', 'unit_type', 'fuel_type', 'project_complex', 'longitude', 'latitude','coordinate_accuracy', 'location_source', 'operator_name', 'operator_source', 'Entity ID', 'resource_type', 'resource_type_source','Discovery year','discovery_year_source','well_no', 'total_hydrocarbons_production']].copy()
elif row_choice == 'formation': WY_Clean = choice[['name', 'unit_type', 'fuel_type', 'project_complex', 'longitude', 'latitude','coordinate_accuracy', 'location_source', 'operator_name', 'operator_source', 'Entity ID', 'resource_type', 'resource_type_source','well_no', 'total_hydrocarbons_production']].copy()

# ===== Cell 33 =====
# import existing GOGET IDs and names
GOGET_IDs = pd.read_csv(f'{WY_GOGET_Folder}Existing GOGET IDs.csv')

# ===== Cell 34 =====
# Create a list of Unit Names from GOGET_IDs for fuzzy matching -
goget_unit_names = GOGET_IDs['Unit Name'].tolist()

# Function to perform fuzzy matching and return the Unit ID
def fuzzy_match_unit_id(row, choices, ids_df, threshold=88): # Increased threshold to 90
    match = process.extractOne(row['name'], choices, score_cutoff=threshold)
    if match:
        # match[0] is the matched 'Unit Name', match[1] is the score
        # We need to find the original index in GOGET_IDs to get the Unit ID
        original_unit_name = match[0]
        unit_id = ids_df[ids_df['Unit Name'] == original_unit_name]['Unit ID'].iloc[0]
        return unit_id
    return np.nan

# Apply the fuzzy matching function to WY_Clean
WY_Clean['GOGET_Unit_ID'] = WY_Clean.apply(fuzzy_match_unit_id, axis=1, choices=goget_unit_names, ids_df=GOGET_IDs)

# calculate how many matches were made
matches = len(WY_Clean[WY_Clean['GOGET_Unit_ID'].notna()])

print("Fuzzy matching complete.")
print(f"{matches}" +' matches were made')

print("Displaying first 5 rows with new GOGET_Unit_ID:")
display(WY_Clean.head())

# ===== Cell 35 =====
production_cols = ['gross_gas_vol', 'dry_gas_vol', 'oil_and_condensate_vol', 'ngl_vol']
id_cols = [col for col in choice.columns if col not in production_cols] # This gets all non-production cols from 'choice'

WY_long_prod = pd.melt(choice,
                                  id_vars=id_cols,
                                  value_vars=production_cols,
                                  var_name='production_type',
                                  value_name='volume')

# Define columns to drop, based on which ones are present in the melted DataFrame
cols_to_drop_from_melted = ['Entity ID','well_no','longitude','latitude','unit_type', 'project_complex','coordinate_accuracy','operator_source','location_source', 'field_name','resource_type',	'resource_type_source',	'fuel_type',	'discovery_year_source',	'Discovery year']
if 'formation_name' in choice.columns:
    cols_to_drop_from_melted.append('formation_name')
elif 'field_name' in choice.columns:
    cols_to_drop_from_melted.append('field_name')
if 'operator_name' in choice.columns:
    cols_to_drop_from_melted.append('operator_name')

# Filter the list to only include columns actually present in WY_long_prod
existing_cols_to_drop = [col for col in cols_to_drop_from_melted if col in WY_long_prod.columns]
WY_long_prod.drop(columns=existing_cols_to_drop, inplace=True)

# ===== Cell 36 =====
# replace production type entries as follows, 'gross_gas_vol' = gross gas 'dry_gas_vol' = dry gas, 'oil_and_condensate_vol' = oil and condensates, 'ngl_vol' = NGL
WY_long_prod['fuel description'] = WY_long_prod['production_type'].replace({'gross_gas_vol': 'gross gas', 'dry_gas_vol': 'dry gas', 'oil_and_condensate_vol': 'oil and condensates', 'ngl_vol': 'NGL'})

# add production year column, add entries as 2024
WY_long_prod['Year'] = 2024

# add "Production/Reserves" column, set all rows as "production"
WY_long_prod['production/reserves'] = 'production'

# rename volume as "Quantity"
WY_long_prod.rename(columns={'volume': 'Quantity'}, inplace=True)

# add quantity unit column, if gross gas or dry gas, set as million cubic meters/y
WY_long_prod['quantity_unit'] = WY_long_prod['fuel description'].apply(lambda x: 'million cubic meters/y' if x in ['gross gas', 'dry gas'] else 'million bbl/y')

# add it production source
WY_long_prod['Datasource'] = 'WOGCC_Prod_2024'

# ===== Cell 37 =====
print(f'Number of rows in WY_long_prod before deduplication: {len(WY_long_prod)}')
WY_long_prod.drop_duplicates(inplace=True)
print(f'Number of rows in WY_long_prod after deduplication: {len(WY_long_prod)}')

# ===== Cell 38 =====
# sum entries by production_type in WY_long_prod
WY_long_prod_gas = WY_long_prod[WY_long_prod['fuel description'] == 'dry gas']['Quantity'].sum()
WY_long_prod_oil = WY_long_prod[WY_long_prod['fuel description'] == 'oil and condensates']['Quantity'].sum()

print(f"Total sales gas volume: {WY_long_prod_gas}")
print(f"Total oil and condensates volume: {WY_long_prod_oil}")

# ===== Cell 39 =====
WY_Clean

# ===== Cell 40 =====
# create time stamp
import datetime

time_stamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

print(time_stamp)

# ===== Cell 41 =====
# save as csv

# wyoming_df_grouped_formation.to_csv(f'{WY_GOGET_Folder}/wyoming_grouped_formation_{key_year}.csv', index=False)
WY_Clean.to_csv(f'{WY_GOGET_Folder}/WY_AI_FOR_GOGET{key_year}_{time_stamp}.csv', index=False)
WY_long_prod.to_csv(f'{WY_GOGET_Folder}/wyoming_grouped_formation_long_{key_year}.csv', index=False)

# # Ohio Gemini Task

# ## Filter Ohio Data
#
# ### Subtask:
# Filter the main DataFrame (df) to include only records for the state of 'ohio' and the specified 'key_year' (2024).

# **Reasoning**:
# To filter the DataFrame `df` for records corresponding to 'ohio' and the `key_year`, I will use boolean indexing on both conditions and store the result in `OHkeyyear`.
#

# ===== Cell 42 =====
OHkeyyear = AIkeyyear[(df['state'] == 'ohio') & (df['year'] == key_year)]
print(f"The 'df' DataFrame has been filtered for the state of ohio and the year {key_year}, resulting in {len(OHkeyyear)} rows.")

# ## Clean and Capitalize Ohio Data
#
# ### Subtask:
# Create a copy of the filtered Ohio data, clean and standardize operator, field, and formation names, and convert geographic coordinates.

# **Reasoning**:
# To prepare the Ohio data for analysis and GOGET bulk upload, I will create a copy of the filtered Ohio DataFrame, convert text columns to title case, handle missing values in field and formation names, standardize geographic coordinates to numeric, and replace 'WC' with 'Wild cat' in field names for consistency.
#

# ===== Cell 43 =====
ohio_df_capitalized = OHkeyyear.copy()
ohio_df_capitalized['operator_name'] = ohio_df_capitalized['operator_name'].str.title()
ohio_df_capitalized['field_name'] = ohio_df_capitalized['field_name'].str.title()
ohio_df_capitalized['formation_name'] = ohio_df_capitalized['formation_name'].str.title()

ohio_df_capitalized['longitude'] = pd.to_numeric(ohio_df_capitalized['longitude'], errors='coerce')
ohio_df_capitalized['latitude'] = pd.to_numeric(ohio_df_capitalized['latitude'], errors='coerce')

ohio_df_capitalized['formation_name'] = ohio_df_capitalized['formation_name'].fillna('Formation not assigned')
ohio_df_capitalized['field_name'] = ohio_df_capitalized['field_name'].fillna('Field not assigned')

ohio_df_capitalized['field_name'] = ohio_df_capitalized['field_name'].str.replace('WC', 'Wild cat', regex=False)

print("Ohio data has been cleaned and standardized.")

# **Reasoning**:
# The previous step cleaned and standardized the Ohio data. The next logical step, according to the overall task, is to group the data by `field_name` and `operator_name` to aggregate production volumes and other relevant details, similar to how the Wyoming data was processed.
#

# ===== Cell 44 =====
ohio_df_grouped_field = ohio_df_capitalized.groupby(['field_name', 'operator_name']).agg({
    'well_no': lambda x: '; '.join(x.astype(str).unique()),
    'longitude': 'mean',
    'latitude': 'mean',
    'gross_gas_vol': 'sum',
    'dry_gas_vol': 'sum',
    'oil_and_condensate_vol': 'sum',
    'ngl_vol': 'sum',
    'formation_name': lambda x: '; '.join(x.astype(str).unique()),
    'resource_type': lambda x: '; '.join(x.astype(str).unique())
}).reset_index()

print(f'Ohio has {len(ohio_df_grouped_field)} rows when grouped by field + operator')
print(f'Ohio has {len(ohio_df_grouped_field[ohio_df_grouped_field["field_name"] == "Field not assigned"])} rows with "Field not assigned"')

# **Reasoning**:
# The previous grouping by `field_name` and `operator_name` unexpectedly resulted in an empty DataFrame. To proceed with the overall task of grouping by both field and formation, and to further diagnose the issue, the next logical step is to perform the grouping by `formation_name` and `operator_name` as specified in the task, similar to how it was done for Wyoming data. This will help determine if the problem is specific to the 'field_name' grouping or a more general issue with the Ohio data for grouping.
#

# ===== Cell 45 =====
ohio_df_grouped_formation = ohio_df_capitalized.groupby(['formation_name', 'operator_name']).agg({
    'well_no': lambda x: '; '.join(x.astype(str).unique()),
    'longitude': 'mean',
    'latitude': 'mean',
    'gross_gas_vol': 'sum',
    'dry_gas_vol': 'sum',
    'oil_and_condensate_vol': 'sum',
    'ngl_vol': 'sum',
    'resource_type': lambda x: '; '.join(x.astype(str).unique())
}).reset_index()

print(f'Ohio has {len(ohio_df_grouped_formation)} rows when grouped by formation + operator')
print(f'Ohio has {len(ohio_df_grouped_formation[ohio_df_grouped_formation["formation_name"] == "Formation not assigned"])} rows with "Formation not assigned"')

# **Reasoning**:
# Both previous grouping attempts (by field and by formation) resulted in empty DataFrames, which is unexpected. To diagnose this, I need to inspect the `ohio_df_capitalized` DataFrame, specifically the columns used for grouping and aggregation, to identify why no groups are being formed. I will display the head of the DataFrame and check for nulls in critical columns.
#

# ===== Cell 46 =====
print("Head of ohio_df_capitalized:")
display(ohio_df_capitalized.head())

print("Checking for nulls in grouping and aggregation columns:")
print(ohio_df_capitalized[['field_name', 'operator_name', 'formation_name', 'gross_gas_vol', 'dry_gas_vol', 'oil_and_condensate_vol', 'ngl_vol']].isnull().sum())

# **Reasoning**:
# The previous output showed that the 'operator_name' column in `ohio_df_capitalized` is entirely null, causing the groupby operations to return empty DataFrames. To enable grouping by operator, I need to fill these null values with a placeholder, such as 'Operator not assigned'.
#

# ## California

# ===== Cell 47 =====
# set year and state

CAkeyyear = AIkeyyear[(AIkeyyear['state'] == 'california')]
print(f"The 'df' DataFrame has been filtered for the state of california and the year {key_year}, resulting in {len(CAkeyyear)} rows.")

# ===== Cell 48 =====
# clean names and fix capitalization
CA_df_capitalized = CAkeyyear.copy()

CA_df_capitalized['operator_name'] = CA_df_capitalized['operator_name'].str.title()
CA_df_capitalized['field_name'] = CA_df_capitalized['field_name'].str.title()
CA_df_capitalized['formation_name'] = CA_df_capitalized['formation_name'].str.title()

CA_df_capitalized['longitude'] = pd.to_numeric(CA_df_capitalized['longitude'], errors='coerce')
CA_df_capitalized['latitude'] = pd.to_numeric(CA_df_capitalized['latitude'], errors='coerce')

CA_df_capitalized['formation_name'] = CA_df_capitalized['formation_name'].fillna('Formation not assigned')
CA_df_capitalized['field_name'] = CA_df_capitalized['field_name'].fillna('Field not assigned')

CA_df_capitalized['field_name'] = CA_df_capitalized['field_name'].str.replace('Wc', 'Wild cat', regex=False)

CA_df_capitalized['operator_name'] = CA_df_capitalized['operator_name'].fillna('Operator not assigned')

print("California data has been cleaned and standardized.")

# ===== Cell 49 =====
CA_df_capitalized.columns

# ===== Cell 50 =====
# check entries where Field_name = Elk Hills, operator_name = California Resources
Elkhills_CR = CA_df_capitalized[(CA_df_capitalized['field_name'] == 'Elk Hills') & (CA_df_capitalized['operator_name'] == 'California Resources Elk Hills  Llc')]

# # Previous data was more granular

# ===== Cell 51 =====
# group by field
CA_df_grouped_field = CA_df_capitalized.groupby(['field_name', 'operator_name']).agg({
    'well_no': lambda x: '; '.join(x.astype(str).unique()),
    'longitude': 'mean',
    'latitude': 'mean',
    'gross_gas_vol': 'sum',
    'dry_gas_vol': 'sum',
    'oil_and_condensate_vol': 'sum',
    'ngl_vol': 'sum',
    'formation_name': lambda x: '; '.join(x.astype(str).unique()),
    'resource_type': lambda x: '; '.join(x.astype(str).unique())
}).reset_index()

print(f'California has {len(CA_df_grouped_field)} rows when grouped by field + operator')
print(f'California has {len(CA_df_grouped_field[CA_df_grouped_field["field_name"] == "Field not assigned"])} rows with "Field not assigned"')

# ===== Cell 52 =====
# group by formation
CA_df_grouped_formation = CA_df_capitalized.groupby(['formation_name', 'operator_name']).agg({
    'well_no': lambda x: '; '.join(x.astype(str).unique()),
    'longitude': 'mean',
    'latitude': 'mean',
    'gross_gas_vol': 'sum',
    'dry_gas_vol': 'sum',
    'oil_and_condensate_vol': 'sum',
    'ngl_vol': 'sum',
    'resource_type': lambda x: '; '.join(x.astype(str).unique())
}).reset_index()

print(f'California has {len(CA_df_grouped_formation)} rows when grouped by formation + operator')
print(f'California has {len(CA_df_grouped_formation[CA_df_grouped_formation["formation_name"] == "Formation not assigned"])} rows with "Formation not assigned"')

# ===== Cell 53 =====
# check totals
CA_dry_gas_vol_sum_form = CA_df_grouped_formation['dry_gas_vol'].sum()
CA_gross_gas_vol_sum_form = CA_df_grouped_formation['gross_gas_vol'].sum()
CA_oil_and_condensate_vol_sum_form = CA_df_grouped_formation['oil_and_condensate_vol'].sum()
CA_ngl_vol_sum_form = CA_df_grouped_formation['ngl_vol'].sum()

CA_dry_gas_vol_sum_fied = CA_df_grouped_field['dry_gas_vol'].sum()
CA_gross_gas_vol_sum_field = CA_df_grouped_field['gross_gas_vol'].sum()
CA_oil_and_condensate_vol_sum_field = CA_df_grouped_field['oil_and_condensate_vol'].sum()
CA_ngl_vol_sum_field = CA_df_grouped_field['ngl_vol'].sum()

print(f'Formation grouped dry gas sum = {CA_dry_gas_vol_sum_form}')
print(f'Formation grouped gross gas sum = {CA_gross_gas_vol_sum_form}')
print(f'Formation grouped oil and condensate sum = {CA_oil_and_condensate_vol_sum_form}')
print(f'Formation grouped ngl sum = {CA_ngl_vol_sum_form}')

print(f'Field grouped dry gas sum = {CA_dry_gas_vol_sum_fied}')
print(f'Field grouped gross gas sum = {CA_gross_gas_vol_sum_field}')
print(f'Field grouped oil and condensate sum = {CA_oil_and_condensate_vol_sum_field}')
print(f'Field grouped ngl sum = {CA_ngl_vol_sum_field}')

# ===== Cell 54 =====
# parse operators, to add in Entity ID's manually
# calculate total production
CA_df_grouped_field['total_hydrocarbons_production'] = (CA_df_grouped_field['dry_gas_vol']*0.005883) + CA_df_grouped_field['oil_and_condensate_vol']+ CA_df_grouped_field['ngl_vol']
CA_df_grouped_formation['total_hydrocarbons_production'] =  (CA_df_grouped_formation['dry_gas_vol']*0.005883) + CA_df_grouped_formation['oil_and_condensate_vol'] + CA_df_grouped_formation['ngl_vol']

# group by operator for datacleaning
CA_df_grouped_field_op = CA_df_grouped_field.groupby('operator_name').agg({'total_hydrocarbons_production': 'sum'})

# sort by production high to low
CA_df_grouped_field_op =CA_df_grouped_field_op.sort_values(by='total_hydrocarbons_production', ascending=False)

CA_GOGET_Folder = '/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/Data sets & reports (O&G)/O&G country materials/United States (GOGET O&G)/California (GOGET)'
CA_df_grouped_field_op.to_csv(f'{CA_GOGET_Folder}/CA_grouped_field_op.csv')

# ===== Cell 55 =====
# load in operator and discovery data (manually gathered)
CA_top_op = pd.read_csv(f'{CA_GOGET_Folder}/CA_grouped_field_top_op - CA_grouped_field_op.csv')
CA_disco_years = pd.read_csv(f'{CA_GOGET_Folder}/California Field Code and Discovery Year - Units in GOGET.csv')

print("California operator entity IDs and field discovery years have been loaded.")

# ===== Cell 56 =====
# update based on top operator cut offs
CA_top_op_for_merge = CA_top_op[['operator_name', 'Entity ID']].copy()

# merge Entity ID based on operator_name
CA_Form_ID = CA_df_grouped_formation.merge(CA_top_op_for_merge, on='operator_name', how='left')
CA_Field_ID = CA_df_grouped_field.merge(CA_top_op_for_merge, on='operator_name', how='left')

# drop rows where Entity ID is null
CA_Form_ID_noNull = CA_Form_ID.dropna(subset=['Entity ID']).copy()
CA_Field_ID_noNull = CA_Field_ID.dropna(subset=['Entity ID']).copy()

# print row count pre and post drop formation and field
print(f'Formation grouped has {len(CA_df_grouped_formation)} rows')
print(f'Formation groups with only top ops has {len(CA_Form_ID_noNull)} rows')
print(f'Field grouped has {len(CA_df_grouped_field)} rows')
print(f'Field groups with only top ops has {len(CA_Field_ID_noNull)} rows')

# ===== Cell 57 =====
row_choice = 'field' # User can change this to 'formation'

if row_choice == 'formation':
    choice = CA_Form_ID_noNull
    name_col = 'formation_name'
    project_complex_col = 'formation_name'
elif row_choice == 'field':
    choice = CA_Field_ID_noNull
    name_col = 'field_name'
    project_complex_col = 'formation_name'
else:
    raise ValueError("Invalid row_choice. Must be 'formation' or 'field'.")

print(f'Choice is {row_choice}')
choice.head()

# ===== Cell 58 =====
# standardize the 'resource_type' column for GOGET bulk upload

choice['resource_type'] = choice['resource_type'].replace({
    'Unconventional; Conventional': 'Unconventional',
    'Conventional; Unconventional': 'Unconventional',
    'Conventional': 'Conventional'
})

print("Resource types standardized.")

# ===== Cell 59 =====
# define fuel type
import numpy as np

conditions = [
    (choice['dry_gas_vol'] > 0) & (choice['oil_and_condensate_vol'] > 0),
    (choice['dry_gas_vol'] == 0) & (choice['oil_and_condensate_vol'] > 0),
    (choice['dry_gas_vol'] > 0) & (choice['oil_and_condensate_vol'] == 0)
]

choices = ['oil and gas', 'oil', 'gas']

choice['fuel_type'] = np.select(conditions, choices, default=None)

print("Fuel types have been assigned.")

# ===== Cell 60 =====
choice = choice.merge(CA_disco_years, left_on=name_col, right_on='Unit Name', how='left')
choice = choice.drop(columns=['Unit Name'])

print("Discovery years merged.")

# ===== Cell 61 =====
# format names based on field or formation list - add source
choice.loc[:, 'name'] = choice[name_col] + ' - ' + choice['operator_name']
choice.loc[:, 'unit_type'] = "asset"
choice.loc[:, 'project_complex'] = choice[project_complex_col]
choice.loc[:, 'coordinate_accuracy'] = "exact"
choice.loc[:, 'operator_source'] = "DOGGR_Op_2025"
choice.loc[:, 'location_source'] = "DOGGR_Loc_2025; DOGGR_Prod_2024"
choice.loc[:, 'resource_type_source'] = "DOGGR_Prod_2024"
choice.loc[:, 'discovery_year_source'] = "DOGGR_Prod_2024"
choice['name'] = choice['name'].str.replace('Wc', 'Wildcat', regex=False)

print("Data formatted for GOGET bulk upload.")

# ===== Cell 62 =====
# add total production column if it doesn't already exist (it should from the earlier step, but this is a safeguard)
if 'total_hydrocarbons_production' not in choice.columns:
    choice['total_hydrocarbons_production'] = (choice['dry_gas_vol']*0.005883) + choice['oil_and_condensate_vol'] + choice['ngl_vol']

# Select and order the final columns for CA_Clean
CA_Clean = choice[[
    'name',
    'unit_type',
    'fuel_type',
    'project_complex',
    'longitude',
    'latitude',
    'coordinate_accuracy',
    'location_source',
    'operator_name',
    'operator_source',
    'Entity ID',
    'resource_type',
    'resource_type_source',
    'Discovery year',
    'discovery_year_source',
    'well_no',
    'total_hydrocarbons_production'
]].copy()

# sort by total_hydrocarbons_production high to low
CA_Clean = CA_Clean.sort_values(by='total_hydrocarbons_production', ascending=False).reset_index(drop=True)

print("CA_Clean DataFrame created with selected and ordered columns.")
display(CA_Clean.head())

# ===== Cell 63 =====
# check totals in choice
CA_choice_dry_gas = choice['dry_gas_vol'].sum()
CA_choice_gross_gas = choice['gross_gas_vol'].sum()
CA_choice_condensate = choice['oil_and_condensate_vol'].sum()
CA_choice_ngl = choice['ngl_vol'].sum()

# print totals
print(f'{row_choice} top op dry gas sum = {CA_choice_dry_gas}')
print(f'{row_choice} top op gross gas sum = {CA_choice_gross_gas}')
print(f'{row_choice} top op oil and condensate sum = {CA_choice_condensate}')
print(f'{row_choice} top op  NGL sum = {CA_choice_ngl}')

# ===== Cell 64 =====
GOGET_IDs = pd.read_csv(f'{CA_GOGET_Folder}/GOGET CA - 2025-12-15T212103 - Unit ids.csv')

goget_unit_names = GOGET_IDs['Unit Name'].tolist()

def fuzzy_match_unit_id(row, choices, ids_df, threshold=87): #70 was way too low, 85 still too low, 86 had 205 matches, 87 had 4 - 2025 01 21
    match = process.extractOne(row['name'], choices, score_cutoff=threshold)
    if match:
        original_unit_name = match[0]
        unit_id = ids_df[ids_df['Unit Name'] == original_unit_name]['Unit ID'].iloc[0]
        return unit_id
    return np.nan

CA_Clean['GOGET_Unit_ID'] = CA_Clean.apply(fuzzy_match_unit_id, axis=1, choices=goget_unit_names, ids_df=GOGET_IDs)

matches = len(CA_Clean[CA_Clean['GOGET_Unit_ID'].notna()])

print("Fuzzy matching complete.")
print(f"{matches}" +' matches were made')
print("Displaying first 5 rows with new GOGET_Unit_ID:")
display(CA_Clean.head())

# ===== Cell 65 =====
production_cols = ['gross_gas_vol', 'dry_gas_vol', 'oil_and_condensate_vol', 'ngl_vol']
id_cols = [col for col in choice.columns if col not in production_cols]

CA_long_prod = pd.melt(choice,
                                  id_vars=id_cols,
                                  value_vars=production_cols,
                                  var_name='production_type',
                                  value_name='volume')

cols_to_drop_from_melted = ['Entity ID','well_no','longitude','latitude','unit_type', 'project_complex','coordinate_accuracy','operator_source','location_source', 'field_name','resource_type','resource_type_source','fuel_type','discovery_year_source','Discovery year', 'operator_name', 'total_hydrocarbons_production']

# Dynamically add 'formation_name' if it was not used as name_col
if row_choice == 'field': # if row_choice is 'field', formation_name is still a column and needs to be dropped
    if 'formation_name' in CA_long_prod.columns:
        cols_to_drop_from_melted.append('formation_name')

existing_cols_to_drop = [col for col in cols_to_drop_from_melted if col in CA_long_prod.columns]
CA_long_prod.drop(columns=existing_cols_to_drop, inplace=True)

print("California production data melted into long format.")
display(CA_long_prod.head())

# ===== Cell 66 =====
CA_long_prod['fuel description'] = CA_long_prod['production_type'].replace({'gross_gas_vol': 'gross gas', 'dry_gas_vol': 'dry gas', 'oil_and_condensate_vol': 'oil and condensates', 'ngl_vol': 'NGL'})

CA_long_prod['Year'] = key_year

CA_long_prod['production/reserves'] = 'production'

CA_long_prod.rename(columns={'volume': 'Quantity'}, inplace=True)

CA_long_prod['quantity_unit'] = CA_long_prod['fuel description'].apply(lambda x: 'million cubic meters/y' if x in ['gross gas', 'dry gas'] else 'million bbl/y')

CA_long_prod['Datasource'] = 'DOGGR_Prod_2024'

print("CA_long_prod has been formatted for GOGET bulk upload.")
display(CA_long_prod.head())

# ===== Cell 67 =====
import datetime
time_stamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# try saving as an excel instead
CA_Clean.to_excel(f'{CA_GOGET_Folder}/CA_AI_FOR_GOGET{key_year}_{time_stamp}.xlsx', index=False)
# add CA_long_prod as a tab to existing excel CA_Clean
with pd.ExcelWriter(f'{CA_GOGET_Folder}/CA_AI_FOR_GOGET{key_year}_{time_stamp}.xlsx', engine='openpyxl', mode='a') as writer:
    CA_long_prod.to_excel(writer, sheet_name='long_prod', index=False)
    print(f'Saved CA_AI_FOR_GOGET{key_year}_{time_stamp}.xlsx with long_prod tab')

# ## Texas

# ===== Cell 68 =====
# set year and state
key_year = 2024
active_state = 'texas'
activestatekeyyear = df[(df['state'] == active_state) & (df['year'] == key_year)]
print(f"The 'df' DataFrame has been filtered for the state of {active_state} and the year {key_year}, resulting in {len(activestatekeyyear)} rows.")

# ===== Cell 69 =====
# clean names and fix capitalization
ASKY_df_capitalized = activestatekeyyear.copy()

ASKY_df_capitalized['operator_name'] = ASKY_df_capitalized['operator_name'].str.title()
ASKY_df_capitalized['field_name'] = ASKY_df_capitalized['field_name'].str.title()
ASKY_df_capitalized['formation_name'] = ASKY_df_capitalized['formation_name'].str.title()

ASKY_df_capitalized['longitude'] = pd.to_numeric(ASKY_df_capitalized['longitude'], errors='coerce')
ASKY_df_capitalized['latitude'] = pd.to_numeric(ASKY_df_capitalized['latitude'], errors='coerce')

ASKY_df_capitalized['formation_name'] = ASKY_df_capitalized['formation_name'].fillna('Formation not assigned')
ASKY_df_capitalized['field_name'] = ASKY_df_capitalized['field_name'].fillna('Field not assigned')

ASKY_df_capitalized['field_name'] = ASKY_df_capitalized['field_name'].str.replace('Wc', 'Wild cat', regex=False)

ASKY_df_capitalized['operator_name'] = ASKY_df_capitalized['operator_name'].fillna('Operator not assigned')

print(f"{active_state} data has been cleaned and standardized.")

# ===== Cell 70 =====
# group by field
ASKY_df_grouped_field = ASKY_df_capitalized.groupby(['field_name', 'operator_name']).agg({
    'well_no': lambda x: '; '.join(x.astype(str).unique()),
    'longitude': 'mean',
    'latitude': 'mean',
    'gross_gas_vol': 'sum',
    'dry_gas_vol': 'sum',
    'oil_and_condensate_vol': 'sum',
    'ngl_vol': 'sum',
    'formation_name': lambda x: '; '.join(x.astype(str).unique()),
    'resource_type': lambda x: '; '.join(x.astype(str).unique())
}).reset_index()

print(f'{active_state} has {len(ASKY_df_grouped_field)} rows when grouped by field + operator')
print(f'{active_state} has {len(ASKY_df_grouped_field[ASKY_df_grouped_field["field_name"] == "Field not assigned"])} rows with "Field not assigned"')

# ===== Cell 71 =====
# group by formation
ASKY_df_grouped_formation = ASKY_df_capitalized.groupby(['formation_name', 'operator_name']).agg({
    'well_no': lambda x: '; '.join(x.astype(str).unique()),
    'longitude': 'mean',
    'latitude': 'mean',
    'gross_gas_vol': 'sum',
    'dry_gas_vol': 'sum',
    'oil_and_condensate_vol': 'sum',
    'ngl_vol': 'sum',
    'resource_type': lambda x: '; '.join(x.astype(str).unique())
}).reset_index()

print(f'{active_state} has {len(ASKY_df_grouped_formation)} rows when grouped by formation + operator')
print(f'{active_state} has {len(ASKY_df_grouped_formation[ASKY_df_grouped_formation["formation_name"] == "Formation not assigned"])} rows with "Formation not assigned"')

# ===== Cell 72 =====
# check totals
ASKY_dry_gas_vol_sum_form = ASKY_df_grouped_formation['dry_gas_vol'].sum()
ASKY_gross_gas_vol_sum_form = ASKY_df_grouped_formation['gross_gas_vol'].sum()
ASKY_oil_and_condensate_vol_sum_form = ASKY_df_grouped_formation['oil_and_condensate_vol'].sum()
ASKY_ngl_vol_sum_form = ASKY_df_grouped_formation['ngl_vol'].sum()

ASKY_dry_gas_vol_sum_field = ASKY_df_grouped_field['dry_gas_vol'].sum()
ASKY_gross_gas_vol_sum_field = ASKY_df_grouped_field['gross_gas_vol'].sum()
ASKY_oil_and_condensate_vol_sum_field = ASKY_df_grouped_field['oil_and_condensate_vol'].sum()
ASKY_ngl_vol_sum_field = ASKY_df_grouped_field['ngl_vol'].sum()

# check if sums are equal in both formation and field
if ASKY_dry_gas_vol_sum_form == ASKY_dry_gas_vol_sum_field and ASKY_gross_gas_vol_sum_form == ASKY_gross_gas_vol_sum_field and ASKY_oil_and_condensate_vol_sum_form == ASKY_oil_and_condensate_vol_sum_field and ASKY_ngl_vol_sum_form == ASKY_ngl_vol_sum_field: print('sums match')
else: print('sums do not match')

print(f'Formation grouped dry gas sum = {ASKY_dry_gas_vol_sum_form}')
print(f'Formation grouped gross gas sum = {ASKY_gross_gas_vol_sum_form}')
print(f'Formation grouped oil and condensate sum = {ASKY_oil_and_condensate_vol_sum_form}')
print(f'Formation grouped ngl sum = {ASKY_ngl_vol_sum_form}')

print(f'Field grouped dry gas sum = {ASKY_dry_gas_vol_sum_field}')
print(f'Field grouped gross gas sum = {ASKY_gross_gas_vol_sum_field}')
print(f'Field grouped oil and condensate sum = {ASKY_oil_and_condensate_vol_sum_field}')
print(f'Field grouped ngl sum = {ASKY_ngl_vol_sum_field}')

# ===== Cell 73 =====
# parse operators, to add in Entity ID's manually
# calculate total production
ASKY_df_grouped_field['total_hydrocarbons_production'] = (ASKY_df_grouped_field['dry_gas_vol']*0.005883) + ASKY_df_grouped_field['oil_and_condensate_vol']+ ASKY_df_grouped_field['ngl_vol']
ASKY_df_grouped_formation['total_hydrocarbons_production'] =  (ASKY_df_grouped_formation['dry_gas_vol']*0.005883) + ASKY_df_grouped_formation['oil_and_condensate_vol'] + ASKY_df_grouped_formation['ngl_vol']

# group by operator for datacleaning
ASKY_df_grouped_field_op = ASKY_df_grouped_field.groupby('operator_name').agg({'total_hydrocarbons_production': 'sum'})

# sort by production high to low
ASKY_df_grouped_field_op =ASKY_df_grouped_field_op.sort_values(by='total_hydrocarbons_production', ascending=False)

TX_GOGET_Folder = '/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/Data sets & reports (O&G)/O&G country materials/United States (GOGET O&G)/Texas (GOGET)'
ASKY_df_grouped_field_op.to_csv(f'{TX_GOGET_Folder}/TX_grouped_field_op.csv')

# ===== Cell 74 =====
# load in operator data (manually gathered)
ASKY_top_op = pd.read_csv(f'{TX_GOGET_Folder}/TX_grouped_field_op filled out - TX_grouped_field_op.csv')

# rename Database ID as Entity ID
ASKY_top_op = ASKY_top_op.rename(columns={'Database ID': 'Entity ID'})

# update based on top operator cut offs
ASKY_top_op_for_merge = ASKY_top_op[['operator_name', 'Entity ID']].copy()

# merge Entity ID based on operator_name
ASKY_Form_ID = ASKY_df_grouped_formation.merge(ASKY_top_op_for_merge, on='operator_name', how='left')
ASKY_Field_ID = ASKY_df_grouped_field.merge(ASKY_top_op_for_merge, on='operator_name', how='left')

# drop rows where Entity ID is null
ASKY_Form_ID_noNull = ASKY_Form_ID.dropna(subset=['Entity ID']).copy()
ASKY_Field_ID_noNull = ASKY_Field_ID.dropna(subset=['Entity ID']).copy()

# print row count pre and post drop formation and field
print(f'Formation grouped has {len(ASKY_df_grouped_formation)} rows')
print(f'Formation groups with only top ops has {len(ASKY_Form_ID_noNull)} rows')
print(f'Field grouped has {len(ASKY_df_grouped_field)} rows')
print(f'Field groups with only top ops has {len(ASKY_Field_ID_noNull)} rows')

# ===== Cell 75 =====
# check totals
ASKY_dry_gas_vol_sum_form_top_op = ASKY_Form_ID_noNull['dry_gas_vol'].sum()
ASKY_gross_gas_vol_sum_form_top_op = ASKY_Form_ID_noNull['gross_gas_vol'].sum()
ASKY_oil_and_condensate_vol_sum_form_top_op = ASKY_Form_ID_noNull['oil_and_condensate_vol'].sum()
ASKY_ngl_vol_sum_form_top_op = ASKY_Form_ID_noNull['ngl_vol'].sum()

ASKY_dry_gas_vol_sum_field_top_op = ASKY_Field_ID_noNull['dry_gas_vol'].sum()
ASKY_gross_gas_vol_sum_field_top_op = ASKY_Field_ID_noNull['gross_gas_vol'].sum()
ASKY_oil_and_condensate_vol_sum_field_top_op = ASKY_Field_ID_noNull['oil_and_condensate_vol'].sum()
ASKY_ngl_vol_sum_field_top_op = ASKY_Field_ID_noNull['ngl_vol'].sum()

print(f'Top op percent of formation grouped dry gas = {ASKY_dry_gas_vol_sum_form_top_op / ASKY_dry_gas_vol_sum_form:.2%}')
print(f'Top op percent of formation grouped gross gas sum = {ASKY_gross_gas_vol_sum_form_top_op / ASKY_gross_gas_vol_sum_form:.2%}')
print(f'Top op percent of formation grouped oil and condensate sum = {ASKY_oil_and_condensate_vol_sum_form_top_op / ASKY_oil_and_condensate_vol_sum_form:.2%}')
print(f'Top op percent of formation grouped ngl sum = {ASKY_ngl_vol_sum_form_top_op / ASKY_ngl_vol_sum_form:.2%}')

print(f'Top op percent of field grouped dry gas = {ASKY_dry_gas_vol_sum_field_top_op / ASKY_dry_gas_vol_sum_field:.2%}')
print(f'Top op percent of field grouped gross gas sum = {ASKY_gross_gas_vol_sum_field_top_op / ASKY_gross_gas_vol_sum_field:.2%}')
print(f'Top op percent of field grouped oil and condensate sum = {ASKY_oil_and_condensate_vol_sum_field_top_op / ASKY_oil_and_condensate_vol_sum_field:.2%}')
print(f'Top op percent of field grouped ngl sum = {ASKY_ngl_vol_sum_field_top_op / ASKY_ngl_vol_sum_field:.2%}')

# ===== Cell 76 =====
# adding in previously written texas code from https://colab.research.google.com/drive/1m_UD1GSsmFjzyObIlEgAHJSlLM3wrwU9?usp=sharing

# # Pennsylvania
# 2024 data had 1,240 million boe of production across 41 assets

# ===== Cell 77 =====
# set year and state
key_year = 2024
active_state = 'pennsylvania'
activestatekeyyear = df[(df['state'] == active_state) & (df['year'] == key_year)]
print(f"The 'df' DataFrame has been filtered for the state of {active_state} and the year {key_year}, resulting in {len(activestatekeyyear)} rows.")

# ===== Cell 78 =====
# clean names and fix capitalization
ASKY_df_capitalized = activestatekeyyear.copy()

ASKY_df_capitalized['operator_name'] = ASKY_df_capitalized['operator_name'].str.title()
ASKY_df_capitalized['field_name'] = ASKY_df_capitalized['field_name'].str.title()
ASKY_df_capitalized['formation_name'] = ASKY_df_capitalized['formation_name'].str.title()

ASKY_df_capitalized['longitude'] = pd.to_numeric(ASKY_df_capitalized['longitude'], errors='coerce')
ASKY_df_capitalized['latitude'] = pd.to_numeric(ASKY_df_capitalized['latitude'], errors='coerce')

ASKY_df_capitalized['formation_name'] = ASKY_df_capitalized['formation_name'].fillna('Formation not assigned')
ASKY_df_capitalized['field_name'] = ASKY_df_capitalized['field_name'].fillna('Field not assigned')

ASKY_df_capitalized['field_name'] = ASKY_df_capitalized['field_name'].str.replace('Wc', 'Wild cat', regex=False)

ASKY_df_capitalized['operator_name'] = ASKY_df_capitalized['operator_name'].fillna('Operator not assigned')

print(f"{active_state} data has been cleaned and standardized.")

# ===== Cell 79 =====
# group by field
ASKY_df_grouped_field = ASKY_df_capitalized.groupby(['field_name', 'operator_name']).agg({
    'well_no': lambda x: '; '.join(x.astype(str).unique()),
    'longitude': 'mean',
    'latitude': 'mean',
    'gross_gas_vol': 'sum',
    'dry_gas_vol': 'sum',
    'oil_and_condensate_vol': 'sum',
    'ngl_vol': 'sum',
    'formation_name': lambda x: '; '.join(x.astype(str).unique()),
    'resource_type': lambda x: '; '.join(x.astype(str).unique())
}).reset_index()

print(f'{active_state} has {len(ASKY_df_grouped_field)} rows when grouped by field + operator')
print(f'{active_state} has {len(ASKY_df_grouped_field[ASKY_df_grouped_field["field_name"] == "Field not assigned"])} rows with "Field not assigned"')

# ===== Cell 80 =====
# group by formation
ASKY_df_grouped_formation = ASKY_df_capitalized.groupby(['formation_name', 'operator_name']).agg({
    'well_no': lambda x: '; '.join(x.astype(str).unique()),
    'longitude': 'mean',
    'latitude': 'mean',
    'gross_gas_vol': 'sum',
    'dry_gas_vol': 'sum',
    'oil_and_condensate_vol': 'sum',
    'ngl_vol': 'sum',
    'resource_type': lambda x: '; '.join(x.astype(str).unique())
}).reset_index()

print(f'{active_state} has {len(ASKY_df_grouped_formation)} rows when grouped by formation + operator')
print(f'{active_state} has {len(ASKY_df_grouped_formation[ASKY_df_grouped_formation["formation_name"] == "Formation not assigned"])} rows with "Formation not assigned"')

# ===== Cell 81 =====
# check totals
ASKY_dry_gas_vol_sum_form = ASKY_df_grouped_formation['dry_gas_vol'].sum()
ASKY_gross_gas_vol_sum_form = ASKY_df_grouped_formation['gross_gas_vol'].sum()
ASKY_oil_and_condensate_vol_sum_form = ASKY_df_grouped_formation['oil_and_condensate_vol'].sum()
ASKY_ngl_vol_sum_form = ASKY_df_grouped_formation['ngl_vol'].sum()

ASKY_dry_gas_vol_sum_field = ASKY_df_grouped_field['dry_gas_vol'].sum()
ASKY_gross_gas_vol_sum_field = ASKY_df_grouped_field['gross_gas_vol'].sum()
ASKY_oil_and_condensate_vol_sum_field = ASKY_df_grouped_field['oil_and_condensate_vol'].sum()
ASKY_ngl_vol_sum_field = ASKY_df_grouped_field['ngl_vol'].sum()

# check if sums are equal in both formation and field
if ASKY_dry_gas_vol_sum_form == ASKY_dry_gas_vol_sum_field and ASKY_gross_gas_vol_sum_form == ASKY_gross_gas_vol_sum_field and ASKY_oil_and_condensate_vol_sum_form == ASKY_oil_and_condensate_vol_sum_field and ASKY_ngl_vol_sum_form == ASKY_ngl_vol_sum_field: print('sums match')
else: print('sums do not match')

print(f'Formation grouped dry gas sum = {ASKY_dry_gas_vol_sum_form}')
print(f'Formation grouped gross gas sum = {ASKY_gross_gas_vol_sum_form}')
print(f'Formation grouped oil and condensate sum = {ASKY_oil_and_condensate_vol_sum_form}')
print(f'Formation grouped ngl sum = {ASKY_ngl_vol_sum_form}')

print(f'Field grouped dry gas sum = {ASKY_dry_gas_vol_sum_field}')
print(f'Field grouped gross gas sum = {ASKY_gross_gas_vol_sum_field}')
print(f'Field grouped oil and condensate sum = {ASKY_oil_and_condensate_vol_sum_field}')
print(f'Field grouped ngl sum = {ASKY_ngl_vol_sum_field}')

# ===== Cell 82 =====
# parse operators, to add in Entity ID's manually
# calculate total production
ASKY_df_grouped_field['total_hydrocarbons_production'] = (ASKY_df_grouped_field['dry_gas_vol']*0.005883) + ASKY_df_grouped_field['oil_and_condensate_vol']+ ASKY_df_grouped_field['ngl_vol']
ASKY_df_grouped_formation['total_hydrocarbons_production'] =  (ASKY_df_grouped_formation['dry_gas_vol']*0.005883) + ASKY_df_grouped_formation['oil_and_condensate_vol'] + ASKY_df_grouped_formation['ngl_vol']

# group by operator for datacleaning
ASKY_df_grouped_formation_op = ASKY_df_grouped_formation.groupby('operator_name').agg({'total_hydrocarbons_production': 'sum'})

# sort by production high to low
ASKY_df_grouped_formation_op =ASKY_df_grouped_formation_op.sort_values(by='total_hydrocarbons_production', ascending=False)

PA_GOGET_Folder = '/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/Data sets & reports (O&G)/O&G country materials/United States (GOGET O&G)/Pennsylvania (GOGET)'
ASKY_df_grouped_formation_op.to_csv(f'{PA_GOGET_Folder}/PA_grouped_field_op.csv')

# ===== Cell 83 =====
# load in operator data (manually gathered)
ASKY_top_op = pd.read_csv(f'{PA_GOGET_Folder}/PA_grouped_field_op -  filled out - PA_grouped_field_op.csv')

# rename Database ID as Entity ID
ASKY_top_op = ASKY_top_op.rename(columns={'Database ID': 'Entity ID'})

# update based on top operator cut offs
ASKY_top_op_for_merge = ASKY_top_op[['operator_name', 'Entity ID']].copy()

# merge Entity ID based on operator_name
ASKY_Form_ID = ASKY_df_grouped_formation.merge(ASKY_top_op_for_merge, on='operator_name', how='left')
ASKY_Field_ID = ASKY_df_grouped_field.merge(ASKY_top_op_for_merge, on='operator_name', how='left')

# drop rows where Entity ID is null
ASKY_Form_ID_noNull = ASKY_Form_ID.dropna(subset=['Entity ID']).copy()
ASKY_Field_ID_noNull = ASKY_Field_ID.dropna(subset=['Entity ID']).copy()

# print row count pre and post drop formation and field
print(f'Formation grouped has {len(ASKY_df_grouped_formation)} rows')
print(f'Formation groups with only top ops has {len(ASKY_Form_ID_noNull)} rows')
print(f'Field grouped has {len(ASKY_df_grouped_field)} rows')
print(f'Field groups with only top ops has {len(ASKY_Field_ID_noNull)} rows')

# ===== Cell 84 =====
# check totals
ASKY_dry_gas_vol_sum_form_top_op = ASKY_Form_ID_noNull['dry_gas_vol'].sum()
ASKY_gross_gas_vol_sum_form_top_op = ASKY_Form_ID_noNull['gross_gas_vol'].sum()
ASKY_oil_and_condensate_vol_sum_form_top_op = ASKY_Form_ID_noNull['oil_and_condensate_vol'].sum()
ASKY_ngl_vol_sum_form_top_op = ASKY_Form_ID_noNull['ngl_vol'].sum()

ASKY_dry_gas_vol_sum_field_top_op = ASKY_Field_ID_noNull['dry_gas_vol'].sum()
ASKY_gross_gas_vol_sum_field_top_op = ASKY_Field_ID_noNull['gross_gas_vol'].sum()
ASKY_oil_and_condensate_vol_sum_field_top_op = ASKY_Field_ID_noNull['oil_and_condensate_vol'].sum()
ASKY_ngl_vol_sum_field_top_op = ASKY_Field_ID_noNull['ngl_vol'].sum()

print(f'Top op percent of formation grouped dry gas = {ASKY_dry_gas_vol_sum_form_top_op / ASKY_dry_gas_vol_sum_form:.2%}')
print(f'Top op percent of formation grouped gross gas sum = {ASKY_gross_gas_vol_sum_form_top_op / ASKY_gross_gas_vol_sum_form:.2%}')
print(f'Top op percent of formation grouped oil and condensate sum = {ASKY_oil_and_condensate_vol_sum_form_top_op / ASKY_oil_and_condensate_vol_sum_form:.2%}')
print(f'Top op percent of formation grouped ngl sum = {ASKY_ngl_vol_sum_form_top_op / ASKY_ngl_vol_sum_form:.2%}')

print(f'Top op percent of field grouped dry gas = {ASKY_dry_gas_vol_sum_field_top_op / ASKY_dry_gas_vol_sum_field:.2%}')
print(f'Top op percent of field grouped gross gas sum = {ASKY_gross_gas_vol_sum_field_top_op / ASKY_gross_gas_vol_sum_field:.2%}')
print(f'Top op percent of field grouped oil and condensate sum = {ASKY_oil_and_condensate_vol_sum_field_top_op / ASKY_oil_and_condensate_vol_sum_field:.2%}')
print(f'Top op percent of field grouped ngl sum = {ASKY_ngl_vol_sum_field_top_op / ASKY_ngl_vol_sum_field:.2%}')

# ===== Cell 85 =====
# select field or formation
row_choice = 'formation' # User can change this to 'formation'

if row_choice == 'formation':
    choice = ASKY_Form_ID_noNull
    name_col = 'formation_name'
    project_complex_col = 'formation_name'
elif row_choice == 'field':
    choice = ASKY_Field_ID_noNull
    name_col = 'field_name'
    project_complex_col = 'formation_name'
else:
    raise ValueError("Invalid row_choice. Must be 'formation' or 'field'.")

print(f'Choice is {row_choice}')
choice.head()

# ===== Cell 86 =====
# standardize the 'resource_type' column for GOGET bulk upload

choice['resource_type'] = choice['resource_type'].replace({
    'Unconventional; Conventional': 'Unconventional',
    'Conventional; Unconventional': 'Unconventional',
    'Conventional': 'Conventional'
})

print("Resource types standardized.")

# ===== Cell 87 =====
# define fuel type
import numpy as np

conditions = [
    (choice['dry_gas_vol'] > 0) & (choice['oil_and_condensate_vol'] > 0),
    (choice['dry_gas_vol'] == 0) & (choice['oil_and_condensate_vol'] > 0),
    (choice['dry_gas_vol'] > 0) & (choice['oil_and_condensate_vol'] == 0)
]

choices = ['oil and gas', 'oil', 'gas']

choice['fuel_type'] = np.select(conditions, choices, default=None)

print("Fuel types have been assigned.")

# ===== Cell 88 =====
# format names based on field or formation list - add source
choice.loc[:, 'name'] = choice[name_col] + ' - ' + choice['operator_name']
choice.loc[:, 'unit_type'] = "asset"
choice.loc[:, 'project_complex'] = choice[project_complex_col]
choice.loc[:, 'coordinate_accuracy'] = "exact"
choice.loc[:, 'operator_source'] = "PAProduction2024"
choice.loc[:, 'location_source'] = "PAProduction2024"
choice.loc[:, 'resource_type_source'] = "PAProduction2024"
choice.loc[:, 'discovery_year_source'] = "PAProduction2024"
choice['name'] = choice['name'].str.replace('Wc', 'Wildcat', regex=False)

print("Data formatted for GOGET bulk upload.")

# ===== Cell 89 =====
# add total production column if it doesn't already exist (it should from the earlier step, but this is a safeguard)
if 'total_hydrocarbons_production' not in choice.columns:
    choice['total_hydrocarbons_production'] = (choice['dry_gas_vol']*0.005883) + choice['oil_and_condensate_vol'] + choice['ngl_vol']

# Select and order the final columns for ASKY_Clean
ASKY_Clean = choice[[
    'name',
    'unit_type',
    'fuel_type',
    'project_complex',
    'longitude',
    'latitude',
    'coordinate_accuracy',
    'location_source',
    'operator_name',
    'operator_source',
    'Entity ID',
    'resource_type',
    'resource_type_source',
    # 'Discovery year',
    # 'discovery_year_source',
    'well_no',
    'total_hydrocarbons_production'
]].copy()

# sort by total_hydrocarbons_production high to low
ASKY_Clean = ASKY_Clean.sort_values(by='total_hydrocarbons_production', ascending=False).reset_index(drop=True)

print("ASKY_Clean DataFrame created with selected and ordered columns.")
display(ASKY_Clean.head())

# ===== Cell 90 =====
# check totals in choice
ASKY_choice_total = ASKY_Clean['total_hydrocarbons_production'].sum()


# print totals
print(f'{active_state} parsed data has {ASKY_choice_total} million boe')

# ===== Cell 91 =====
# save out ASKY_Clean for manual matching
ASKY_Clean.to_excel(f'{PA_GOGET_Folder}/PA_GOGET_Clean_for_ID_Match.xlsx', index=False)

# ===== Cell 92 =====
GOGET_IDs = pd.read_csv(f'{PA_GOGET_Folder}/PA_GOGET_Clean_for_ID_Match.xlsx - Manually Matched - fixed - PA_GOGET_Clean_for_ID_Match.xlsx - Manually Matched.csv') # fuzzy match was not owrking, so i manually matched these

# add goget IDs matching on name to append "GOGET_Unit_ID"
ASKY_Clean = ASKY_Clean.merge(GOGET_IDs[['name', 'GOGET_Unit_ID']], on='name', how='left')

ASKY_Clean

# ===== Cell 93 =====
production_cols = ['gross_gas_vol', 'dry_gas_vol', 'oil_and_condensate_vol', 'ngl_vol']
id_cols = [col for col in choice.columns if col not in production_cols]

ASKY_long_prod = pd.melt(choice,
                                  id_vars=id_cols,
                                  value_vars=production_cols,
                                  var_name='production_type',
                                  value_name='volume')

cols_to_drop_from_melted = ['Entity ID','well_no','longitude','latitude','unit_type', 'project_complex','coordinate_accuracy','operator_source','location_source', 'field_name','resource_type','resource_type_source','fuel_type', 'operator_name','discovery_year_source' ,'total_hydrocarbons_production']

# Dynamically add 'formation_name' if it was not used as name_col
if row_choice == 'field': # if row_choice is 'field', formation_name is still a column and needs to be dropped
    if 'formation_name' in ASKY_long_prod.columns:
        cols_to_drop_from_melted.append('formation_name')

existing_cols_to_drop = [col for col in cols_to_drop_from_melted if col in ASKY_long_prod.columns]
ASKY_long_prod.drop(columns=existing_cols_to_drop, inplace=True)

print(f'{active_state} parsed data has been melted into long format')
display(ASKY_long_prod.head())

# ===== Cell 94 =====
ASKY_long_prod['fuel description'] = ASKY_long_prod['production_type'].replace({'gross_gas_vol': 'gross gas', 'dry_gas_vol': 'dry gas', 'oil_and_condensate_vol': 'oil and condensates', 'ngl_vol': 'NGL'})

ASKY_long_prod['Year'] = key_year

ASKY_long_prod['production/reserves'] = 'production'

ASKY_long_prod.rename(columns={'volume': 'Quantity'}, inplace=True)

ASKY_long_prod['quantity_unit'] = ASKY_long_prod['fuel description'].apply(lambda x: 'million cubic meters/y' if x in ['gross gas', 'dry gas'] else 'million bbl/y')

ASKY_long_prod['Datasource'] = 'PAProduction2024'

print("ASKY_long_prod has been formatted for GOGET bulk upload.")
display(ASKY_long_prod.head())

# ===== Cell 95 =====
import datetime
time_stamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

ASKY_Clean.to_excel(f'{PA_GOGET_Folder}/{active_state}_AI_FOR_GOGET{key_year}_{time_stamp}.xlsx', index=False)
ASKY_long_prod.to_excel(f'{PA_GOGET_Folder}/{active_state}_grouped_formation_long_{key_year}.xlsx', index=False)

print(f'Saved {active_state}_AI_FOR_GOGET{key_year}_{time_stamp}.xlsx and {active_state}_grouped_formation_long_{key_year}.xlsx to {PA_GOGET_Folder}')

# # New Mexico

# ===== Cell 96 =====
# set year and state
key_year = 2024
active_state = 'new_mexico'
activestatekeyyear = df[(df['state'] == active_state) & (df['year'] == key_year)]
print(f"The 'df' DataFrame has been filtered for the state of {active_state} and the year {key_year}, resulting in {len(activestatekeyyear)} rows.")

# ===== Cell 97 =====
# add in formation parsed here https://colab.research.google.com/drive/152Mdo5hBz_PsVZzRHgRO34sJOwzR2SCl#scrollTo=XgIA2Avx2ek3
formation_file = '/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/Data sets & reports (O&G)/O&G country materials/United States (GOGET O&G)/New Mexico (GOGET)/County Level Data (GOGET)/Location and General Data 2025/api_formation_all_2026-01-15_18-06-42.csv'
formation_df = pd.read_csv(formation_file)
# Ensure the 'api' column in formation_df is of string type for merging
formation_df['api'] = formation_df['api'].astype(str)
formation_df.head()

# ===== Cell 98 =====
activestatekeyyear.columns

# ===== Cell 99 =====
# remove dashes in well_no for matching
activestatekeyyear['api'] = activestatekeyyear['well_no'].str.replace('-', '')

# ===== Cell 100 =====
# matching well_no and api, append formation as formation_gotech
activestatekeyyear = activestatekeyyear.merge(formation_df[['api', 'formation']], left_on='api', right_on='api', how='left')
activestatekeyyear.head()

# ===== Cell 101 =====
# rename "formation" as "NM_added_formation"
activestatekeyyear.rename(columns={'formation': 'NM_added_formation'}, inplace=True)

# ===== Cell 102 =====
activestatekeyyear.columns

# ===== Cell 103 =====
# drop existing formation_name
activestatekeyyear.drop(columns=['formation_name'], inplace=True)

# ===== Cell 104 =====
# clean names and fix capitalization
ASKY_df_capitalized = activestatekeyyear.copy()

ASKY_df_capitalized['operator_name'] = ASKY_df_capitalized['operator_name'].str.title()
ASKY_df_capitalized['field_name'] = ASKY_df_capitalized['field_name'].str.title()
ASKY_df_capitalized['formation_name'] = ASKY_df_capitalized['NM_added_formation'].str.title()

# clean blank space on formation name
ASKY_df_capitalized['formation_name'] = ASKY_df_capitalized['formation_name'].str.strip()

ASKY_df_capitalized['longitude'] = pd.to_numeric(ASKY_df_capitalized['longitude'], errors='coerce')
ASKY_df_capitalized['latitude'] = pd.to_numeric(ASKY_df_capitalized['latitude'], errors='coerce')

ASKY_df_capitalized['formation_name'] = ASKY_df_capitalized['formation_name'].fillna('Formation not assigned')
ASKY_df_capitalized['field_name'] = ASKY_df_capitalized['field_name'].fillna('Field not assigned')

ASKY_df_capitalized['field_name'] = ASKY_df_capitalized['field_name'].str.replace('Wc', 'Wild cat', regex=False)

ASKY_df_capitalized['operator_name'] = ASKY_df_capitalized['operator_name'].fillna('Operator not assigned')

print(f"{active_state} data has been cleaned and standardized.")

# ===== Cell 105 =====
# sort ASKY_df_capitalized by oil_and_condensate_vol high to low
ASKY_df_capitalized = ASKY_df_capitalized.sort_values(by='oil_and_condensate_vol', ascending=False)

# save out wells to examine
NM_GOGET_Folder = '/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/Data sets & reports (O&G)/O&G country materials/United States (GOGET O&G)/New Mexico (GOGET)'
ASKY_df_capitalized.to_csv(f'{NM_GOGET_Folder}/NM_df_capitalized.csv', index=False)

# ===== Cell 106 =====
# group by field
ASKY_df_grouped_field = ASKY_df_capitalized.groupby(['field_name', 'operator_name']).agg({
    'well_no': lambda x: '; '.join(x.astype(str).unique()),
    'longitude': 'mean',
    'latitude': 'mean',
    'gross_gas_vol': 'sum',
    'dry_gas_vol': 'sum',
    'oil_and_condensate_vol': 'sum',
    'ngl_vol': 'sum',
    'formation_name': lambda x: '; '.join(x.astype(str).unique()),
    'resource_type': lambda x: '; '.join(x.astype(str).unique())
}).reset_index()

print(f'{active_state} has {len(ASKY_df_grouped_field)} rows when grouped by field + operator')
print(f'{active_state} has {len(ASKY_df_grouped_field[ASKY_df_grouped_field["field_name"] == "Field not assigned"])} rows with "Field not assigned"')

# ===== Cell 107 =====
# group by formation
ASKY_df_grouped_formation = ASKY_df_capitalized.groupby(['formation_name', 'operator_name']).agg({
    'well_no': lambda x: '; '.join(x.astype(str).unique()),
    'longitude': 'mean',
    'latitude': 'mean',
    'gross_gas_vol': 'sum',
    'dry_gas_vol': 'sum',
    'oil_and_condensate_vol': 'sum',
    'ngl_vol': 'sum',
    'resource_type': lambda x: '; '.join(x.astype(str).unique())
}).reset_index()

print(f'{active_state} has {len(ASKY_df_grouped_formation)} rows when grouped by formation + operator')
print(f'{active_state} has {len(ASKY_df_grouped_formation[ASKY_df_grouped_formation["formation_name"] == "Formation not assigned"])} rows with "Formation not assigned"')

# ===== Cell 108 =====
# check totals
ASKY_dry_gas_vol_sum_form = ASKY_df_grouped_formation['dry_gas_vol'].sum()
ASKY_gross_gas_vol_sum_form = ASKY_df_grouped_formation['gross_gas_vol'].sum()
ASKY_oil_and_condensate_vol_sum_form = ASKY_df_grouped_formation['oil_and_condensate_vol'].sum()
ASKY_ngl_vol_sum_form = ASKY_df_grouped_formation['ngl_vol'].sum()

ASKY_dry_gas_vol_sum_field = ASKY_df_grouped_field['dry_gas_vol'].sum()
ASKY_gross_gas_vol_sum_field = ASKY_df_grouped_field['gross_gas_vol'].sum()
ASKY_oil_and_condensate_vol_sum_field = ASKY_df_grouped_field['oil_and_condensate_vol'].sum()
ASKY_ngl_vol_sum_field = ASKY_df_grouped_field['ngl_vol'].sum()

# check if sums are equal in both formation and field
if ASKY_dry_gas_vol_sum_form == ASKY_dry_gas_vol_sum_field and ASKY_gross_gas_vol_sum_form == ASKY_gross_gas_vol_sum_field and ASKY_oil_and_condensate_vol_sum_form == ASKY_oil_and_condensate_vol_sum_field and ASKY_ngl_vol_sum_form == ASKY_ngl_vol_sum_field: print('sums match')
else: print('sums do not match')

print(f'Formation grouped dry gas sum = {ASKY_dry_gas_vol_sum_form}')
print(f'Formation grouped gross gas sum = {ASKY_gross_gas_vol_sum_form}')
print(f'Formation grouped oil and condensate sum = {ASKY_oil_and_condensate_vol_sum_form}')
print(f'Formation grouped ngl sum = {ASKY_ngl_vol_sum_form}')

print(f'Field grouped dry gas sum = {ASKY_dry_gas_vol_sum_field}')
print(f'Field grouped gross gas sum = {ASKY_gross_gas_vol_sum_field}')
print(f'Field grouped oil and condensate sum = {ASKY_oil_and_condensate_vol_sum_field}')
print(f'Field grouped ngl sum = {ASKY_ngl_vol_sum_field}')

# ===== Cell 109 =====
# parse operators, to add in Entity ID's manually
# calculate total production
ASKY_df_grouped_field['total_hydrocarbons_production'] = (ASKY_df_grouped_field['dry_gas_vol']*0.005883) + ASKY_df_grouped_field['oil_and_condensate_vol']+ ASKY_df_grouped_field['ngl_vol']
ASKY_df_grouped_formation['total_hydrocarbons_production'] =  (ASKY_df_grouped_formation['dry_gas_vol']*0.005883) + ASKY_df_grouped_formation['oil_and_condensate_vol'] + ASKY_df_grouped_formation['ngl_vol']

# group by operator for datacleaning
ASKY_df_grouped_formation_op = ASKY_df_grouped_formation.groupby('operator_name').agg({'total_hydrocarbons_production': 'sum'})

# sort by production high to low
ASKY_df_grouped_formation_op =ASKY_df_grouped_formation_op.sort_values(by='total_hydrocarbons_production', ascending=False)

ASKY_df_grouped_formation_op.to_csv(f'{NM_GOGET_Folder}/NM_grouped_formation_op.csv')

# ===== Cell 110 =====
# load in operator data (manually gathered)
ASKY_top_op = pd.read_csv(f'{NM_GOGET_Folder}/NM_grouped_formation_op - NM Matched 2025 01 15.csv')

# rename Database ID as Entity ID
ASKY_top_op = ASKY_top_op.rename(columns={'Database ID': 'Entity ID'})

# update based on top operator cut offs
ASKY_top_op_for_merge = ASKY_top_op[['operator_name', 'Entity ID']].copy()

# merge Entity ID based on operator_name
ASKY_Form_ID = ASKY_df_grouped_formation.merge(ASKY_top_op_for_merge, on='operator_name', how='left')
ASKY_Field_ID = ASKY_df_grouped_field.merge(ASKY_top_op_for_merge, on='operator_name', how='left')

# drop rows where Entity ID is null
ASKY_Form_ID_noNull = ASKY_Form_ID.dropna(subset=['Entity ID']).copy()
ASKY_Field_ID_noNull = ASKY_Field_ID.dropna(subset=['Entity ID']).copy()

# print row count pre and post drop formation and field
print(f'Formation grouped has {len(ASKY_df_grouped_formation)} rows')
print(f'Formation groups with only top ops has {len(ASKY_Form_ID_noNull)} rows')
print(f'Field grouped has {len(ASKY_df_grouped_field)} rows')
print(f'Field groups with only top ops has {len(ASKY_Field_ID_noNull)} rows')

# ===== Cell 111 =====
# check totals
ASKY_dry_gas_vol_sum_form_top_op = ASKY_Form_ID_noNull['dry_gas_vol'].sum()
ASKY_gross_gas_vol_sum_form_top_op = ASKY_Form_ID_noNull['gross_gas_vol'].sum()
ASKY_oil_and_condensate_vol_sum_form_top_op = ASKY_Form_ID_noNull['oil_and_condensate_vol'].sum()
ASKY_ngl_vol_sum_form_top_op = ASKY_Form_ID_noNull['ngl_vol'].sum()

ASKY_dry_gas_vol_sum_field_top_op = ASKY_Field_ID_noNull['dry_gas_vol'].sum()
ASKY_gross_gas_vol_sum_field_top_op = ASKY_Field_ID_noNull['gross_gas_vol'].sum()
ASKY_oil_and_condensate_vol_sum_field_top_op = ASKY_Field_ID_noNull['oil_and_condensate_vol'].sum()
ASKY_ngl_vol_sum_field_top_op = ASKY_Field_ID_noNull['ngl_vol'].sum()

print(f'Top op percent of formation grouped dry gas = {ASKY_dry_gas_vol_sum_form_top_op / ASKY_dry_gas_vol_sum_form:.2%}')
print(f'Top op percent of formation grouped gross gas sum = {ASKY_gross_gas_vol_sum_form_top_op / ASKY_gross_gas_vol_sum_form:.2%}')
print(f'Top op percent of formation grouped oil and condensate sum = {ASKY_oil_and_condensate_vol_sum_form_top_op / ASKY_oil_and_condensate_vol_sum_form:.2%}')
print(f'Top op percent of formation grouped ngl sum = {ASKY_ngl_vol_sum_form_top_op / ASKY_ngl_vol_sum_form:.2%}')

print(f'Top op percent of field grouped dry gas = {ASKY_dry_gas_vol_sum_field_top_op / ASKY_dry_gas_vol_sum_field:.2%}')
print(f'Top op percent of field grouped gross gas sum = {ASKY_gross_gas_vol_sum_field_top_op / ASKY_gross_gas_vol_sum_field:.2%}')
print(f'Top op percent of field grouped oil and condensate sum = {ASKY_oil_and_condensate_vol_sum_field_top_op / ASKY_oil_and_condensate_vol_sum_field:.2%}')
print(f'Top op percent of field grouped ngl sum = {ASKY_ngl_vol_sum_field_top_op / ASKY_ngl_vol_sum_field:.2%}')

# ===== Cell 112 =====
# select field or formation
row_choice = 'formation' # User can change this to 'formation'

if row_choice == 'formation':
    choice = ASKY_Form_ID_noNull
    name_col = 'formation_name'
    project_complex_col = 'formation_name'
elif row_choice == 'field':
    choice = ASKY_Field_ID_noNull
    name_col = 'field_name'
    project_complex_col = 'formation_name'
else:
    raise ValueError("Invalid row_choice. Must be 'formation' or 'field'.")

print(f'Choice is {row_choice}')
choice.head()

# ===== Cell 113 =====
# standardize the 'resource_type' column for GOGET bulk upload

choice['resource_type'] = choice['resource_type'].replace({
    'Unconventional; Conventional': 'Unconventional',
    'Conventional; Unconventional': 'Unconventional',
    'Conventional': 'Conventional'
})

print("Resource types standardized.")

# ===== Cell 114 =====
# define fuel type
import numpy as np

conditions = [
    (choice['dry_gas_vol'] > 0) & (choice['oil_and_condensate_vol'] > 0),
    (choice['dry_gas_vol'] == 0) & (choice['oil_and_condensate_vol'] > 0),
    (choice['dry_gas_vol'] > 0) & (choice['oil_and_condensate_vol'] == 0)
]

choices = ['oil and gas', 'oil', 'gas']

choice['fuel_type'] = np.select(conditions, choices, default=None)

print("Fuel types have been assigned.")

# ===== Cell 115 =====
# format names based on field or formation list - add source
choice.loc[:, 'name'] = choice[name_col] + ' - ' + choice['operator_name']
choice.loc[:, 'unit_type'] = "asset"
choice.loc[:, 'project_complex'] = choice[project_complex_col]
choice.loc[:, 'coordinate_accuracy'] = "exact"
choice.loc[:, 'operator_source'] = "OngardNMProd2024"
choice.loc[:, 'location_source'] = "OngardNMProd2024"
choice.loc[:, 'resource_type_source'] = "OngardNMProd2024"
choice.loc[:, 'discovery_year_source'] = "OngardNMProd2024"
choice['name'] = choice['name'].str.replace('Wc', 'Wildcat', regex=False)

print("Data formatted for GOGET bulk upload.")

# ===== Cell 116 =====
# add total production column if it doesn't already exist (it should from the earlier step, but this is a safeguard)
if 'total_hydrocarbons_production' not in choice.columns:
    choice['total_hydrocarbons_production'] = (choice['dry_gas_vol']*0.005883) + choice['oil_and_condensate_vol'] + choice['ngl_vol']

# Select and order the final columns for ASKY_Clean
ASKY_Clean = choice[[
    'name',
    'unit_type',
    'fuel_type',
    'project_complex',
    'longitude',
    'latitude',
    'coordinate_accuracy',
    'location_source',
    'operator_name',
    'operator_source',
    'Entity ID',
    'resource_type',
    'resource_type_source',
    # 'Discovery year',
    # 'discovery_year_source',
    'well_no',
    'total_hydrocarbons_production'
]].copy()

# sort by total_hydrocarbons_production high to low
ASKY_Clean = ASKY_Clean.sort_values(by='total_hydrocarbons_production', ascending=False).reset_index(drop=True)

print("ASKY_Clean DataFrame created with selected and ordered columns.")
display(ASKY_Clean.head())

# ===== Cell 117 =====
# check totals in choice
ASKY_choice_total = ASKY_Clean['total_hydrocarbons_production'].sum()


# print totals
print(f'{active_state} parsed data has {ASKY_choice_total} million boe')

# ===== Cell 118 =====
# save out ASKY_Clean for manual matching
ASKY_Clean.to_excel(f'{NM_GOGET_Folder}/NM_GOGET_Clean_for_ID_Match.xlsx', index=False)
