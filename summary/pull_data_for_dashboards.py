"""
pull_data_for_dashboards.py

Migrated from Colab notebook: Pull Data for Dashboards 2026 02 18 .ipynb
Auto-converted to a Python script. Colab-specific lines
(drive.mount, google.colab imports, shell/magic commands) have been
commented out and flagged; pip installs moved to ../requirements.txt.
"""

# Code for generating data for the GOGET dashboard - Written Feb 18, 2026

# Code here for parsing official data is adapted from https://colab.research.google.com/drive/1Upzff2ThxaVgQObcA4RP3IKOf0rreRh3#scrollTo=*PLmVQauN8UTg*
#
# Starting point is the filtered dataset from the GOGET DB instance

# ===== Cell 1 =====
#run this to pull content from google drive
# [colab-only removed] from google.colab import drive
# [colab drive mount removed] drive.mount('/content/drive')

#Loading the libraries
import pandas as pd
import numpy as np
import re
from datetime import datetime

# ===== Cell 2 =====
# Load the main dataset
Alt_folder = ('/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/GOGET Iterations/Alternative Formats of GOGET/')
Official_field_data = pd.ExcelFile(Alt_folder+ 'goget-field-export-2026-manual-keep-for-summary.xlsx')
field_data = Official_field_data.parse('Field-level main data')
field_prod = Official_field_data.parse('Field-level production data')
field_res = Official_field_data.parse('Field-level reserves data')

# add project data -
Official_project_data = pd.ExcelFile(Alt_folder + 'goget-project-export-2026-02-18T143642.xlsx')
project_data = Official_project_data.parse('Project-level main data')
proj_prod = Official_project_data.parse('Project-level data production')
proj_res = Official_project_data.parse('Project-level data reserves')

# output folder
output_folder = '/content/drive/MyDrive/GOGET q1 2026/Dashboard'

# Load the regional definitions
regions_path = '/content/drive/MyDrive/GOGET Q1 2024/QC Process/Region definitions 2025 02 18 - Region definitions.csv'  # Update this path to your regions file
regions_df = pd.read_csv(regions_path)

# ===== Cell 3 =====
# time stamp for batch
timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

# print time stamp
print(f'this output will tagged as {timestamp}')

# ===== Cell 4 =====
# find and mark fields covered at the project level
# load dfs
fields_main_df = field_data
projects_main_df = project_data

# count unfiltered rows
print(f"fields_main_df has {fields_main_df.shape[0]} rows.")
print(f"projects_main_df has {projects_main_df.shape[0]} rows.")

# Rename 'Country/Area' to 'Country' in fields_main_df for consistency
fields_main_df = fields_main_df.rename(columns={'Country/Area': 'Country'})

# extract project ids
project_level_ids = projects_main_df['Units (list of IDs)'].dropna().apply(lambda x: [item.strip() for item in str(x).split(',')]).explode().unique()

# mark ids covered by project
fields_main_df['Covered_by_Project_Level_Data'] = fields_main_df['Project ID'].isin(project_level_ids)

fields_main_df['Covered_by_Project_Level_Data'] = fields_main_df['Covered_by_Project_Level_Data'].map({True: 'covered on the project level', False: 'not covered'})

# count values of fields covered at project level
print(fields_main_df['Covered_by_Project_Level_Data'].value_counts())

# if covered at the project level, filter out
proj_cover_filter_fields_main_df = fields_main_df[fields_main_df['Covered_by_Project_Level_Data'] == 'not covered']

# use proj_cover_filter_fields_main_df for production

# ===== Cell 5 =====
# fill in GEM region and GEM sub-region as unknown if nan on regions_df
regions_df['GEM region'] = regions_df['GEM region'].fillna('Unknown')
regions_df['GEM sub-region'] = regions_df['GEM sub-region'].fillna('Unknown')

#shown countries where region or subregion is unknown
unknown_regions = regions_df[regions_df['GEM region'] == 'Unknown']
print(unknown_regions)

# ===== Cell 6 =====
# sum each production value by Project ID	and Units (converted), summing Quantity (converted)
field_prod_sum = field_prod.groupby(['Project ID', 'Units (converted)'], as_index=False)['Quantity (converted)'].sum()
project_prod_sum = proj_prod.groupby(['Project ID', 'Units (converted)'], as_index=False)['Quantity (converted)'].sum()

print ("summed production by shared units (i.e. gases and liquids)")

# sort field_prod_sum by Quantity (converted)
field_prod_sum = field_prod_sum.sort_values(by='Quantity (converted)', ascending=False)
project_prod_sum = project_prod_sum.sort_values(by='Quantity (converted)', ascending=False)

# pivot field_prod_sum so Units (converted) are columns
field_prod_sum_pivot = field_prod_sum.pivot(index='Project ID', columns='Units (converted)', values = 'Quantity (converted)')
project_prod_sum_pivot = project_prod_sum.pivot(index='Project ID', columns='Units (converted)', values = 'Quantity (converted)')

print("pivoted production so that million boe/y million bbl/y and million cubic meters/y are all columns")

# merge field_prod_sum onto proj_cover_filter_fields_main_df on project id
main_with_prod_no_project = pd.merge(proj_cover_filter_fields_main_df, field_prod_sum_pivot, left_on='Project ID', right_on='Project ID', how='left')
projects_main_df = pd.merge(projects_main_df, project_prod_sum_pivot, left_on='Project ID', right_on='Project ID', how='left')

print ("merged production onto main data")

# ===== Cell 7 =====
# tag all entries in projects_main_df as "project"
projects_main_df['Type'] = 'project-level'
main_with_prod_no_project['Type'] = 'field-level'

print ("tagged projects as project or field level")

# replace "Project" in column headers with "Unit" within projects_main_df
projects_main_df.columns = projects_main_df.columns.str.replace('Project', 'Unit')

# Create "Covered_by_Project_Level_Data" as "Is project level"
projects_main_df['Covered_by_Project_Level_Data'] = 'this is the project level'

# ===== Cell 8 =====
# print row count in main_with_prod_no_project and projects_main_df
fields_row_count = main_with_prod_no_project.shape[0]
projects_row_count = projects_main_df.shape[0]
print(f"main_with_prod_no_project has {fields_row_count} rows.")
print(f"project_main_df has {projects_row_count} rows.")
print (f"sum of project and field is {fields_row_count + projects_row_count}")

# ===== Cell 9 =====
# add projects_main_df to main_with_prod_no_project
project_and_field_data = pd.concat([main_with_prod_no_project, projects_main_df], ignore_index=True)

# added project level to the field-level without project

combined_row_count = project_and_field_data.shape[0]
if combined_row_count == (fields_row_count + projects_row_count): print(f"project_and_fields_data has the right number of rows.")
else: print(f"project_and_fields_data does not have the right number of rows")

# ===== Cell 10 =====
# rename GEM Standard Country Name in regions df to Country
regions_df = regions_df.rename(columns={'GEM Standard Country Name': 'Country'})

# merge regions df onto project_and_field_data based on country
project_and_field_data = project_and_field_data.merge(regions_df[['Country', 'GEM region', 'GEM sub-region']], on='Country', how='left')

print ("merged regions onto main df")

# ===== Cell 11 =====
# for some analysis (e.g. discoveries lists) we want to use the unfiltered field level data. so that data needs to also have regions merged
fields_main_regions = fields_main_df.merge(regions_df[['Country', 'GEM region', 'GEM sub-region']], on='Country', how='left')

print ("merged regions onto field level main df")
# fill in "unknown" status for blank values
fields_main_regions['Status'] = fields_main_regions['Status'].fillna('unknown')

print ("filled in blank status with 'unknown'")

# clean and show
all_field = fields_main_regions.copy()
all_field_row_count = all_field.shape[0]
print(f"all_field has {all_field_row_count} rows")
all_field.head()


# ===== Cell 12 =====
merged_data = project_and_field_data.copy()
# merged data row count
merged_data_row_count = merged_data.shape[0]
print(f"merged data has {merged_data_row_count} rows")
merged_data.head()

# ===== Cell 13 =====
# define year of interest
year_of_interest = 2025
# find 2025 discoveries and fids
disco = merged_data[merged_data['Discovery year'] == year_of_interest]
fid = merged_data[merged_data['FID Year'] == year_of_interest]

#display discovries and FIDs
print(f"{year_of_interest} had {disco.shape[0]} discoveries")
print(f"{year_of_interest} had {fid.shape[0]} fids")

# ===== Cell 14 =====
# sort disco alphabetically
disco = disco.sort_values(by=['Unit Name'])
fid = fid.sort_values(by=['Unit Name'])

disco

# ===== Cell 15 =====
# tag disco as "Discovery or FID" = "discovery"
disco = disco.copy()
fid = fid.copy()

# Filter for field-level entries - discovery
disco_field_level_ids_for_reserves = disco[
    disco['Type'] == 'field-level'
]['Project ID'].dropna().unique()

# Filter for field-level entries - FID
fid_field_level_ids_for_reserves = fid[
    fid['Type'] == 'field-level'
]['Project ID'].dropna().unique()


# Filter field_res using the identified Project IDs - Disvoery
discovery_filtered_field_reserves = field_res[field_res['Project ID'].isin(disco_field_level_ids_for_reserves)]
fid_filtered_field_reserves = field_res[field_res['Project ID'].isin(fid_field_level_ids_for_reserves)]

# Filter for project-level entries
# For project-level entries, 'Unit ID' in disco corresponds to 'Project ID' in proj_res_sum
disco_project_level_ids_for_reserves = disco[
    disco['Type'] == 'project-level'
]['Unit ID'].dropna().unique()

Fid_project_level_ids_for_reserves = fid[
    fid['Type'] == 'project-level'
]['Unit ID'].dropna().unique()

# Filter proj_res_sum using the identified Unit IDs (which are Project IDs in proj_res_sum)
disco_filtered_project_reserves = proj_res[proj_res['Project ID'].isin(disco_project_level_ids_for_reserves)]
fid_filtered_project_reserves = proj_res[proj_res['Project ID'].isin(Fid_project_level_ids_for_reserves)]


# ===== Cell 16 =====
discovery_filtered_field_reserves.to_csv(f'{output_folder}/discovery_filtered_field_reserves_{timestamp}.csv', index=False)
fid_filtered_field_reserves.to_csv(f'{output_folder}/fid_filtered_field_reserves_{timestamp}.csv', index=False)
disco_filtered_project_reserves.to_csv(f'{output_folder}/disco_filtered_project_reserves_{timestamp}.csv', index=False)
fid_filtered_project_reserves.to_csv(f'{output_folder}/fid_filtered_project_reserves_{timestamp}.csv', index=False)

# ### Merging 'Discovery or FID' tags and displaying separated reserves

# ===== Cell 17 =====
display(filtered_project_reserves.head())
