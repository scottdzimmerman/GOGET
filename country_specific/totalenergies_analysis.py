"""
totalenergies_analysis.py

Migrated from Colab notebook: GOGET TotalEnergies Analysis 2024 04 18
Auto-converted to a Python script. Colab-specific lines
(drive.mount, google.colab imports, shell/magic commands) have been
commented out and flagged; pip installs moved to ../requirements.txt.
"""

# ===== Cell 1 =====
#Loading the libraries
import pandas as pd
import numpy as np

# ===== Cell 2 =====
#run this to pull content from google drive
# [colab-only removed] from google.colab import drive
# [colab drive mount removed] drive.mount('/content/drive')

# ===== Cell 3 =====
#Loading the main Excel File, use this block for pulling info from official data
file_path = '/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/GOGET Iterations/Official Releases of GOGET/Global-Oil-and-Gas-Extraction-Tracker-March-2024.xlsx'
xl = pd.ExcelFile(file_path)

#setting dataframes with main, P&R
main_data_df = xl.parse('Main data')
production_reserves_df = xl.parse('Production & reserves')

#Use this block for any necessary filters: See example of filter for FID year-
  #main_data_df["FID Year"] = main_data_df["FID Year"].astype(str).str.replace(" \(expected\)", "", regex=True)
  #filtered_main_data_df = main_data_df[main_data_df["FID Year"].isin(["2022", "2023"])]
filtered_main_data_df = main_data_df

# # Add Reserve and production Data to Main Data Frame

# ===== Cell 4 =====
# Convert 'Data year' to integers in the 'production_reserves_df'
production_reserves_df['Data year'] = pd.to_numeric(production_reserves_df['Data year'], errors='coerce').fillna(-1).astype(int)

# ===== Cell 5 =====
#Define functions for getting the most recent value, calculate the total reserves, calculate the total production and define the conversion factor
# Function to get the most recent value based on the criteria
def get_most_recent_value(unit_id, prod_res, units, df):
    # Filter based on Unit ID, Production/reserves, and Units (converted)
    filtered = df[
        (df["Unit ID"] == unit_id) &
        (df["Production/reserves"] == prod_res) &
        (df["Units (converted)"] == units)
    ]

    # Sort by Data year and get the most recent entry
    filtered = filtered.sort_values(by="Data year", ascending=False)
    return filtered.iloc[0]["Quantity (converted)"] if not filtered.empty else np.nan

# Function to calculate the total reserves
def calculate_total_reserves(row):
    if pd.notna(row['Reserves- Hydrocarbons (unspecified)']):
        return row['Reserves- Hydrocarbons (unspecified)']
    else:
        # Convert gas reserves to boe
        gas_in_boe = row['Reserves- Gas'] * conversion_factor if pd.notna(row['Reserves- Gas']) else 0
        oil_reserves = row['Reserves - Oil'] if pd.notna(row['Reserves - Oil']) else 0
        return gas_in_boe + oil_reserves

# Function to calculate the total production
def calculate_total_production(row):
    if pd.notna(row['Production - Hydrocarbons (unspecified)']):
        return row['Production - Hydrocarbons (unspecified)']
    else:
        # Convert gas production to boe
        gas_in_boe = row['Production - Gas'] * conversion_factor if pd.notna(row['Production - Gas']) else 0
        oil_production = row['Production - Oil'] if pd.notna(row['Production - Oil']) else 0
        return gas_in_boe + oil_production

# Conversion factor from million m³ to million boe for gas
conversion_factor = 5.883 / 1000

# ===== Cell 6 =====
# Populate reserves and production columns with the most recent data
filtered_main_data_df["Reserves - Oil"] = filtered_main_data_df["Unit ID"].apply(lambda x: get_most_recent_value(x, "reserves", "million bbl", production_reserves_df))
filtered_main_data_df["Reserves- Gas"] = filtered_main_data_df["Unit ID"].apply(lambda x: get_most_recent_value(x, "reserves", "million m³", production_reserves_df))
filtered_main_data_df["Reserves- Hydrocarbons (unspecified)"] = filtered_main_data_df["Unit ID"].apply(lambda x: get_most_recent_value(x, "reserves", "million boe", production_reserves_df))

filtered_main_data_df["Production - Oil"] = filtered_main_data_df["Unit ID"].apply(lambda x: get_most_recent_value(x, "production", "million bbl/y", production_reserves_df))
filtered_main_data_df["Production - Gas"] = filtered_main_data_df["Unit ID"].apply(lambda x: get_most_recent_value(x, "production", "million m³/y", production_reserves_df))
filtered_main_data_df["Production - Hydrocarbons (unspecified)"] = filtered_main_data_df["Unit ID"].apply(lambda x: get_most_recent_value(x, "production", "million boe/y", production_reserves_df))

# Calculate total reserves and production
filtered_main_data_df['Reserves- Total (Oil, Gas and Hydrocarbons)'] = filtered_main_data_df.apply(calculate_total_reserves, axis=1)
filtered_main_data_df['Production - Total (Oil, Gas and Hydrocarbons)'] = filtered_main_data_df.apply(calculate_total_production, axis=1)

# Filter for Company Specific Data

# ===== Cell 7 =====
filtered_main_data_df.to_excel('/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/GOGET Iterations/Compiled Versions of GOGET/March 2024 GOGET With Production 2024 0418.xlsx', index=False)


# # Load in compiled data - Parse

# ===== Cell 8 =====
# Load the data from an Excel file into a DataFrame
file_path = '/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/GOGET Iterations/Compiled Versions of GOGET/March 2024 GOGET With Production 2024 0418.xlsx'
xls = pd.ExcelFile(file_path)
data = pd.read_excel(xls, sheet_name='Sheet1')

# Filter the data for rows where the "Parent column contains "TotalEnergies"
filtered_data = data[data['Parent'].str.contains('TotalEnergies', na=False)]

# Calculate the sum of reserves and production totals
total_reserves = filtered_data['Reserves- Total (Oil, Gas and Hydrocarbons)'].sum()
total_production = filtered_data['Production - Total (Oil, Gas and Hydrocarbons)'].sum()

#Calculate row count
total_rows_filtered = filtered_data.shape[0]

# Output the results
print(f'Total Reserves: {total_reserves}')
print(f'Total Production: {total_production}')
print(f'Area Count: {total_rows_filtered}')

# # Extract Total's Share

# ===== Cell 9 =====
import re

data = filtered_data

# Function to extract percentage ownership from strings
def extract_te_ownership(text):
    # Regex to find TotalEnergies and its percentage ownership
    match = re.search(r'TotalEnergies \((\d+)%\)', text)
    return float(match.group(1)) if match else 0

# Filter data for TotalEnergies involvement
data['TotalEnergies Ownership'] = data['Parent'].apply(lambda x: extract_te_ownership(str(x)) if 'TotalEnergies' in str(x) else 0)

# Calculate TotalEnergies' share of reserves and production
data['TotalEnergies Reserves'] = data['Reserves- Total (Oil, Gas and Hydrocarbons)'] * data['TotalEnergies Ownership'] / 100
data['TotalEnergies Production'] = data['Production - Total (Oil, Gas and Hydrocarbons)'] * data['TotalEnergies Ownership'] / 100

# Summing the TotalEnergies' share of reserves and production across all entries
total_reserves_te = data['TotalEnergies Reserves'].sum()
total_production_te = data['TotalEnergies Production'].sum()

# Display results
print(f'Total Reserves attributed to TotalEnergies: {total_reserves_te}')
print(f'Total Production attributed to TotalEnergies: {total_production_te}')

# Optionally save the detailed DataFrame
#output_file_path = 'Detailed_TotalEnergies_Share_Parent.xlsx'
#data.to_excel(output_file_path, index=False)

# ===== Cell 10 =====
# Unique Country List

unique_countries = filtered_data['Country'].unique()

# Output the list of unique countries
print("Unique countries with TotalEnergies' involvement:")
print(unique_countries)

# ===== Cell 11 =====
# Count the number of entries per country
country_counts = filtered_data['Country'].value_counts()

# Display the counts per country
print("Counts per country for TotalEnergies' involvement:")
print(country_counts)

# ===== Cell 12 =====
# Filter to include only data where the region is 'Africa'
africa_data = merged_data[merged_data['GEM region'] == 'Africa']

# Calculate TotalEnergies' share of reserves and production in Africa
africa_data['TotalEnergies Reserves'] = africa_data['Reserves- Total (Oil, Gas and Hydrocarbons)'] * africa_data['TotalEnergies Ownership'] / 100
africa_data['TotalEnergies Production'] = africa_data['Production - Total (Oil, Gas and Hydrocarbons)'] * africa_data['TotalEnergies Ownership'] / 100

# Summing the TotalEnergies' share of reserves and production across the Africa entries
total_reserves_te_africa = africa_data['TotalEnergies Reserves'].sum()
total_production_te_africa = africa_data['TotalEnergies Production'].sum()

# Count the number of entries per country
country_counts_africa = africa_data['Country'].value_counts()

# Sum country counts
sumcounts = country_counts_africa.sum()

# Unique country list
unique_countries_africa = africa_data['Country'].unique()


# Display the results
print(f'Total Reserves attributed to TotalEnergies in Africa: {total_reserves_te_africa}')
print(f'Total Production attributed to TotalEnergies in Africa: {total_production_te_africa}')
print("Counts per country for TotalEnergies' involvement in Africa:")
print(country_counts_africa)
print(sumcounts)
print(unique_countries_africa)

# # Map Making

# ===== Cell 13 =====
# Libraries
# note that the order of points in GeoPandas is longitude, latitude
# (opposite order from that of many data sets)
# [moved to requirements.txt] !pip install cartopy

import geopandas as gpd
import shapely.geometry
import shapely.ops
import pyproj
import pandas as pd
import time
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import matplotlib.patches
import matplotlib.lines
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.image as mpimg  # Correct import for image handling
from matplotlib.font_manager import fontManager, FontProperties

import numpy # to get sqrt, pi functionality

# ===== Cell 14 =====
## Font Management
# Import OpenSans to Colab
font_path = '/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/Reports/Q1 2024 GOGET Report/Code/GOGET Maps Files/OpenSans-Regular.ttf'  # Update this to the path where the font file is located

# Add the font to Matplotlib's font manager
fontManager.addfont(font_path)

# ===== Cell 15 =====
#GEM Plot Variables

footer_color = "#222222"
footer_lineheight = 1.2
footer_fontsize = 14

# default height of a figure is 450 pixels

# gemstyle does this:
# specify a base_ratio, then set base_size = base_ratio*16
# 1. add 6 line margin all the way around
# 2. color of title is "#222222", margin 6666, size=base_size*1.5, lineheight=1.35, bold font
# 3. color of subtitle is "#333333", margin 0666, padding top=12, bottom=12, size=base_size*1.15, lineheight=1.45
# 4. set caption info as linehight=1.2, size=base_size*0.875, color="#222222", margin=18,6,6,6

base_ratio = 1.0
base_size = base_ratio * 16
color_title = "#222222"
color_subtitle = "#333333"
color_grid = "#cbcbcb"

text_weight_normal = 400
text_weight_bold = 700

# save fig
#' @keywords save_gem_plot
#' @examples
#' save_gem_plot(
#' plot_grid = line_plot_with_gem_footer,
#' save_filepath = "filename_that_my_plot_should_be_saved_to-nc.png",
#' width_pixels = 770,
#' height_pixels = 540,
#' resolution = 4
#' )
#'
#' @export
# save plot function - now separated from finalise_plot function and setting the resolution as part of the arguments
# save_gem_plot <- function (plot_grid, save_filepath, width_pixels = 640, height_pixels = 450, resolution = 3) {
#   grid::grid.draw(plot_grid)

#   #save it
#   ggplot2::ggsave(plot=plot_grid,
#                   width= (width_pixels/72),
#                   height= (height_pixels/72),
#                   dpi = resolution * 100,
#                   filename = save_filepath,
#                   bg="white")
# }

#width_pixels = 640 # default
#height_pixels = 450 # default

# ===== Cell 16 =====
#Map colors
construction_color = '#BF532C'
TwentyTwoFID_color = '#F27D16' #matches GOGET Q1 report color scheme (darker)
TwentyThreeFID_color = '#BF532C' #matches GOGET Q1 report color scheme (lighter)
other_land_color = '#E5E5E5'
other_land_alpha = 1
other_land_edge = '#cbcbcb'
highlight_land_color = '#c2c2c2'
water_color = '#ffffff'
water_alpha = 0.3
operating_color = '0.25'
operating_terms_color = '0.666'
construction_lw = 1.
operating_lw = 0.25
ehb_alpha = 1.

# ===== Cell 17 =====
# import states/provinces, countries, lakes shapefile
ne_states_provinces = '/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/Reports/Q1 2024 GOGET Report/Code/GOGET Maps Files/50m_cultural copy/ne_50m_admin_1_states_provinces_lines.shp'
ne_states_provinces_gdf = gpd.read_file(ne_states_provinces)
countries_gdf = gpd.read_file('/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/Reports/Q1 2024 GOGET Report/Code/GOGET Maps Files/50m_cultural copy/ne_50m_admin_0_countries.shp')
lakes_gdf = gpd.read_file('/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/Reports/Q1 2024 GOGET Report/Code/GOGET Maps Files/10m_physical copy/ne_10m_lakes.shp')
oceans_gdf = gpd.read_file('/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/Reports/Q1 2024 GOGET Report/Code/GOGET Maps Files/10m_physical copy/ne_10m_ocean.shp')

# ===== Cell 18 =====
filtered_data
