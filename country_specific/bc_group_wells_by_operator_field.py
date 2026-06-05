"""
bc_group_wells_by_operator_field.py

Migrated from Colab notebook: BC Group Wells by Operator and Field 2024 09 06- GPT.ipynb
Auto-converted to a Python script. Colab-specific lines
(drive.mount, google.colab imports, shell/magic commands) have been
commented out and flagged; pip installs moved to ../requirements.txt.
"""

# ===== Cell 1 =====
#Download Well Data for British Columbia (Canada) from https://reports.bc-er.ca/ogc/f?p=200:8:15361179614398::NO:::

# ===== Cell 2 =====
# Mount google drive
# [colab-only removed] from google.colab import drive
# [colab drive mount removed] drive.mount('/content/drive')

# ===== Cell 3 =====
import pandas as pd

# Assuming your CSV file is named 'your_file.csv'
csv_file = '/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/Data sets & reports (O&G)/O&G country materials/Canada (GOGET O&G)/British Columbia/BC Total Production 2023.csv'

# Read the CSV file into a pandas DataFrame
df = pd.read_csv(csv_file)

# Convert relevant columns to numeric
numeric_columns = ['Production Days', 'Gas Production (e3m3)', 'Oil Production (m3)', 'Condensate Production (m3)']
df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')

# ===== Cell 4 =====
# Filter for 2023 production data
data_2023 = df[df['Zone Prod Period'].astype(str).str.startswith('2023')]

data_2023.head()

# ===== Cell 5 =====
# Group by Well Area Name and Operator Abbreviation and sum gas, oil, and condensate
totals_2023 = data_2023.groupby(['Well Area Name', 'Oper Abbreviation']).agg({
    'Gas Production (e3m3)': 'sum',
    'Oil Production (m3)': 'sum',
    'Condensate Production (m3)': 'sum',
    'UWI': lambda x: ';'.join(sorted(x.unique()))
}).reset_index()

totals_2023.head()

# ===== Cell 6 =====
# Conversion factors
gas_to_boe_factor = 5.8 / 1000  # 1 e3m³ of gas equals 5.8 BOE, so in million BOE, it's 0.0058 MMboe
m3_to_bbl_factor = 6.2898  # 1 m³ of oil or condensate equals 6.2898 barrels (bbl)

# Convert to MMBOE and bbl
totals_2023['Gas (MMBOE)'] = totals_2023['Gas Production (e3m3)'] * gas_to_boe_factor
totals_2023['Oil (bbl)'] = totals_2023['Oil Production (m3)'] * m3_to_bbl_factor
totals_2023['Condensate (bbl)'] = totals_2023['Condensate Production (m3)'] * m3_to_bbl_factor

# Total Hydrocarbons in BOE
totals_2023['Total Hydrocarbons (BOE)'] = totals_2023['Gas (BOE)'] + totals_2023['Oil (bbl)'] + totals_2023['Condensate (bbl)']
totals_2023['Total Hydrocarbons (MMBOE)'] = totals_2023['Total Hydrocarbons (BOE)'] / 1e6

totals_2023.head()

# ===== Cell 7 =====
# Sort by Total Hydrocarbons (MMBOE), high to low
totals_2023_sorted = totals_2023.sort_values(by='Total Hydrocarbons (MMBOE)', ascending=False)

totals_2023_sorted.head()

# ===== Cell 8 =====
# Print the rows that contribute to duplicates
duplicates = totals_2023_sorted[totals_2023_sorted.duplicated(subset=['Well Area Name', 'Oper Abbreviation'], keep=False)]
print("Rows contributing to duplicates:")
print(duplicates)

# ===== Cell 9 =====
# save to excel format
totals_2023_sorted.to_excel('/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/Data sets & reports (O&G)/O&G country materials/Canada (GOGET O&G)/British Columbia/BC_2023_production2.xlsx', index=False)
