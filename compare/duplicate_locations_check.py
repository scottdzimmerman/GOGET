"""
duplicate_locations_check.py

Migrated from Colab notebook: Duplicate Locations Check GOGET 2024 08 26
Auto-converted to a Python script. Colab-specific lines
(drive.mount, google.colab imports, shell/magic commands) have been
commented out and flagged; pip installs moved to ../requirements.txt.
"""

# ===== Cell 1 =====
# Checks for duplicate locations within GOGET Sheet

# ===== Cell 2 =====
# import pandas as pd, mount google drive
import pandas as pd
# [colab-only removed] from google.colab import drive
# [colab drive mount removed] drive.mount('/content/drive')

# ===== Cell 3 =====
# import cleaned data

df = '/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/QC/GOGET Locations Duplicate Check (2024 08 26).xlsx'

# ===== Cell 4 =====
# check if Unit ID have the same entry for latitude and longitude

GOGET_data = pd.read_excel(df)
GOGET_data.head()

# ===== Cell 5 =====
# prompt: return Unit ID where entries where Latitude Longitude are the same across multiple units excluding blanks

# Drop rows with missing Latitude or Longitude
GOGET_data_cleaned = GOGET_data.dropna(subset=['Latitude', 'Longitude'])

# Group by Latitude and Longitude and count occurrences
location_counts = GOGET_data_cleaned.groupby(['Latitude', 'Longitude'])['Unit ID'].count().reset_index(name='count')

# Filter for locations with count > 1 (duplicates)
duplicate_locations = location_counts[location_counts['count'] > 1]

# Merge with original DataFrame to get Unit IDs
duplicate_units = pd.merge(duplicate_locations, GOGET_data_cleaned, on=['Latitude', 'Longitude'])

# Extract unique Unit IDs
result = duplicate_units['Unit ID'].unique()

# count units
print(len(result))

# Print units
print(result)
