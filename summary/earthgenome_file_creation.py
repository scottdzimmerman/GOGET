"""
earthgenome_file_creation.py

Migrated from Colab notebook: GOGET Earthgenome file creation 2024 07 03
Auto-converted to a Python script. Colab-specific lines
(drive.mount, google.colab imports, shell/magic commands) have been
commented out and flagged; pip installs moved to ../requirements.txt.
"""

# ===== Cell 1 =====
#run this to pull content from google drive
# [colab-only removed] from google.colab import drive
# [colab drive mount removed] drive.mount('/content/drive')

# ===== Cell 2 =====
#Loading the libraries
import pandas as pd
import numpy as np

# ===== Cell 3 =====
#Loading the main Excel File
file_path = '/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/GOGET Iterations/Official Releases of GOGET/Global-Oil-and-Gas-Extraction-Tracker-March-2024.xlsx'
xl = pd.ExcelFile(file_path)

# ===== Cell 4 =====
#setting dataframes with main, P&R
main_data_df = xl.parse('Main data')
production_reserves_df = xl.parse('Production & reserves')

# ===== Cell 5 =====
#Use this block for any necessary main data filters: See example of filter for FID year-
  #main_data_df["FID Year"] = main_data_df["FID Year"].astype(str).str.replace(" \(expected\)", "", regex=True)
  #filtered_main_data_df = main_data_df[main_data_df["FID Year"].isin(["2022", "2023"])]
#filtered_main_data_df = main_data_df[main_data_df['Latitude'].notna()]
filtered_main_data_df = main_data_df #Use this when no filter is applicable

# # Add Reserve and production Data to Main Data Frame

# ===== Cell 6 =====
# Convert 'Data year' to integers in the 'production_reserves_df'
production_reserves_df['Data year'] = pd.to_numeric(production_reserves_df['Data year'], errors='coerce').fillna(-1).astype(int)

# ===== Cell 7 =====
#Define functions for getting the most recent value, calculate the total reserves, calculate the total production and define the conversion factor
# Function to get the most recent value based on the criteria
def get_most_recent_value_and_year(unit_id, prod_res, units, df):
    # Filter based on Unit ID, Production/reserves, and Units (converted)
    filtered = df[
        (df["Unit ID"] == unit_id) &
        (df["Production/reserves"] == prod_res) &
        (df["Units (converted)"] == units)
    ]

    # Sort by Data year and get the most recent entry
    filtered = filtered.sort_values(by="Data year", ascending=False)
    if not filtered.empty:
        most_recent = filtered.iloc[0]
        return most_recent["Quantity (converted)"], most_recent["Data year"]
    else:
        return np.nan, np.nan

# Function to calculate the total reserves - Commenting out as were using production values only.
#def calculate_total_reserves(row):
   # if pd.notna(row['Reserves- Hydrocarbons (unspecified)']):
     #   return row['Reserves- Hydrocarbons (unspecified)']
    #else:
        # Convert gas reserves to boe
       # gas_in_boe = row['Reserves- Gas'] * conversion_factor if pd.notna(row['Reserves- Gas']) else 0
      #  oil_reserves = row['Reserves - Oil'] if pd.notna(row['Reserves - Oil']) else 0
      #  return gas_in_boe + oil_reserves

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

# ===== Cell 8 =====
# Populate reserves and production columns with the most recent data - commenting out reserves as were only mapping production
#filtered_main_data_df["Reserves - Oil"] = filtered_main_data_df["Unit ID"].apply(lambda x: get_most_recent_value(x, "reserves", "million bbl", production_reserves_df))
#filtered_main_data_df["Reserves- Gas"] = filtered_main_data_df["Unit ID"].apply(lambda x: get_most_recent_value(x, "reserves", "million m³", production_reserves_df))
#filtered_main_data_df["Reserves- Hydrocarbons (unspecified)"] = filtered_main_data_df["Unit ID"].apply(lambda x: get_most_recent_value(x, "reserves", "million boe", production_reserves_df))

# Update for Production - Oil and its year
filtered_main_data_df[["Production - Oil", "Production Year - Oil"]] = filtered_main_data_df.apply(
    lambda x: pd.Series(get_most_recent_value_and_year(x["Unit ID"], "production", "million bbl/y", production_reserves_df)),
    axis=1
)
# Update for Production - Gas and its year
filtered_main_data_df[["Production - Gas", "Production Year - Gas"]] = filtered_main_data_df.apply(
    lambda x: pd.Series(get_most_recent_value_and_year(x["Unit ID"], "production", "million m³/y", production_reserves_df)),
    axis=1
)

# Update for Production - Hydrocarbons (unspecified) and its year
filtered_main_data_df[["Production - Hydrocarbons (unspecified)", "Production Year - Hydrocarbons (unspecified)"]] = filtered_main_data_df.apply(
    lambda x: pd.Series(get_most_recent_value_and_year(x["Unit ID"], "production", "million boe/y", production_reserves_df)),
    axis=1
)

# Calculate total reserves and production
#filtered_main_data_df['Reserves- Total (Oil, Gas and Hydrocarbons)'] = filtered_main_data_df.apply(calculate_total_reserves, axis=1)
filtered_main_data_df['Production - Total (Oil, Gas and Hydrocarbons)'] = filtered_main_data_df.apply(calculate_total_production, axis=1)

# ===== Cell 9 =====
filtered_main_data_df

# ===== Cell 10 =====
# Convert Discovery Year to String
filtered_main_data_df['Discovery year'] = filtered_main_data_df['Discovery year'].astype(object)

# Ensure there are no NaN values in the year columns before conversion to avoid errors
filtered_main_data_df['Production Year - Oil'].fillna(0, inplace=True)
filtered_main_data_df['Production Year - Gas'].fillna(0, inplace=True)
filtered_main_data_df['Production Year - Hydrocarbons (unspecified)'].fillna(0, inplace=True)

# Convert to integer first to remove the trailing zero, then to string
filtered_main_data_df['Production Year - Oil'] = filtered_main_data_df['Production Year - Oil'].astype(int).astype(str)
filtered_main_data_df['Production Year - Gas'] = filtered_main_data_df['Production Year - Gas'].astype(int).astype(str)
filtered_main_data_df['Production Year - Hydrocarbons (unspecified)'] = filtered_main_data_df['Production Year - Hydrocarbons (unspecified)'].astype(int).astype(str)

# Replace "0" with np.nan or a placeholder if you had NaN values initially
filtered_main_data_df.replace('0', np.nan, inplace=True)

# Check the conversion by printing the dtypes again
column_data_types = filtered_main_data_df.dtypes
print(column_data_types)

# ===== Cell 11 =====
filtered_main_data_df

# ===== Cell 12 =====
# GEM Standard Country Name and Area List mappings
gem_country_area_mapping = {
    'Azerbaijan-Turkmenistan': 'Azerbaijan; Turkmenistan',
    'Iran-Iraq': 'Iran; Iraq',
    'Kuwait-Saudi Arabia': 'Kuwait; Saudi Arabia',
    'Kuwait-Saudi Arabia-Iran': 'Kuwait; Saudi Arabia; Iran',
    'Saudi Arabia-Bahrain': 'Saudi Arabia; Bahrain',
    'Saudi Arabia-Iran': 'Saudi Arabia; Iran',
    'Senegal-Mauritania': 'Senegal; Mauritania',
    'South China Sea': 'China; Taiwan; Philippines',
    'Thailand-Malaysia': 'Thailand; Malaysia',
    'Timor Gap': 'East Timor; Australia; Indonesia',
    'United Arab Emirates-Iran': 'United Arab Emirates; Iran'
}

# Function to find Area List based on GEM Standard Country Name
def get_country_list(gem_name):
    return gem_country_area_mapping.get(gem_name, '')

# Apply the function to create a new column 'Country List'
filtered_main_data_df['Country List'] = filtered_main_data_df['Country'].apply(get_country_list)

# Display the updated DataFrame
filtered_main_data_df

# ===== Cell 13 =====
dropped_filtered_main_data = filtered_main_data_df.drop(['Government unit ID',  'Basin', 'Concession / block'], axis=1)

# ===== Cell 14 =====
dropped_filtered_main_data

# ===== Cell 15 =====
average_production_total = filtered_main_data_df["Production - Total (Oil, Gas and Hydrocarbons)"].mean()
print("Average Production - Total (Oil, Gas and Hydrocarbons):", average_production_total)

# ===== Cell 16 =====
# Create new column for scaling where there is a fill in value based on average when data is not there.
dropped_filtered_main_data["Production for Map Scaling"] = np.where(dropped_filtered_main_data["Production - Total (Oil, Gas and Hydrocarbons)"] != 0,
                                                               dropped_filtered_main_data["Production - Total (Oil, Gas and Hydrocarbons)"],
                                                               average_production_total)

# ===== Cell 17 =====
dropped_filtered_main_data.head()

# ===== Cell 18 =====
# Add regions
Regions_File_Path = '/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/QC/Earth Genome File Creation/GOGET Country Names and Region Definitions (as of 2024 03 27).csv'
Regions = pd.read_csv(Regions_File_Path)

# Add Wiki Name
Wiki_Name_File_Path = '/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/QC/Earth Genome File Creation/GOGET oil & gas extraction sites Wiki Names as of 2024 03 27.csv'
Wiki_Name = pd.read_csv(Wiki_Name_File_Path)

# ===== Cell 19 =====
# Adjust 'wiki name' to match the exact column name in your Wiki_Name DataFrame
# This selects only 'Unit ID' and the 'wiki name' column from Wiki_Name for the merge
wiki_name_column = Wiki_Name[['Unit ID', 'Wiki name']]

# Perform the merge, focusing only on adding the 'wiki name' column
dropped_production_Wiki_name = pd.merge(dropped_filtered_main_data, wiki_name_column, on='Unit ID', how='left')

# Check the first few rows to ensure the 'wiki name' column was added correctly
dropped_production_Wiki_name.head()

# ===== Cell 20 =====
# Perform the merge to add the 'GEM region' column from the 'Regions' DataFrame to 'dropped_production_Wiki_name',
# using 'Country' from 'dropped_production_Wiki_name' and 'GEM Standard Country Name' from 'Regions'.
# The 'on' parameter is replaced with 'left_on' and 'right_on' to specify the column names in each DataFrame.

dropped_production_Wiki_name = pd.merge(
    dropped_production_Wiki_name,
    Regions[['GEM Standard Country Name', 'GEM region']],
    left_on='Country',
    right_on='GEM Standard Country Name',
    how='left'
)

# After the merge, you might have an extra column 'GEM Standard Country Name' which is a duplicate of 'Country'.
# You can drop this extra column if it's not needed.
dropped_production_Wiki_name.drop('GEM Standard Country Name', axis=1, inplace=True)

# Check the first few rows to ensure the 'GEM region' column was added correctly and the merge was successful.
dropped_production_Wiki_name

# ===== Cell 21 =====
#check columns and type
dropped_production_Wiki_name.dtypes

# ===== Cell 22 =====
# drop superfluous columns
clean_export = dropped_production_Wiki_name.drop(['Fuel type', 'Unit type'], axis=1)
clean_export

# ===== Cell 23 =====
# Set up DF of Units without locations
missing_location_df = clean_export[clean_export['Latitude'].isna()]

# Get unique entries from the 'Country' column
unique_countries_with_missing_locations = missing_location_df['Country'].unique()

# Display the unique countries
unique_countries_df = pd.DataFrame(unique_countries_with_missing_locations, columns=['Country'])
unique_countries_df.head()

# ===== Cell 24 =====
# Add Locations in Based on Cetroids to missing location areas
Country_Centroid_File_Path = '/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/QC/Earth Genome File Creation/Fill In Coordinates from Country Centroid - 04 01 2024.csv'
Country_Centroid = pd.read_csv(Country_Centroid_File_Path)

# ===== Cell 25 =====
# prompt: add a column based on the Country_Centroid to the clean_export df

clean_export_center = pd.merge(clean_export, Country_Centroid, how='left', on='Country')
clean_export_center

# ===== Cell 26 =====
# prompt: fill in Latitude_x with Latitude_y when Latitude_x=NaN, do the same for Longitude_y. Whenever a fill in value is used, mark "Location accuracy" as "country level only"

# Fill in missing latitudes and longitudes
clean_export_center['Latitude_x'] = clean_export_center.apply(lambda row: row['Latitude_y'] if pd.isna(row['Latitude_x']) else row['Latitude_x'], axis=1)
clean_export_center['Longitude_x'] = clean_export_center.apply(lambda row: row['Longitude_y'] if pd.isna(row['Longitude_x']) else row['Longitude_x'], axis=1)

# Update 'Location accuracy' for filled-in values
clean_export_center['Location accuracy'] = clean_export_center.apply(lambda row: 'country level only' if pd.isna(row['Latitude_x']) or pd.isna(row['Longitude_x']) else row['Location accuracy'], axis=1)

# Display the updated DataFrame
clean_export_center

# ===== Cell 27 =====
#drop centroid fill in columns
clean_export_center_clean = clean_export_center.drop(['Latitude_y', 'Longitude_y'], axis=1)
clean_export_center_clean

# ===== Cell 28 =====
# Set output order, dropping more columns
desired_column_order = [
    'Unit ID',
    'Wiki name',
    'Status',
    'Country',
    'Country List',
    'Subnational unit (province, state)',
    'GEM region',
    'Latitude_x',
    'Longitude_x',
    'Location accuracy',
    'Discovery year',
    'FID Year',
    'Production start year',
    'Operator',
    'Owner',
    'Parent',
    'Project or complex',
    'Production - Oil',
    'Production Year - Oil',
    'Production - Gas',
    'Production Year - Gas',
    'Production - Total (Oil, Gas and Hydrocarbons)',
    'Wiki URL',
]

# Step 2: Reorder the DataFrame
clean_export_center_clean_reorder = clean_export_center_clean[desired_column_order]

# ===== Cell 29 =====
# Define a dictionary with old column names as keys and new names with units as values
column_rename_map = {
    'Production - Oil': 'Production - Oil (Million bbl/y)',
    'Production - Gas': 'Production - Gas (Million m³/y)',
    'Production - Total (Oil, Gas and Hydrocarbons)': 'Production - Total (Oil, Gas and Hydrocarbons) (Million boe/y)',
    'Latitude_x': 'Latitude',
    'Longitude_x': 'Longitude',
    # Add other columns you wish to rename similarly here
}

# Rename the columns
clean_export_center_clean_reorder_rename = clean_export_center_clean_reorder.rename(columns=column_rename_map)

# ===== Cell 30 =====
from datetime import datetime

# Generate a timestamp
timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')

# Define the base path for your files
base_path = '/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/GOGET Iterations/Compiled Versions of GOGET/'

# Append the timestamp to your filenames
output_excel_filename = f'GOGET Earthgenome file {timestamp}.xlsx'
output_csv_filename = f'GOGET Earthgenome file {timestamp}.csv'

# Full paths
output_excel_path = base_path + output_excel_filename
output_csv_path = base_path + output_csv_filename

# Save the files
clean_export_center_clean_reorder_rename.to_excel(output_excel_path, index=False)
clean_export_center_clean_reorder_rename.to_csv(output_csv_path, index=False)

# Print out the saved file names with their locations
print(f'Excel file saved as: {output_excel_path}')
print(f'CSV file saved as: {output_csv_path}')
