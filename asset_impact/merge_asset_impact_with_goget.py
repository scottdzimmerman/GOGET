"""
merge_asset_impact_with_goget.py

Migrated from Colab notebook: Merge Asset Impact Data With GOGET (2024 12 18)
Auto-converted to a Python script. Colab-specific lines
(drive.mount, google.colab imports, shell/magic commands) have been
commented out and flagged; pip installs moved to ../requirements.txt.
"""

# Purpose of this notebook is to Merge Asset Impact Data with GOGET Data
#
# See [Asset Impact Data Parse 2024 12 09.ipynb ](https://colab.research.google.com/drive/1m_UD1GSsmFjzyObIlEgAHJSlLM3wrwU9?usp=sharing) for parsing of Asset Impact Data
#
# And see [Asset Impact Data Integration Workplan](https://docs.google.com/document/d/18ErkkB0Bw8ngkf2gnnuxptHNJqjipSX0EAfp5n0g4qg/edit?usp=sharing) for more details

# ===== Cell 1 =====
# load in libraries
# [colab-only removed] from google.colab import drive
# [colab drive mount removed] drive.mount('/content/drive')

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
# [moved to requirements.txt] !pip install xlsxwriter
import xlsxwriter
import numpy as np
# [moved to requirements.txt] !pip install fuzzywuzzy
from fuzzywuzzy import fuzz

# ===== Cell 2 =====
# define files
goget_path = '/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/'
parsed_AI_data = goget_path + '/Data sets & reports (O&G)/O&G global materials/Asset Impact Data/Parsed_Filtered_Asset_Impact_Data_2024_12_26_15:58.xlsx'

existing_goget = goget_path + '/GOGET Iterations/Snapshots of GOGET main data set/GOGET oil & gas extraction sites (2024 12 24).xlsx'
existing_goget = pd.read_excel(existing_goget) # This line is added to load the data from the file path.

# ===== Cell 3 =====
# check if data was properly imported
parsed_AI_data = pd.read_excel(parsed_AI_data)
parsed_AI_data.head()

# ===== Cell 4 =====
# Filter GOGET to relevant sections - USA, Texas, Pennslyvania and California
relevant_goget = existing_goget[
    (existing_goget['Country/Area'] == 'United States') &
    (existing_goget['Subnational unit (province, state)'].isin(['Texas', 'California', 'Pennsylvania']))
]

# ===== Cell 5 =====
# # prompt: Provide a count of "Government unit ID" matches between relevant_goget and parsed_AI_data

# # Ensure "Government unit ID" column exists in both dataframes
# if "Government unit ID" not in relevant_goget.columns:
#   print("Error: 'Government unit ID' column not found in relevant_goget dataframe.")
#   exit()
# if "Government unit ID" not in parsed_AI_data.columns:
#     print("Error: 'Government unit ID' column not found in parsed_AI_data dataframe.")
#     exit()

# # Count of matches
# matches = 0
# for id_goget in relevant_goget["Government unit ID"].dropna().unique():
#   if id_goget in parsed_AI_data["Government unit ID"].dropna().unique():
#     matches +=1

# print(f"Number of 'Government unit ID' matches between relevant_goget and parsed_AI_data: {matches}")

# ===== Cell 6 =====
# Define correct totals
California_Total = 116.6
Pennsylvania_total = 1204.9
Texas_total = 4140

#Group by state and sum Production Total
production_by_state_1 = parsed_AI_data.groupby('Subnational unit (province, state)')['Total hydrocarbon production (million bbl/y)'].sum()

# Print the result
production_by_state_1

# ===== Cell 7 =====
# # prompt: merge relevant_goget's "Discovery year"	"Discovery year source" and "Basin" for all rows where the government ID matches onto parsed_AI_data

# # Merge the dataframes based on "Government unit ID", keeping only parsed_AI_data rows
# merged_data = pd.merge(parsed_AI_data, relevant_goget[['Government unit ID', 'Discovery year', 'Discovery year source', 'Basin']], on='Government unit ID', how='left')

# # Remove duplicate rows based on 'Government unit ID', keeping the first occurrence
# merged_data = merged_data.drop_duplicates(subset=['Government unit ID'], keep='first')

# # Display the first few rows of the merged data
# print(f"Shape of merged_data before deduplication: {merged_data.shape}")

# ===== Cell 8 =====
# # Deduplicate merged_data based on all columns.
# deduplicated_merged_data = merged_data.drop_duplicates()

# # Display the shape before and after deduplication
# print(f"Shape of merged_data before deduplication: {merged_data.shape}")
# print(f"Shape of merged_data after deduplication: {deduplicated_merged_data.shape}")

# # You can also deduplicate based on a subset of columns, for example:
# # deduplicated_merged_data = merged_data.drop_duplicates(subset=['Government unit ID'])
# # print(f"Shape of merged_data after deduplication by 'Government unit ID': {deduplicated_merged_data.shape}")

# # optionally: overwrite the previous variable
# merged_data = deduplicated_merged_data
# merged_data.head()

merged_data = parsed_AI_data

# ===== Cell 9 =====
#Group by state and sum Production Total
production_by_state_2 = merged_data.groupby('Subnational unit (province, state)')['Total hydrocarbon production (million bbl/y)'].sum()

# check production total still matches
production_by_state_1 == production_by_state_2

# ===== Cell 10 =====
# Using assign and lambda functions for a more concise approach
california_goget = (
    relevant_goget[relevant_goget['Subnational unit (province, state)'] == 'California']
    .assign(Field_ID=lambda x: x['Government unit ID'].astype(str).str.split('_').str[0], # Convert to string before using .str
            Field_Name=lambda x: x['Unit Name'].astype(str).str.split(' - ').str[0]) # Convert to string before using .str
    [['Field_Name', 'Field_ID', 'Discovery year', 'Discovery year source']]
)
california_goget

# ===== Cell 11 =====
# Function to find the best fuzzy match and merge data
def fuzzy_merge_california(row, california_goget):
    if row['Subnational unit (province, state)'] == 'California':
        best_match = None
        best_ratio = 0
        for index, cali_row in california_goget.iterrows():
            ratio = fuzz.ratio(row['Field Name'], cali_row['Field_Name'])
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = cali_row

        # Check if a good match was found (e.g., above a certain threshold)
        if best_ratio > 70:  # Adjust threshold as needed
            return pd.Series([best_match['Discovery year'], best_match['Discovery year source']])
    return pd.Series([None, None])

# Apply the function to create new columns
new_columns = merged_data.apply(fuzzy_merge_california, axis=1, args=(california_goget,))
merged_data['California Discovery year'] = new_columns[0]
merged_data['California Discovery year source'] = new_columns[1]

# ===== Cell 12 =====
#Group by state and sum Production Total
production_by_state_3 = merged_data.groupby('Subnational unit (province, state)')['Total hydrocarbon production (million bbl/y)'].sum()

# check if production still matches
production_by_state_3 == production_by_state_2

# ===== Cell 13 =====
# Replace "Discovery year" and "Discovery year source" with "California Discovery year" and "California Discovery year source" for California rows
merged_data.loc[merged_data['Subnational unit (province, state)'] == 'California', 'Discovery year'] = merged_data['California Discovery year']
merged_data.loc[merged_data['Subnational unit (province, state)'] == 'California', 'Discovery year source'] = merged_data['California Discovery year source']

# show california rows of merged_data
merged_data[merged_data['Subnational unit (province, state)'] == 'California']

# ===== Cell 14 =====
# drop 'California Discovery year' and 'California Discovery year source' from merged_data
merged_data = merged_data.drop(columns=['California Discovery year', 'California Discovery year source'])
merged_data.head()

# ===== Cell 15 =====
# format Discovery year as four character from the left
merged_data['Discovery year'] = merged_data['Discovery year'].astype(str)
merged_data['Discovery year'] = merged_data['Discovery year'].str[:4]
merged_data.head()

# ===== Cell 16 =====
#Group by state and sum Production Total
production_by_state_4 = merged_data.groupby('Subnational unit (province, state)')['Total hydrocarbon production (million bbl/y)'].sum()

# Print the result
production_by_state_4 == production_by_state_1

# ===== Cell 17 =====
# seperate out PA to create ID seperately
merged_data_noPA = merged_data[merged_data['Subnational unit (province, state)'] != 'Pennsylvania']
merged_data_PA = merged_data[merged_data['Subnational unit (province, state)'] == 'Pennsylvania']

# ===== Cell 18 =====
def create_unit_name_and_tag_duplicates(df, state_specific_column):
    """
    Creates a 'Unit Name' column and tags duplicates.

    Args:
        df: The input DataFrame (merged_data_noPA or merged_data_PA).
        state_specific_column: The column to use for Unit Name creation
                               ('Field Name' for TX/CA, 'Formation Name' for PA).

    Returns:
        The modified DataFrame with 'Unit Name' and 'Duplicate' columns.
    """
    df['Unit Name'] = df[state_specific_column] + ' - ' + df['Operator']
    df['Duplicate'] = df['Unit Name'].duplicated(keep=False)
    return df

# Apply the function to both DataFrames
merged_data_noPA = create_unit_name_and_tag_duplicates(merged_data_noPA, 'Field Name')
merged_data_PA = create_unit_name_and_tag_duplicates(merged_data_PA, 'Formation Name')

merged_data_PA.head()

# ===== Cell 19 =====
# prompt: merge merged_data_noPA back with merged_data_PA

# Concatenate the two dataframes back together
merged_data = pd.concat([merged_data_noPA, merged_data_PA], ignore_index=True)

# Display the first few rows of the merged data
merged_data.head()

# ===== Cell 20 =====
#Group by state and sum Production Total
production_by_state_5 = merged_data.groupby('Subnational unit (province, state)')['Total hydrocarbon production (million bbl/y)'].sum()

# Print the result
production_by_state_5 == production_by_state_1

# ===== Cell 21 =====
# clean Unit Names
# List of terms to remove
terms_to_remove = [" Inc.", " LLC", " Llc", " L.P.", " L.L.C.", "Ltd.", " LP", " Corp", " Ltd", " Lp",  " Incorporated", " Limited Liability Company", " Limited Partnership", " Corporation"," Company", ", "]

# Function to strip the terms from the Unit Name
def strip_terms(unit_name):
    if isinstance(unit_name, str):  # Check if the unit name is a string
        for term in terms_to_remove:
            unit_name = unit_name.replace(term, "")
        return unit_name.strip()  # Remove leading/trailing whitespace
    else:
        return unit_name

# Apply the function to the 'Unit Name' column
merged_data['Unit Name'] = merged_data['Unit Name'].apply(strip_terms)


merged_data.head()

# ===== Cell 22 =====
# replace "United_States" with United States
merged_data['Country/Area'] = merged_data['Country/Area'].replace('United_States', 'United States')
merged_data.head()

# ===== Cell 23 =====
#Group by state and sum Production Total
production_by_state_6 = merged_data.groupby('Subnational unit (province, state)')['Total hydrocarbon production (million bbl/y)'].sum()

# Print the result
production_by_state_6 == production_by_state_1

# ===== Cell 24 =====
# Create new columns and initialize with None
merged_data[['Status', 'Status year', 'Status source', 'Location accuracy', 'Location source']] = None

# Fill in 'Status' related columns based on hydrocarbon production
mask_production = merged_data['Total hydrocarbon production (million bbl/y)'] > 0
merged_data.loc[mask_production, ['Status', 'Status year', 'Status source']] = ['operating', 2023, 'AIProduction2023']

# Fill in 'Location' related columns based on latitude availability
mask_latitude = merged_data['Latitude'].notna()
merged_data.loc[mask_latitude, ['Location accuracy', 'Location source']] = ['exact', 'AIlocation2023']

merged_data.head()

# ===== Cell 25 =====
# Add specicifity to sources

# Append Subnational unit to Status source and Location source
merged_data['Status source'] = merged_data.apply(lambda row: f"{row['Status source']} ({row['Subnational unit (province, state)']})" if pd.notnull(row['Status source']) else None, axis=1)
merged_data['Location source'] = merged_data.apply(lambda row: f"{row['Location source']} ({row['Subnational unit (province, state)']})" if pd.notnull(row['Location source']) else None, axis=1)


merged_data.head()

# ===== Cell 26 =====
merged_data.columns

# ===== Cell 27 =====
# show merged_data columns
merged_data_clean = merged_data.rename(columns={
    'Country/Area': 'Country/Area',
    'Subnational unit (province, state)': 'Subnational unit (province, state)',
    'Unit Name': 'Unit Name',  # generated name of field name plus operator for tx and ca, formation name plus operator in pa
    'Field Name': 'Sub Formation Name',
    'Formation Name': 'Project Name',  # for summing by formation
    'Status': 'Status',
    'Status year': 'Status year',
    'Status source': 'Status source',
    'Location accuracy': 'Location accuracy',
    'Location source': 'Location source',
    'Well ID(s)': 'Well ID(s)',
    'Latitude': 'Latitude',
    'Longitude': 'Longitude',
    'Operator': 'Operator',
    'Owner': 'Owner',
    'Resource Type': 'Resource Type',
    'Recovery mechanism': 'Recovery mechanism',
    'Onshore/Offshore': 'Onshore/Offshore',
    'Oil production (million bbl/y)': 'Oil production (million bbl/y)',
    'Condensate production (million bbl/y)': 'Condensate production (million bbl/y)',
    'Raw gas production (million m³/y)': 'Raw gas production (million m³/y)',
    'Dry gas production (million m³/y)': 'Dry gas production (million m³/y)',
    'NGL production (million bbl/y)': 'NGL production (million bbl/y)',
    'Total hydrocarbon production (million bbl/y)': 'Total hydrocarbon production (million boe/y)',
    'Government unit ID': 'Government unit ID',
    #'Discovery year': 'Discovery year',
    #'Discovery year source': 'Discovery year source',
    'Duplicate': 'Duplicate'
})

# reorder merged_data_clean
merged_data_clean_reorder = ['Unit Name', 'Country/Area', 'Subnational unit (province, state)', 'Status', 'Status year', 'Status source', 'Latitude', 'Longitude', 'Location accuracy', 'Location source', 'Operator', 'Owner','Project Name', 'Government unit ID', 'Well ID(s)', 'Onshore/Offshore', 'Resource Type', 'Recovery mechanism', 'Oil production (million bbl/y)', 'Condensate production (million bbl/y)', 'Raw gas production (million m³/y)', 'Dry gas production (million m³/y)', 'NGL production (million bbl/y)', 'Total hydrocarbon production (million boe/y)', "Duplicate"]
# Explicitly define the desired column order

merged_data_clean = merged_data_clean[merged_data_clean_reorder]

# show merged_data_clean
merged_data_clean.columns

# ===== Cell 28 =====
# enure production_by_state totals match

#Group by state and sum Production Total
production_by_state_6 = merged_data_clean.groupby('Subnational unit (province, state)')['Total hydrocarbon production (million boe/y)'].sum()

# Print the result
production_by_state_1 == production_by_state_6

# ===== Cell 29 =====
# # if "Unit Name" is a duplicate, add "Resource Type" + "_" + "Recovery mechanism" to the unit name
# for unit_name in merged_data_clean['Unit Name'].unique():
#     if merged_data_clean['Unit Name'].value_counts()[unit_name] > 1:  # Check if unit name is non-unique
#         # Get the Resource Type and Recovery mechanism for rows with the non-unique unit name
#         resource_types = merged_data_clean.loc[merged_data['Unit Name'] == unit_name, 'Resource Type'].astype(str)
#         recovery_mechanisms = merged_data_clean.loc[merged_data['Unit Name'] == unit_name, 'Recovery mechanism'].astype(str)
#         project_name = merged_data_clean.loc[merged_data['Unit Name'] == unit_name, 'Project Name'].astype(str)

#         # Update the Unit Name for rows with the non-unique unit name
#         merged_data_clean.loc[merged_data_clean['Unit Name'] == unit_name, 'Unit Name'] = (
#             merged_data_clean.loc[merged_data_clean['Unit Name'] == unit_name, 'Unit Name'] +
#             " (" +
#             project_name +
#             ", " +
#             resource_types +
#             "_" +
#             recovery_mechanisms +
#             ")"

#         )

# Count non-unique unit names
num_non_unique_unit_names = merged_data_clean['Unit Name'].duplicated(keep=False).sum()
print(f"Number of non-unique Unit Names: {num_non_unique_unit_names}")

# ===== Cell 30 =====
# Function to modify Unit Name based on Onshore/Offshore and Resource Type
def modify_unit_name(row, df):
    unit_name = row['Unit Name']
    if df['Unit Name'].value_counts()[unit_name] > 1:  # Check if unit name is non-unique

        subset = df[df['Unit Name'] == unit_name]

        if len(subset['Onshore/Offshore'].unique()) > 1:
            if row['Onshore/Offshore'] == 'Onshore':
                unit_name += ' (Onshore)'
            elif row['Onshore/Offshore'] == 'Offshore':
                unit_name += ' (Offshore)'
        elif len(subset['Resource Type'].unique()) > 1:
            if row['Resource Type'] == 'Unconventional':
                unit_name += ' (Unconventional)'
            elif row['Resource Type'] == 'Conventional':
                unit_name += ' (Conventional)'
         # Modified project name handling
        elif len(subset['Project Name'].unique()) > 1:
            unit_name += ' (' + row['Project Name'] + ')' # appends project name
    return unit_name

# Apply the function to modify Unit Names
merged_data_clean['Unit Name'] = merged_data_clean.apply(lambda row: modify_unit_name(row, merged_data_clean), axis=1)

# ===== Cell 31 =====
# Recheck non-unique names
num_non_unique_unit_names = merged_data_clean['Unit Name'].duplicated(keep=False).sum()

# update duplicate tag
merged_data_clean['Duplicate'] = merged_data_clean['Unit Name'].duplicated(keep=False)

print(f"Number of non-unique Unit Names: {num_non_unique_unit_names}")

# ===== Cell 32 =====
import datetime
current_datetime = datetime.datetime.now()
formatted_datetime = current_datetime.strftime("%Y_%m_%d_%H:%M")

output_file_path = goget_path + '/Data sets & reports (O&G)/O&G global materials/Asset Impact Data/'
output_file_name = f"formatted_Asset_Impact_Data_{formatted_datetime}.xlsx"
Full_output_file_path = output_file_path + output_file_name

# Create a new ExcelWriter object
writer = pd.ExcelWriter(Full_output_file_path, engine='xlsxwriter') # Create writer with path

# Create the "About" sheet
about_df = pd.DataFrame({
    'Information': [
        f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Source file: /Data sets & reports (O&G)/O&G global materials/Asset Impact Data/Parsed_Filtered_Asset_Impact_Data_2024_12_18_19:32.xlsx'",
        f"Goget data: /GOGET Iterations/Snapshots of GOGET main data set/GOGET oil & gas extraction sites (2024 12 18 PM).xlsx"
            ]
})
about_df.to_excel(writer, sheet_name='About', index=False)

merged_data_clean.to_excel(writer, sheet_name='Data', index=False)

# Save the Excel file (only once)
writer.close()

# ===== Cell 33 =====
# print saved location
print(f"The file has been saved to: {Full_output_file_path}")
