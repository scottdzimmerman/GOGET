"""
check_ownership_for_duplicates.py

Migrated from Colab notebook: GOGET QC - Check Ownership for Duplicates 2024 10 08
Auto-converted to a Python script. Colab-specific lines
(drive.mount, google.colab imports, shell/magic commands) have been
commented out and flagged; pip installs moved to ../requirements.txt.
"""

# ===== Cell 1 =====
import pandas as pd

# ===== Cell 2 =====
# mount google drive
# [colab-only removed] from google.colab import drive
# [colab drive mount removed] drive.mount('/content/drive')

# ===== Cell 3 =====
# import goget excel sheet, indicate sheet
GOGET = pd.read_excel("/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/GOGET Iterations/Snapshots of GOGET main data set/GOGET oil & gas extraction sites (2024 10 08).xlsx","Main data", engine='openpyxl')

# ===== Cell 4 =====
# List of columns related to ownership
ownership_columns = ['Owner 1', 'Owner 2', 'Owner 3', 'Owner 4', 'Owner 5']

# Function to check for duplicate values within a row for the ownership columns excluding blanks
def has_duplicates(row):
  values = [row[col] for col in ownership_columns if pd.notna(row[col]) and row[col] != '']
  return len(set(values)) != len(values)

# Apply the function to each row of the DataFrame
GOGET['Has_Duplicate_Ownership'] = GOGET.apply(has_duplicates, axis=1)

# Display rows with duplicate ownership values
duplicates_df = GOGET[GOGET['Has_Duplicate_Ownership'] == True]
duplicates_df.head()


# ===== Cell 5 =====
# Clean duplicate DF to only include ownership columns and the Has_Duplicate_Ownership tag
ownership_df = duplicates_df[ownership_columns + ['Has_Duplicate_Ownership']+['Unit ID']]
ownership_df.head()

# ===== Cell 6 =====
# save comparison to google drive folder
ownership_df.to_excel("/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/QC/duplicate_ownership_2024_10_08.xlsx")
