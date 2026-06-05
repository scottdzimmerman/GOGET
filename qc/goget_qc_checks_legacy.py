"""
goget_qc_checks_legacy.py

Migrated from Colab notebook: GOGET QC checks 2025 08 14.ipynb
Auto-converted to a Python script. Colab-specific lines
(drive.mount, google.colab imports, shell/magic commands) have been
commented out and flagged; pip installs moved to ../requirements.txt.
"""

# ===== Cell 1 =====
#import libraries
from ctypes.util import find_library
find_library('geos_c')
import pandas as pd
import geopandas as gpd
import numpy as np
# [moved to requirements.txt] !pip install config
import config
import shapely
import datetime
from datetime import datetime
from shapely.geometry.base import BaseGeometry
from shapely.geometry import MultiPolygon, mapping, shape, Point # Added Point import
from shapely.validation import make_valid
# [moved to requirements.txt] !pip install fuzzywuzzy[speedup]
from fuzzywuzzy import fuzz
# [moved to requirements.txt] !pip install rtree
from rtree import index

# ===== Cell 2 =====
# define datastamp for all outputs for consistency
now = datetime.now()
timestamp_str = now.strftime("%Y_%m_%d_%H:%M")
print('this runs qc output will all be timestamped: ' + timestamp_str)

# ===== Cell 3 =====
# mount drive
# [colab-only removed] from google.colab import drive
# [colab drive mount removed] drive.mount('/content/drive')

# ===== Cell 4 =====
# define files
gem_goget_path = '/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/'
goget_file = 'GOGET oil & gas extraction sites (2025 08 20).xlsx' # <--- change this with the newest version of goget - so that this code can be more easily shared, do this instead of autheticating and having the script save the copy of the file

eez_path = '/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/O&G global materials/EEZ Outlines/'
eez_file = 'EEZ_Land_v3_202030.shp'

qc_out_path = '/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/QC/QC Output Dump/'

# ## Read and filter data

# ===== Cell 5 =====
# takes about 30 seconds
# import GOGET data set
goget_versions_path = gem_goget_path + 'GOGET Iterations/Snapshots of GOGET main data set/'
goget_xl = pd.ExcelFile(goget_versions_path + goget_file)

# ===== Cell 6 =====
# Read and clean main data
def read_and_clean_goget_main(goget_xl):
    df = pd.read_excel(goget_xl, sheet_name='Main data')

    df = df.dropna(subset=['Unit ID'])

    for col in df.columns:
        if 'Unnamed: ' in col:
            df = df.drop(col, axis=1)

    # exclude empty rows
    df = df[df['Unit Name'].isna()==False]

    goget_main = df
    return goget_main

# ===== Cell 7 =====
# Read and clean production and reserves data
def read_and_clean_goget_prod(goget_xl):
    df = pd.read_excel(goget_xl, sheet_name='Reserves and Production')

    df = df.dropna(subset=['Unit ID', 'Unit name'], how='any')

    for col in df.columns:
        if 'Unnamed: ' in col:
            df = df.drop(col, axis=1)

    # exclude empty rows
    df = df[df['Unit name'].isna()==False]

    goget_prod = df
    return goget_prod

# ===== Cell 8 =====
# read and clean sources data
def read_and_clean_goget_sources(goget_xl):
    df = pd.read_excel(goget_xl, sheet_name='Sources')
    df = df.dropna(subset=['short name'], how='any')
    goget_sources = df
    return goget_sources

# ===== Cell 9 =====
# takes about 20 seconds
goget_main = read_and_clean_goget_main(goget_xl)
goget_prod = read_and_clean_goget_prod(goget_xl)
goget_sources = read_and_clean_goget_sources(goget_xl)

# ### Filter for fields over thresholds

# ===== Cell 10 =====
# # filter for only units we want to keep - can do this for speed, but might as well QC the whole thing
#goget_main_keep = goget_main[goget_main['keep']=='yes'] # comment this out if QC'ing whole sheet
#goget_main = goget_main_keep.copy() # comment this out if QC'ing whole sheet

# ## Data checks - main sheet

# ===== Cell 11 =====
# find units with no status, but do have production data. CAVEAT: If "0" production is known, that is entered and those should be shut in.

df = goget_main.copy()
no_status_but_prod = df[
    (df['Status'].isna()) &  # Missing status
    (~df['Production data?'].astype(str).str.contains('no data')) &  # Production data present
    (~df['Production data?'].astype(str).str.contains(r'/\s*\d{4}\s*/')) &  # Exclude / YYYY/ format
    (~df['Production data?'].astype(str).str.contains(r'/\s*/\s*\d{4}')) &  # Exclude / / YYYY format
    (~df['Production data?'].astype(str).str.contains(r'\b0\b')) # excludes unknown production year (0 means production data without a known year)

]

# create file name
no_status_but_prod_name = f"no status but production_{timestamp_str}"

no_status_but_prod[['Unit Name', 'Unit type', 'Country/Area', 'Production data?']]
no_status_but_prod.to_csv(qc_out_path + no_status_but_prod_name + '.csv')

print("examine " + str(len(no_status_but_prod)) + " fields in file named: '" + no_status_but_prod_name + "' in the QC dump folder")

# Note: as of 2025 08 26 - there are 38 fields in the main dataset that have no status, but a production value. Most recent value there is 2014 - so not a relevant production year. 26 are pre 2010. Tagged some of the Russia and Venzuela as Amalia and Hanna are actively working on those countries

# ===== Cell 12 =====
# TEST: find those that are complex/project (unit type), but don't have an entry in the column "Project/complex"
df = goget_main.copy()
test = df[(df['Unit type'].isin(['project', 'complex'])) &
   (df['Project or complex'].isna())][
    ['Country/Area', 'Unit ID', 'Unit Name', 'Project or complex', 'Unit type']].sort_values(by=['Country/Area', 'Unit Name'])
print(len(test))
test

# ===== Cell 13 =====
# find those with Owner 2, Owner 3, etc.--but no entry for Owner 1
df = goget_main.copy()
df[(df['Owner 1'].isna()) &
   ((df['Owner 2'].isna()==False) |
    (df['Owner 3'].isna()==False) |
    (df['Owner 4'].isna()==False) |
    (df['Owner 5'].isna()==False)
   )][['Unit Name',
       'Owner 1', 'Owner 1 %',
       'Owner 2', 'Owner 2 %',
       'Owner 3', 'Owner 3 %',
       'Owner 4', 'Owner 4 %',
       'Owner 5', 'Owner 5 %',
       'Owner % sum']]

# ===== Cell 14 =====
# find ownership duplicates between columns (e.g. owner 1 and 2 is the same) - sandboxed added from stand alone QC script here https://colab.research.google.com/drive/17qDfhWIdlgGUXYU-YJFaETOLJXnNpsqX?usp=sharing

df = goget_main.copy()
# List of columns related to ownership
ownership_columns = ['Owner 1', 'Owner 2', 'Owner 3', 'Owner 4', 'Owner 5']

# Function to check for duplicate values within a row for the ownership columns excluding blanks

def has_duplicates(row):
        values = [row[col].lower() for col in ownership_columns if pd.notna(row[col]) and row[col] != '']
        for i in range(len(values)):
            for j in range(i + 1, len(values)):
                if fuzz.ratio(values[i], values[j]) > 90:  # Adjust the threshold as needed
                    return True
        return False

# Apply the function to each row of the DataFrame
df['Has_Duplicate_Ownership'] = df.apply(has_duplicates, axis=1)

# Display rows where 'Has_Duplicate_Ownership' is True
duplicate_ownership_df = df[df['Has_Duplicate_Ownership'] == True]
duplicate_ownership_df

# ===== Cell 15 =====
# find units with no Unit type
# previously there were only 10 (2 in Malaysia and 8 in Vietnam)
df = goget_main.copy()
test = df[df['Unit type'].isna()]
for row in test.index:
    print(test.at[row, 'Unit Name'])

# ===== Cell 16 =====
# look for possibly incorrect Unit types: mismatches between unit name and 'Unit type' entry
# For all Alberta, Canada, tar sands projects, change Unit type to project?
sel_term = 'project'
df = goget_main.copy()
df[(df['Unit Name'].str.lower().str.contains(sel_term, regex=False)) & (df['Unit type']!=sel_term)]

# ===== Cell 17 =====
# look for possibly incorrect Unit types: mismatches between unit name and 'Unit type' entry
sel_term = 'complex'
df = goget_main.copy()
df[(df['Unit Name'].str.lower().str.contains(sel_term, regex=False)) & (df['Unit type']!=sel_term)]

# ===== Cell 18 =====
# see all unit types, look for outliers
goget_main['Unit type'].value_counts()


# ===== Cell 19 =====
# see all status entries, look for outliers

# could exclude UGS, shut in, decommissioned...
# although in the long term, we would want to track such retirements,
# including fields that are retired and turned into UGS

# why would UGS be over our threshold? Do we have old production/reserves data for them, before they became UGS?
# I would exclude all UGS from what we create wiki pages for right now.
# should exclude exploration fully, because its not like blocks will have production or reserve numbers
goget_main['Status'].value_counts()

# ===== Cell 20 =====
# check for name duplicates

def check_for_potential_duplicate_unit_names(df):
    df['Subnational unit (province, state)'] = df['Subnational unit (province, state)'].fillna('')
    name_counts = df.groupby(['Country/Area', 'Subnational unit (province, state)', 'Unit Name'])['Unit Name'].count()
    name_counts.name = 'Counts'
    potential_duplicates = pd.DataFrame(name_counts[name_counts > 1]).reset_index()
    duplicates_df = df[df['Unit Name'].isin(potential_duplicates['Unit Name'])][
        ['Unit ID', 'Unit Name', 'Unit type', 'Country/Area']].sort_values(by=['Country/Area', 'Unit Name', 'Unit type'])

    # Save the DataFrame to a CSV file
    duplicates_df.to_csv(qc_out_path + f"potential_duplicate_unit_names_{timestamp_str}.csv", index=False)

    return duplicates_df

duplicates_df = check_for_potential_duplicate_unit_names(goget_main)
print ('check csv at' + " " + f"potential_duplicate_unit_names_{timestamp_str}.csv")

# ===== Cell 21 =====
# Look for those that have more than one entry with the same name, in a given jurisdiction
def check_for_duplicate_unit_assets_combinations(df):
    df['Subnational unit (province, state)'] = df['Subnational unit (province, state)'].fillna('')
    df['Unit_asset'] = df['Unit Name'] + '_' + df['Unit type']
    unit_asset_counts = df.groupby(['Country/Area', 'Subnational unit (province, state)', 'Unit_asset'])['Unit_asset'].count()

    print(unit_asset_counts[unit_asset_counts > 1])

# ### Number formatting

# ===== Cell 22 =====
# ensure years are valid, ignoring (expected)
def check_if_data_is_float(df):
    main_num_cols = [
        'Status year', 'Discovery year', 'Production start year',
        'Latitude', 'Longitude',
        'Owner 1 %', 'Owner 2 %', 'Owner 3 %', 'Owner 4 %', 'Owner 5 %'
    ]
    for col in main_num_cols:
        print("=========================")
        # Add exception for "(expected)" in Production start year
        if col == "Production start year":
            df[col] = df[col].str.replace(r'\(expected\)', '', regex=True)
        # Check if the column can be converted to float
        try:
            df[col] = df[col].astype(float)
        except ValueError:
            print(f"Column '{col}' contains non-numeric values.")

# ===== Cell 23 =====
check_if_data_is_float(df)

# ## Production & reserves data

# ===== Cell 24 =====
# checks if all production data is time limited.

# Define a list of valid units
valid_units = ['million m³/y', 'million bbl/y', 'million boe/y']

# Filter the DataFrame based on the condition
PR_P_df = goget_prod[goget_prod['Production/reserves'] == 'production']
PR_P_df = PR_P_df[~PR_P_df['Units (converted)'].isin(valid_units)]

# Select the desired columns
PR_P_df = PR_P_df[['Unit ID', 'Production/reserves', 'Units (converted)']]

PR_P_df

# ===== Cell 25 =====
# Look for mismatches between fuel type and units
# (E.g., fuel type is gas but units are bbl)

df = goget_prod.copy()
df[(df['Fuel description'].str.contains('gas')) &
   (~df['Fuel description'].isin(['oil and gas condensate', 'gas condensate'])) &
   (df['Units (converted)'].str.contains('million bbl'))]

# ===== Cell 26 =====
# Look for mismatches between fuel type and units
df = goget_prod.copy()
df[(df['Fuel description'].str.contains('oil')) &
   # (df['Fuel description']!='gas condensate') &
   (df['Units (converted)'].str.contains('million m³'))]

# ===== Cell 27 =====
# (at) Hanna - this checks if an unit has multiple data points from the same year - I need to consolidate these up before we migrate to the dataset.
def check_duplicates(df):
    # Group by the specified columns and count occurrences
    duplicates = df.groupby(['Unit ID', 'Production/reserves','Fuel description', 'Data year', 'Data source type']).size().reset_index(name='counts')

    # Filter for counts greater than 1
    duplicates = duplicates[duplicates['counts'] > 1]

    return duplicates

duplicates = check_duplicates(goget_prod)

if not duplicates.empty:
  print("Duplicate entries found, see file duplicate_entries_" + timestamp_str + " in QC dump folder")
  # save out to dump
  duplicates.to_csv(qc_out_path + f"duplicate_entries_{timestamp_str}.csv")
else:
  print("No duplicate entries found.")

# ===== Cell 28 =====
# (at) Hanna - this checks if an unit has multiple *exactly matching* data points from the same year - I think these have all been resolved
def check_exact_duplicates(df):
    # Group by the specified columns and count occurrences
    duplicates = df.groupby(['Unit ID', 'Production/reserves', 'Fuel description','Quantity (original)','Units (original)', 'Data year', 'Data source type']).size().reset_index(name='counts')

    # Filter for counts greater than 1
    duplicates = duplicates[duplicates['counts'] > 1]

    return duplicates

duplicates = check_exact_duplicates(goget_prod)

if not duplicates.empty:
  print("Full entry duplicate entries found, see file duplicate_full_entries_" + timestamp_str + " in QC dump folder")
  # save out to dump
  duplicates.to_csv(qc_out_path + f"duplicate_full_entries_{timestamp_str}.csv")
else:
  print("No duplicate entries found.")


# ===== Cell 29 =====
# TODO: consolidate duplicate entries on production sheet  - Need to figure this out later
# def consolidate_duplicate_sources(df):
#     """
#     Consolidates "Data source" and "Notes" entries for duplicate rows,
#     and updates "Data source type" to "Multiple".

#     Args:
#         df: The pandas DataFrame to process.

#     Returns:
#         A pandas DataFrame with consolidated entries for duplicates.
#     """

#     # Group by the specified columns and aggregate data
#     consolidated_df = df.groupby(['Unit ID', 'Production/reserves', 'Fuel description',
#                                    'Reserves classification (original)', 'Quantity (original)',
#                                    'Units (original)', 'Data year'])[['Data source', 'Notes']].agg(
#         lambda x: ';'.join(x.astype(str).unique())  # Join unique values with semicolon
#     ).reset_index()

#     # Update 'Data source type' to 'Multiple' for consolidated rows
#     consolidated_df['Data source type'] = 'Multiple'

#     # Get indices of original non-duplicate rows
#     non_duplicate_indices = df[~df.duplicated(subset=['Unit ID', 'Production/reserves', 'Fuel description',
#                                                      'Reserves classification (original)', 'Quantity (original)',
#                                                      'Units (original)', 'Data year'], keep=False)].index

#     # Concatenate non-duplicate rows and consolidated rows
#     final_df = pd.concat([df.loc[non_duplicate_indices], consolidated_df]).reset_index(drop=True)

#     return final_df

# # Call the function to consolidate duplicates in goget_prod
# goget_prod_consolidated = consolidate_duplicate_sources(goget_prod)

# save goget_prod_consolidated to qc output
# goget_prod_consolidated.to_csv(qc_out_path + f"goget_prod_consolidated_{timestamp_str}.csv")

# ===== Cell 30 =====
# TO DO: check data from this source; it had some data-entry problems - add others we want to check here
EIARussia1997 = df.copy()[(df['Data source']=='EIARussia1997')]

EIARussia1997

# ## Spatial data

# ### Check coordinates

# ===== Cell 31 =====
def test_all_rows_have_coordinates(df):
    # TEST: if all fields included have Latitude
    test = df[df['Latitude'].isna()==True]
    if len(test)==0:
        pass
    else:
        print("Error!" + f" There were {len(test)} rows with no Latitude")
    # END OF TEST

    # TEST: if all fields included have Longitude
    test = df[df['Longitude'].isna()==True]
    if len(test)==0:
        pass
    else:
        print("Error!" + f" There were {len(test)} rows with no Longitude")
    # END OF TEST

# ===== Cell 32 =====
test_all_rows_have_coordinates(goget_main) # we now fill in country centroid when location is missing

# ===== Cell 33 =====
goget_main[goget_main['Latitude'].isna()]['Country/Area'].value_counts() #see worst data denisity for missing coordiates.

# ===== Cell 34 =====
# Check US states for missing to see if anything jumps out
goget_main[
    (goget_main['Country/Area']=='United States') &
    (goget_main['Latitude'].isna())
]['Subnational unit (province, state)'].value_counts()

# ### GIS analysis

# ===== Cell 35 =====
# check if coordinates are withing EEZ of country
def read_eez_file(eez_path, eez_file):
    # import EEZ data set
    # use boundaries from MarineRegions.org
    # union of world country boundaries and Exclusive Economic Zones (2014)
    # http://www.marineregions.org/downloads.php#unioneezcountry

    df = gpd.read_file( '/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/Data sets & reports (O&G)/O&G global materials/EEZ Outlines/' +
        'EEZ_Land_v3_202030.shp'
    )

    df['UNION'] = df['UNION'].replace({
        'Trinidad & Tobago': 'Trinidad and Tobago',
    })

    df = df.set_index('UNION')

    # # create one blob for all world land and EEZ boundaries, using Shapely function cascaded_union
    # # whatever is left out is, presumably, international waters
    # # this is used below to determine whether any parts of pipelines are in international waters
    # world_eez_and_land_boundaries = cascaded_union(eez_and_land_boundaries['geometry'])

    df = df.set_crs('epsg:4326')
    df = df.to_crs('epsg:4087')
    eez_and_land_boundaries = df

    return eez_and_land_boundaries

# ===== Cell 36 =====
# convert dataset to geodf
def convert_dataset_to_geopandas_df(df):
    """ Convert into GeoPandas DataFrame (gdf)"""

    for col in ['Latitude', 'Longitude']:
        try:
            # exclude empty cells
            df = df.dropna(subset=[col], how='any')
            # exclude empty strings
            df = df[(df[col]!='') & (df[col]!=' ')]
            # convert to float
            df[col] = df[col].astype(float)
        except:
            print("Error!" + f" Problem converting col {col}")

    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude))

    gdf = gdf.set_crs('epsg:4326')
    gdf = gdf.to_crs('epsg:4087')

    return gdf

# ===== Cell 37 =====
# define GOGET special cases
special_cases = [
    'United Arab Emirates-Iran',
    'Kuwait-Saudi Arabia',
    'Qatar-Oman',
    'Thailand-Malaysia',
    'Vietnam-Indonesia',
    'Russia-Ukraine',
    'Angola-Republic of the Congo',
    'Azerbaijan-Turkmenistan',
    'Iran-Iraq',
    'Kuwait-Saudi Arabia-Iran',
    'Saudi Arabia-Bahrain',
    'Saudi Arabia-Iran',
    'Senegal-Mauritania',
    'South China Sea',
    'Timor Gap',
    'Russia-Kazakhstan',
    'China-Japan',
]

# ===== Cell 38 =====
# # TODO: batch this to limit run time
# # function to check if field is in the same country as listed in the country column
# def check_if_project_is_in_correct_country(gdf, eez_and_land_boundaries):
#     """
#     Convert GOGET main data coordinates into the same coordinates system as EEZ (4087).
#     Use shapely function contains to see if each point is within the boundaries of the country's EEZ that it's supposedly in.
#     """

#     errors_to_handle = []

#     # TEST CRS
#     if (eez_and_land_boundaries.crs == gdf.crs) == True:
#         pass
#     else:
#         print("CRS error!")

#     eez_4087 = eez_and_land_boundaries.to_crs('epsg:4087')
#     gdf_4087 = gdf.to_crs('epsg:4087')

#     for row in gdf.index:
#         unit_id = gdf.at[row, 'Unit ID']
#         unit_name = gdf.at[row, 'Unit Name']
#         point = gdf.at[row, 'geometry']
#         country = gdf.at[row, 'Country/Area']

#         # Special handling for US States - was throwing an error for all asalkan fields not saying they were in US EEZ
#         if country == "United States" and gdf.at[row, 'Subnational unit (province, state)'] == "Alaska":
#             # Assume Alaska is within the US EEZ
#             fail_flag = 'N'
#             continue  # Skip further checks for Alaska entries

#         if country == "United States" and gdf.at[row, 'Subnational unit (province, state)'] == "Hawaii":
#             # Assume Hawaii is within the US EEZ
#             fail_flag = 'N'
#             continue  # Skip further checks for Hawaii entries

#         # Bypass checks for special cases
#         if country in special_cases:
#             fail_flag = 'N'
#             continue

#         # check if point is within country's EEZ it's supposed to be in
#         fail_flag = 'N' # initialize
#         try:
#             country_eez = eez_and_land_boundaries.at[country, 'geometry']
#             try:
#                 if point.within(country_eez):
#                     pass
#                 else:
#                     fail_flag = 'Y'
#             except:
#                     fail_flag = 'Y'
#         except:
#             print(f"country not found: {country}")

#         if fail_flag == 'Y':
#             # print("Error!" + f" The coord for {unit_name} ({unit_id}) are not within the EEZ of {country}; coord: {df.at[row, 'Latitude']}, {df.at[row, 'Longitude']}")
#             # print("Error!" + f" The coord for {unit_name} ({unit_id}) are not within the EEZ of {country}; coord: {point}")

#             # calculate distance away:
#             dist_threshold = 50  # km (changed to 50)
#             dist_away_km = eez_4087.at[country, 'geometry'].distance(gdf_4087.at[row, 'geometry'])/1000
#             if dist_away_km <= dist_threshold:
#                 pass # Do nothing if distance is less than or equal to 50km
#             else:
#                 print("Error!" + f" The coord for {unit_name} ({unit_id}) are not within the EEZ of {country}; coord: {point}")
#                 print(f"Distance away from EEZ is {round(dist_away_km, 1)} km")

#                 # find which country's EEZ it is in
#                 while fail_flag == 'Y':
#                     # print("entering case for checking other countries")

#                     for other_country in eez_and_land_boundaries.index:
#                         try:
#                             other_country_eez = eez_and_land_boundaries.at[other_country, 'geometry']
#                             if point.within(other_country_eez):
#                                 print(f"Found the coordinates are in other EEZ for: {other_country}")
#                                 print()
#                                 errors_to_handle += [(unit_id, unit_name, country, other_country, dist_away_km)]
#                                 fail_flag = 'N'
#                         except:
#                             print(f"Other comparison failed for {unit_id} & {other_country})")
#                             print()
#                             fail_flag = 'N'

#     errors_to_handle_df = pd.DataFrame(
#         errors_to_handle,
#         columns=['Unit ID', 'Unit Name', 'Country/Area', 'Found in other country', 'Distance away (km)'])
#     return errors_to_handle_df

# ===== Cell 39 =====
def check_if_project_is_in_correct_country_optimized(gdf, eez_and_land_boundaries, qc_out_path, timestamp_str):
    """
    Optimized version using spatial indexing (rtree) to speed up EEZ checks.
    Saves results to a CSV file in addition to printing.
    """

    errors_to_handle = []

    # Create spatial index for EEZs
    idx = index.Index()
    for i, country in enumerate(eez_and_land_boundaries.index):
        idx.insert(i, eez_and_land_boundaries.at[country, 'geometry'].bounds, obj=country)

    # Coordinate System Check (unchanged)
    if (eez_and_land_boundaries.crs == gdf.crs) == True:
        pass
    else:
        print("CRS error!")

    eez_4087 = eez_and_land_boundaries.to_crs('epsg:4087')
    gdf_4087 = gdf.to_crs('epsg:4087')

    for row in gdf.index:
        unit_id = gdf.at[row, 'Unit ID']
        unit_name = gdf.at[row, 'Unit Name']
        point = gdf.at[row, 'geometry']
        country = gdf.at[row, 'Country/Area']

        # Special handling for US States (unchanged)
        if country == "United States" and gdf.at[row, 'Subnational unit (province, state)'] in ["Alaska", "Hawaii"]:
            continue  # Skip to the next iteration

        # Bypass checks for special cases (unchanged)
        if country in special_cases:
            continue  # Skip to the next iteration

        # Get potential countries using the index
        potential_countries_ids = list(idx.intersection(point.bounds))
        potential_countries = [eez_and_land_boundaries.index[id] for id in potential_countries_ids]

        # Check within only potential countries
        found_in_eez = False  # Initialize a flag to track if found in any EEZ
        for other_country in potential_countries:
            try:
                country_eez = eez_and_land_boundaries.at[other_country, 'geometry']
                if point.within(country_eez):
                    found_in_eez = True  # Mark as found in an EEZ
                    if country != other_country:
                        # If found in a different country's EEZ, add to errors
                        print(f"Coordinates for {unit_name} ({unit_id}) are in {other_country}'s EEZ, but listed as {country}.")
                        errors_to_handle.append((unit_id, unit_name, country, other_country))
                    break  # Stop checking further as soon as one EEZ match is found.
            except Exception as e:
                print(f"Comparison failed for {unit_id} & {other_country}: {e}")
                # Consider handling the exception more specifically if needed

        if not found_in_eez:
            print(f"Coordinates for {unit_name} ({unit_id}) are outside any EEZ.")
            errors_to_handle.append((unit_id, unit_name, country, "Outside any EEZ"))

    errors_to_handle_df = pd.DataFrame(
        errors_to_handle,
        columns=['Unit ID', 'Unit Name', 'Country/Area', 'Found in other country'])

    # Save the DataFrame to a CSV file
    errors_to_handle_df.to_csv(qc_out_path + f"eez_check_errors_{timestamp_str}.csv", index=False)
    print(f"EEZ check errors saved to: {qc_out_path}eez_check_errors_{timestamp_str}.csv")

    return errors_to_handle_df

# ===== Cell 40 =====
# define files
eez_and_land_boundaries = read_eez_file(eez_path, eez_file)
goget_main_gdf = convert_dataset_to_geopandas_df(goget_main)

# ===== Cell 41 =====
# Angola-DRC: EEZ in this region does not match the licensed areas and "the DRC has repeatedly and consciously avoided making effective claims to this territory and its oil"
errors_to_handle_df = check_if_project_is_in_correct_country_optimized(goget_main_gdf, eez_and_land_boundaries, qc_out_path, timestamp_str) # Added qc_out_path and timestamp_str arguments

# ===== Cell 42 =====
def check_production_vs_reserves(goget_prod, goget_main):
    """
    Checks if the largest production values for a given field are higher than the largest reserves value within the dataset,
    considering only fields with non-zero values for both production and reserves, and saves the results to a CSV file.
    Also prints the Unit IDs where Quantity (converted) values were non-numeric.
    """

    # Identify non-numeric Quantity (converted) values
    non_numeric_ids = goget_prod[pd.to_numeric(goget_prod['Quantity (converted)'], errors='coerce').isna()]['Unit ID'].unique()
    print("Unit IDs with non-numeric Quantity (converted) values:")
    print(non_numeric_ids)

    # Convert 'Quantity (converted)' to numeric, forcing errors to NaN
    goget_prod['Quantity (converted)'] = pd.to_numeric(goget_prod['Quantity (converted)'], errors='coerce')

    # Filter for production data
    production_df = goget_prod[goget_prod['Production/reserves'] == 'production']

    # Filter for reserves data
    reserves_df = goget_prod[goget_prod['Production/reserves'] == 'reserves']

    # Group by Unit ID and get the largest values for gas
    production_gas_max = production_df[production_df['Units (converted)'] == 'million m³/y'].groupby('Unit ID')['Quantity (converted)'].max()
    reserves_gas_max = reserves_df[reserves_df['Units (converted)'] == 'million m³'].groupby('Unit ID')['Quantity (converted)'].max()

    # Group by Unit ID and get the largest values for oil
    production_oil_max = production_df[production_df['Units (converted)'] == 'million bbl/y'].groupby('Unit ID')['Quantity (converted)'].max()
    reserves_oil_max = reserves_df[reserves_df['Units (converted)'] == 'million bbl'].groupby('Unit ID')['Quantity (converted)'].max()

    # Merge the four series
    merged_df = pd.concat([production_gas_max, reserves_gas_max, production_oil_max, reserves_oil_max], axis=1)
    merged_df.columns = ['Production_gas', 'Reserves_gas', 'Production_oil', 'Reserves_oil']

    # Filter out rows with zero values for both production and reserves
    merged_df = merged_df[(merged_df['Production_gas'] > 0) & (merged_df['Reserves_gas'] > 0) &
                          (merged_df['Production_oil'] > 0) & (merged_df['Reserves_oil'] > 0)]

    # Calculate the difference between production and reserves
    merged_df['Difference'] = (merged_df['Production_gas'] - merged_df['Reserves_gas']) + (merged_df['Production_oil'] - merged_df['Reserves_oil'])

    # Filter for cases where production is higher than reserves
    higher_production = merged_df[merged_df['Difference'] > 0]

    # Sort by the greatest difference
    higher_production_sorted = higher_production.sort_values(by='Difference', ascending=False)

    # Save the results to a CSV file
    file_path = qc_out_path + f'productionhigherthanreserves'+ timestamp_str +'.csv'
    higher_production_sorted.to_csv(file_path)

    # Print the results
    if len(higher_production_sorted) > 0:
        print("Fields with production values higher than reserves (sorted by greatest difference):")
        print(higher_production_sorted)
    else:
        print("No fields found with production values higher than reserves.")

check_production_vs_reserves(goget_prod, qc_out_path)

# # Find non-links in reference columns
# If they're in the "Sources" sheet, that's OK. Otherwise, flag them.

# ===== Cell 43 =====
# Playground - need to fix cause blank rows still showing problematic
def check_source_columns(df, goget_sources):
    """
    Counts the number of problematic cells (containing potential URL issues)
    for each Unit ID in the DataFrame and provides a list of problematic columns.
    Accepts blank cells, cells with "http" as valid, and ignores blank entries.

    Args:
        df: The pandas DataFrame to check.
        goget_sources: The DataFrame containing the "short name" column.

    Returns:
        A pandas DataFrame with Unit IDs as index, counts of problematic cells,
        and a list of problematic columns for each row.
    """
    source_cols = [col for col in df.columns if 'source' in col.lower()]

    if not source_cols:
        print("No columns found containing 'source' in their name.")
        return None

    df = df.copy()  # Avoid chained assignment warnings
    df['Problematic_Count'] = 0
    df['Problematic_Columns'] = ''

    for col in source_cols:
        problematic_cells = df[
            df[col].apply(lambda x: all(
                part.strip().startswith("http") or
                part.strip().startswith("Assumed") or
                part.strip().startswith("Unknown") or
                part.strip().startswith("www") or
                part.strip() in goget_sources['short name'].tolist() or
                not part.strip()  # Ignore blank parts
                for part in str(x).split(';') if part.strip() or not part.strip() # consider blank parts
            ) is False)  # If any part fails the check, mark as problematic
        ].index

        df.loc[problematic_cells, 'Problematic_Count'] += 1
        df.loc[problematic_cells, 'Problematic_Columns'] += col + ', '

    # Remove trailing commas and spaces
    df['Problematic_Columns'] = df['Problematic_Columns'].str.rstrip(', ')

    # Group by Unit ID and aggregate results
    problematic_data = df.groupby('Unit ID').agg(
        Problematic_Count=('Problematic_Count', 'sum'),
        Problematic_Columns=('Problematic_Columns', lambda x: ', '.join(set(', '.join(x).split(', '))))
    )

    return problematic_data

# ===== Cell 44 =====
# save problematic_data to csv
problematic_data = check_source_columns(goget_main, goget_sources) # Call the function and assign its output
if problematic_data is not None:
    print(f"Found {len(problematic_data)} entries with problematic source data.")
    problematic_data.to_csv(qc_out_path + 'problematic_source_data_' + timestamp_str + '.csv')
    print(f"Problematic source data saved to: {qc_out_path}problematic_source_data_{timestamp_str}.csv")
else:
    print("No problematic source data found.")

# ### Links in non-reference columns

# ===== Cell 45 =====
def check_for_links_in_nonref_cols(df):
    ref_columns = ['Wiki URL', 'Wiki URL local', 'Notes']

    for col in df.columns:
        # Include both "source" and "Source" in the condition
        if col.endswith(('source', 'Source')) or col in ref_columns:
            continue

        # check for links in this column
        for index, row in df.iterrows():
            field_name = row['Unit Name' and 'Unit ID']
            cell_value = str(row[col])

            if cell_value.startswith('http'):
                print(f"Found link in non-ref column for {field_name} in {col}: {cell_value}")

# ===== Cell 46 =====
check_for_links_in_nonref_cols(goget_main)

# # Additional things after sharing with Jenny

# ===== Cell 47 =====
# # 2024 07 09 Note - this is less elegant than the check above. It does not work well for complex check. It does not distingush between subnational domains.
# def find_nonunique_field_names(df):
#     # filter for Latin America

#     project_mask = df['Unit Name'].str.lower().str.contains('project level')
#     concession_mask = df['Unit Name'].str.lower().str.contains('concession level')
#     basin_mask = df['Unit Name'].str.lower().str.contains('basin level')
#     df = df[(~project_mask) & (~concession_mask) & (~basin_mask)]

#     for country in df['Country/Area'].unique().tolist():
#         # find duplicated field names within a country
#         one_country = df[df['Country/Area']==country]
#         one_country_dups = one_country[one_country['Unit Name'].duplicated(keep=False)].sort_values(by=['Unit Name', 'Country/Area'])

#         if len(one_country_dups)>0:
#             print(f"Duplicate field names within {country}")
#             print(one_country_dups[['Unit Name', 'Country/Area']])
#             print()

#     other_dups = df[
#         (~df['Unit ID'].isin(one_country_dups['Unit ID'])) &
#         (df['Unit Name'].duplicated(keep=False))
#     ].sort_values(by=['Unit Name', 'Country/Area'])

#     if len(other_dups) > 0:
#         print("Show other duplicate field names")
#         print(other_dups[['Unit Name', 'Country/Area']])

# find_nonunique_field_names(goget_main)

# ## sandbox: GFIT checking

# ===== Cell 48 =====
# # sandbox:
# gfit_lng_file = 'GFIT LNG Terminals_Current (dl 2021-05-12_1615).xlsx'
# gfit_lng_path = '/Users/masoninman/Dropbox/GEM/GFIT (Global Fossil Infrastructure Tracker)/GFIT LNG Terminals Current - versions saved/'
# gfit_lng_xl = pd.ExcelFile(gfit_lng_path + gfit_lng_file)

# ===== Cell 49 =====
# # sandbox
# gfit_lng = pd.read_excel(gfit_lng_xl, sheet_name='Terminals')

# gfit_lng = gfit_lng.rename(columns={'TerminalID': 'Unit ID'})

# # exclude 'Unknown' etc
# gfit_lng = gfit_lng[~gfit_lng['Latitude'].isin(['Unknown', 'TBD'])]
# gfit_lng = gfit_lng[~gfit_lng['Longitude'].isin(['Unknown', 'TBD'])]

# gfit_lng_gdf = convert_dataset_to_geopandas_df(gfit_lng)
# check_if_project_is_in_correct_country(gfit_lng_gdf)

# [Download Duplicate Entries CSV](file/{qc_out_path}duplicate_entries_{timestamp_str}.csv)
