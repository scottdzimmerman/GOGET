"""
top_companies_per_county_mergers.py

Migrated from Colab notebook: List top oil and gas companies per county, check for mergers or acquisitions (2026 03 19).ipynb
Auto-converted to a Python script. Colab-specific lines
(drive.mount, google.colab imports, shell/magic commands) have been
commented out and flagged; pip installs moved to ../requirements.txt.
"""

#
# # This notebook generates a list of top owners and operators in GOGET for a country, then uses AI to check for mergers and acquisitions
#
# Method: Cobbled together by SZ on 2026 03 19 based on existing codebase, added the AI prompting based on directions from Googles "[Welcome to Colab](https://colab.research.google.com/#scrollTo=C1XfGyQXQK1n)"

# ===== Cell 1 =====
# prepare and gather data
#run this to pull content from google drive
# [colab-only removed] from google.colab import drive
# [colab drive mount removed] drive.mount('/content/drive')

#Loading the libraries
import pandas as pd
import numpy as np
import re
from datetime import datetime
# [colab-only removed] from google.colab import ai
# [moved to requirements.txt] !pip install xlsxwriter

# name export path
export_gen_path = "/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/GOGET Iterations/Snapshots of GOGET main data set/"
export_qc_path = '/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/QC/QC Output Dump/'

# make timestamp
from datetime import datetime
now = datetime.now()
timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")

print('this runs qc output will all be timestamped: ' + timestamp)

# ===== Cell 2 =====
# load in GOGET Field Export and Project Export
field_file_name = "goget-field-export-2026-03-19T155832.xlsx"
project_file_name= "goget-project-export-2026-03-19T164542.xlsx"
field_data = pd.read_excel(export_gen_path + field_file_name)
project_data = pd.read_excel(export_gen_path + project_file_name)

print(field_data.columns)
print(project_data.columns)

# ===== Cell 3 =====
# define ownership columns
ownership_columns = ['Project ID', 'Country', 'Operator', 'Owner(s)', 'Parent(s)']

# filter to just ownership columns
GOGET_ownership_field = field_data[ownership_columns]
GOGET_ownership_project = project_data[ownership_columns]

#count rows in both projects and fields
print(GOGET_ownership_field.shape)
print(GOGET_ownership_project.shape)

# consolidate
GOGET_ownership = pd.concat([GOGET_ownership_field, GOGET_ownership_project])

print(GOGET_ownership.shape)

# ===== Cell 4 =====
# Explode 'Owner(s)' column by semicolon
GOGET_ownership_exploded = GOGET_ownership.assign(
    **{'Owner(s)': GOGET_ownership['Owner(s)'].str.split(';')} # wrap in list for explode
).explode('Owner(s)')

# Explode 'Parent(s)' column by semicolon on the already exploded DataFrame
GOGET_ownership_exploded = GOGET_ownership_exploded.assign(
    **{'Parent(s)': GOGET_ownership_exploded['Parent(s)'].str.split(';')} # wrap in list for explode
).explode('Parent(s)')

import re

# Function to remove ownership percentages
def remove_ownership_percents(text):
    if pd.isna(text):
        return text
    # Regex to find patterns like [xx.x%] or [x.x%] or [xx%] etc. and remove them along with any leading/trailing whitespace
    return re.sub(r'\s*\[\d+(\.\d+)?%\]', '', text).strip()

# Apply the function to 'Owner(s)' and 'Parent(s)' columns
GOGET_ownership_exploded['Owner(s)'] = GOGET_ownership_exploded['Owner(s)'].apply(remove_ownership_percents)
GOGET_ownership_exploded['Parent(s)'] = GOGET_ownership_exploded['Parent(s)'].apply(remove_ownership_percents)

# ===== Cell 5 =====
GOGET_ownership_exploded

# ===== Cell 6 =====
# break into 3 dataframes
Operator = GOGET_ownership_exploded[['Project ID', 'Country','Operator']]
Owner = GOGET_ownership_exploded[['Project ID', 'Country','Owner(s)']]
Parent = GOGET_ownership_exploded[['Project ID', 'Country','Parent(s)']]

# ===== Cell 7 =====
# operator count by country
operator_counts = Operator.groupby(['Country', 'Operator'])['Project ID'].nunique().reset_index()
operator_counts.rename(columns={'Project ID': 'Asset Count'}, inplace=True)

top_10_operators_per_country = operator_counts.groupby('Country').apply(lambda x: x.nlargest(10, 'Asset Count')).reset_index(drop=True)

# owner count by country
owner_counts = Owner.groupby(['Country', 'Owner(s)'])['Project ID'].nunique().reset_index()
owner_counts.rename(columns={'Project ID': 'Asset Count'}, inplace=True)

top_10_owners_per_country = owner_counts.groupby('Country').apply(lambda x: x.nlargest(10, 'Asset Count')).reset_index(drop=True)

# parent count by country
parent_counts = Parent.groupby(['Country', 'Parent(s)'])['Project ID'].nunique().reset_index()
parent_counts.rename(columns={'Project ID': 'Asset Count'}, inplace=True)

top_10_parents_per_country = parent_counts.groupby('Country').apply(lambda x: x.nlargest(10, 'Asset Count')).reset_index(drop=True)

# ===== Cell 8 =====
# export results to excel
output_excel_path = export_qc_path + 'top_ownership_data.xlsx'
writer = pd.ExcelWriter(output_excel_path, engine='xlsxwriter')

print(f"ExcelWriter object initialized for: {output_excel_path}")

top_10_operators_per_country.to_excel(writer, sheet_name='Operator', index=False)
print("Operator data written to 'Operator' sheet.")

top_10_owners_per_country.to_excel(writer, sheet_name='Owner', index=False)
print("Owner data written to 'Owner' sheet.")

top_10_parents_per_country.to_excel(writer, sheet_name='Parent', index=False)
print("Parent data written to 'Parent' sheet.")

writer.close()
print(f"Excel file saved at: {output_excel_path}")

# ===== Cell 9 =====
# unique countries in top_10_owners_per_country
unique_countries = top_10_owners_per_country['Country'].unique()

print(unique_countries)

# ===== Cell 10 =====
# set country of interest
country_of_interest = 'Iran'

# filter operators to see top in set country
operators_in_country = top_10_operators_per_country[top_10_operators_per_country['Country'] == country_of_interest]

# Prepare a list to store AI responses
ai_check_results = []

# Iterate through each row in operators_in_country and query AI
for index, row in operators_in_country.iterrows():
    operator_name = row['Operator']
    AI_Merger_check = ai.generate_text("has" + operator_name + "had any recent mergers? please answer as briefly as possible")
    ai_check_results.append(AI_Merger_check)

# Add the AI responses as a new column to the DataFrame
operators_in_country['AI check'] = ai_check_results

print(operators_in_country)
