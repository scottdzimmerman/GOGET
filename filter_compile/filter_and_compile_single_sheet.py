"""
filter_and_compile_single_sheet.py

Migrated from Colab notebook: GOGET Filter and Compile into single sheet 2025 01 16
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

# # Load in recent data file

# ===== Cell 3 =====
#Loading the Excel File. (Save an excel sheet of the GOGET Main file to GOGET iterations prior to doing this)
goget_folder = '/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/GOGET Iterations/Snapshots of GOGET main data set/'
goget_xl = pd.ExcelFile(goget_folder + 'GOGET oil & gas extraction sites (2025 02 18 1043).xlsx')

xl = goget_xl

# ===== Cell 4 =====
#setting dataframes with main, P&R
main_data_df = xl.parse('Main data')
production_reserves_df = xl.parse('Reserves and Production')

# ===== Cell 5 =====
#Use this block for any necessary filters: See example of filter for FID year-
  #main_data_df["FID Year"] = main_data_df["FID Year"].astype(str).str.replace(" \(expected\)", "", regex=True)
  #filtered_main_data_df = main_data_df[main_data_df["FID Year"].isin(["2022", "2023"])]
filtered_main_data_df = main_data_df[main_data_df["keep"] == "yes"]

# ===== Cell 6 =====
filtered_main_data_df.head()

# # Add Reserve and production Data to Main Data Frame

# ===== Cell 7 =====
# Convert 'Data year' to integers in the 'production_reserves_df'
production_reserves_df['Data year'] = pd.to_numeric(production_reserves_df['Data year'], errors='coerce').fillna(-1).astype(int)

# ===== Cell 8 =====
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

# ===== Cell 9 =====
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

# ===== Cell 10 =====
filtered_main_data_df.head()

# # Add Keep Tag

# ===== Cell 11 =====
# prompt: filter the filtered_main_data_df for only values where "Reserves- Total (Oil, Gas and Hydrocarbons)" are greater than 25 and/or Production - Total (Oil, Gas and Hydrocarbons) is greater than 1. Add another column thats labelled "Keep?" and enter "yes" for all rows where that criteria is met.

# Filter the DataFrame
filtered_main_data_df['Keep?'] = np.where(
    (filtered_main_data_df['Reserves- Total (Oil, Gas and Hydrocarbons)'] > 25) |
    (filtered_main_data_df['Production - Total (Oil, Gas and Hydrocarbons)'] > 1),
    'yes',
    ''
)

# Display the filtered DataFrame
filtered_main_data_df.head()

# ===== Cell 12 =====
# prompt: save filtered_main_data_df to /content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/GOGET Iterations/Snapshots of GOGET main data set/ + GOGET with PR as of + time stamp

from datetime import datetime

timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
file_name = f"GOGET with PR as of {timestamp}.xlsx"
output_path = f"/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/GOGET Iterations/Snapshots of GOGET main data set/{file_name}"
filtered_main_data_df.to_excel(output_path, index=False)

# ===== Cell 13 =====
# print output path
print(output_path)

# # Bypass generation

# ===== Cell 14 =====
# Optional: use pregenerated version of the data, to avoid long run time of regenerating
Rendered_file = '/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/GOGET Iterations/Snapshots of GOGET main data set/GOGET with PR as of 20250218-182036.xlsx'
gogetwithpr = pd.read_excel(Rendered_file)

# remove data source, project level reserves, project led columns from df for re-generation
#filtered_main_data_df = filtered_main_data_df.drop(columns=['Data Source', 'Project Level Reserves', 'Project Level Production','Project Led, key data here'])

# ===== Cell 15 =====
# Count blank entries in 'Project' and 'Complex' columns
blank_project_count = gogetwithpr['Project or complex'].isnull().sum()

print(f"Number of blank entries in 'Project' column: {blank_project_count}")

# # Group projects and complexes

# ===== Cell 16 =====
# Sort units by Country/Area, then Project or complex
# Convert 'Country/Area' and 'Project or complex' columns to string type before sorting, and replace NaN with custom string
filledgogetwithpr = gogetwithpr.copy()
filledgogetwithpr['Country/Area'] = filledgogetwithpr['Country/Area'].astype(str)
filledgogetwithpr['Project or complex'] = filledgogetwithpr['Project or complex'].astype(str).replace('nan', 'Unit Only')
gogetwithprsorted = filledgogetwithpr.sort_values(by=['Country/Area', 'Project or complex'])

# ===== Cell 17 =====
# show for qc
gogetwithprsorted.head()

# ===== Cell 18 =====
# if Unit type = anything other than asset, field, unit, pool or phase, and there is no production and reserve data as an entry where unit type = project, complex, block, or concession, then sum asset, field, unit, pool or phase production and reserve rows for each project. if there is unit type = project, complex, block, or concession production and reserve data, use those values, ignoring the asset, field, unit, pool or phase production or reserve figures

# Group data by 'Project or complex'
grouped = gogetwithprsorted.groupby('Project or complex')

# Create an empty list to store the results
results = []

# Create counters for project-level and aggregated data
project_level_count = 0
aggregated_count = 0

# Iterate through each project group
for project, group in grouped:
  # Check for project-level production/reserve data
  project_data = group[group['Unit type'].isin(['project', 'complex', 'block', 'concession'])]

  if not project_data.empty:
    # If project-level data exists, use it and skip aggregating lower levels
    project_level_count += 1  # Increment project-level counter
    for index, row in project_data.iterrows():
      results.append({
          'Project or complex': row['Project or complex'],
          'Country/Area': row['Country/Area'],  # Include country for project-level data
          'Gas Reserves': row['Reserves- Gas'],
          'Oil Reserves': row['Reserves - Oil'],
          'Unspecified Hydrocarbons Reserves': row['Reserves- Hydrocarbons (unspecified)'],
          'Gas Production': row['Production - Gas'],
          'Oil Production': row['Production - Oil'],
          'Unspecified Hydrocarbons Production': row['Production - Hydrocarbons (unspecified)'],
          'Total Reserves': row['Reserves- Total (Oil, Gas and Hydrocarbons)'],
          'Total Production': row['Production - Total (Oil, Gas and Hydrocarbons)'],
          'Data Source': 'Project Level' # Tag for project level data
      })

  else:
    # If no project-level data, aggregate lower-level data by country
    aggregated_count += 1  # Increment aggregated counter
    for country, country_group in group[group['Unit type'].isin(['asset', 'field', 'unit', 'pool', 'phase'])].groupby('Country/Area'):
      gas_reserves = country_group['Reserves- Gas'].sum()
      oil_reserves = country_group['Reserves - Oil'].sum()
      unspecified_hydrocarbons_reserves = country_group['Reserves- Hydrocarbons (unspecified)'].sum()
      total_reserves = country_group['Reserves- Total (Oil, Gas and Hydrocarbons)'].sum()
      gas_production = country_group['Production - Gas'].sum()
      oil_production = country_group['Production - Oil'].sum()
      unspecified_hydrocarbons_production = country_group['Production - Hydrocarbons (unspecified)'].sum()
      total_production = country_group['Production - Total (Oil, Gas and Hydrocarbons)'].sum()
      results.append({
          'Project or complex': project,
          'Country/Area': country, # Include country for aggregated data
          'Gas Reserves': gas_reserves,
          'Oil Reserves': oil_reserves,
          'Unspecified Hydrocarbons Reserves': unspecified_hydrocarbons_reserves,
          'Gas Production': gas_production,
          'Oil Production': oil_production,
          'Unspecified Hydrocarbons Production': unspecified_hydrocarbons_production,
          'Total Reserves': total_reserves,
          'Total Production': total_production,
          'Data Source': 'Aggregated'
      })


# Create a new DataFrame from the results
project_summary_df = pd.DataFrame(results)

# Print the counts
print(f"Units with project-level data: {project_level_count}")
print(f"Units with aggregated lower-level data: {aggregated_count}")
print(project_summary_df.shape)
project_summary_df.head()

# ===== Cell 19 =====
# Add unit-only data to project_summary_df
for index, row in gogetwithprsorted[gogetwithprsorted['Project or complex'] == 'Unit Only'].iterrows():
    project_summary_df = pd.concat([project_summary_df, pd.DataFrame({
        'Project or complex': [row['Project or complex']],
        'Unit name': [row['Unit Name']],
        'Country/Area': [row['Country/Area']],
        'Gas Reserves': [row['Reserves- Gas']],
        'Oil Reserves': [row['Reserves - Oil']],
        'Unspecified Hydrocarbons Reserves': [row['Reserves- Hydrocarbons (unspecified)']],
        'Gas Production': [row['Production - Gas']],
        'Oil Production': [row['Production - Oil']],
        'Unspecified Hydrocarbons Production': [row['Production - Hydrocarbons (unspecified)']],
        'Total Reserves': [row['Reserves- Total (Oil, Gas and Hydrocarbons)']],
        'Total Production': [row['Production - Total (Oil, Gas and Hydrocarbons)']],
        'Data Source': ['Unit Level']
    })], ignore_index=True)



# ===== Cell 20 =====
# prompt: project_summary_df to excel

# Assuming project_summary_df is already created as in your provided code.

# [colab-only removed] from google.colab import files

timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
excel_file_name = f"project_summary_{timestamp}.xlsx"
project_summary_df.to_excel(excel_file_name, index=False)

files.download(excel_file_name)

# ===== Cell 21 =====
# # prompt: add all none project associated units from to filtered_main_data to project_summary_df and fill out the columns in that table based on the data in filtered_main_data

# # Filter for units tagged as "Unit Only"
# non_project_units = gogetwithprsorted['Project or complex'] == 'Unit Only'

# # Create a list to store the new rows
# new_rows = []

# for index, row in non_project_units.iterrows():
#     new_row = {
#         'Project or complex': row['Project or complex'],
#         'Unit name': row['Unit Name'],
#         'Country/Area': row['Country/Area'],
#         'Gas Reserves': row['Reserves- Gas'],
#         'Oil Reserves': row['Reserves - Oil'],
#         'Unspecified Hydrocarbons Reserves': row['Reserves- Hydrocarbons (unspecified)'],
#         'Gas Production': row['Production - Gas'],
#         'Oil Production': row['Production - Oil'],
#         'Unspecified Hydrocarbons Production': row['Production - Hydrocarbons (unspecified)'],
#         'Total Reserves': row['Reserves- Total (Oil, Gas and Hydrocarbons)'],
#         'Total Production': row['Production - Total (Oil, Gas and Hydrocarbons)'],
#         'Data Source': 'Unit Level' # Tagging the source as unit level
#     }
#     new_rows.append(new_row)

# # Create a DataFrame from the new rows
# new_units_df = pd.DataFrame(new_rows)

# # Concatenate the new DataFrame with project_summary_df
# project_summary_df = pd.concat([project_summary_df, new_units_df], ignore_index=True)

# project_summary_df.shape

# ===== Cell 22 =====
# prompt: Make two DF, one with the counts and a project_summary_df.

# Create the counts DataFrame
counts_df = pd.DataFrame({
    'Data Source': ['Units with project-level data', 'Units with aggregated lower-level data', "Units with stand alone data"],
    'Count': [project_level_count, aggregated_count, blank_project_count]
})

print("Counts DataFrame:")
print(counts_df)
print("\nProject Summary DataFrame:")
print(project_summary_df.head())

# ===== Cell 23 =====
# [moved to requirements.txt] !pip install xlsxwriter

import xlsxwriter

# ===== Cell 24 =====
#save out complied sheet with Reserves, counts_df, and Project Summary DataFrame as one excel sheet

# time stamp generation
from datetime import datetime

# Get the current date and time
now = datetime.now()

# Format the date and time as "GOGET as of {timestamp_str} with PR"
timestamp_str = now.strftime("%Y_%m_%d_%H:%M")

print(timestamp_str)

# ===== Cell 25 =====
counts_df

# ===== Cell 26 =====
import os

# ===== Cell 27 =====
# prompt: save counts_df project_summary_df and filtered_main_data_df to excel sheets
# Create the necessary directories if they don't exist
output_dir = os.path.dirname(output_file)  # Get the directory part of the path
os.makedirs(output_dir, exist_ok=True)     # Create the directory (and any parent directories) if they don't exist


# Create a Pandas Excel writer using XlsxWriter as the engine.
output_file = f'/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/GOGET Iterations/Compiled Versions of GOGET/GOGET as of {timestamp_str} with PR grouped by project/complex.xlsx'
writer = pd.ExcelWriter(output_file, engine='xlsxwriter')

# Write each DataFrame to a different worksheet.
filtered_main_data_df.to_excel(writer, sheet_name='Main Data', index=False)
counts_df.to_excel(writer, sheet_name='Counts', index=False)
project_summary_df.to_excel(writer, sheet_name='Project Summary', index=False)

# Close the Pandas Excel writer and output the Excel file.
writer.close()

# ===== Cell 28 =====
print("output saved at " + output_file)
