"""
compare_ownership_between_sheets.py

Migrated from Colab notebook: Compare Ownership Between Two Sheets 2024 10 04.ipynb
Auto-converted to a Python script. Colab-specific lines
(drive.mount, google.colab imports, shell/magic commands) have been
commented out and flagged; pip installs moved to ../requirements.txt.
"""

# ===== Cell 1 =====
# Mount Google Drive
# [colab-only removed] from google.colab import drive
# [colab drive mount removed] drive.mount('/content/drive')

# ===== Cell 2 =====
# Import libs
import pandas as pd
import datetime

# ===== Cell 3 =====
# Load in sheets
Aug26 = pd.read_excel("/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/GOGET Iterations/Snapshots of GOGET main data set/GOGET oil & gas extraction sites (2024 08 26).xlsx","Main data", engine='openpyxl')
Sept27 = pd.read_excel("/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/GOGET Iterations/Snapshots of GOGET main data set/GOGET oil & gas extraction sites (2024 09 27).xlsx","Main data", engine='openpyxl')
Oct4 = pd.read_excel("/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/GOGET Iterations/Snapshots of GOGET main data set/GOGET oil & gas extraction sites (2024 10 04).xlsx","Main data", engine='openpyxl')
sheet_name = "Main data"

# ===== Cell 4 =====
Sept27.head()

# ===== Cell 5 =====
# prompt: write function to combine Owner 1 through owner 5 into one column, alphabetized

def combine_owners(df):
  """Combines Owner 1 through Owner 5 into one column, alphabetized."""

  owner_cols = ['Owner 1', 'Owner 2', 'Owner 3', 'Owner 4', 'Owner 5']
  df['Combined Owners'] = df[owner_cols].apply(lambda row: '; '.join(sorted([str(x) for x in row if not pd.isnull(x)])), axis=1)
  return df

# Apply the function to the DataFrame
Aug26 = combine_owners(Aug26)
Sept27 = combine_owners(Sept27)
Oct4 = combine_owners(Oct4)

# Print the updated DataFrame (Optional)
print(Aug26[['Owner 1', 'Owner 2', 'Owner 3', 'Owner 4', 'Owner 5', 'Combined Owners']].head())
print(Sept27[['Owner 1', 'Owner 2', 'Owner 3', 'Owner 4', 'Owner 5', 'Combined Owners']].head())
print(Oct4[['Owner 1', 'Owner 2', 'Owner 3', 'Owner 4', 'Owner 5', 'Combined Owners']].head())

# ===== Cell 6 =====
Sept27.columns

# ===== Cell 7 =====
# prompt: write function to clean sheets to only 'Unit ID' 'Country/Area' and 'Combined Owners'

def clean_sheets(df):
  """Cleans the DataFrame to only include 'Unit ID', 'Country/Area', and 'Combined Owners' columns."""
  return df[['Unit ID', 'Country/Area', 'Combined Owners']]

# Apply the function to the DataFrames
Aug26_cleaned = clean_sheets(Aug26)
Sept27_cleaned = clean_sheets(Sept27)
Oct4_cleaned = clean_sheets(Oct4)

# Print the cleaned DataFrames (Optional)
print(Aug26_cleaned.head())
print(Sept27_cleaned.head())
print(Oct4_cleaned.head())

# ===== Cell 8 =====
# prompt: Merge Aug26_cleaned,  Sept27_cleaned and Oct4_cleaned using unit ID

merged_df= pd.merge(Aug26_cleaned, Oct4_cleaned, on='Unit ID', how='outer', suffixes=('_Aug26','_Oct4'))
# merged_df = pd.merge(Aug26_cleaned, Oct4_cleaned, on='Unit ID', how='outer',
# suffixes=('Aug26','_Sept27', '_Oct4'))
print(merged_df.head())

# ===== Cell 9 =====
# prompt: compare Combined Owners_Aug26  and  Combined Owners_Oct4 columns for each row, indicate if they match

merged_df['Owners_Match'] = merged_df['Combined Owners_Aug26'] == merged_df['Combined Owners_Oct4']
print(merged_df[['Unit ID', 'Combined Owners_Aug26', 'Combined Owners_Oct4', 'Owners_Match']].head())

# ===== Cell 10 =====
merged_df.to_excel("/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/QC/Sep27vsOct4 owners 2024 10 04-b.xlsx")
