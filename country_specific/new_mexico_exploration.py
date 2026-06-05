"""
new_mexico_exploration.py

Migrated from Colab notebook: New Mexico Exploration 2025 01 09.ipynb
Auto-converted to a Python script. Colab-specific lines
(drive.mount, google.colab imports, shell/magic commands) have been
commented out and flagged; pip installs moved to ../requirements.txt.
"""

# ===== Cell 1 =====
# import libs
import pandas as pd
import numpy as np
import os

# mount google drive
# [colab-only removed] from google.colab import drive
# [colab drive mount removed] drive.mount('/content/drive')

# create time stamp
from datetime import datetime
now = datetime.now()
dt = now.strftime("%d/%m/%Y %H:%M:%S")
dt_string = str(dt)

# ===== Cell 2 =====
# name folder
nm_folder = '/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/Data sets & reports (O&G)/O&G country materials/United States (GOGET O&G)/New Mexico (GOGET)'
county_folder = nm_folder + '/County Level Data (GOGET)/Location and General Data 2025'
raw_data = county_folder + '/Raw Data'

# ===== Cell 3 =====
print(f"Contents of {raw_data}:")
# [shell cmd - run manually] !ls "{raw_data}"

# ===== Cell 4 =====
# join all csvs in county_folder
all_counties = pd.concat(map(pd.read_csv, [f"{raw_data}/{file}" for file in os.listdir(raw_data) if file.endswith('.csv')]))

all_counties.columns

# ===== Cell 5 =====
# save all counties to preserve memory
# The original dt_string contains characters like '/' and ' ' which are interpreted as directory separators,
# causing the file path to be treated as a series of non-existent directories.
# To fix this, we will create a file-safe timestamp string.
file_safe_dt_string = now.strftime("%Y-%m-%d_%H-%M-%S")
all_counties.to_csv(f"{county_folder}/all_counties_{file_safe_dt_string}.csv", index=False)

# ===== Cell 6 =====
# skip previous steps and start here once all counties csv is created

# all_counties = pd.read_csv(f"{county_folder}/all_counties_2026-01-09_21-42-01.csv")

# Explicitly create a copy to avoid SettingWithCopyWarning
all_counties_active_well = all_counties.loc[all_counties['compl_status'] == 'Active'].copy()

all_counties_active_well.to_csv(f"{county_folder}/all_counties_active_well_{file_safe_dt_string}.csv", index=False)

# ===== Cell 7 =====
# formation is one_producing_pool_name after the semicolon, split on the semicolon to get pool formation
all_counties_active_well['formation'] = all_counties_active_well['one_producing_pool_name'].str.split(';').str[-1]

# title case all_counties_active_well['formation']
all_counties_active_well['formation'] = all_counties_active_well['formation'].str.title()

# ===== Cell 8 =====
# formation is one_producing_pool_name after the semicolon, split on the semicolon to get pool formation - removing active well filter to look for more matches
all_counties['formation'] = all_counties['one_producing_pool_name'].str.split(';').str[-1]

# title case all_counties_active_well['formation']
all_counties['formation'] = all_counties['formation'].str.title()

# ===== Cell 9 =====
import re

def format_api_standardized(api_raw):
    s_api = str(api_raw)
    cleaned_digits = re.sub(r'\D', '', s_api) # Remove all non-digits

    if not cleaned_digits:
        return "" # Handle cases with no digits

    state_part = cleaned_digits[:2].zfill(2)
    remaining_digits = cleaned_digits[2:]

    county_part = remaining_digits[:3].zfill(3)
    well_part_raw = remaining_digits[3:]

    well_part = well_part_raw.zfill(5)

    # Ensure parts are truncated to their standard lengths
    state_part = state_part[:2]
    county_part = county_part[:3]
    well_part = well_part[:5]

    return f"{state_part}-{county_part}-{well_part}"

# Apply the robust formatting to the 'api' column for all wells
all_counties['api_cleaned'] = all_counties['api'].apply(format_api_standardized)

# Apply the robust formatting to the 'api' column for active wells
all_counties_active_well['api_cleaned'] = all_counties_active_well['api'].apply(format_api_standardized)


# ===== Cell 10 =====
# make new df with just API and formation
api_formation_all = all_counties[['api', 'formation']]
api_formation_active = all_counties_active_well[['api', 'formation']]

api_formation_all.head()

# ===== Cell 11 =====
# count unique entries in formation - all
api_formation_all['formation'].value_counts()

# ===== Cell 12 =====
# count unique entries in formation
api_formation_active['formation'].value_counts()

# ===== Cell 13 =====
# check specfic APIs for QC: 3002552244
api_formation_all[api_formation_all['api'] == '3002552244']

# ===== Cell 14 =====
api_formation_all.to_csv(f"{county_folder}/api_formation_all_{file_safe_dt_string}.csv", index=False)
all_counties_active_well.to_csv(f"{county_folder}/all_counties_active_well_{file_safe_dt_string}.csv", index=False)
