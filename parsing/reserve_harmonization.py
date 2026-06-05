"""
reserve_harmonization.py

Migrated from Colab notebook: Reserve Harmonization - 2026 02 27 .ipynb
Auto-converted to a Python script. Colab-specific lines
(drive.mount, google.colab imports, shell/magic commands) have been
commented out and flagged; pip installs moved to ../requirements.txt.
"""

# ===== Cell 1 =====
# import libraries

# import pandas for manipulation
import pandas as pd

# mount google drive
# [colab-only removed] from google.colab import drive
# [colab drive mount removed] drive.mount('/content/drive')

# ===== Cell 2 =====
# name export path
export_gen_path = "/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/GOGET Iterations/Alternative Formats of GOGET/"
export_qc_path = '/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/QC/QC Output Dump/'
# import conversion factors
conversion_factors = pd.read_csv('/content/drive/MyDrive/GOGET q1 2026/GOGET oil & gas extraction sites conversion factors for QC  2026 01 30 1633 - Conversion factors.csv')

# make timestamp
from datetime import datetime
now = datetime.now()
timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")

print('this runs qc output will all be timestamped: ' + timestamp)

# ===== Cell 3 =====
# import recent production and reserve sheet
prod_reserves = pd.read_csv(export_gen_path + 'reserves-production-2026-02-27T160021.csv')

# pull in just reserves
reserves = prod_reserves.copy()
reserves = prod_reserves[prod_reserves['Type'] == 'reserves']

# print shape of reserves
print(reserves.shape)

# ===== Cell 4 =====
import re

def extract_country(project_name):
    # Extract content from the last set of parentheses
    match = re.search(r'\(([^)]+)\)[^\(]*$', project_name)
    if match:
        content = match.group(1).strip()
        # If there's a comma, take the last part (assumed to be the country)
        if ',' in content:
            return content.split(',')[-1].strip()
        return content
    return None

# Apply the function to create the 'Country/Area' column in the reserves DataFrame
reserves['Country/Area'] = reserves['Project Name'].apply(extract_country)

print("Extracted countries and created 'Country/Area' column in 'reserves' dataframe.")
# You can uncomment the line below to check some of the extracted countries
# print(reserves['Country/Area'].unique())

# ===== Cell 5 =====
# import rf sheet
rf_sheet = pd.read_csv(export_qc_path + 'recent_reserve_byfuel_converted_df 2026-01-30_22-36-42 - rf sheet.csv')

# filter recent_reserve_byfuel_converted_df for rows where reserveClassification is listed in rf_sheet "description"
in_place_recent = reserves[reserves['Reserve Classification'].isin(rf_sheet['description'])].copy()

# for in_place_recent, create country specifc id by joining Country/Area - fuelDesc - reserveClassification
in_place_recent['country_specific_id'] = in_place_recent['Country/Area'] + ' - ' + in_place_recent['Fuel Description'] + ' - ' + in_place_recent['Reserve Classification']

# matching on "Combo" in rf_sheet bring over Recovery Factor from rf_sheet to in_place_recent
in_place_recent = in_place_recent.merge(rf_sheet[['Combo', 'Recovery Factor']], left_on='country_specific_id', right_on='Combo', how='left')

# Clean and convert 'Recovery Factor' to numeric
in_place_recent['Recovery Factor'] = in_place_recent['Recovery Factor'].str.replace('%', '', regex=False).astype(float) / 100

# apply Recovery Factor to shared unit (million boe) value creating "estimated recoverable"
in_place_recent['estimated recoverable (RF applied to in-place)'] = in_place_recent['Quantity (converted)'] * in_place_recent['Recovery Factor']

# tag all rows where estimated recoverable (1P_2P, 3P_2P) > 0 as "converted from 1p to 2p, 3P to 2p"
in_place_recent['conversion type'] = in_place_recent.apply(lambda row: f"RF applied (Recovery Factor: {row['Recovery Factor']:.2f})" if row['estimated recoverable (RF applied to in-place)'] > 0 else 'not converted', axis=1)

# rename estimated recoverable (RF applied to in-place)
in_place_recent['estimated recoverable'] = in_place_recent['estimated recoverable (RF applied to in-place)']

# drop columns
in_place_recent = in_place_recent.drop(columns=['Combo', 'country_specific_id', 'Recovery Factor','estimated recoverable (RF applied to in-place)'])

in_place_recent

# ===== Cell 6 =====
# import 1P2P3P sheet
p1p2p3p_sheet = pd.read_csv(export_qc_path + 'recent_reserve_byfuel_converted_df 2026-01-30_22-36-42 - Clean 2p conversion.csv')

# filter recent_reserve_byfuel_converted_df for rows where reserveClassification is listed in p1p2p3p "reserveClassification"
closeto1p2p3p = reserves[reserves['Reserve Classification'].isin(p1p2p3p_sheet['reserveClassification'])].copy()

# map p1p2p3p_sheet Conversion_factor to closeto1p2p3p on reserveClassification
closeto1p2p3p = closeto1p2p3p.merge(p1p2p3p_sheet[['reserveClassification', 'Conversion_factor']], left_on='Reserve Classification', right_on='reserveClassification', how='left')

# apply Recovery Factor to shared unit (million boe) value creating "estimated recoverable"
closeto1p2p3p['estimated recoverable (1P_2P, 3P_2P)'] = closeto1p2p3p['Quantity (converted)'] * closeto1p2p3p['Conversion_factor']

# tag all rows where estimated recoverable (1P_2P, 3P_2P) > 0 as "converted from 1p to 2p, 3P to 2p"
closeto1p2p3p['conversion type'] = closeto1p2p3p.apply(lambda row: f"converted from 1p to 2p, 3P to 2p (Conversion Factor: {row['Conversion_factor']:.2f})"  if row['estimated recoverable (1P_2P, 3P_2P)'] > 0 else 'not converted', axis=1)

# rename estimated recoverable (RF applied to in-place)
closeto1p2p3p['estimated recoverable'] = closeto1p2p3p['estimated recoverable (1P_2P, 3P_2P)']

# drop columns
closeto1p2p3p = closeto1p2p3p.drop(columns=['Conversion_factor', 'estimated recoverable (1P_2P, 3P_2P)'])

closeto1p2p3p

# ===== Cell 7 =====
# join closeto1p2p3p and in_place_recent
in_place_and1p2p3p = pd.concat([in_place_recent, closeto1p2p3p])

# labelling columns to keep
keep_columns = ('Project ID', 'Project Name', 'Country/Area', 'Type', 'Fuel Description',
       'Reserve Classification', 'Quantity', 'Quantity Unit',
        'Quantity (converted)', 'Quantity Unit (converted)', 'Year','conversion type', 'estimated recoverable')
# drop non-keep columns, reorder to match keep list
in_place_and1p2p3p = in_place_and1p2p3p[list(keep_columns)]

# ===== Cell 8 =====
in_place_and1p2p3p.columns

# ===== Cell 9 =====
# rename
harmonized_reserves = in_place_and1p2p3p.copy()

# pull in just production
all_prod = prod_reserves.copy()
all_prod = prod_reserves[prod_reserves['Type'].isin(['production', 'production design capacity'])]

# ===== Cell 10 =====
# define million m³/y to million boe/y conversion
mcm_mboe = 0.00588

# ===== Cell 11 =====
# when "Common units" = "million m³/y" multiply by .00588 new "shared unit" column
all_prod.loc[all_prod['Quantity Unit (converted)'] == 'million m³/y', 'shared unit (million boe/y)'] = all_prod['Quantity (converted)'] * .00588

# when common units = million bbl/y or million boe/y, put that value in shared unit column
all_prod.loc[all_prod['Quantity Unit (converted)'].isin(['million bbl/y', 'shared unit (million boe/y)']), 'shared unit (million boe/y)'] = all_prod['Quantity (converted)']
all_prod.loc[all_prod['Quantity Unit (converted)'].isin(['million boe/y', 'shared unit (million boe/y)']), 'shared unit (million boe/y)'] = all_prod['Quantity (converted)']

# sort recent_production_byfuel_converted_df by shared unit (million boe/y) in ascending order
all_prod = all_prod.sort_values(by=['shared unit (million boe/y)'], ascending=[False])



# ===== Cell 12 =====
# Define common identifying columns for comparison
# Note: 'estimated recoverable' and 'conversion type' are only in harmonized_reserves, so they are excluded from the merge key
common_cols = [
    'Project ID', 'Project Name', 'Type', 'Fuel Description',
    'Reserve Classification', 'Quantity', 'Quantity Unit',
    'Quantity (converted)', 'Quantity Unit (converted)', 'Year', 'Country/Area'
]

# Perform a left merge to find rows in reserves that are not in harmonized_reserves
# using indicator=True to show merge origins
reserves_not_in_harmonized = reserves.merge(
    harmonized_reserves[common_cols], # Merge only on common columns from harmonized_reserves
    on=common_cols,
    how='left',
    indicator=True
)

# Filter for rows that are only present in the 'left' (reserves) DataFrame
reserves_only = reserves_not_in_harmonized[reserves_not_in_harmonized['_merge'] == 'left_only'].drop(columns='_merge')

print(f"Found {len(reserves_only)} entries in 'reserves' that are not in 'harmonized_reserves'.")

if not reserves_only.empty:
    print("Here are the first 5 rows of reserves not in harmonized_reserves:")
    print(reserves_only.head())
else:
    print("All entries in 'reserves' appear to be included in 'harmonized_reserves'.")

# ===== Cell 13 =====
reserves_only.drop(columns=['Notes', 'Data Source'], inplace=True)

# ===== Cell 14 =====
# append harmonized_reserves and reserves_not_in_harmonized as "all reserves"
all_reserves = pd.concat([harmonized_reserves, reserves_only])

# ===== Cell 15 =====
all_prod = all_prod.drop(columns=['Notes', 'Reserve Classification'])

# ===== Cell 16 =====
# drop index
all_prod = all_prod.reset_index(drop=True)
all_reserves = all_reserves.reset_index(drop=True)

# ===== Cell 17 =====
# import excel writer
from pandas import ExcelWriter
import os

# Ensure the export directory exists
os.makedirs(export_gen_path, exist_ok=True)

# save all_prod and harmonized_reserves to a excel titled "Full Production and Reserves"
with ExcelWriter(export_gen_path + f'Full Production and Reserves {timestamp}.xlsx') as writer:
    all_prod.to_excel(writer, sheet_name='Production')
    all_reserves.to_excel(writer, sheet_name='Reserves')
