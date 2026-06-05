"""
compare_versions_missing_entries.py

Migrated from Colab notebook: Compare two versions of GOGET to find Missing Entries.ipynb
Auto-converted to a Python script. Colab-specific lines
(drive.mount, google.colab imports, shell/magic commands) have been
commented out and flagged; pip installs moved to ../requirements.txt.
"""

# ===== Cell 1 =====
# load in libraries
# [colab-only removed] from google.colab import drive
# [colab drive mount removed] drive.mount('/content/drive')

import pandas as pd
# [moved to requirements.txt] !pip install xlsxwriter
import xlsxwriter

# ===== Cell 2 =====
# load in two csvs as df
GOGET_pre_texas_removal = pd.read_csv('/content/drive/MyDrive/GOGET Q4 2024/GOGET oil & gas extraction sites (2024 12 19) - Reserves and Production.csv')
GOGET_post_texas_removal = pd.read_csv('/content/drive/MyDrive/GOGET Q4 2024/GOGET oil & gas extraction sites (main data set) - Reserves and Production.csv')


# ===== Cell 3 =====
print(len(GOGET_pre_texas_removal), len(GOGET_post_texas_removal))

# ===== Cell 4 =====
# Example DataFrames
# Replace these with your actual DataFrames
df_original = GOGET_pre_texas_removal

df_modified = GOGET_post_texas_removal

# Identify deleted rows
deleted_rows = pd.concat([df_original, df_modified]).drop_duplicates(keep=False)

# check length of deleted_rows
len(deleted_rows)

# ===== Cell 5 =====
df_original = df_original.drop_duplicates(keep='first')  # Or 'last' depending on your need

merged_df = pd.merge(df_original, df_modified, on='unique_id', how='outer', indicator=True)
modified_rows = merged_df[merged_df['_merge'] == 'both'][(df_original != df_modified).any(axis=1)]

# ===== Cell 6 =====
# Check if all deleted rows contain "Texas"
all_texas_deleted = deleted_rows['State'].str.contains("Texas").all()

# Display the deleted rows and verification
print("Deleted Rows:")
print(deleted_rows)
print(f"All deleted rows contain 'Texas': {all_texas_deleted}")

# ===== Cell 7 =====
# Create Unique ID for each row by combining Unit name,Country/Area,"Subnational unit (province, state)","Production/reserves","Fuel description",Reserves classification (original),Quantity (original),Units (original),Data year,Data source

GOGET_post_texas_removal['id'] = GOGET_post_texas_removal['Unit name'] + GOGET_post_texas_removal['Country/Area'] + GOGET_post_texas_removal['Quantity (original)'] + GOGET_post_texas_removal['Units (original)'] + GOGET_post_texas_removal['Data year'] + GOGET_post_texas_removal['Data source']
GOGET_pre_texas_removal['id'] = GOGET_pre_texas_removal['Unit name'] + GOGET_pre_texas_removal['Country/Area'] + GOGET_pre_texas_removal['Quantity (original)'] + GOGET_pre_texas_removal['Units (original)'] + GOGET_pre_texas_removal['Data year'] + GOGET_pre_texas_removal['Data source']

GOGET_pre_texas_removal

# ===== Cell 8 =====
# ignore texas
GOGET_pre_texas_no_texas = GOGET_pre_texas_removal[GOGET_pre_texas_removal['Subnational unit (province, state)'] != 'Texas']

# drop blank unit ID
GOGET_pre_texas_no_texas = GOGET_pre_texas_no_texas.dropna(subset=['id'])
GOGET_post_texas_removal = GOGET_post_texas_removal.dropna(subset=['id'])

# ===== Cell 9 =====
# find difference between GOGET_pre_texas_no_texas and GOGET_post_texas_removal
difference = pd.concat([GOGET_pre_texas_no_texas, GOGET_post_texas_removal]).drop_duplicates(keep=False)

# ===== Cell 10 =====
difference

# ===== Cell 11 =====


# Identify rows in GOGET_pre_texas_no_texas that are missing from GOGET_post_texas_no_texas
# Assuming a unique identifier for each row (e.g., 'id' or a combination of columns)
# Replace 'id' with the actual unique identifier column name or combination of columns if needed.
if 'id' in GOGET_pre_texas_no_texas.columns:
  missing_rows = GOGET_pre_texas_no_texas[~GOGET_pre_texas_no_texas['id'].isin(GOGET_post_texas_no_texas['id'])]
elif all(col in GOGET_pre_texas_no_texas.columns for col in ['Production/reserves','Fuel description','Quantity (original)', 'Units (original)', 'Data source', 'Quantity (converted)']):
    missing_rows = pd.merge(GOGET_pre_texas_no_texas, GOGET_post_texas_no_texas, on=['Production/reserves','Fuel description','Quantity (original)', 'Units (original)', 'Data source', 'Quantity (converted)'], how='left', indicator=True)
    missing_rows = missing_rows[missing_rows['_merge'] == 'left_only']

else:
  print("No unique identifier found, and site, lat and long not present. Counting based on all columns may not be accurate.")
  missing_rows = pd.concat([GOGET_pre_texas_no_texas, GOGET_post_texas_no_texas]).drop_duplicates(keep=False)


# Count the number of missing rows
count_missing_rows = len(missing_rows)

# Print the count
print(f"Number of rows in GOGET_pre_texas (excluding Texas) missing from GOGET_post_texas (excluding Texas): {count_missing_rows}")
