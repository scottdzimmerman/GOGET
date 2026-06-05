"""
asset_impact_data_parse_texas_2025.py

Migrated from Colab notebook: Copy of Asset Impact Data Parse 2024 12 26 - modified for 2025 texas data.ipynb
Auto-converted to a Python script. Colab-specific lines
(drive.mount, google.colab imports, shell/magic commands) have been
commented out and flagged; pip installs moved to ../requirements.txt.
"""

# Code to parse the Asset Impact Data sent from Daan Koop to Scott on November 28, 2024. Data includes Texas, California and Pennsylvania and the well level.

# ===== Cell 1 =====
# mount drive and define files
# [colab-only removed] from google.colab import drive
# [colab drive mount removed] drive.mount('/content/drive')

# ===== Cell 2 =====
# load in pandas, geopandas, shapely
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
# [moved to requirements.txt] !pip install xlsxwriter

# ===== Cell 3 =====
# load in Asset Impact CSV, display header
goget_path = '/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/'
assetimpactdata = goget_path + 'Data sets & reports (O&G)/O&G global materials/Asset Impact Data/2025 Data/texas_2024.csv'

AIfull = pd.read_csv(assetimpactdata)
AIfull.head()

# ===== Cell 4 =====
# show entries for field_name = Newark, East (Barnett Shale)
NEWARK = AIfull[AIfull['field_name'] == 'NEWARK, EAST (BARNETT SHALE)']

# show unique field_terrain in NEWARK
NEWAR_offshore = NEWARK[NEWARK['field_terrain'] == 'Offshore']
NEWAR_offshore.columns

# ===== Cell 5 =====
NEWAR_offshore.to_csv('/content/sample_data/texas_offshore.csv')

# ===== Cell 6 =====
# display columns, to get a sense of the data - comment out as this is not needed
AIfull.columns

# ===== Cell 7 =====
# rename oil and gas column dry_gas_vol to gas_dry_vol to match 2023 data
AIfull = AIfull.rename(columns={'dry_gas_vol': 'gas_dry_vol'})
AIfull = AIfull.rename(columns={'gross_gas_vol': 'gas_raw_vol'})

# ===== Cell 8 =====
# set data year filter to make data more manageable, per dan 2024 is modelled, but 2023 should not be.
yeardf = AIfull[AIfull['year'] == 2024]

# ===== Cell 9 =====
# check totals pre-group
print('oil total ' + str(yeardf['oil_and_condensate_vol'].sum()))
print('condensate total ' + str(yeardf['oil_and_condensate_vol'].sum())) # note change from 2024 data, they combined oil and condensate
print('gas_raw_vol total ' + str(yeardf['gas_raw_vol'].sum()))
print('gas_dry_vol total ' + str(yeardf['gas_dry_vol'].sum()))
print('ngl_vol total ' + str(yeardf['ngl_vol'].sum()))

# ===== Cell 10 =====
# check totals by state pre-group, per dan: gas_dry_vol represents the dry gas volume, gas_raw_vol the gross gas production. For PA and CA, we haven’t modelled dry gas yet
raw_state_totals = yeardf.groupby('state')[['oil_and_condensate_vol', 'gas_raw_vol', 'gas_dry_vol', 'ngl_vol',]].sum().reset_index() # Changed tuple to list

# Ensure 'state' is a column after groupby
# The 'state' column might have become the index after the groupby operation
# reset_index() will make it a column again
raw_state_totals = raw_state_totals.reset_index()

raw_state_totals

# ===== Cell 11 =====
# define EIA totals to compare to
EIA_State_Totals = {
    'texas': {'EIA_liquids_vol':2011.52, 'EIA_gas_vol':326403.45},
    'pennsylvania': {'EIA_liquids_vol':4.82, 'EIA_gas_vol':214990.16},
    'california':{'EIA_liquids_vol':0, 'EIA_gas_vol':3701.09}
}

# Convert EIA_State_Totals to a DataFrame with 'state' as the index
EIA_State_Totals = pd.DataFrame(EIA_State_Totals).T.rename_axis('state').reset_index() # Changed to set 'state' as index

# add total hydrocarbon column to EIA data
# set gas conversion variable (Conversion factor for gas to million boe) #using SWRE here
gas_conversion_factor = 0.005883 #SWRE 2023 conversion

EIA_State_Totals['EIA_total_hydrocarbons'] = (EIA_State_Totals['EIA_gas_vol'] * gas_conversion_factor) + EIA_State_Totals['EIA_liquids_vol']
raw_state_totals['raw_total_hydrocarbons'] = (raw_state_totals['gas_dry_vol'] * gas_conversion_factor) + raw_state_totals['oil_and_condensate_vol']

# Merge raw_state_totals and EIA_State_Totals for comparison
# lowercase for consistent comparison
raw_state_totals['state'] = raw_state_totals['state'].str.lower()
EIA_State_Totals['state'] = EIA_State_Totals['state'].str.lower()

merged_df = pd.merge(raw_state_totals, EIA_State_Totals, on='state', how='inner') # Changed to inner merge for clarity
merged_df

# **In** texas, the EIA total does not seem to include NGLs, but it does in this dataset

# ===== Cell 12 =====
# Check data density for specific columns
columns_to_check = ['country', 'state', 'field_name', 'formation_name', 'operator_name', 'owner_name','resource_type','recovery_mechanism', 'field_terrain']

for col in columns_to_check:
  density = yeardf[col].count() / len(yeardf)
  print(f"Data density for '{col}': {density:.2%}")

# Formation name only at 65.37. Owner and operator not found for some? Implementing -  "Not Stated in delivered data" for missing data so it is not dropped?

# ===== Cell 13 =====
# Create a copy of the DataFrame
yeardf_filled = yeardf.copy()

# Ensure columns can hold string values before filling NaNs
for col in ['field_name', 'formation_name', 'operator_name', 'owner_name', 'resource_type', 'recovery_mechanism', 'field_terrain']:
    if yeardf_filled[col].dtype != 'object': # Only convert if not already object type
        yeardf_filled[col] = yeardf_filled[col].astype(str)

# Fill in missing values on the copy
yeardf_filled.loc[yeardf_filled['field_name'].isnull(), 'field_name'] = 'No Field Stated in delivered data'
yeardf_filled.loc[yeardf_filled['formation_name'].isnull(), 'formation_name'] = 'No Formation Stated in delivered data'
yeardf_filled.loc[yeardf_filled['operator_name'].isnull(), 'operator_name'] = 'Operator not stated in delivered dataset'
yeardf_filled.loc[yeardf_filled['owner_name'].isnull(), 'owner_name'] = 'Owner not stated in delivered dataset'
yeardf_filled.loc[yeardf_filled['resource_type'].isnull(), 'resource_type'] = 'Resource Type Not Stated in delivered data'
yeardf_filled.loc[yeardf_filled['recovery_mechanism'].isnull(), 'recovery_mechanism'] = ' Recovery Mechanism Not Stated in delivered data'
yeardf_filled.loc[yeardf_filled['field_terrain'].isnull(), 'field_terrain'] = 'Field Terrian Not Stated in delivered data'

# ===== Cell 14 =====
# prompt: check 'country', 'state', 'field_name', 'formation_name', 'operator_name', 'owner_name' data density

# Check data density for specific columns
columns_to_check = ['country', 'state', 'field_name', 'formation_name', 'operator_name', 'owner_name','resource_type','recovery_mechanism', 'field_terrain']

for col in columns_to_check:
  density = yeardf_filled[col].count() / len(yeardf_filled)
  print(f"Data density for '{col}': {density:.2%}")

# ===== Cell 15 =====
# Texas filter for GOV ID later
texas_filtered = yeardf_filled[yeardf_filled['state'] == 'texas']
texas_filtered

# ===== Cell 16 =====
# Handle PA seperately since the field name tends to be blank. group by formation instead. Per Daan "PA: field names were mapped by ourselves, using geographical coordinates and a field shape file, but the mapping is not complete. I would recommend not to publish by this indicator until we’ve further improved it"
PA_filtered = yeardf_filled[yeardf_filled['state'] == 'pennsylvania']
PA_filtered

# ===== Cell 17 =====
# display unique PA_filtered formations for trouble shooting pe
PA_filtered['formation_name'].unique()

# ===== Cell 18 =====
# check row count of PA_filtered
PA_filtered.shape

# ===== Cell 19 =====
grouped_PA_df = PA_filtered.groupby(['country', 'state', 'formation_name', 'operator_name', 'resource_type', 'field_terrain'])[['oil_vol', 'condensate_vol', 'gas_raw_vol', 'gas_dry_vol', 'ngl_vol', 'recovery_mechanism', 'well_no','oil_gravity','gas_gravity', 'longitude', 'latitude','county_name']].agg({ # Added 'well_no', 'longitude', 'latitude' here
    'oil_vol': 'sum',
    'condensate_vol': 'sum',
    'gas_raw_vol': 'sum',
    'gas_dry_vol': 'sum',
    'ngl_vol': 'sum',
    'well_no': lambda x: '; '.join(x.dropna().astype(str).unique()),  # Convert to string before joining
    'recovery_mechanism': lambda x: '; '.join(x.dropna().unique()),  # Join unique recovery mechanisms
    'oil_gravity': 'mean', # average gravity for oil wells
    'gas_gravity': 'mean', # average gravity for gas wells
    'longitude': 'mean',  # Calculate mean longitude for centroid
    'latitude': 'mean',   # Calculate mean latitude for centroid
    'county_name': lambda x: '; '.join(x.dropna().astype(str).unique())  # Convert to string before joining
}).reset_index()

# ===== Cell 20 =====
# check grouped_PA_df row count
print(f'Grouping reduced PA from {PA_filtered.shape} down to {grouped_PA_df.shape}')

# ===== Cell 21 =====
grouped_PA_df

# ===== Cell 22 =====
texas_filtered

# ===== Cell 23 =====
# Group by state, field name, formation name, owner and operator and sum the volumes
grouped_SFOO_df = texas_filtered.groupby(['field_name', 'formation_name', 'operator_name'])[['oil_and_condensate_vol', 'gas_raw_vol', 'gas_dry_vol', 'ngl_vol', 'recovery_mechanism', 'well_no','oil_gravity','gas_gravity', 'longitude', 'latitude', 'resource_type', 'field_terrain', 'country', 'state']].agg({ # Added 'well_no', 'longitude', 'latitude' here
    'oil_and_condensate_vol': 'sum',
    'gas_raw_vol': 'sum',
    'gas_dry_vol': 'sum',
    'ngl_vol': 'sum',
    'well_no': lambda x: '; '.join(x.dropna().astype(str).unique()),  # Convert to string before joining
    'recovery_mechanism': lambda x: '; '.join(x.dropna().unique()),  # Join unique recovery mechanisms
    'resource_type': lambda x: '; '.join(x.dropna().unique()),  # Join unique resource type
    'field_terrain': lambda x: '; '.join(x.dropna().unique()),  # join unique field type
    'country': lambda x: '; '.join(x.dropna().unique()),
    'state': lambda x: '; '.join(x.dropna().unique()),
    'oil_gravity': 'mean', # average gravity for oil wells
    'gas_gravity': 'mean', # average gravity for gas wells
    'longitude': 'mean',  # Calculate mean longitude for centroid
    'latitude': 'mean'   # Calculate mean latitude for centroid
}).reset_index()

# ===== Cell 24 =====
# creat asset name as combination of field name and operator
grouped_SFOO_df['asset_name'] = grouped_SFOO_df['field_name'] + ' - ' + grouped_SFOO_df['operator_name']

# title case asset name
grouped_SFOO_df['asset_name'] = grouped_SFOO_df['asset_name'].str.title()

# ===== Cell 25 =====
grouped_SFOO_df

# ===== Cell 26 =====
# check for field_name = BLOCKER (COTTON VALLEY)
grouped_SFOO_df[grouped_SFOO_df['field_name'] == 'SPRABERRY (TREND AREA)']

# ===== Cell 27 =====
# check total post group function
print('oil and condenssate percent =' + str(grouped_SFOO_df['oil_and_condensate_vol'].sum()/yeardf['oil_and_condensate_vol'].sum()))
print('gas_raw_vol percent =' + str(grouped_SFOO_df['gas_raw_vol'].sum()/yeardf['gas_raw_vol'].sum()))
print('gas_dry_vol percent =' + str(grouped_SFOO_df['gas_dry_vol'].sum()/yeardf['gas_dry_vol'].sum()))
print('ngl_vol percent =' + str(grouped_SFOO_df['ngl_vol'].sum()/yeardf['ngl_vol'].sum()))

# Check: *Visualize*

# ===== Cell 28 =====
# prompt: Visualize the data by plotting the centroid_longitude	centroid_latitude on a US map

import matplotlib.pyplot as plt

# Create a GeoDataFrame
geometry = [Point(xy) for xy in zip(grouped_SFOO_df['longitude'], grouped_SFOO_df['latitude'])]
gdf = gpd.GeoDataFrame(grouped_SFOO_df, geometry=geometry, crs="EPSG:4326")

# Load US states shapefile
States = gpd.read_file('/content/drive/MyDrive/Russia and Ukrainian Conflict, Fossil Fuel Map/Russia and Ukraine, QGIS files/Natural_Earth_quick_start/50m_cultural/ne_50m_admin_1_states_provinces_lines.shp')

 # Define the center point for Texas (approximately)
center_longitude = -98.5795
center_latitude = 39.8283

# Set the extent for zooming (adjust as needed)
x_min = center_longitude - 25  # 10 degrees of longitude to the left
x_max = center_longitude + 25  # 10 degrees of longitude to the right
y_min = center_latitude - 15   # 5 degrees of latitude below
y_max = center_latitude + 15   # 5 degrees of latitude above

# Plot the map
fig, ax = plt.subplots(figsize=(10, 10))
States.plot(ax=ax, color='lightgray', edgecolor='black')

# Plot the centroids on the map
gdf.plot(ax=ax, marker='o', color='red', markersize=5, label='Asset Centroids')

# Customize the plot
plt.title('Asset Centroids on US Map')
plt.xlabel('Longitude')
plt.ylabel('Latitude')

# Set the map extent to zoom in on the US
ax.set_xlim([x_min, x_max])
ax.set_ylim([y_min, y_max])

plt.legend()
plt.show()

# ===== Cell 29 =====
# prompt: Create total hydrocarbons column, adding oil_vol	and condensate_vol, and converting gas_dry_vol to million boe

# Calculate total hydrocarbons
grouped_SFOO_df['total_hydrocarbons'] = grouped_SFOO_df['oil_and_condensate_vol'] + grouped_SFOO_df['ngl_vol'] + (grouped_SFOO_df['gas_dry_vol'] * gas_conversion_factor)
#grouped_FOO_df['total_hydrocarbons'] = grouped_FOO_df['oil_vol'] + grouped_FOO_df['condensate_vol'] + (grouped_FOO_df['gas_dry_vol'] * gas_conversion_factor)
# grouped_PA_df ['total_hydrocarbons'] = grouped_PA_df['oil_vol'] + grouped_PA_df['condensate_vol'] + grouped_PA_df['ngl_vol'] + (grouped_PA_df['gas_raw_vol'] * gas_conversion_factor) # using Raw gas for PA as raw gas appears not to be modelled

grouped_SFOO_df

# ===== Cell 30 =====
# Filter out Pennsylvania data from filtered_SFOO_df
filtered_SFOO_df = grouped_SFOO_df[grouped_SFOO_df['state'] != 'pennsylvania']

# Concatenate the filtered DataFrame with grouped_PA_df
updated_SFOO_df = pd.concat([filtered_SFOO_df, grouped_PA_df], ignore_index=True)

# ===== Cell 31 =====
# for ease, redefine the PA replaced data, as the grouped data
grouped_SFOO_df = updated_SFOO_df

# ===== Cell 32 =====
# check state totals in grouped_SFOO_df
grouped_state_totals_unfiltered = grouped_SFOO_df.groupby('state')[['oil_and_condensate_vol', 'gas_raw_vol', 'gas_dry_vol', 'ngl_vol', 'total_hydrocarbons']].sum().reset_index()

grouped_state_totals_unfiltered

# ===== Cell 33 =====
# sort on total_hydrocarbons
grouped_SFOO_sorted_df = grouped_SFOO_df.sort_values(by='total_hydrocarbons', ascending=False)
#grouped_FOO_sorted_df = grouped_FOO_df.sort_values(by='total_hydrocarbons', ascending=False)
grouped_SFOO_sorted_df

# ===== Cell 34 =====
def filter_top_producers(df, group_col, value_col, percentile=0.95):
    """
    Filters a DataFrame to include rows representing the top percentile of a value
    within each group.

    Args:
        df: The input DataFrame.
        group_col: The column to group by (e.g., 'state').
        value_col: The column containing the value to rank by (e.g., 'total_hydrocarbons').
        percentile: The desired percentile (default is 0.95 for top 95%).

    Returns:
        A filtered DataFrame.
    """

    df['cumulative_sum'] = df.groupby(group_col)[value_col].cumsum()
    state_totals = df.groupby(group_col)[value_col].transform('sum')  # Using transform for efficiency
    df['threshold'] = state_totals * percentile
    filtered_df = df[df['cumulative_sum'] <= df['threshold']]

    return filtered_df.drop(columns=['cumulative_sum', 'threshold'])  # Remove temporary columns

# Apply the function
filteredSFOO_df = filter_top_producers(
    grouped_SFOO_sorted_df,
    group_col='state',
    value_col='total_hydrocarbons'
)
filteredSFOO_df

# ===== Cell 35 =====
#compare filtered (filteredSFOO_df) and unfiltered (grouped_SFOO_sorted_df) state totals

# calculate filteredSFOO_df state totals
filtered_state_totals = filteredSFOO_df.groupby('state')[['total_hydrocarbons']].sum().reset_index()


# calculate unfiltered state totals
unfiltered_state_totals = grouped_SFOO_sorted_df.groupby('state')[['total_hydrocarbons']].sum().reset_index()

filtered_state_totals

# ===== Cell 36 =====
unfiltered_state_totals

# ===== Cell 37 =====
# Data Cleaning
# Rename columns for clarity
filteredSFOO_clean = filteredSFOO_df.rename(columns={
    'oil_and_condensate_vol': 'Oil and Condensate production (million bbl/y)',
    'gas_raw_vol': 'Raw gas production (million m³/y)',
    'gas_dry_vol': 'Dry gas production (million m³/y)',
    'well_no': 'Well ID(s)',
    'ngl_vol': 'NGL production (million bbl/y)',
    'recovery_mechanism': 'Recovery mechanism',
    'longitude': 'Longitude',
    'latitude': 'Latitude',
    'total_hydrocarbons': 'Total hydrocarbon production (million bbl/y)',
    'cumulative_sum': 'Cumulative sum',
    'threshold': 'State Inclusion Threshold',
    'owner_name': 'Owner',
    'operator_name': 'Operator',
    'resource_type': 'Resource Type',
    'field_terrain': 'Onshore/Offshore',
    'field_name': 'Field Name',
    'formation_name': 'Formation Name',
    'country': 'Country/Area',
    'state': 'Subnational unit (province, state)',
    'county_name': 'county'
})

# ===== Cell 38 =====
filteredSFOO_clean

# ===== Cell 39 =====
# reorder columns
filtered_df_clean_reorder = filteredSFOO_clean[['Country/Area', 'Subnational unit (province, state)', 'Field Name', 'asset_name', 'Formation Name', 'Well ID(s)', 'Longitude', 'Latitude','Operator', 'Resource Type', 'Recovery mechanism', 'Onshore/Offshore', 'Oil and Condensate production (million bbl/y)', 'Raw gas production (million m³/y)', 'Dry gas production (million m³/y)', 'NGL production (million bbl/y)','Total hydrocarbon production (million bbl/y)']]

# ===== Cell 40 =====
# prompt: title case data in the  field name, operator, owner, country, state columns

# Assuming 'filtered_df' is your DataFrame

# Columns to title case
columns_to_title_case = ['Field Name', 'Operator', 'Owner', 'Country/Area', 'Subnational unit (province, state)','Formation Name']

# Title case the specified columns
for col in columns_to_title_case:
    if col in filtered_df_clean_reorder.columns:
        filtered_df_clean_reorder.loc[:, col] = filtered_df_clean_reorder[col].str.title()

# Example usage for further processing or display
filtered_df_clean_reorder

# ===== Cell 41 =====
# Add in Government Formation ID and Operator ID for Texas
# Define texas subset
texas_subset = filtered_df_clean_reorder[filtered_df_clean_reorder['Subnational unit (province, state)'] == 'Texas']

# load in df with texas field/formation names/numbers and operator names/numbers
texas_IDOP_excel = goget_path + '/Data sets & reports (O&G)/O&G country materials/United States (GOGET O&G)/Texas (GOGET)/Texas 2023 Field and Operator Names.xlsx'

# load in texas excel doc, define tabs
texas_Field_ids = pd.read_excel(texas_IDOP_excel, sheet_name='Field and Formation Name')
texas_op_ids = pd.read_excel(texas_IDOP_excel, sheet_name='Operator Name')

# ===== Cell 42 =====
# prompt: add Field_No to from texas_Field_ids to texas_subset matching FIELD_NAME to Field Name

# title case field name on texas_Field_ids
texas_Field_ids['FIELD_NAME'] = texas_Field_ids['FIELD_NAME'].str.title()

# convert field_no to string
texas_Field_ids['Field_No'] = texas_Field_ids['Field_No'].astype(str)


# Merge texas_subset with texas_Field_ids based on 'Field Name'
texas_subset = pd.merge(texas_subset, texas_Field_ids[['FIELD_NAME', 'Field_No']], left_on='Field Name', right_on='FIELD_NAME', how='left')

# Drop the duplicate 'FIELD_NAME' column
texas_subset = texas_subset.drop(columns=['FIELD_NAME'])

texas_subset

# ===== Cell 43 =====
# add Operator_No to from texas_op_ids to texas_subset matching OPERATOR_NAME to Operator

# title case field name on texas_Field_ids
texas_op_ids['OPERATOR_NAME'] = texas_op_ids['OPERATOR_NAME'].str.title()

# convert Operator_no to string
texas_op_ids['Operator_no'] = texas_op_ids['Operator_no'].astype(str)

# Merge texas_subset with texas_op_ids based on 'Operator'
texas_subset = pd.merge(texas_subset, texas_op_ids[['OPERATOR_NAME', 'Operator_no']], left_on='Operator', right_on='OPERATOR_NAME', how='left')

# Drop the duplicate 'OPERATOR_NAME' column
texas_subset = texas_subset.drop(columns=['OPERATOR_NAME'])

texas_subset

# ===== Cell 44 =====
# Create "Government unit ID" as Field_No + "_" + Operator_no
texas_subset['Government unit ID'] = texas_subset['Field_No'] + '_' + texas_subset['Operator_no']

texas_subset

# ===== Cell 45 =====
# prompt: Merge the "Government unit ID" from texas_subset onto filtered_df_clean_reorder, adding a new column

filtered_df_clean_reorder['Field Name'] = filtered_df_clean_reorder['Field Name'].astype(str)
texas_subset['Field Name'] = texas_subset['Field Name'].astype(str)

filtered_df_clean_reorder['Operator'] = filtered_df_clean_reorder['Operator'].astype(str)
texas_subset['Operator'] = texas_subset['Operator'].astype(str)

# Merge the "Government unit ID" from texas_subset onto filtered_df_clean_reorder
filtered_df_clean_reorder_govid = pd.merge(filtered_df_clean_reorder, texas_subset[['Government unit ID', 'Field Name', 'Operator']], on=['Field Name', 'Operator'], how='left')

filtered_df_clean_reorder_govid

# ===== Cell 46 =====
# prompt: deduplicate filtered_df_clean_reorder_govid

# Assuming filtered_df_clean_reorder_govid is your DataFrame

# Deduplicate the DataFrame based on all columns
filtered_df_clean_reorder_govid = filtered_df_clean_reorder_govid.drop_duplicates()

# Display or further process the deduplicated DataFrame
final_texas = filtered_df_clean_reorder_govid[filtered_df_clean_reorder_govid['Subnational unit (province, state)'] == 'Texas']
final_texas

# ===== Cell 47 =====
# prompt: Clean are order grouped_FOO_df in the same manner as filtered_df_clean_reorder

# Clean and reorder grouped_FOO_df in the same manner as filtered_df_clean_reorder

# Rename columns for grouped_FOO_df
grouped_FOO_clean = grouped_FOO_df.rename(columns={
    'oil_vol': 'Oil production (million bbl/y)',
    'condensate_vol': 'Condensate production (million bbl/y)',
    'gas_raw_vol': 'Raw gas production (million m³/y)',
    'gas_dry_vol': 'Dry gas production (million m³/y)',
    'ngl_vol': 'NGL production (million bbl/y)',
    'recovery_mechanism': 'Recovery mechanism',
    'well_no': 'Well ID(s)',
    'centroid_longitude': 'Longitude',
    'centroid_latitude': 'Latitude',
    'total_hydrocarbons': 'Total hydrocarbon production (million bbl/y)',
    'owner_name': 'Owner',
    'operator_name': 'Operator',
    'resource_type': 'Resource Type',
    'field_terrain': 'Onshore/Offshore',
    'field_name': 'Field Name',
    'formation_name': 'Formation Name',
    'country': 'Country/Area',
})

# Reorder columns to match filtered_df_clean_reorder
grouped_FOO_clean_reorder = grouped_FOO_clean[[
    'Country/Area', 'Field Name', 'Formation Name', 'Well ID(s)', 'Longitude', 'Latitude',
    'Operator', 'Owner', 'Resource Type', 'Recovery mechanism', 'Onshore/Offshore',
    'Oil production (million bbl/y)', 'Condensate production (million bbl/y)', 'Raw gas production (million m³/y)',
    'Dry gas production (million m³/y)', 'NGL production (million bbl/y)', 'Total hydrocarbon production (million bbl/y)'
]]

# Title case the specified columns for grouped_FOO_df
columns_to_title_case = ['Field Name', 'Operator', 'Owner', 'Country/Area', 'Subnational unit (province, state)', 'Formation Name']
for col in columns_to_title_case:
    if col in grouped_FOO_clean_reorder.columns:
        grouped_FOO_clean_reorder.loc[:, col] = grouped_FOO_clean_reorder[col].str.title()

grouped_FOO_clean_reorder

# ===== Cell 48 =====
# prompt: Create excel file, have one tab be filtered_df_clean_reorder, another be comparison_df and a final be an about page that says "generated on (time stamp) via Asset Impact Data Parse code. Draws on (assetimpactdata file)

import pandas as pd
from datetime import datetime

# Get the current date and time
now = datetime.now()

# Format the date and time as "AI Data Parsed on [day and date]"
timestamp_str = now.strftime("%Y_%m_%d_%H:%M")

output_file_path = goget_path + 'Data sets & reports (O&G)/O&G global materials/Asset Impact Data/'
output_file_name = f"Parsed_Filtered_Asset_Impact_Data_{timestamp_str}.xlsx"

full_output_path = output_file_path + output_file_name

# Create a new ExcelWriter object
writer = pd.ExcelWriter(full_output_path, engine='xlsxwriter') # Create writer with path

# Write each DataFrame to a separate sheet
#pennsylvania_filtered_clean_reorder.to_excel(writer, sheet_name='PA Field Formation, filtered', index=False)
final_texas.to_excel(writer, sheet_name='State Field Formation, filtered', index=False)
#comparison_df.to_excel(writer, sheet_name='comparison to EIA', index=False)
# grouped_FOO_clean_reorder.to_excel(writer, sheet_name='Field Formation Groupby, raw', index=False)

# Create the "About" sheet
about_df = pd.DataFrame({
    'Information': [
        f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Source file: {assetimpactdata}"
    ]
})
about_df.to_excel(writer, sheet_name='About', index=False)

# save
writer.close()

# print save location
print(f"File saved to: {full_output_path}")

# To do - include unique IDs for each AI asset as a combo of the pieces aggregated
