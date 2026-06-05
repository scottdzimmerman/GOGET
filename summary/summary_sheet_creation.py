"""
summary_sheet_creation.py

Migrated from Colab notebook: GOGET Summary Sheet Creation 2026 02 17
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
import re
from datetime import datetime

# Based on the code in https://colab.research.google.com/drive/1c1Y7MHV6f8lEAeb8l0nw1B_d1ETmwVRb#scrollTo=HkstmIhZt2sV
#
# Using the compiled official GOGET download

# #load in needed data and additional libraries

# ===== Cell 3 =====
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
output_folder = '/content/drive/MyDrive/GOGET q1 2026/Summary Tables Draft'

# Load the regional definitions
regions_path = '/content/drive/MyDrive/GOGET Q1 2024/QC Process/Region definitions 2025 02 18 - Region definitions.csv'  # Update this path to your regions file
regions_df = pd.read_csv(regions_path)

# ===== Cell 4 =====
# time stamp for batch
timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

# print time stamp
print(f'this output will tagged as {timestamp}')

# ===== Cell 5 =====
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

# ===== Cell 6 =====
# fill in GEM region and GEM sub-region as unknown if nan on regions_df
regions_df['GEM region'] = regions_df['GEM region'].fillna('Unknown')
regions_df['GEM sub-region'] = regions_df['GEM sub-region'].fillna('Unknown')

#shown countries where region or subregion is unknown
unknown_regions = regions_df[regions_df['GEM region'] == 'Unknown']
print(unknown_regions)

# ===== Cell 7 =====
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

# ===== Cell 8 =====
# tag all entries in projects_main_df as "project"
projects_main_df['Type'] = 'project-level'
main_with_prod_no_project['Type'] = 'field-level'

print ("tagged projects as project or field level")

# replace "Project" in column headers with "Unit" within projects_main_df
projects_main_df.columns = projects_main_df.columns.str.replace('Project', 'Unit')

# Create "Covered_by_Project_Level_Data" as "Is project level"
projects_main_df['Covered_by_Project_Level_Data'] = 'this is the project level'

# ===== Cell 9 =====
# print row count in main_with_prod_no_project and projects_main_df
fields_row_count = main_with_prod_no_project.shape[0]
projects_row_count = projects_main_df.shape[0]
print(f"main_with_prod_no_project has {fields_row_count} rows.")
print(f"project_main_df has {projects_row_count} rows.")
print (f"sum of project and field is {fields_row_count + projects_row_count}")

# ===== Cell 10 =====
# add projects_main_df to main_with_prod_no_project
project_and_field_data = pd.concat([main_with_prod_no_project, projects_main_df], ignore_index=True)

# added project level to the field-level without project

combined_row_count = project_and_field_data.shape[0]
if combined_row_count == (fields_row_count + projects_row_count): print(f"project_and_fields_data has the right number of rows.")
else: print(f"project_and_fields_data does not have the right number of rows")

# ===== Cell 11 =====
# rename GEM Standard Country Name in regions df to Country
regions_df = regions_df.rename(columns={'GEM Standard Country Name': 'Country'})

# merge regions df onto project_and_field_data based on country
project_and_field_data = project_and_field_data.merge(regions_df[['Country', 'GEM region', 'GEM sub-region']], on='Country', how='left')

print ("merged regions onto main df")

# ===== Cell 12 =====
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


# ===== Cell 13 =====
merged_data = project_and_field_data.copy()
# merged data row count
merged_data_row_count = merged_data.shape[0]
print(f"merged data has {merged_data_row_count} rows")
merged_data.head()

# ===== Cell 14 =====
# define regional summary table ideal order
desired_sub_region_row_order = ['Northern America', 'Latin America and the Caribbean', 'Northern Europe', 'Eastern Europe', 'Northern Africa','Sub-Saharan Africa', 'South-eastern Asia', 'Western Europe','Western Asia', 'Southern Asia', 'Australia and New Zealand', 'Eastern Asia', 'Central Asia', 'Southern Europe', 'Melanesia', 'Micronesia', 'Polynesia']

# ===== Cell 15 =====
# define gas bcm to million boe - https://www.bp.com/content/dam/bp/business-sites/en/global/corporate/pdfs/energy-economics/statistical-review/bp-stats-review-2022-approximate-conversion-factors.pdf
gas_bcm_to_boe = 5.883

#
# # Gas Extraction Sites by Region

# ===== Cell 16 =====
# Filter for extraction sites
gas_sites = all_field[all_field['Fuel type'].str.contains('Gas', case=False, na=False)]

# Group by sub-region and status, then count
gas_sites_by_sub_region_status = gas_sites.groupby(['GEM sub-region', 'Status']).size().reset_index(name='Number of Gas Extraction Sites')

# Pivot with status as columns
pivot_table = gas_sites_by_sub_region_status.pivot(index='GEM sub-region', columns='Status', values='Number of Gas Extraction Sites').fillna(0)

# Define the list of status columns that should be combined into 'Other'
statuses_for_other = ['UGS', 'abandoned', 'cancelled', 'decommissioned', 'exploration', 'Unknown']

# Find which of these columns actually exist in the pivot_table
existing_statuses_for_other = [status for status in statuses_for_other if status in pivot_table.columns]

# Initialize 'Other' column with zeros if no existing statuses are found
if not existing_statuses_for_other:
    pivot_table['Other'] = 0
else:
    # Sum the existing columns and assign to 'Other'
    pivot_table['Other'] = pivot_table[existing_statuses_for_other].sum(axis=1)

# Create pivot_table_final by dropping the columns that were combined into 'Other'
# Ensure we only drop columns that actually exist
columns_to_drop = [col for col in statuses_for_other if col in pivot_table.columns]
pivot_table_final = pivot_table.drop(columns=columns_to_drop)

# Calculate GEM region sums and append them to the pivot table
# First, add a column for GEM region to the pivot table for grouping purposes
pivot_table_final['GEM region'] = merged_data.groupby('GEM sub-region')['GEM region'].first()

# Calculate the sums for each GEM region
gem_region_sums = pivot_table_final.groupby('GEM region').sum()

# Prepare the GEM region sums for appending by setting a multi-level index with empty sub-region
gem_region_sums.index = pd.MultiIndex.from_product([gem_region_sums.index, ['Total']], names=['GEM sub-region', 'GEM region'])

# Append the GEM region sums to the original pivot table
final_table_with_region_sums = pd.concat([pivot_table_final.set_index('GEM region', append=True), gem_region_sums]).sort_index()

# Remove the GEM region level for display purposes (optional, for cleaner presentation)
final_table_with_region_sums.index = final_table_with_region_sums.index.droplevel(1)

# add total column to df
final_table_with_region_sums['Total'] = final_table_with_region_sums.sum(axis=1)

# Safely add pre-production (discovered + in development) to df
discovered_col = final_table_with_region_sums['discovered'] if 'discovered' in final_table_with_region_sums.columns else 0
in_development_col = final_table_with_region_sums['in-development'] if 'in-development' in final_table_with_region_sums.columns else 0
final_table_with_region_sums['Pre-production (discovered+ in-development)'] = discovered_col + in_development_col

# Define the desired order of columns
desired_columns = ['discovered', 'in-development', 'Pre-production (discovered+ in-development)', 'operating', 'mothballed', 'Other', 'Total']

# Filter and reorder columns, adding missing ones with 0 if they don't exist
for col in desired_columns:
    if col not in final_table_with_region_sums.columns:
        final_table_with_region_sums[col] = 0

final_table_with_region_sums = final_table_with_region_sums[desired_columns]

# Order by sub_region_order if those sub regions exist
# Filter sub_region_order to include only regions present in the DataFrame's index
present_sub_regions = [sr for sr in desired_sub_region_row_order if sr in final_table_with_region_sums.index]

# Get any 'Total' rows from the index that are not part of the sub_region_order
total_rows = [idx for idx in final_table_with_region_sums.index if 'Total' in idx]

# Combine the ordered sub-regions with the total rows
ordered_index = present_sub_regions + total_rows

# Reindex the DataFrame
final_table_with_region_sums = final_table_with_region_sums.reindex(ordered_index)

# Display the final table
print(final_table_with_region_sums.head())

# print total count
print('total gas extraction count =' + str(final_table_with_region_sums['Total'].sum()))

# Save the table with GEM region sums
output_filename = output_folder + f'/Gas Extraction Sites by Region and Total{timestamp}.csv'

final_table_with_region_sums.to_csv(output_filename)
print(f"File saved as {output_filename}")

# # Gas Extraction Sites by Country

# ===== Cell 17 =====
# Filter for extraction sites, assuming this has already been done for gas sites
# If you're starting fresh, ensure you have a filtered dataframe for gas extraction sites

# Group by "Country" and "Status", then count
gas_sites_by_country_status = gas_sites.groupby(['Country', 'GEM sub-region', 'Status']).size().reset_index(name='Number of Gas Extraction Sites')

# Pivot with status as columns
pivot_country = gas_sites_by_country_status.pivot(index='Country', columns='Status', values='Number of Gas Extraction Sites').fillna(0)

# for QC, keep region in, comment out for final versions
# Group by "Country" and "Status", then count (keep Sub-region)
gas_sites_by_country_status = gas_sites.groupby(['Country', 'GEM sub-region', 'Status']).size().reset_index(name='Number of Gas Extraction Sites')

# Pivot with status as columns, keep Sub-region as an index level
pivot_country = gas_sites_by_country_status.pivot_table(
    index=['Country', 'GEM sub-region'],  # Include Sub-region in the index
    columns='Status',
    values='Number of Gas Extraction Sites',
    fill_value=0
)

# Define the list of status columns that should be combined into 'Other'
statuses_for_other_country = ['UGS', 'exploration', 'abandoned', 'cancelled', 'decommissioned','Unknown']

# Find which of these columns actually exist in the pivot_country
existing_statuses_for_other_country = [status for status in statuses_for_other_country if status in pivot_country.columns]

# Initialize 'Other' column with zeros if no existing statuses are found
if not existing_statuses_for_other_country:
    pivot_country['Other'] = 0
else:
    # Sum the existing columns and assign to 'Other'
    pivot_country['Other'] = pivot_country[existing_statuses_for_other_country].sum(axis=1)

# Create pivot_country_final by dropping the columns that were combined into 'Other'
# Ensure we only drop columns that actually exist
columns_to_drop_country = [col for col in statuses_for_other_country if col in pivot_country.columns]
pivot_country_final = pivot_country.drop(columns=columns_to_drop_country)

# Calculate the total number of sites for each country
pivot_country_final['Total'] = pivot_country_final.sum(axis=1)

# Safely add pre-production (discovered + in-development) to df
discovered_col_country = pivot_country_final['discovered'] if 'discovered' in pivot_country_final.columns else 0
in_development_col_country = pivot_country_final['in-development'] if 'in-development' in pivot_country_final.columns else 0
pivot_country_final['Pre-production (discovered+ in-development)'] = discovered_col_country + in_development_col_country

# Define the desired order of columns
desired_columns_country = ['discovered', 'in-development', 'Pre-production (discovered+ in-development)', 'operating', 'mothballed', 'Other', 'Total']

# Filter and reorder columns, adding missing ones with 0 if they don't exist
for col in desired_columns_country:
    if col not in pivot_country_final.columns:
        pivot_country_final[col] = 0

pivot_country_final = pivot_country_final[desired_columns_country]

# Display the final table
print(pivot_country_final.head())

# print totals
print('total gas extraction count =' + str(pivot_country_final['Total'].sum()))

# Generate a filename with timestamp for saving the output
output_filename_country = f'{output_folder}/Gas Extraction Sites by Country {timestamp}.csv'

# Save the DataFrame to CSV
pivot_country_final.to_csv(output_filename_country)

print(f"File saved as {output_filename_country}")

# # Gas, Oil and Hydrocarbon Production by country/Area

# ===== Cell 18 =====
# create total production sheet

# Group by 'Country/Area' and sum the specified columns
production_by_country = merged_data.groupby('Country').agg(
    {'million m³/y': lambda x: x.sum() / 1000,  # Convert to bcm during summation
     'million bbl/y': 'sum',
     'million boe/y': 'sum',
     'GEM sub-region': 'first'} # added for QC - found missing country from regional data
)

# Rename the columns
production_by_country = production_by_country.rename(columns={
    'million m³/y': 'Gas Production (bcm/y)',
    'million bbl/y': 'Oil Production (million bbl/y)',
    'million boe/y': 'Unspecified Hydrocarbons Production (million boe/y)'
})

# gas production in million boe
production_by_country['Gas Production (million boe/y)'] = production_by_country['Gas Production (bcm/y)']*gas_bcm_to_boe # per SWRE

# create total production
production_by_country['Total Production (million boe/y)'] = production_by_country['Gas Production (million boe/y)'] + production_by_country['Oil Production (million bbl/y)'] + production_by_country['Unspecified Hydrocarbons Production (million boe/y)']

# Sort by Total Production (million boe/y) in descending order
production_by_country = production_by_country.sort_values(by='Total Production (million boe/y)', ascending=False)

# Display the result
print(production_by_country)

# print total production
print('total production =' + str(production_by_country['Total Production (million boe/y)'].sum()))

# Save the result to a CSV file (optional)
output_filename = f'{output_folder}/Production_by_Country_{timestamp}.csv'
production_by_country.to_csv(output_filename)
print(f"File saved as {output_filename}")

# # Gas, Oil and Hydrocarbon Production by Region

# ===== Cell 19 =====
# create total production

# Group by 'GEM region' and sum the specified columns
production_by_region = merged_data.groupby('GEM sub-region').agg(
    {'million m³/y': lambda x: x.sum() / 1000,  # Convert to bcm during summation
     'million bbl/y': 'sum',
     'million boe/y': 'sum',
     'GEM region': 'first'} # added for QC - found missing country from regional data
)

# Rename the columns
production_by_region = production_by_region.rename(columns={
    'million m³/y': 'Gas Production (bcm/y)',
    'million bbl/y': 'Oil Production (million bbl/y)',
    'million boe/y': 'Unspecified Hydrocarbons Production (million boe/y)'
})

# gas production in million boe
production_by_region['Gas Production (million boe/y)'] = production_by_region['Gas Production (bcm/y)']*gas_bcm_to_boe # per SWRE

# create total production
production_by_region['Total Production (million boe/y)'] = production_by_region['Gas Production (million boe/y)'] + production_by_region['Oil Production (million bbl/y)'] + production_by_region['Unspecified Hydrocarbons Production (million boe/y)']

# Calculate GEM region sums
gem_region_sums = production_by_region.groupby('GEM region').sum()

# Prepare GEM region sums for appending by setting a multi-level index with empty sub-region
gem_region_sums.index = pd.MultiIndex.from_product([gem_region_sums.index, ['Total']], names=['GEM sub-region', 'GEM Region'])

# Append GEM region sums to the original DataFrame
production_by_region_with_totals = pd.concat([production_by_region.set_index('GEM region', append=True), gem_region_sums]).sort_index()

# Remove GEM region level for display purposes (optional)
production_by_region_with_totals.index = production_by_region_with_totals.index.droplevel(1)


# Sort by Total Production (million boe/y) in descending order
production_by_region_with_totals = production_by_region_with_totals.sort_values(by='Total Production (million boe/y)', ascending=False)


# Display the result
print(production_by_region_with_totals)
print('total production =' + str(production_by_region_with_totals['Total Production (million boe/y)'].sum()/2))

# Save the result to a CSV file (optional)
output_filename = f'{output_folder}/Production_by_Region_{timestamp}.csv'
production_by_region_with_totals.to_csv(output_filename)
print(f"File saved as {output_filename}")

# # Onshore/ Offshore Production

# ===== Cell 20 =====
# missing regional tag of South-eastern Asia for Vietnam-Malaysia - manually added in so totals match on two sheets.
# Group by 'Onshore/Offshore' and sum the specified columns
production_by_location = merged_data.groupby('Onshore/Offshore').agg(
    {'million m³/y': lambda x: x.sum() / 1000,  # Convert to bcm during summation
     'million bbl/y': 'sum',
     'million boe/y': 'sum'}
)

# Rename the columns within production_by_location
production_by_location = production_by_location.rename(columns={
    'million m³/y': 'Gas Production (bcm)',
    'million bbl/y': 'Oil Production (million bbl/y)',
    'million boe/y': 'Unspecified Hydrocarbons Production (million boe/y)'
})

# gas production in million boe
production_by_location['Gas Production (million boe/y)'] = production_by_location['Gas Production (bcm)'] * gas_bcm_to_boe

# create total production
production_by_location['Total Production (million boe/y)'] = \
    production_by_location['Gas Production (million boe/y)'] + \
    production_by_location['Oil Production (million bbl/y)'] + \
    production_by_location['Unspecified Hydrocarbons Production (million boe/y)']

# Sort by Total Production (million boe/y) in descending order
production_by_location = production_by_location.sort_values(by='Total Production (million boe/y)', ascending=False)


# Display the result
print(production_by_location)
print('total production =' + str(production_by_location['Total Production (million boe/y)'].sum()))

# Save the result to a CSV file (optional)
output_filename = f'{output_folder}/Production_by_location_{timestamp}.csv'
production_by_location.to_csv(output_filename)
print(f"File saved as {output_filename}")

# # Gas, Oil and Hydrocarbon Areas by production location per region

# ===== Cell 21 =====
# prompt: Count "Onshore/Offshore" units per each region in merged_data

# Count "Onshore/Offshore" units per each region in merged_data
onshore_offshore_counts = all_field.groupby(['GEM sub-region', 'Onshore/Offshore']).size().unstack(fill_value=0)

# Display the result
print(onshore_offshore_counts)
print('total Onshore count =' + str(onshore_offshore_counts['onshore'].sum()))
print('total Offshore count =' + str(onshore_offshore_counts['offshore'].sum()))

# Save the result to a CSV file (optional)
output_filename = f'{output_folder}/Onshore_Offshore_Counts_by_Region_{timestamp}.csv'
onshore_offshore_counts.to_csv(output_filename)
print(f"File saved as {output_filename}")

# # Gas, Oil, and Hydrocarbon Areas discoveries by production location (onshore/offshore)

# ===== Cell 22 =====
# Filter for extraction sites where Fuel type indicates oil, gas, or oil and gas
oil_gas_sites = all_field[all_field['Fuel type'].str.contains('Oil|Gas', case=False, na=False)]

# Convert discovery year to integers, ignore errors and fill NaN with -1 (indicating missing data)
oil_gas_sites['Discovery year'] = pd.to_numeric(oil_gas_sites['Discovery year'], errors='coerce').fillna(-1).astype(int)

# Filter for rows where discovery year is not -1, indicating a valid discovery year
oil_gas_sites_valid_disc = oil_gas_sites[oil_gas_sites['Discovery year'] > 0]

# Group by "Onshore/Offshore" and "Discovery year", then count the number of sites for each combination
offshore_year_counts = oil_gas_sites_valid_disc.groupby(['Onshore/Offshore', 'Discovery year']).size().reset_index(name='Number of Sites')

# Pivot the table so each row is a "GEM sub-region" and each column is a "Discovery year", with values being the "Number of Sites"
pivot_sub_offshore_year = offshore_year_counts.pivot_table(index='Onshore/Offshore', columns='Discovery year', values='Number of Sites', fill_value=0)

# Convert column names back to integers if they are not already
pivot_sub_offshore_year.columns = pivot_sub_offshore_year.columns.astype(int)

# Identify columns representing years before 2016
columns_before_2016 = [col for col in pivot_sub_offshore_year.columns if col < 2016]

# Add a new column for the sum of sites discovered before 2016, using the identified columns
pivot_sub_offshore_year['Before 2016'] = pivot_sub_offshore_year[columns_before_2016].sum(axis=1)

# Optional, drop the columns for years before 2016
# pivot_sub_offshore_year_modified = pivot_sub_offshore_year.drop(columns=columns_before_2016)
pivot_sub_offshore_year_modified = pivot_sub_offshore_year # replace with comment above to keep drop

# Generate a filename with timestamp for saving the output
output_filename = f'{output_folder}/Onshore_Offshore Discovery Year Counts {timestamp}.csv'


# Save the modified DataFrame to CSV
pivot_sub_offshore_year_modified.to_csv(output_filename, index=True)

print(pivot_sub_offshore_year_modified.head())

print(f"File saved as {output_filename}")

# # Oil Extraction Sites by Region

# ===== Cell 23 =====
# Filter for oil extraction sites (assuming 'Fuel type' indicates oil)
oil_sites = all_field[all_field['Fuel type'].str.contains('Oil', case=False, na=False)]

# Group by "GEM sub-region" and "Status", then count
oil_sites_by_region_status = oil_sites.groupby(['GEM sub-region', 'Status']).size().reset_index(name='Number of Oil Extraction Sites')

# Pivot with status as columns
pivot_oil_region = oil_sites_by_region_status.pivot_table(index='GEM sub-region', columns='Status', values='Number of Oil Extraction Sites', fill_value=0)

# Define the list of status columns that should be combined into 'Other'
statuses_for_other_oil = ['UGS', 'abandoned', 'cancelled', 'decommissioned', 'exploration', 'Unknown']

# Find which of these columns actually exist in the pivot_oil_region
existing_statuses_for_other_oil = [status for status in statuses_for_other_oil if status in pivot_oil_region.columns]

# Initialize 'Other' column with zeros if no existing statuses are found
if not existing_statuses_for_other_oil:
    pivot_oil_region['Other'] = 0
else:
    # Sum the existing columns and assign to 'Other'
    pivot_oil_region['Other'] = pivot_oil_region[existing_statuses_for_other_oil].sum(axis=1)

# Drop the original columns now combined into 'Other'
columns_to_drop_oil = [col for col in statuses_for_other_oil if col in pivot_oil_region.columns]
pivot_oil_region_final = pivot_oil_region.drop(columns=columns_to_drop_oil)

# Add a column for GEM region to the pivot table for grouping purposes
# Get GEM region from merged_data based on GEM sub-region
pivot_oil_region_final['GEM region'] = merged_data.groupby('GEM sub-region')['GEM region'].first()

# Calculate the sums for each GEM region
gem_region_sums_oil = pivot_oil_region_final.groupby('GEM region').sum()

# Prepare the GEM region sums for appending by setting a multi-level index with empty sub-region
gem_region_sums_oil.index = pd.MultiIndex.from_product([gem_region_sums_oil.index, ['Total']], names=['GEM sub-region', 'GEM region'])

# Append the GEM region sums to the original pivot table
final_table_with_region_sums_oil = pd.concat([pivot_oil_region_final.set_index('GEM region', append=True), gem_region_sums_oil]).sort_index()

# Remove the GEM region level for display purposes (optional, for cleaner presentation)
final_table_with_region_sums_oil.index = final_table_with_region_sums_oil.index.droplevel(1)

# add total column to df
final_table_with_region_sums_oil['Total'] = final_table_with_region_sums_oil.sum(axis=1)

# Safely add pre-production (discovered + in development) to df
discovered_oil_col = final_table_with_region_sums_oil['discovered'] if 'discovered' in final_table_with_region_sums_oil.columns else 0
in_development_oil_col = final_table_with_region_sums_oil['in-development'] if 'in-development' in final_table_with_region_sums_oil.columns else 0
final_table_with_region_sums_oil['Pre-production (discovered+ in-development)'] = discovered_oil_col + in_development_oil_col

# Define the desired order of columns
desired_columns_oil = ['discovered', 'in-development', 'Pre-production (discovered+ in-development)', 'operating', 'mothballed', 'Other', 'Total']

# Filter and reorder columns, adding missing ones with 0 if they don't exist
for col in desired_columns_oil:
    if col not in final_table_with_region_sums_oil.columns:
        final_table_with_region_sums_oil[col] = 0

final_table_with_region_sums_oil = final_table_with_region_sums_oil[desired_columns_oil]

# Order by sub_region_order if those sub regions exist
# Filter sub_region_order to include only regions present in the DataFrame's index
present_sub_regions_oil = [sr for sr in desired_sub_region_row_order if sr in final_table_with_region_sums_oil.index]

# Get any 'Total' rows from the index that are not part of the sub_region_order
total_rows_oil = [idx for idx in final_table_with_region_sums_oil.index if 'Total' in idx]

# Combine the ordered sub-regions with the total rows
ordered_index_oil = present_sub_regions_oil + total_rows_oil

# Reindex the DataFrame
final_table_with_region_sums_oil = final_table_with_region_sums_oil.reindex(ordered_index_oil)

# Display the sorted final table
print(final_table_with_region_sums_oil.head())

# Generate a filename with timestamp for saving the output
output_filename_oil_count_region_status = f'{output_folder}/Oil extraction sites by region and Status {timestamp}.csv'

# Save the DataFrame to CSV
final_table_with_region_sums_oil.to_csv(output_filename_oil_count_region_status, index=True)

print(f"File saved as {output_filename_oil_count_region_status}")
print('total oil extraction count =' + str(final_table_with_region_sums_oil['Total'].sum()))

# # Oil Extraction site by country

# ===== Cell 24 =====
# Filter for extraction sites, assuming this has already been done for gas sites
# If you're starting fresh, ensure you have a filtered dataframe for gas extraction sites

# Group by "Country" and "Status", then count
oil_sites_by_country_status = oil_sites.groupby(['Country', 'GEM sub-region', 'Status']).size().reset_index(name='Number of Oil Extraction Sites')

# Pivot with status as columns
pivot_country = oil_sites_by_country_status.pivot(index='Country', columns='Status', values='Number of Oil Extraction Sites').fillna(0)

# for QC, keep region in, comment out for final versions
# Group by "Country" and "Status", then count (keep Sub-region)
oil_sites_by_country_status = oil_sites.groupby(['Country', 'GEM sub-region', 'Status']).size().reset_index(name='Number of Oil Extraction Sites')

# Pivot with status as columns, keep Sub-region as an index level
pivot_country = oil_sites_by_country_status.pivot_table(
    index=['Country', 'GEM sub-region'],  # Include Sub-region in the index
    columns='Status',
    values='Number of Oil Extraction Sites',
    fill_value=0
)

# Define the list of status columns that should be combined into 'Other'
statuses_for_other_country = ['UGS', 'exploration', 'abandoned', 'cancelled', 'decommissioned','Unknown']

# Find which of these columns actually exist in the pivot_country
existing_statuses_for_other_country = [status for status in statuses_for_other_country if status in pivot_country.columns]

# Initialize 'Other' column with zeros if no existing statuses are found
if not existing_statuses_for_other_country:
    pivot_country['Other'] = 0
else:
    # Sum the existing columns and assign to 'Other'
    pivot_country['Other'] = pivot_country[existing_statuses_for_other_country].sum(axis=1)

# Create pivot_country_final by dropping the columns that were combined into 'Other'
# Ensure we only drop columns that actually exist
columns_to_drop_country = [col for col in statuses_for_other_country if col in pivot_country.columns]
pivot_country_final = pivot_country.drop(columns=columns_to_drop_country)

# Calculate the total number of sites for each country
pivot_country_final['Total'] = pivot_country_final.sum(axis=1)

# Safely add pre-production (discovered + in-development) to df
discovered_col_country = pivot_country_final['discovered'] if 'discovered' in pivot_country_final.columns else 0
in_development_col_country = pivot_country_final['in-development'] if 'in-development' in pivot_country_final.columns else 0
pivot_country_final['Pre-production (discovered+ in-development)'] = discovered_col_country + in_development_col_country

# Define the desired order of columns
desired_columns_country = ['discovered', 'in-development', 'Pre-production (discovered+ in-development)', 'operating', 'mothballed', 'Other', 'Total']

# Filter and reorder columns, adding missing ones with 0 if they don't exist
for col in desired_columns_country:
    if col not in pivot_country_final.columns:
        pivot_country_final[col] = 0

pivot_country_final = pivot_country_final[desired_columns_country]

# Display the final table
print(pivot_country_final.head())

# print totals
print('total oil extraction count =' + str(pivot_country_final['Total'].sum()))

# Generate a filename with timestamp for saving the output
output_filename_country = f'{output_folder}/Oil Extraction Sites by Country {timestamp}.csv'

# Save the DataFrame to CSV
pivot_country_final.to_csv(output_filename_country)

print(f"File saved as {output_filename_country}")

# # Oil and gas Extraction Sites by Region
#
#

# ===== Cell 25 =====
# Filter for extraction sites where Fuel type indicates oil, gas, or oil and gas
oil_gas_sites = all_field[all_field['Fuel type'].str.contains('Oil|Gas|condensate|ngl', case=False, na=False)]

# Group by "GEM sub-region" and "Status", then count
oil_gas_sites_by_region_status = oil_gas_sites.groupby(['GEM sub-region', 'Status']).size().reset_index(name='Number of Extraction Sites')

# Pivot with status as columns
pivot_oil_gas_region = oil_gas_sites_by_region_status.pivot_table(index='GEM sub-region', columns='Status', values='Number of Extraction Sites', fill_value=0)

# Define the list of status columns that should be combined into 'Other'
statuses_for_other_all_fuel = ['UGS', 'abandoned', 'cancelled', 'decommissioned', 'exploration', 'Unknown']

# Find which of these columns actually exist in the pivot_oil_gas_region
existing_statuses_for_other_all_fuel = [status for status in statuses_for_other_all_fuel if status in pivot_oil_gas_region.columns]

# Initialize 'Other' column with zeros if no existing statuses are found
if not existing_statuses_for_other_all_fuel:
    pivot_oil_gas_region['Other'] = 0
else:
    # Sum the existing columns and assign to 'Other'
    pivot_oil_gas_region ['Other'] = pivot_oil_gas_region [existing_statuses_for_other_all_fuel].sum(axis=1)

# Drop the original columns now combined into 'Other'
columns_to_drop_all_fuel = [col for col in statuses_for_other_all_fuel if col in pivot_oil_gas_region.columns]
pivot_oil_gas_region_final = pivot_oil_gas_region.drop(columns=columns_to_drop_all_fuel)

# Add a column for GEM region to the pivot table for grouping purposes
# Get GEM region from merged_data based on GEM sub-region
pivot_oil_gas_region_final['GEM region'] = merged_data.groupby('GEM sub-region')['GEM region'].first()

# Calculate the sums for each GEM region
gem_region_sums_all_fuel = pivot_oil_gas_region_final.groupby('GEM region').sum()

# Prepare the GEM region sums for appending by setting a multi-level index with empty sub-region
gem_region_sums_all_fuel.index = pd.MultiIndex.from_product([gem_region_sums_all_fuel.index, ['Total']], names=['GEM sub-region', 'GEM region'])

# Append the GEM region sums to the original pivot table
final_table_all_fuel_with_region_sums = pd.concat([pivot_oil_gas_region_final.set_index('GEM region', append=True), gem_region_sums_all_fuel]).sort_index()

# Remove the GEM region level for display purposes (optional, for cleaner presentation)
final_table_all_fuel_with_region_sums.index = final_table_all_fuel_with_region_sums.index.droplevel(1)

# add total column to df
final_table_all_fuel_with_region_sums['Total'] = final_table_all_fuel_with_region_sums.sum(axis=1)

# add pre production total
discovered_all_fuel_col = final_table_all_fuel_with_region_sums['discovered'] if 'discovered' in final_table_all_fuel_with_region_sums.columns else 0
in_development_all_fuel_col = final_table_all_fuel_with_region_sums['in-development'] if 'in-development' in final_table_all_fuel_with_region_sums.columns else 0
final_table_all_fuel_with_region_sums['Pre-production (discovered+ in-development)'] = discovered_all_fuel_col + in_development_all_fuel_col

# sort columns
desired_columns_all_fuel = ['discovered', 'in-development', 'Pre-production (discovered+ in-development)', 'operating', 'mothballed', 'Other', 'Total']

# Filter and reorder columns, adding missing ones with 0 if they don't exist
for col in desired_columns_all_fuel:
    if col not in final_table_all_fuel_with_region_sums.columns:
        final_table_all_fuel_with_region_sums[col] = 0

final_table_all_fuel_with_region_sums = final_table_all_fuel_with_region_sums[desired_columns_all_fuel]

# Order by sub_region_order if those sub regions exist
# Filter sub_region_order to include only regions present in the DataFrame's index
present_sub_regions_all_fuel = [sr for sr in desired_sub_region_row_order if sr in final_table_all_fuel_with_region_sums.index]

# Get any 'Total' rows from the index that are not part of the sub_region_order
total_rows_all_fuel = [idx for idx in final_table_all_fuel_with_region_sums.index if 'Total' in idx]

# Combine the ordered sub-regions with the total rows
ordered_index_all_fuel = present_sub_regions_all_fuel + total_rows_all_fuel

# Reindex the DataFrame
final_table_all_fuel_with_region_sums = final_table_all_fuel_with_region_sums.reindex(ordered_index_all_fuel)

# Print the result
print(final_table_all_fuel_with_region_sums.head())

# Generate a filename with timestamp for saving the output
output_filename_oil_gas_region_status = f'{output_folder}/All extraction sites by region and status {timestamp}.csv'

# Save the DataFrame to CSV
final_table_all_fuel_with_region_sums.to_csv(output_filename_oil_gas_region_status, index=True)

print(f"File saved as {output_filename_oil_gas_region_status}")
print('total oil and gas extraction count =' + str(final_table_all_fuel_with_region_sums['Total'].sum()))

# # Oil and gas Sites by Country

# ===== Cell 26 =====
# Filter for extraction sites, assuming this has already been done for gas sites
# If you're starting fresh, ensure you have a filtered dataframe for gas extraction sites

# Group by "Country" and "Status", then count
oil_gas_sites_by_country_status = oil_gas_sites.groupby(['Country', 'GEM sub-region', 'Status']).size().reset_index(name='Number of Extraction Sites')

# Pivot with status as columns
pivot_country = oil_gas_sites_by_country_status.pivot(index='Country', columns='Status', values='Number of Extraction Sites').fillna(0)

# for QC, keep region in, comment out for final versions
# Group by "Country" and "Status", then count (keep Sub-region)
oil_gas_sites_by_country_status = oil_gas_sites.groupby(['Country', 'GEM sub-region', 'Status']).size().reset_index(name='Number of Extraction Sites')

# Pivot with status as columns, keep Sub-region as an index level
pivot_country = oil_gas_sites_by_country_status.pivot_table(
    index=['Country', 'GEM sub-region'],  # Include Sub-region in the index
    columns='Status',
    values='Number of Extraction Sites',
    fill_value=0
)

# Define the list of status columns that should be combined into 'Other'
statuses_for_other_country = ['UGS', 'exploration', 'abandoned', 'cancelled', 'decommissioned','Unknown']

# Find which of these columns actually exist in the pivot_country
existing_statuses_for_other_country = [status for status in statuses_for_other_country if status in pivot_country.columns]

# Initialize 'Other' column with zeros if no existing statuses are found
if not existing_statuses_for_other_country:
    pivot_country['Other'] = 0
else:
    # Sum the existing columns and assign to 'Other'
    pivot_country['Other'] = pivot_country[existing_statuses_for_other_country].sum(axis=1)

# Create pivot_country_final by dropping the columns that were combined into 'Other'
# Ensure we only drop columns that actually exist
columns_to_drop_country = [col for col in statuses_for_other_country if col in pivot_country.columns]
pivot_country_final = pivot_country.drop(columns=columns_to_drop_country)

# Calculate the total number of sites for each country
pivot_country_final['Total'] = pivot_country_final.sum(axis=1)

# Safely add pre-production (discovered + in-development) to df
discovered_col_country = pivot_country_final['discovered'] if 'discovered' in pivot_country_final.columns else 0
in_development_col_country = pivot_country_final['in-development'] if 'in-development' in pivot_country_final.columns else 0
pivot_country_final['Pre-production (discovered+ in-development)'] = discovered_col_country + in_development_col_country

# Define the desired order of columns
desired_columns_country = ['discovered', 'in-development', 'Pre-production (discovered+ in-development)', 'operating', 'mothballed', 'Other', 'Total']

# Filter and reorder columns, adding missing ones with 0 if they don't exist
for col in desired_columns_country:
    if col not in pivot_country_final.columns:
        pivot_country_final[col] = 0

pivot_country_final = pivot_country_final[desired_columns_country]

# Display the final table
print(pivot_country_final.head())

# print totals
print('total oil and gas extraction count =' + str(pivot_country_final['Total'].sum()))

# Generate a filename with timestamp for saving the output
output_filename_country = f'{output_folder}/All Extraction Sites by Country {timestamp}.csv'

# Save the DataFrame to CSV
pivot_country_final.to_csv(output_filename_country)

print(f"File saved as {output_filename_country}")

# # Discoveries per Year by Region

# ===== Cell 27 =====
# Filter for extraction sites where Fuel type indicates oil, gas, or oil and gas
oil_gas_sites = all_field[all_field['Fuel type'].str.contains('Oil|Gas', case=False, na=False)]

# Convert discovery year to integers, ignore errors and fill NaN with -1 (indicating missing data)
oil_gas_sites['Discovery year'] = pd.to_numeric(oil_gas_sites['Discovery year'], errors='coerce').fillna(-1).astype(int)

# Filter for rows where discovery year is not -1, indicating a valid discovery year
oil_gas_sites_valid_disc = oil_gas_sites[oil_gas_sites['Discovery year'] > 0]

# Group by "GEM sub-region" and "Discovery year", then count the number of sites for each combination
sub_region_year_counts = oil_gas_sites_valid_disc.groupby(['GEM sub-region', 'Discovery year']).size().reset_index(name='Number of Sites')

# Pivot the table so each row is a "GEM sub-region" and each column is a "Discovery year", with values being the "Number of Sites"
pivot_sub_region_year = sub_region_year_counts.pivot_table(index='GEM sub-region', columns='Discovery year', values='Number of Sites', fill_value=0)

# Convert column names back to integers if they are not already
pivot_sub_region_year.columns = pivot_sub_region_year.columns.astype(int)

# Identify columns representing years before 2016
columns_before_2016 = [col for col in pivot_sub_region_year.columns if col < 2016]

# Add a new column for the sum of sites discovered before 2016, using the identified columns
pivot_sub_region_year['Before 2016'] = pivot_sub_region_year[columns_before_2016].sum(axis=1)

# Now, drop the columns for years before 2016
pivot_sub_region_year_modified = pivot_sub_region_year.drop(columns=columns_before_2016)

# Generate a filename with timestamp for saving the output
output_filename_sub_region_year = f'{output_folder}/discoyearregion {timestamp}.csv'

# Save the modified DataFrame to CSV
pivot_sub_region_year_modified.to_csv(output_filename_sub_region_year, index=True)

print(pivot_sub_region_year_modified.head())

print(f"File saved as {output_filename_sub_region_year}")

# # Discoveries per Year by Country

# ===== Cell 28 =====
# Filter for extraction sites where Fuel type indicates oil, gas, or oil and gas
oil_gas_sites = all_field[all_field['Fuel type'].str.contains('Oil|Gas', case=False, na=False)]

# Convert discovery year to integers, ignore errors and fill NaN with -1 (indicating missing data)
oil_gas_sites['Discovery year'] = pd.to_numeric(oil_gas_sites['Discovery year'], errors='coerce').fillna(-1).astype(int)

# Filter for rows where discovery year is not -1, indicating a valid discovery year
oil_gas_sites_valid_disc = oil_gas_sites[oil_gas_sites['Discovery year'] > 0]

# Group by "Country" and "Discovery year", then count the number of sites for each combination
country_year_counts = oil_gas_sites_valid_disc.groupby(['Country', 'Discovery year']).size().reset_index(name='Number of Sites')

# Pivot the table so each row is a "Country" and each column is a "Discovery year", with values being the "Number of Sites"
pivot_country_year = country_year_counts.pivot_table(index='Country', columns='Discovery year', values='Number of Sites', fill_value=0)

# Convert column names back to integers if they are not already
pivot_country_year.columns = pivot_country_year.columns.astype(int)

# Identify columns representing years before 2016
columns_before_2016 = [col for col in pivot_country_year.columns if col < 2016]

# Add a new column for the sum of sites discovered before 2016, using the identified columns
pivot_country_year['Before 2016'] = pivot_country_year[columns_before_2016].sum(axis=1)

# Now, drop the columns for years before 2016
pivot_country_year_modified = pivot_country_year.drop(columns=columns_before_2016)

# Generate a filename with timestamp for saving the output
output_filename_country_year = f'{output_folder}/discoyearcountry {timestamp}.csv'

# Save the modified DataFrame to CSV
pivot_country_year_modified.to_csv(output_filename_country_year, index=True)

print(pivot_country_year_modified.head())

print(f"File saved as {output_filename_country_year}")

# # FID by Year and Region

# ===== Cell 29 =====
# Filter for extraction sites where Fuel type indicates oil, gas, or oil and gas
oil_gas_sites =all_field[all_field['Fuel type'].str.contains('Oil|Gas', case=False, na=False)]

# Convert FID year to integers, ignore errors and fill NaN with -1 (indicating missing data)
oil_gas_sites['FID Year'] = pd.to_numeric(oil_gas_sites['FID Year'], errors='coerce').fillna(-1).astype(int)

# Filter for rows where FID year is not -1, indicating a valid FID year
oil_gas_sites_valid_FID = oil_gas_sites[oil_gas_sites['FID Year'] > 0]

# Group by "GEM sub-region" and "FID Year", then count the number of sites for each combination
sub_region_year_counts_FID = oil_gas_sites_valid_FID.groupby(['GEM sub-region', 'FID Year']).size().reset_index(name='Number of Sites')

# Pivot the table so each row is a "GEM sub-region" and each column is a "FID Year", with values being the "Number of Sites"
pivot_sub_region_year_FID = sub_region_year_counts_FID.pivot_table(index='GEM sub-region', columns='FID Year', values='Number of Sites', fill_value=0)

# Convert column names back to integers if they are not already
pivot_sub_region_year_FID.columns = pivot_sub_region_year_FID.columns.astype(int)

# Identify columns representing years before 2016
columns_before_2016 = [col for col in pivot_sub_region_year_FID.columns if col < 2016]

# Add a new column for the sum of sites discovered before 2016, using the identified columns
pivot_sub_region_year_FID['Before 2016'] = pivot_sub_region_year_FID[columns_before_2016].sum(axis=1)

# Now, drop the columns for years before 2016
pivot_sub_region_year_FID_modified = pivot_sub_region_year_FID.drop(columns=columns_before_2016)

# Generate a filename with timestamp for saving the output
output_filename_sub_region_FID_year = f'{output_folder}/fid_year_region {timestamp}.csv'

# Save the modified DataFrame to CSV
pivot_sub_region_year_FID_modified.to_csv(output_filename_sub_region_FID_year, index=True)

# Correctly print the first few rows of the modified DataFrame
print(pivot_sub_region_year_FID_modified.head())

print(f"File saved as {output_filename_sub_region_FID_year}")

# # Count of FIDs by Year and Country

# ===== Cell 30 =====
# Filter for extraction sites where Fuel type indicates oil, gas, or oil and gas
oil_gas_sites = all_field[all_field['Fuel type'].str.contains('Oil|Gas', case=False, na=False)]

# Convert FID year to integers, ignore errors and fill NaN with -1 (indicating missing data)
oil_gas_sites['FID Year'] = pd.to_numeric(oil_gas_sites['FID Year'], errors='coerce').fillna(-1).astype(int)

# Filter for rows where FID year is not -1, indicating a valid FID year
oil_gas_sites_valid_FID = oil_gas_sites[oil_gas_sites['FID Year'] > 0]

# Group by "Country" and "FID Year", then count the number of sites for each combination
Country_year_counts_FID = oil_gas_sites_valid_FID.groupby(['Country', 'FID Year']).size().reset_index(name='Number of Sites')

# Pivot the table so each row is a "Country" and each column is a "FID Year", with values being the "Number of Sites"
pivot_Country_year_FID = Country_year_counts_FID.pivot_table(index='Country', columns='FID Year', values='Number of Sites', fill_value=0)

# Convert column names back to integers if they are not already
pivot_Country_year_FID.columns = pivot_Country_year_FID.columns.astype(int)

# Identify columns representing years before 2016
columns_before_2016 = [col for col in pivot_Country_year_FID.columns if col < 2016]

# Add a new column for the sum of sites discovered before 2016, using the identified columns
pivot_Country_year_FID['Before 2016'] = pivot_Country_year_FID[columns_before_2016].sum(axis=1)

# Now, drop the columns for years before 2016
pivot_Country_year_FID_modified = pivot_Country_year_FID.drop(columns=columns_before_2016)

# Generate a filename with timestamp for saving the output
output_filename_country_FID_year = f'{output_folder}/fid_year_country {timestamp}.csv'

# Save the modified DataFrame to CSV
pivot_Country_year_FID_modified.to_csv(output_filename_country_FID_year, index=True)

# Correctly print the first few rows of the modified DataFrame
print(pivot_Country_year_FID_modified.head())

print(f"File saved as {output_filename_country_FID_year}")

# # Site count (oil and gas) by parent company and status

# ===== Cell 31 =====
# rename Parent(s) to Parent, so old code works
all_field['Parent'] = all_field['Parent(s)']

# ===== Cell 32 =====
def summarize_site_counts_by_company(merged_data):
    """
    Summarizes oil and gas site counts by parent company and status,
    grouping companies with fewer than 50 sites into a single row.

    Args:
        merged_data: DataFrame containing the oil and gas site data.

    Returns:
        DataFrame: Sorted summary table of site counts by company and status.
    """

    # 1. Filter for Oil and Gas Sites
    oil_gas_sites = all_field[all_field['Fuel type'].str.contains('Oil|Gas', case=False, na=False)]


    oil_gas_sites = oil_gas_sites.dropna(subset=['Parent(s)'])

    # 2. Clean and Prepare Parent Company Data
    oil_gas_sites['Parent'] = oil_gas_sites['Parent'].fillna('Unknown').astype(str)
    oil_gas_sites['Parent'] = oil_gas_sites['Parent'].apply(lambda x: re.sub(r'\s*\[[^\]]*\]|\s*\([^)]*\)', '', x))
    oil_gas_sites['Parent'] = oil_gas_sites['Parent'].str.split(';')
    oil_gas_sites = oil_gas_sites.explode('Parent')
    oil_gas_sites['Parent'] = oil_gas_sites['Parent'].str.strip()

    # 3. Group, Pivot, and Calculate Totals
    site_counts = oil_gas_sites.groupby(['Parent', 'Status']).size().reset_index(name='Number of Sites')
    summary_table = site_counts.pivot_table(index='Parent', columns='Status', values='Number of Sites', fill_value=0)
    summary_table['Total'] = summary_table.sum(axis=1)

    # 4. Group Companies with Fewer than 50 Sites and Keep the Row
    fewer_than_50 = summary_table[summary_table['Total'] < 50].sum(numeric_only=True) #sums across number of sites owned
    fewer_than_50.name = 'Owners of fewer than 50 sites' # renames the index

    #summary_table = summary_table[summary_table['Total'] >= 50]  # Keep only those greater than 50
    summary_table = pd.concat([summary_table, pd.DataFrame([fewer_than_50], index=[fewer_than_50.name])]) # add back in total less than 50 row, using concat

    # 5. Sort and Return the Result
    summary_table_sorted = summary_table.sort_values(by='Total', ascending=False)
    return summary_table_sorted


# --- Main Execution ---
summary_table = summarize_site_counts_by_company(all_field)

output_filename = f'{output_folder}/fields_per_company {timestamp}.csv'
summary_table.to_csv(output_filename, index=True)
print(f"File saved as {output_filename}")

summary_table.head()

# # **Regional Tracker Summary Tables**

# # Define Regions

# ===== Cell 33 =====
# AET covers "The Africa Energy Tracker covers the subregions of Northern Africa and Sub-Saharan Africa" https://globalenergymonitor.org/projects/africa-energy-tracker/methodology/
# Define African Sites
african_countries = [
    "Algeria", "Angola", "Angola-Republic of the Congo", "Benin", "Botswana",
    "British Indian Ocean Territory", "Burkina Faso", "Burundi", "Cabo Verde",
    "Cameroon", "Central African Republic", "Chad", "Comoros", "Côte d'Ivoire",
    "Djibouti", "DR Congo", "Egypt", "Equatorial Guinea", "Eritrea", "Eswatini",
    "Ethiopia", "French Southern Territories", "Gabon", "Ghana", "Guinea",
    "Guinea-Bissau", "Kenya", "Lesotho", "Liberia", "Libya", "Madagascar",
    "Malawi", "Mali", "Mauritania", "Mauritius", "Mayotte", "Morocco",
    "Mozambique", "Namibia", "Niger", "Nigeria", "Republic of the Congo",
    "Réunion", "Rwanda", "Saint Helena, Ascension, and Tristan da Cunha",
    "Sao Tome and Principe", "Senegal", "Senegal-Mauritania", "Seychelles",
    "Sierra Leone", "Somalia", "South Africa", "South Sudan", "Sudan",
    "Tanzania", "The Gambia", "Togo", "Tunisia", "Uganda", "Western Sahara",
    "Zambia", "Zimbabwe"
]

# Define Asian Countries https://globalenergymonitor.org/projects/asia-gas-tracker/methodology/
asia_countries = [
    # South Asia
    "Afghanistan", "Bangladesh", "Bhutan", "India", "Iran",
    "Maldives", "Nepal", "Pakistan", "Sri Lanka",

    # Southeast Asia
    "Brunei", "Cambodia", "Indonesia", "Laos", "Malaysia",
    "Myanmar", "Philippines", "Singapore", "Thailand",
    "Timor-Leste", "Vietnam", "Thailand-Malaysia",  "Vietnam-Malaysia",

    # East Asia
    "China", "China-Japan", "Hong Kong", "Japan", "Macao",
    "Mongolia", "North Korea", "South Korea", "Taiwan",

    # Multinational or Maritime Areas
    "South China Sea"
]

# Define European Countries and Territories https://globalenergymonitor.org/projects/europe-gas-tracker/methodology/
europe_countries = [
    # Northern Europe
    "Åland Islands", "Denmark", "Estonia", "Faroe Islands", "Finland",
    "Iceland", "Ireland", "Isle of Man", "Latvia", "Lithuania",
    "Norway", "Sweden", "United Kingdom", "Guernsey", "Jersey", "Svalbard and Jan Mayen",

    # Western Europe
    "Austria", "Belgium", "France", "Germany", "Liechtenstein",
    "Luxembourg", "Monaco", "Netherlands", "Switzerland",

    # Eastern Europe
    "Belarus", "Czech Republic", "Hungary", "Moldova", "Poland",
    "Romania", "Slovakia", "Ukraine",

    # Southern Europe
    "Albania", "Andorra", "Bosnia and Herzegovina", "Bulgaria", "Croatia",
    "Cyprus", "Gibraltar", "Greece", "Italy", "Kosovo", "Malta",
    "Montenegro", "North Macedonia", "Portugal", "San Marino",
    "Serbia", "Slovenia", "Spain", "Türkiye",

    # Special Cases
    "Israel"  # list in the methodology
]

# Define Latin American and Caribbean Countries and Territories - see "Data request for the new year"
latin_america_caribbean = [
    # Caribbean
    "Anguilla", "Antigua and Barbuda", "Aruba", "Bahamas", "Barbados",
    "Belize", "Cayman Islands", "Cuba", "Curaçao", "Dominica",
    "Dominican Republic", "Grenada", "Guadeloupe", "Haiti", "Jamaica",
    "Martinique", "Montserrat",  "Saint Barthélemy",
    "Saint Kitts and Nevis", "Saint Lucia", "Saint Martin (French part)",
    "Saint Vincent and the Grenadines", "Sint Maarten (Dutch part)",
    "Trinidad and Tobago", "Turks and Caicos Islands", "Virgin Islands (British)",
   # "Virgin Islands (U.S.)", "Puerto Rico", -  gregor excludes

    # Central America
    "Costa Rica", "El Salvador", "Guatemala", "Honduras", "Mexico",
    "Nicaragua", "Panama",

    # South America
    "Argentina", "Bolivia", "Brazil", "Chile", "Colombia", "Ecuador",
    "French Guiana", "Guyana", "Paraguay", "Peru", "Suriname",
    "Uruguay", "Venezuela",

    # Special Cases
    "Bonaire, Sint Eustatius, and Saba", "Bouvet Island",
    "Falkland Islands", "South Georgia and the South Sandwich Islands",
    "Venezuela-Trinidad and Tobago"
]

# ===== Cell 34 =====
def filter_by_region(data, countries, region_name):
    """Filters the input data based on a list of countries and region name."""
    pattern = '|'.join([re.escape(country) for country in countries])  # Escape special characters
    filtered_data = data[data['Country'].isin(countries)]
    return filtered_data


# Apply the function to create regional DataFrames:
African_Sites = filter_by_region(all_field, african_countries, "Africa")
africa_data = filter_by_region(merged_data, african_countries, "Africa")

Asian_Sites = filter_by_region(all_field, asia_countries, "Asia")
Asian_data = filter_by_region(merged_data, asia_countries, "Asia")

Europe_Sites = filter_by_region(all_field, europe_countries, "Europe")
EGT_data = filter_by_region(merged_data, europe_countries, "Europe")


Latin_America_Sites = filter_by_region(all_field, latin_america_caribbean, "Latin America")
lamer_data = filter_by_region(merged_data, latin_america_caribbean, "Latin America")

# ===== Cell 35 =====
# countries in Asian_sites
Asian_Sites['Country'].unique()

# # Oil and Gas sites counts by Region (Africa Subset)

# ===== Cell 36 =====
# Filter for extraction sites where Fuel type indicates oil, gas, or oil and gas
African_Sites_oil_gas_sites = African_Sites[African_Sites['Fuel type'].str.contains('Oil|Gas', case=False, na=False)]

# Group by "GEM sub-region" and "Status", then count
African_Sites_oil_gas_site_by_region_status = African_Sites_oil_gas_sites.groupby(['GEM sub-region', 'Status']).size().reset_index(name='Number of Extraction Sites')

# Pivot with status as columns
Africa_pivot_oil_gas_region = African_Sites_oil_gas_site_by_region_status.pivot_table(index='GEM sub-region', columns='Status', values='Number of Extraction Sites', fill_value=0)

# Columns to potentially combine into 'Other'
columns_to_combine_africa = ['decommissioned', 'Unknown']

# Get the columns that are actually in the DataFrame
existing_columns_africa = [col for col in columns_to_combine_africa if col in Africa_pivot_oil_gas_region.columns]

# Check if any of the existing columns have non-zero values
if any(Africa_pivot_oil_gas_region[col].any() for col in existing_columns_africa):
    # Combine specified columns into 'Other' if any exist and have non-zero values
    Africa_pivot_oil_gas_region['Other'] = Africa_pivot_oil_gas_region[existing_columns_africa].sum(axis=1)
    Africa_pivot_oil_gas_region_final = Africa_pivot_oil_gas_region.drop(columns=existing_columns_africa)
else:
    # If none of the columns exist or have only zero values, skip combining
    Africa_pivot_oil_gas_region_final = Africa_pivot_oil_gas_region

# Calculate the total number of sites for each region
Africa_pivot_oil_gas_region_final['Total'] = Africa_pivot_oil_gas_region_final.sum(axis=1)

# Sort the DataFrame by the 'Total' column in descending order
Africa_pivot_oil_gas_region_final_sorted = Africa_pivot_oil_gas_region_final.sort_values(by='Total', ascending=False)

# add preproduction
discovered_africa_col = Africa_pivot_oil_gas_region_final_sorted['discovered'] if 'discovered' in Africa_pivot_oil_gas_region_final_sorted.columns else 0
in_development_africa_col = Africa_pivot_oil_gas_region_final_sorted['in-development'] if 'in-development' in Africa_pivot_oil_gas_region_final_sorted.columns else 0
Africa_pivot_oil_gas_region_final_sorted['Pre-production (discovered+ in-development)'] = discovered_africa_col + in_development_africa_col

# sort columns
desired_columns_africa = ['discovered', 'in-development', 'Pre-production (discovered+ in-development)', 'operating', 'mothballed', 'Other', 'Total']

# Filter and reorder columns, adding missing ones with 0 if they don't exist
for col in desired_columns_africa:
    if col not in Africa_pivot_oil_gas_region_final_sorted.columns:
        Africa_pivot_oil_gas_region_final_sorted[col] = 0

Africa_pivot_oil_gas_region_final_sorted = Africa_pivot_oil_gas_region_final_sorted[desired_columns_africa]

# Generate a filename with timestamp for saving the output
output_filename_africa_oil_gas_Region_status = f'{output_folder}/ africa_oil_gas_Region{timestamp}.csv'

# Save the DataFrame to CSV
Africa_pivot_oil_gas_region_final_sorted.to_csv(output_filename_africa_oil_gas_Region_status, index=True)

print(f"File saved as {output_filename_africa_oil_gas_Region_status}")
print(f"Total number of sites: {Africa_pivot_oil_gas_region_final_sorted['Total'].sum()}")

Africa_pivot_oil_gas_region_final_sorted.head()

# # Gas sites counts by Region (Europe Subset)
#
# ---
#

# ===== Cell 37 =====
# Filter for extraction sites where Fuel type indicates oil, gas, or oil and gas
Europe_Sites_gas_sites = Europe_Sites[Europe_Sites['Fuel type'].str.contains('Gas', case=False, na=False)]

# Group by "GEM sub-region" and "Status", then count
Europe_Sites_gas_site_by_region_status = Europe_Sites_gas_sites.groupby(['GEM sub-region', 'Status']).size().reset_index(name='Number of Extraction Sites')

# Pivot with status as columns
Europe_pivot_gas_region = Europe_Sites_gas_site_by_region_status.pivot_table(index='GEM sub-region', columns='Status', values='Number of Extraction Sites', fill_value=0)

# Columns to potentially combine into 'Other'
columns_to_combine_europe = ['decommissioned', 'Unknown']

# Get the columns that are actually in the DataFrame
existing_columns_europe = [col for col in columns_to_combine_europe if col in Europe_pivot_gas_region.columns]

# Check if any of the existing columns have non-zero values
if any(Europe_pivot_gas_region[col].any() for col in existing_columns_europe):
    # Combine specified columns into 'Other' if any exist and have non-zero values
    Europe_pivot_gas_region['Other'] = Europe_pivot_gas_region[existing_columns_europe].sum(axis=1)
    Europe_pivot_gas_region_final = Europe_pivot_gas_region.drop(columns=existing_columns_europe)
else:
    # If none of the columns exist or have only zero values, skip combining
    Europe_pivot_gas_region_final = Europe_pivot_gas_region

# Calculate the total number of sites for each region
Europe_pivot_gas_region_final['Total'] = Europe_pivot_gas_region_final.sum(axis=1)

# add preproduction columns
discovered_europe_col = Europe_pivot_gas_region_final['discovered'] if 'discovered' in Europe_pivot_gas_region_final.columns else 0
in_development_europe_col = Europe_pivot_gas_region_final['in-development'] if 'in-development' in Europe_pivot_gas_region_final.columns else 0
Europe_pivot_gas_region_final['Pre-production (discovered+ in-development)'] = discovered_europe_col + in_development_europe_col

# sort columns
desired_columns_europe = ['discovered', 'in-development', 'Pre-production (discovered+ in-development)', 'operating', 'mothballed', 'Other', 'Total']

# Filter and reorder columns, adding missing ones with 0 if they don't exist
for col in desired_columns_europe:
    if col not in Europe_pivot_gas_region_final.columns:
        Europe_pivot_gas_region_final[col] = 0

Europe_pivot_gas_region_final = Europe_pivot_gas_region_final[desired_columns_europe]

# Sort the DataFrame by the 'Total' column in descending order
Europe_pivot_gas_region_final_sorted = Europe_pivot_gas_region_final.sort_values(by='Total', ascending=False)

# Generate a filename with timestamp for saving the output
output_filename_Europe_gas_status = f'{output_folder}/ Europe_gas_status{timestamp}.csv'

# Save the DataFrame to CSV
Europe_pivot_gas_region_final_sorted.to_csv(output_filename_Europe_gas_status, index=True)

print(f"File saved as {output_filename_Europe_gas_status}")
print(f"Total number of sites: {Europe_pivot_gas_region_final_sorted['Total'].sum()}")

Europe_pivot_gas_region_final_sorted.head()

# # Gas sites counts by Region (Asia Subset)
#
# ---
#

# ===== Cell 38 =====
# # filter out Eastern Asia
# Asian_Sites = Asian_Sites[~Asian_Sites['GEM sub-region'].str.contains('Western Asia', case=False, na=False)]

# Filter for extraction sites where Fuel type indicates oil, gas, or oil and gas
Asian_Sites_gas_sites = Asian_Sites[Asian_Sites['Fuel type'].str.contains('Gas', case=False, na=False)]

# Group by "GEM sub-region" and "Status", then count
Asian_Sites_gas_site_by_region_status = Asian_Sites_gas_sites.groupby(['GEM sub-region', 'Status']).size().reset_index(name='Number of Extraction Sites')

# Pivot with status as columns
Asia_pivot_gas_region = Asian_Sites_gas_site_by_region_status.pivot_table(index='GEM sub-region', columns='Status', values='Number of Extraction Sites', fill_value=0)

# Columns to potentially combine into 'Other'
columns_to_combine_asia = ['decommissioned', 'Unknown','cancelled']

# Get the columns that are actually in the DataFrame
existing_columns_asia = [col for col in columns_to_combine_asia if col in Asia_pivot_gas_region.columns]

# Check if any of the existing columns have non-zero values
if any(Asia_pivot_gas_region[col].any() for col in existing_columns_asia):
    # Combine specified columns into 'Other' if any exist and have non-zero values
    Asia_pivot_gas_region['Other'] = Asia_pivot_gas_region[existing_columns_asia].sum(axis=1)
    Asia_pivot_gas_region_final = Asia_pivot_gas_region.drop(columns=existing_columns_asia)
else:
    # If none of the columns exist or have only zero values, skip combining
    Asia_pivot_gas_region_final = Asia_pivot_gas_region

# Calculate the total number of sites for each region
Asia_pivot_gas_region_final['Total'] = Asia_pivot_gas_region_final.sum(axis=1)

# add preproduction
discovered_asia_col = Asia_pivot_gas_region_final['discovered'] if 'discovered' in Asia_pivot_gas_region_final.columns else 0
in_development_asia_col = Asia_pivot_gas_region_final['in-development'] if 'in-development' in Asia_pivot_gas_region_final.columns else 0
Asia_pivot_gas_region_final['Pre-production (discovered+ in-development)'] = discovered_asia_col + in_development_asia_col

# sort columns
desired_columns_asia = ['discovered', 'in-development', 'Pre-production (discovered+ in-development)', 'operating', 'mothballed', 'Other', 'Total']

# Filter and reorder columns, adding missing ones with 0 if they don't exist
for col in desired_columns_asia:
    if col not in Asia_pivot_gas_region_final.columns:
        Asia_pivot_gas_region_final[col] = 0

Asia_pivot_gas_region_final = Asia_pivot_gas_region_final[desired_columns_asia]

# Sort the DataFrame by the 'Total' column in descending order
Asia_pivot_gas_region_final_sorted = Asia_pivot_gas_region_final.sort_values(by='Total', ascending=False)

# Generate a filename with timestamp for saving the output
output_filename_Asia_gas_status = f'{output_folder}/ Asia_gas_status{timestamp}.csv'

# Save the DataFrame to CSV
Asia_pivot_gas_region_final_sorted.to_csv(output_filename_Asia_gas_status, index=True)

print(f"File saved as {output_filename_Asia_gas_status}")
print(f"Total number of sites: {Asia_pivot_gas_region_final_sorted['Total'].sum()}")

Asia_pivot_gas_region_final_sorted.head()

# ===== Cell 39 =====
# print totals for each column in Asia_pivot_gas_region_final_sorted
Asia_pivot_gas_region_final_sorted.sum()

# # Oil and Gas sites counts by Region (LA Subset)

# ===== Cell 40 =====
# note - not currently using this one sense the subregion is just one region
# Filter for extraction sites where Fuel type indicates oil, gas, or oil and gas
Latin_America_Sites_oil_gas_sites = Latin_America_Sites[Latin_America_Sites['Fuel type'].str.contains('Oil|Gas', case=False, na=False)]

# Group by "GEM sub-region" and "Status", then count
Latin_America_Sites_oil_gas_site_by_region_status = Latin_America_Sites_oil_gas_sites.groupby(['GEM sub-region', 'Status']).size().reset_index(name='Number of Extraction Sites')

# Pivot with status as columns
Latin_America_pivot_oil_gas_region = Latin_America_Sites_oil_gas_site_by_region_status.pivot_table(index='GEM sub-region', columns='Status', values='Number of Extraction Sites', fill_value=0)

# Columns to potentially combine into 'Other'
columns_to_combine_latam = ['decommissioned', 'abandoned', 'exploration', 'Unknown']

# Get the columns that are actually in the DataFrame
existing_columns_latam = [col for col in columns_to_combine_latam if col in Latin_America_pivot_oil_gas_region.columns]

# Check if any of the existing columns have non-zero values
if any(Latin_America_pivot_oil_gas_region[col].any() for col in existing_columns_latam):
    # Combine specified columns into 'Other' if any exist and have non-zero values
    Latin_America_pivot_oil_gas_region['Other'] = Latin_America_pivot_oil_gas_region[existing_columns_latam].sum(axis=1)
    Latin_America_pivot_oil_gas_region_final = Latin_America_pivot_oil_gas_region.drop(columns=existing_columns_latam)
else:
    # If none of the columns exist or have only zero values, skip combining
    Latin_America_pivot_oil_gas_region_final = Latin_America_pivot_oil_gas_region

# Calculate the total number of sites for each region
Latin_America_pivot_oil_gas_region_final['Total'] = Latin_America_pivot_oil_gas_region_final.sum(axis=1)

# add preproduction column
discovered_latam_col = Latin_America_pivot_oil_gas_region_final['discovered'] if 'discovered' in Latin_America_pivot_oil_gas_region_final.columns else 0
in_development_latam_col = Latin_America_pivot_oil_gas_region_final['in-development'] if 'in-development' in Latin_America_pivot_oil_gas_region_final.columns else 0
Latin_America_pivot_oil_gas_region_final['Pre-production (discovered+ in-development)'] = discovered_latam_col + in_development_latam_col

# sort columns
desired_columns_latam = ['discovered', 'in-development', 'Pre-production (discovered+ in-development)', 'operating', 'mothballed', 'Other', 'Total']

# Filter and reorder columns, adding missing ones with 0 if they don't exist
for col in desired_columns_latam:
    if col not in Latin_America_pivot_oil_gas_region_final.columns:
        Latin_America_pivot_oil_gas_region_final[col] = 0

Latin_America_pivot_oil_gas_region_final = Latin_America_pivot_oil_gas_region_final[desired_columns_latam]

# Sort the DataFrame by the 'Total' column in descending order
Latin_America_pivot_oil_gas_region_final_sorted = Latin_America_pivot_oil_gas_region_final.sort_values(by='Total', ascending=False)

# Generate a filename with timestamp for saving the output
output_filename_LA_oil_gas_Region_status = f'{output_folder}/ LA_oil_gas_Region{timestamp}.csv'

# Save the DataFrame to CSV
Latin_America_pivot_oil_gas_region_final_sorted.to_csv(output_filename_LA_oil_gas_Region_status, index=True)

print(f"File saved as {output_filename_LA_oil_gas_Region_status}")

Latin_America_pivot_oil_gas_region_final_sorted.head()

# # Oil and Gas Counts by Country (Africa Subset)
#

# ===== Cell 41 =====
# Filter for extraction sites where Fuel type indicates oil, gas, or oil and gas
African_Sites_oil_gas_sites = African_Sites[African_Sites['Fuel type'].str.contains('Oil|Gas', case=False, na=False)]

# for QC, keep region in, comment out for final versions
# Group by "Country" and "Status", then count (keep Sub-region)
African_Sites_oil_gas_site_by_country_status = African_Sites_oil_gas_sites.groupby(['Country', 'GEM sub-region', 'Status']).size().reset_index(name='Number of Gas Extraction Sites')

# Pivot with status as columns, keep Sub-region as an index level
Africa_pivot_oil_gas_country = African_Sites_oil_gas_site_by_country_status.pivot_table(
    index=['Country', 'GEM sub-region'],  # Include Sub-region in the index
    columns='Status',
    values='Number of Gas Extraction Sites',
    fill_value=0
)

# # Group by "Country" and "Status", then count
# African_Sites_oil_gas_site_by_country_status = African_Sites_oil_gas_sites.groupby(['Country/Area', 'Status']).size().reset_index(name='Number of Extraction Sites')

# # Pivot with status as columns
# Africa_pivot_oil_gas_country = African_Sites_oil_gas_site_by_country_status.pivot_table(index='Country/Area', columns='Status', values='Number of Extraction Sites', fill_value=0)

# Columns to potentially combine into 'Other'
columns_to_combine_africa_country = ['decommissioned', 'Unknown']

# Get the columns that are actually in the DataFrame
existing_columns_africa_country = [col for col in columns_to_combine_africa_country if col in Africa_pivot_oil_gas_country.columns]

# Check if any of the existing columns have non-zero values
if any(Africa_pivot_oil_gas_country[col].any() for col in existing_columns_africa_country):
    # Combine specified columns into 'Other' if any exist and have non-zero values
    Africa_pivot_oil_gas_country['Other'] = Africa_pivot_oil_gas_country[existing_columns_africa_country].sum(axis=1)
    Africa_pivot_oil_gas_country_final = Africa_pivot_oil_gas_country.drop(columns=existing_columns_africa_country)
else:
    # If none of the columns exist or have only zero values, skip combining
    Africa_pivot_oil_gas_country_final = Africa_pivot_oil_gas_country

# Calculate the total number of sites for each country
Africa_pivot_oil_gas_country_final['Total'] = Africa_pivot_oil_gas_country_final.sum(axis=1)

# Sort the DataFrame by the 'Total' column in descending order
Africa_pivot_oil_gas_country_final_sorted = Africa_pivot_oil_gas_country_final.sort_values(by='Total', ascending=False)

# add preproduction
discovered_africa_country_col = Africa_pivot_oil_gas_country_final_sorted['discovered'] if 'discovered' in Africa_pivot_oil_gas_country_final_sorted.columns else 0
in_development_africa_country_col = Africa_pivot_oil_gas_country_final_sorted['in-development'] if 'in-development' in Africa_pivot_oil_gas_country_final_sorted.columns else 0
Africa_pivot_oil_gas_country_final_sorted['Pre-production (discovered+ in-development)'] = discovered_africa_country_col + in_development_africa_country_col

# sort columns
desired_columns_africa_country = ['discovered', 'in-development', 'Pre-production (discovered+ in-development)', 'operating', 'mothballed', 'Other', 'Total']

# Filter and reorder columns, adding missing ones with 0 if they don't exist
for col in desired_columns_africa_country:
    if col not in Africa_pivot_oil_gas_country_final_sorted.columns:
        Africa_pivot_oil_gas_country_final_sorted[col] = 0

Africa_pivot_oil_gas_country_final_sorted = Africa_pivot_oil_gas_country_final_sorted[desired_columns_africa_country]

# Generate a filename with timestamp for saving the output
output_filename_africa_oil_gas_country_status = f'{output_folder}/ africa_oil_gas_country_status{timestamp}.csv'

# Save the DataFrame to CSV
Africa_pivot_oil_gas_country_final_sorted.to_csv(output_filename_africa_oil_gas_country_status, index=True)

print(f"File saved as {output_filename_africa_oil_gas_country_status}")

#print sum of total column
print(f"Total number of sites: {Africa_pivot_oil_gas_country_final_sorted['Total'].sum()}")

Africa_pivot_oil_gas_country_final_sorted.head()

# # Oil and Gas Counts by Country (LA Subset)

# ===== Cell 42 =====
# Filter for extraction sites where Fuel type indicates oil, gas, or oil and gas
Latin_America_oil_gas_sites = Latin_America_Sites[Latin_America_Sites['Fuel type'].str.contains('Oil|Gas', case=False, na=False)]

# Group by "Country" and "Status", then count
Latin_America_oil_gas_site_by_country_status = Latin_America_oil_gas_sites.groupby(['Country', 'Status']).size().reset_index(name='Number of Extraction Sites')

# Pivot with status as columns
Latin_America_pivot_oil_gas_country = Latin_America_oil_gas_site_by_country_status.pivot_table(index='Country', columns='Status', values='Number of Extraction Sites', fill_value=0)

# Columns to potentially combine into 'Other'
columns_to_combine_latam_country = ['decommissioned','exploration','cancelled', 'abandoned', 'Unknown']

# Get the columns that are actually in the DataFrame
existing_columns_latam_country = [col for col in columns_to_combine_latam_country if col in Latin_America_pivot_oil_gas_country.columns]

# Check if any of the existing columns have non-zero values
if any(Latin_America_pivot_oil_gas_country[col].any() for col in existing_columns_latam_country):
    # Combine specified columns into 'Other' if any exist and have non-zero values
    Latin_America_pivot_oil_gas_country['Other'] = Latin_America_pivot_oil_gas_country[existing_columns_latam_country].sum(axis=1)
    Latin_America_pivot_oil_gas_country_final = Latin_America_pivot_oil_gas_country.drop(columns=existing_columns_latam_country)
else:
    # If none of the columns exist or have only zero values, skip combining
    Latin_America_pivot_oil_gas_country_final = Latin_America_pivot_oil_gas_country

# Calculate the total number of sites for each country
Latin_America_pivot_oil_gas_country_final['Total'] = Latin_America_pivot_oil_gas_country_final.sum(axis=1)

# add preproduction columns
discovered_latam_country_col = Latin_America_pivot_oil_gas_country_final['discovered'] if 'discovered' in Latin_America_pivot_oil_gas_country_final.columns else 0
in_development_latam_country_col = Latin_America_pivot_oil_gas_country_final['in-development'] if 'in-development' in Latin_America_pivot_oil_gas_country_final.columns else 0
Latin_America_pivot_oil_gas_country_final['Pre-production (discovered+ in-development)'] = discovered_latam_country_col + in_development_latam_country_col

# sort columns
desired_columns_latam_country = ['discovered', 'in-development', 'Pre-production (discovered+ in-development)', 'operating', 'mothballed', 'Other', 'Total']

# Filter and reorder columns, adding missing ones with 0 if they don't exist
for col in desired_columns_latam_country:
    if col not in Latin_America_pivot_oil_gas_country_final.columns:
        Latin_America_pivot_oil_gas_country_final[col] = 0

Latin_America_pivot_oil_gas_country_final = Latin_America_pivot_oil_gas_country_final[desired_columns_latam_country]

# Sort the DataFrame by the 'Total' column in descending order
Latin_America_pivot_oil_gas_country_final_sorted = Latin_America_pivot_oil_gas_country_final.sort_values(by='Total', ascending=False)

# Generate a filename with timestamp for saving the output
output_filename_LA_oil_gas_country_status = f'{output_folder}/ LA_oil_gas_country_status{timestamp}.csv'

# Save the DataFrame to CSV
Latin_America_pivot_oil_gas_country_final_sorted.to_csv(output_filename_LA_oil_gas_country_status, index=True)

print(f"File saved as {output_filename_LA_oil_gas_country_status}")
print(f"Total number of sites: {Latin_America_pivot_oil_gas_country_final_sorted['Total'].sum()}")

Latin_America_pivot_oil_gas_country_final_sorted.head()

# # Gas Counts by Country (AsiaSubset)

# ===== Cell 43 =====
#check countries in Asian_Sites
Asian_Sites['Country'].unique()
# Vietnam-Malaysia seems to be getting excluded, but it should be there.... manually overriding
#Filter for extraction sites where Fuel type indicates oil, gas, or oil and gas
Asian_Sites_gas_sites = Asian_Sites[Asian_Sites['Fuel type'].str.contains('Gas', case=False, na=False)]

# Group by "Country" and "Status", then count
Asian_Sites_gas_site_by_country_status = Asian_Sites_gas_sites.groupby(['Country', 'Status']).size().reset_index(name='Number of Extraction Sites')

# Pivot with status as columns
Asia_pivot_gas_country = Asian_Sites_gas_site_by_country_status.pivot_table(index='Country', columns='Status', values='Number of Extraction Sites', fill_value=0)

# Columns to potentially combine into 'Other'
columns_to_combine_asia_country = ['decommissioned', 'abandoned', 'exploration','Unknown']

# Get the columns that are actually in the DataFrame
existing_columns_asia_country = [col for col in columns_to_combine_asia_country if col in Asia_pivot_gas_country.columns]

# Check if any of the existing columns have non-zero values
if any(Asia_pivot_gas_country[col].any() for col in existing_columns_asia_country):
    # Combine specified columns into 'Other' if any exist and have non-zero values
    Asia_pivot_gas_country['Other'] = Asia_pivot_gas_country[existing_columns_asia_country].sum(axis=1)
    Asia_pivot_gas_country_final = Asia_pivot_gas_country.drop(columns=existing_columns_asia_country)
else:
    # If none of the columns exist or have only zero values, skip combining
    Asia_pivot_gas_country_final = Asia_pivot_gas_country


# Calculate the total number of sites for each region
Asia_pivot_gas_country_final['Total'] = Asia_pivot_gas_country_final.sum(axis=1)

# pre production column
discovered_asia_country_col = Asia_pivot_gas_country_final['discovered'] if 'discovered' in Asia_pivot_gas_country_final.columns else 0
in_development_asia_country_col = Asia_pivot_gas_country_final['in-development'] if 'in-development' in Asia_pivot_gas_country_final.columns else 0
Asia_pivot_gas_country_final['Pre-production (discovered+ in-development)'] = discovered_asia_country_col + in_development_asia_country_col

# sort columns
desired_columns_asia_country = ['discovered', 'in-development', 'Pre-production (discovered+ in-development)', 'operating', 'mothballed', 'Other', 'Total']

# Filter and reorder columns, adding missing ones with 0 if they don't exist
for col in desired_columns_asia_country:
    if col not in Asia_pivot_gas_country_final.columns:
        Asia_pivot_gas_country_final[col] = 0

Asia_pivot_gas_country_final = Asia_pivot_gas_country_final[desired_columns_asia_country]

# Sort the DataFrame by the 'Total' column in descending order
Asia_pivot_gas_country_final_sorted = Asia_pivot_gas_country_final.sort_values(by='Total', ascending=False)

# Generate a filename with timestamp for saving the output
output_filename_Asia_gas_country_status = f'{output_folder}/ Asia_gas_country_statu{timestamp}.csv'

# Save the DataFrame to CSV
Asia_pivot_gas_country_final_sorted.to_csv(output_filename_Asia_gas_country_status, index=True)

print(f"File saved as {output_filename_Asia_gas_country_status}")
print(f"Total number of sites: {Asia_pivot_gas_country_final_sorted['Total'].sum()}")

Asia_pivot_gas_country_final_sorted.head()

# ===== Cell 44 =====
# within Asia_pivot_gas_country_final, show country = china
# The original code was trying to perform a bitwise AND operation between two DataFrames, which is not supported.
# To correctly filter a DataFrame with multiple conditions, apply the boolean masks (conditions) within a single filtering operation using the '&' operator between them.
filtered_data = Asian_Sites_gas_sites[
    (Asian_Sites_gas_sites['Country'] == 'Brunei') &
    (Asian_Sites_gas_sites['Status'] == 'operating')
]

# sort alphabetically
filtered_data.sort_values(by='Unit Name')

# ===== Cell 45 =====
filtered_field = Asian_Sites[
    (Asian_Sites['Unit Name'] == 'Qinhuangdao 29-6 Field') &
    (Asian_Sites['Status'] == 'discovered')
]

# # Oil, gas and hydrocarbon production by Region (Africa)

# ===== Cell 46 =====
# Group by 'GEM sub-region' and sum the specified columns (for Africa only)
production_by_subregion_africa = africa_data.groupby('GEM sub-region').agg(
    {'million m³/y': lambda x: x.sum() / 1000,  # Convert to bcm during summation
     'million bbl/y': 'sum',
     'million boe/y': 'sum'
    })

# Rename the columns for clarity
production_by_subregion_africa = production_by_subregion_africa.rename(columns={
    'million m³/y': 'Gas Production (bcm/y)',
    'million bbl/y': 'Liquids Production (million bbl/y)',
    'million boe/y': 'Unspecified Hydrocarbons Production (million boe/y)',
})

# create total hydrocarbons columns
production_by_subregion_africa["Total Production (million boe/y)"] = production_by_subregion_africa["Liquids Production (million bbl/y)"] + production_by_subregion_africa["Unspecified Hydrocarbons Production (million boe/y)"]  + (production_by_subregion_africa["Gas Production (bcm/y)"]*gas_bcm_to_boe)

# Save the result to a CSV file (optional)
output_filename = f'{output_folder}/Production_by_subregion_Africa_{timestamp}.csv'
production_by_subregion_africa.to_csv(output_filename)
print(f"File saved as {output_filename}")
print(f"Total number of production: {production_by_subregion_africa['Total Production (million boe/y)'].sum()}")

# Display the result
production_by_subregion_africa.head()

# # Gas production by Region (Europe)

# ===== Cell 47 =====
# Group by 'GEM Subregion' and sum the specified columns (for Europe only)
production_by_Region_Europe = EGT_data.groupby('GEM sub-region').agg(
    {'million m³/y': lambda x: x.sum() / 1000,  # Convert to bcm during summation
    }
)

# Rename the columns for clarity
production_by_Region_Europe = production_by_Region_Europe.rename(columns={
    'million m³/y': 'Gas Production (bcm/y)'
})

# Save the result to a CSV file (optional)
output_filename = f'{output_folder}/Production_by_subregion_Europe_{timestamp}.csv'
production_by_Region_Europe.to_csv(output_filename)
print(f"File saved as {output_filename}")
print(f"Total production: {production_by_Region_Europe['Gas Production (bcm/y)'].sum()}")

#display head
production_by_Region_Europe.head()

# # Gas production by Region (Asia)

# ===== Cell 48 =====
# Group by 'GEM sub-region' and sum the specified columns (for Asia only)
production_by_subregion_asia = Asian_data.groupby('GEM sub-region').agg(
    {'million m³/y': lambda x: x.sum() / 1000,  # Convert to bcm during summation
    }
)

# Rename the columns for clarity
production_by_subregion_asia = production_by_subregion_asia.rename(columns={
    'million m³/y': 'Gas Production (bcm/y)'
})

# Save the result to a CSV file (optional)
output_filename = f'{output_folder}/Production_by_subregion_Asia_{timestamp}.csv'
production_by_subregion_asia.to_csv(output_filename)
print(f"File saved as {output_filename}")
print(f"Total production: {production_by_subregion_asia['Gas Production (bcm/y)'].sum()}")

# show header
production_by_subregion_asia.head()

# # Oil, gas and hydrocarbon production by Region (LA Subset)

# ===== Cell 49 =====
# Not using as its only one region
# Group by 'GEM sub-region' and sum the specified columns (for LA only)
production_by_subregion_lamer = lamer_data.groupby('GEM sub-region').agg(
    {'million m³/y': lambda x: x.sum() / 1000,  # Convert to bcm during summation
     'million bbl/y': 'sum',
     'million boe/y': 'sum'
    })

# Rename the columns for clarity
production_by_subregion_lamer = production_by_subregion_lamer.rename(columns={
    'million m³/y': 'Gas Production (bcm/y)',
    'million bbl/y': 'Oil Production (million bbl/y)',
    'million boe/y': 'Unspecified Hydrocarbons Production (million boe/y)',
})

# create total hydrocarbons columns
production_by_subregion_lamer["Total Production (million boe/y)"] = production_by_subregion_lamer['Oil Production (million bbl/y)'] + production_by_subregion_lamer['Unspecified Hydrocarbons Production (million boe/y)'] + (production_by_subregion_lamer["Gas Production (bcm/y)"]*gas_bcm_to_boe)

# Save the result to a CSV file (optional)
output_filename = f'{output_folder}/Production_by_subregion_LatinAmerica_{timestamp}.csv'
production_by_subregion_lamer.to_csv(output_filename)
print(f"File saved as {output_filename}")
print(f"Total production: {production_by_subregion_lamer['Total Production (million boe/y)'].sum()}")

#show header
production_by_subregion_lamer.head()

# # Oil, gas and hydrocarbon production By Country (Africa):
#

# ===== Cell 50 =====
# Group by 'Country/Area' and sum the specified columns (for Africa only)
production_by_country_africa = africa_data.groupby('Country').agg(
    {'million m³/y': lambda x: x.sum() / 1000,  # Convert to bcm during summation
     'million bbl/y': 'sum',
     'million boe/y': 'sum'
    })

# Rename the columns for clarity
production_by_country_africa = production_by_country_africa.rename(columns={
    'million m³/y': 'Gas Production (bcm/y)',
    'million bbl/y': 'Oil Production (million bbl/y)',
    'million boe/y': 'Unspecified Hydrocarbons Production (million boe/y)',
})

# create total hydrocarbons columns
production_by_country_africa["Total Production (million boe/y)"] = production_by_country_africa['Oil Production (million bbl/y)'] + production_by_country_africa['Unspecified Hydrocarbons Production (million boe/y)'] + (production_by_country_africa["Gas Production (bcm/y)"]*gas_bcm_to_boe)

# Sort by Total Production (million boe/y) in descending order
production_by_country_africa = production_by_country_africa.sort_values(by='Total Production (million boe/y)', ascending=False)

# Save the result to a CSV file (optional)
output_filename = f'{output_folder}/Production_by_Country_Africa_{timestamp}.csv'
production_by_country_africa.to_csv(output_filename)
print(f"File saved as {output_filename}")
print(f"Total production: {production_by_country_africa['Total Production (million boe/y)'].sum()}")

# show header
production_by_country_africa.head()

# # Gas production by country (Europe)

# ===== Cell 51 =====
# Group by 'GEM Country' and sum the specified columns (for Europe only)
production_by_country_Europe = EGT_data.groupby('Country').agg(
    {'million m³/y': lambda x: x.sum() / 1000,  # Convert to bcm during summation
    }
)

production_by_country_Europe = production_by_country_Europe.rename(columns={
    'million m³/y': 'Gas Production (bcm/y)'})

# Display the result
print(production_by_country_Europe)
print(f"Total production: {production_by_country_Europe['Gas Production (bcm/y)'].sum()}")

# Save the result to a CSV file (optional)
output_filename = f'{output_folder}/Production_by_country_Europe_{timestamp}.csv'
production_by_country_Europe.to_csv(output_filename)
print(f"File saved as {output_filename}")

# # Gas production By Country (Asia):

# ===== Cell 52 =====
# Group by 'GEM Country' and sum the specified columns (for Asia only)
production_by_country_asia = Asian_data.groupby('Country').agg(
    {'million m³/y': lambda x: x.sum() / 1000}) # Convert to bcm during summation

production_by_country_asia = production_by_country_asia.rename(columns={
    'million m³/y': 'Gas Production (bcm/y)'})

# Display the result
print(production_by_country_asia)
print(f"Total production: {production_by_country_asia['Gas Production (bcm/y)'].sum()}")

# Save the result to a CSV file (optional)
output_filename = f'{output_folder}/Production_by_country_Asia_{timestamp}.csv'
production_by_country_asia.to_csv(output_filename)
print(f"File saved as {output_filename}")

# # Oil, gas and hydrocarbon production Country (Latin America)

# ===== Cell 53 =====
# Group by 'Country/Area' and sum the specified columns (for Latin America and the Caribbean only)
production_by_country_Latam = lamer_data.groupby('Country').agg(
    {'million m³/y': lambda x: x.sum() / 1000,  # Convert to bcm during summation
     'million bbl/y': 'sum',
     'million boe/y': 'sum'
    })

# rename for clarity
production_by_country_Latam = production_by_country_Latam.rename(columns={
    'million m³/y': 'Gas Production (bcm/y)',
    'million bbl/y': 'Oil Production (million bbl/y)',
    'million boe/y': 'Unspecified Hydrocarbons Production (million boe/y)',
})

# create total hydrocarbons
production_by_country_Latam["Total Production (million boe/y)"] = production_by_country_Latam['Oil Production (million bbl/y)'] + production_by_country_Latam['Unspecified Hydrocarbons Production (million boe/y)'] + (production_by_country_Latam["Gas Production (bcm/y)"]*gas_bcm_to_boe)
# Sort by Total Production (million boe/y) in descending order
production_by_country_Latam = production_by_country_Latam.sort_values(by='Total Production (million boe/y)', ascending=False)

# Display the result
print(production_by_country_Latam)
print(f"Total production: {production_by_country_Latam['Total Production (million boe/y)'].sum()}")

# Save the result to a CSV file (optional)
output_filename = f'{output_folder}/Production_by_Country_LatAm_{timestamp}.csv'
production_by_country_Latam.to_csv(output_filename)
print(f"File saved as {output_filename}")

# # Put Relevant CSVs into a drive folder, then write them to an excel file

# ===== Cell 54 =====
# [moved to requirements.txt] !pip install xlsxwriter
import os
import re

# ===== Cell 55 =====
# print recent timestamp
print(timestamp)

# ===== Cell 56 =====
# The timestamp used in generated CSV filenames was 20260217200829 for the initial set
# We need to explicitly set data_timestamp to this value for the moving logic to work correctly.
active_draft_folder = '/content/drive/MyDrive/GOGET q1 2026/Summary Tables Draft/'
data_timestamp = timestamp # Ensure data_timestamp is the current timestamp

# Define the new_folder_path correctly using the current timestamp
new_folder_name = f'Drafts_{data_timestamp}'
new_folder_path = os.path.join(active_draft_folder, new_folder_name)

# Create the new folder if it doesn't exist
os.makedirs(new_folder_path, exist_ok=True)

# Ensure the new_folder_path is the base for subsequent operations
base_csv_directory = new_folder_path

# ===== Cell 57 =====
# manually check if this folder is created
print(f'hey you, look if {new_folder_name} is in {active_draft_folder}. If not, create it!')

# ===== Cell 58 =====
import shutil

# Get a list of all files in the initial output_folder that match the current timestamp
# These are the files that were just generated and need to be moved
files_to_move = [f for f in os.listdir(output_folder) if data_timestamp in f and f.endswith('.csv')]

# Move these files from output_folder to new_folder_path
for filename in files_to_move:
    source_path = os.path.join(output_folder, filename)
    destination_path = os.path.join(new_folder_path, filename)
    try:
        shutil.move(source_path, destination_path)
        print(f"Moved '{filename}' to '{new_folder_name}'")
    except Exception as e:
        print(f"Error moving '{filename}': {e}")

# Now, get the list of CSV files from the newly populated folder
csv_files = [f for f in os.listdir(base_csv_directory) if f.endswith('.csv')]

# ===== Cell 59 =====

# Get a list of all files and directories in the active_draft_folder
files_in_draft_folder = os.listdir(active_draft_folder)

# Iterate through each item and move it if it contains the data_timestamp
for filename in files_in_draft_folder:
    source_path = os.path.join(active_draft_folder, filename)

    # Skip moving the newly created target folder into itself
    if source_path == new_folder_path:
        continue

    # Check if the filename contains the data_timestamp
    if data_timestamp in filename:
        destination_path = os.path.join(new_folder_path, filename)
        try:
            shutil.move(source_path, destination_path)
            print(f"Moved '{filename}' to '{new_folder_name}'")
        except Exception as e:
            print(f"Error moving '{filename}': {e}")

# ===== Cell 60 =====
def get_categorized_sheet_name(filename_with_ext):
    """
    Generates a categorized and clean Excel sheet name from a filename,
    ensuring it's no longer than 31 characters.

    Args:
        filename_with_ext (str): The original filename (e.g., 'Production_by_Country_Africa_20260217194008.csv').

    Returns:
        str: A cleaned, categorized, and truncated sheet name (max 31 characters).
    """
    # Remove file extension
    base_name = os.path.splitext(filename_with_ext)[0]

    # Remove the timestamp (14 digits) and any preceding underscore or space
    core_name_raw = re.sub(r'(_|\s)?\d{14}$', '', base_name).strip('_ ').strip()

    # Define region keywords (case-insensitive) and their standard names for direct matching
    # Using patterns that appear directly in the `core_name_raw` or after simple lowercasing
    region_patterns_map = {
        "africa": "Africa",
        "europe": "Europe",
        "asia": "Asia",
        "latinamerica": "LatinAmerica", # Matches "LatinAmerica" as one word
        "latam": "LatinAmerica",
        "la": "LatinAmerica" # For "LA_" files
    }

    detected_region_prefix = "World"
    # Convert core_name_raw to lower for case-insensitive matching
    core_name_lower = core_name_raw.lower()

    # Sort patterns by length descending to prioritize longer matches (e.g., 'latinamerica' over 'la')
    sorted_patterns = sorted(region_patterns_map.keys(), key=len, reverse=True)

    matched_keyword = None
    for pattern in sorted_patterns:
        # Check for existence of the pattern in the lowercased core name.
        # Using a simple 'in' check, which is more flexible than word boundaries for concatenated names.
        if pattern in core_name_lower:
            detected_region_prefix = region_patterns_map[pattern]
            matched_keyword = pattern
            break # Take the first match

        # Special handling for 'la' to match 'LA_' (e.g., 'LA_oil_gas_Region')
        if pattern == 'la' and 'la_' in core_name_lower:
             detected_region_prefix = region_patterns_map[pattern]
             matched_keyword = pattern
             break # Take the first match

    # Now construct the sheet name based on detected region and original core_name_raw
    if matched_keyword:
        # Remove the matched keyword from the lowercased core_name_raw to avoid redundancy.
        # Re-capitalize words to form the descriptive part of the sheet name.
        if matched_keyword == 'la':
            # For 'la', specifically target 'la_' if present
            temp_core_name = re.sub(r'la_', '', core_name_lower, flags=re.IGNORECASE).strip('_ ').strip()
        else:
            # For other keywords, replace the pattern found
            temp_core_name = re.sub(re.escape(matched_keyword), '', core_name_lower, flags=re.IGNORECASE).strip('_ ').strip()

        # If after removing the keyword, temp_core_name is empty, use a generic name for the region
        if not temp_core_name:
            final_sheet_name = f"{detected_region_prefix}_Summary"
        else:
            # Capitalize each word, preserving underscores from the original structure
            capitalized_words = [word.capitalize() for word in temp_core_name.split('_')]
            final_sheet_name = f"{detected_region_prefix}_{'_'.join(capitalized_words)}"
    else:
        # No specific region matched, use "World" prefix and capitalize the full raw core name
        capitalized_words = [word.capitalize() for word in core_name_raw.lower().split('_')]
        final_sheet_name = f"{detected_region_prefix}_{'_'.join(capitalized_words)}"

    # Clean up multiple spaces/underscores and strip leading/trailing ones
    final_sheet_name = re.sub(r'[ _]+', '_', final_sheet_name).strip('_')

    # Ensure max 31 characters
    return final_sheet_name[:31]

# apply final_sheet_name to csv_files
categorized_csv_files = {
    "World": [],
    "Africa": [],
    "Europe": [],
    "Asia": [],
    "LatinAmerica": []
}

# Iterate through each csv filename
for csv_file_name in csv_files:
    # Get the categorized sheet name, which starts with the region prefix
    sheet_name = get_categorized_sheet_name(csv_file_name)
    # Extract the region from the sheet name (e.g., "Africa_Oil_Gas_Region" -> "Africa")
    region = sheet_name.split('_')[0]

    # Construct the full path to the CSV file, now using base_csv_directory
    full_csv_path = os.path.join(base_csv_directory, csv_file_name)

    # Assign to the correct category.
    if region in categorized_csv_files:
        categorized_csv_files[region].append(full_csv_path)
    else:
        # Fallback for unexpected regions, though get_categorized_sheet_name should default to 'World'
        categorized_csv_files["World"].append(full_csv_path)

# Print the categorization to verify
for region, files in categorized_csv_files.items():
    print(f"{region} files: {len(files)} files")

# ===== Cell 61 =====
# define a helper function combine_csvs_to_excel that will take a list of CSV file paths and combine them into a single Excel file
def combine_csvs_to_excel(csv_file_paths, output_dir, timestamp, region_name):
    """
    Combines a list of CSV files into a single Excel file.

    Args:
        csv_file_paths (list): A list of full paths to the CSV files.
        output_dir (str): The base directory for output.
        timestamp (str): The timestamp to append to the output filename.
        region_name (str): The name of the region for the output directory and filename.
    """
    # Create region-specific output directory if it doesn't exist
    region_output_dir = os.path.join(output_dir, region_name)
    print(f"Attempting to create directory: {region_output_dir}") # Added for debugging
    os.makedirs(region_output_dir, exist_ok=True)

    output_excel_file = os.path.join(region_output_dir, f'combined_{region_name}_{timestamp}.xlsx')

    with pd.ExcelWriter(output_excel_file, engine='xlsxwriter') as writer:
        for file_path in csv_file_paths:
            df = pd.read_csv(file_path)
            # Use the existing get_categorized_sheet_name function to get the sheet name
            sheet_name = get_categorized_sheet_name(os.path.basename(file_path))
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    print(f"All {region_name} CSVs combined into one Excel file: {output_excel_file}")

# ===== Cell 62 =====
# The base directory for output Excel files will now be the new_folder_path
csv_directory_base = new_folder_path

# Iterate through each region and its associated CSV file paths
for region_name, file_paths in categorized_csv_files.items():
    if file_paths: # Only process if there are files for the region
        combine_csvs_to_excel(file_paths, csv_directory_base, data_timestamp, region_name)
    else:
        print(f"No files to combine for region: {region_name}")

print(f"All regional Excel files generated in subfolders under {csv_directory_base}")
