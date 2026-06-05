"""
compare_goget_locations_to_brazil.py

Migrated from Colab notebook: Compare GOGET Locations to Brazil Data (2025 08 07)
Auto-converted to a Python script. Colab-specific lines
(drive.mount, google.colab imports, shell/magic commands) have been
commented out and flagged; pip installs moved to ../requirements.txt.
"""

# Script to compare GOGET locations to Gov data locations. Please run this code in playground mode.

# ===== Cell 1 =====
# import libraries

import geopandas
import shapely.geometry
import shapely.ops
import pyproj
import openpyxl
import pandas as pd

import time

# ===== Cell 2 =====
# [colab-only removed] from google.colab import drive
# [colab drive mount removed] drive.mount('/content/drive')

# ===== Cell 3 =====
# load in files
GOGET_Iteration_Folder = '/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/GOGET Iterations/Snapshots of GOGET main data set/'
GOGET_Iteration = GOGET_Iteration_Folder + 'GOGET oil & gas extraction sites (2025 07 08).xlsx' #change this with the interation you want to us

# ===== Cell 4 =====
# set parameters
country_of_interest = 'Brazil' # change this with the country you are working on. Make sure the name is exactly what is used in GOGET and in Rystad.
# add handling of mistmatch name
now = time.localtime()

# create timestamp
timestamp = time.strftime("%Y%m%d_%H%M", now)

# ===== Cell 5 =====
# import field data
Field_data = GOGET_Iteration

# convert csv to gdf, creating geometry from longitude and latitude
# First, read the CSV file into a pandas DataFrame
Fielddata_df = pd.read_excel(GOGET_Iteration, sheet_name='Main data', engine='openpyxl')

# filter for country of interest
Fielddata_df = Fielddata_df[Fielddata_df['Country/Area'] == country_of_interest]

# Clean the 'Longitude' and 'Latitude' columns by replacing empty strings with NaN
Fielddata_df['Longitude'] = pd.to_numeric(Fielddata_df['Longitude'], errors='coerce')
Fielddata_df['Latitude'] = pd.to_numeric(Fielddata_df['Latitude'], errors='coerce')

# Now, convert the cleaned pandas DataFrame to a GeoDataFrame
Fielddata_gdf = geopandas.GeoDataFrame(
    Fielddata_df,
    geometry=geopandas.points_from_xy(Fielddata_df.Longitude,
                                      Fielddata_df.Latitude)
)
# Set the CRS for Fielddata_gdf
Fielddata_gdf = Fielddata_gdf.set_crs(epsg=4326)

# Drop rows with invalid geometries
Fielddata_gdf = Fielddata_gdf[Fielddata_gdf.geometry.is_valid]

# ===== Cell 6 =====
Fielddata_gdf

# ===== Cell 7 =====
# define folders
goget_country_folder = '/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/Data sets & reports (O&G)/O&G country materials/'
country = 'Brazil (GOGET O&G)/' # change for country you are working on

# ===== Cell 8 =====
# import comparison data
Comparison_folder = goget_country_folder + country
Comparison_file = 'Brazil fields with coord and wkt - Location Comparison Sheet.csv'

# read in data
compdf = pd.read_csv(Comparison_folder + Comparison_file)

# Filter and convert 'Longitude' and 'Latitude' using .loc
compdf.loc[:, 'Longitude'] = pd.to_numeric(compdf.loc[:, 'Longitude'], errors='coerce')
compdf.loc[:, 'Latitude'] = pd.to_numeric(compdf.loc[:, 'Latitude'], errors='coerce')

# Now, convert the cleaned pandas DataFrame to a GeoDataFrame
compgdf = geopandas.GeoDataFrame(
    compdf,
    geometry=geopandas.points_from_xy(compdf.Longitude,
                                      compdf.Latitude)
)
# Set the CRS for compgdf
compgdf = compgdf.set_crs(epsg=4326)

# Drop rows with invalid geometries
compgdf = compgdf[compgdf.geometry.is_valid]

# ===== Cell 9 =====
compgdf

# ===== Cell 10 =====
# Find closest assets in Fielddata_df to compgdf
def find_closest_assets(Fielddata_gdf, compgdf):
    """
    Finds the closest assets in Fielddata_gdf to each asset in compgdf.

    Args:
        Fielddata_gdf: GeoDataFrame of field data assets.
        compgdf: GeoDataFrame of comparison assets.

    Returns:
        pandas.DataFrame: DataFrame with closest asset information.
    """

    closest_assets = []
    for index, row in compgdf.iterrows():
        distances = Fielddata_gdf.distance(row['geometry'])
        min_distance = distances.min()
        closest_asset_index = distances.idxmin()
        closest_asset = Fielddata_gdf.loc[closest_asset_index]
        closest_assets.append({
            'comp_asset_index': index,
            'comp_longitude': row['Longitude'],
            'comp_latitude': row['Latitude'],
            'BrazilGov Name': row['Field Name'],  # Include Govdata Name
            'BrazilGov Field ID': row['Field ID'],  # Include Govdata Field ID
            'closest_asset_index': closest_asset_index,
            'closest_asset_longitude': closest_asset['Longitude'],
            'closest_asset_latitude': closest_asset['Latitude'],
            'Unit Name': closest_asset['Unit Name'],  # Include Unit Name
            'distance': min_distance
        })

    return pd.DataFrame(closest_assets)

# Apply function
Brazil_to_goget_assets_df = find_closest_assets(Fielddata_gdf, compgdf)

# ===== Cell 11 =====
# sort by distance, low to high
Brazil_to_goget_assets_df = Brazil_to_goget_assets_df.sort_values(by='distance')

# ===== Cell 12 =====
Brazil_to_goget_assets_df

# ===== Cell 13 =====
# Save Brazil_to_goget_assets_df to csv
Brazil_to_goget_assets_df.to_csv(Comparison_folder + 'Brazil_to_goget_assets_df_' + timestamp + '.csv', index=False)
