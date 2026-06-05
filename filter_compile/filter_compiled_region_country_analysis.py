"""
filter_compiled_region_country_analysis.py

Migrated from Colab notebook: Filter Compiled Sheet for Region_Country Analysis 2024 10 08
Auto-converted to a Python script. Colab-specific lines
(drive.mount, google.colab imports, shell/magic commands) have been
commented out and flagged; pip installs moved to ../requirements.txt.
"""

# ===== Cell 1 =====
# Code for filtering down and existing compiled sheet by region. In this case,
# data was filtered via https://colab.research.google.com/drive/1uf1Jeh6SEhyeDqhkM9LMwoZ1SEaj5PHn?usp=sharing
# and compliled via https://drive.google.com/file/d/1FFYtF5JGyUlAQpY4PXz8Ni8VsdORYjHe/view?usp=sharing

# ===== Cell 2 =====
# Mount google drive
# [colab-only removed] from google.colab import drive
# [colab drive mount removed] drive.mount('/content/drive')

# ===== Cell 3 =====
goget = ('/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/GOGET Iterations/Compiled Versions of GOGET/Global Oil and Gas Extraction Tracker - 2024-10-08_1526.xlsx')

# ===== Cell 4 =====
# prompt: Read in GOGET data, and pandas as PD

import pandas as pd
goget_df = pd.read_excel(goget)

# ===== Cell 5 =====
# prompt: filter goget df so that it only includes "Country/Area" = "Filter target"
target_country = "United Kingdom"
goget_df_filtered = goget_df[goget_df["Country/Area"].isin([target_country])]

# ===== Cell 6 =====
# check filter, see header

goget_df_filtered.head()

# ===== Cell 7 =====
# prompt: Apply the same filter to the Production & reserves sheet

# Assuming the 'Production & reserves' sheet is in the same Excel file
prod_reserves_df = pd.read_excel(goget, sheet_name='Production & reserves')
prod_reserves_df_filtered = prod_reserves_df[prod_reserves_df["Country/Area"].isin([target_country])]
prod_reserves_df_filtered.head()

# ===== Cell 8 =====
# Assuming you want to read the "About" sheet as well
about_df = pd.read_excel(goget, sheet_name='About')

# Create an ExcelWriter object
# Save the file to your Google Drive
output_path = '/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/GOGET Iterations/Compiled Versions of GOGET/'+ target_country + '-Filter Global Oil and Gas Extraction Tracker - 2024-10-08_1033.xlsx'
with pd.ExcelWriter(output_path) as writer:
  goget_df_filtered.to_excel(writer, sheet_name='Main data', index=False)
  prod_reserves_df_filtered.to_excel(writer, sheet_name='Production & Reserves', index=False)
  about_df.to_excel(writer, sheet_name='About', index=False)

# print save location
print("saved at", output_path)

# ===== Cell 9 =====
import os
os.listdir('/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/GOGET Iterations/Compiled Versions of GOGET')
