"""
filter_data.py

Migrated from Colab notebook: GOGET_filter_data_2_6_23.ipynb
Auto-converted to a Python script. Colab-specific lines
(drive.mount, google.colab imports, shell/magic commands) have been
commented out and flagged; pip installs moved to ../requirements.txt.
"""

# # GOGET filter number of fields down

# ===== Cell 1 =====
import pandas as pd
import numpy as np
import time
import os
import requests

# ===== Cell 2 =====
# [colab-only removed] from google.colab import auth
auth.authenticate_user()

import gspread
from google.auth import default
creds, _ = default()

gc = gspread.authorize(creds)

# ===== Cell 3 =====
sh = gc.open('GOGET oil & gas extraction sites (main data set)')

main_data_sheet =  sh.get_worksheet(0)  # 0 means the first sheet in the file
prodandreserves_sheet = sh.get_worksheet(1)
ownership_sheet = sh.get_worksheet(2)

goget_main = pd.DataFrame(main_data_sheet.get_all_records())
goget_prodandreserves = pd.DataFrame(prodandreserves_sheet.get_all_records())
goget_ownership = pd.DataFrame(ownership_sheet.get_all_records())

# ===== Cell 4 =====
# [colab-only removed] from google.colab import drive
# [colab drive mount removed] drive.mount('/content/drive')

# ===== Cell 5 =====
gem_path = '/content/drive/My Drive/GOGET Q1 2023'

# ===== Cell 6 =====
# create timestamp for the whole batch
page_creation_timestamp = time.strftime('%Y-%m-%d_%H%M%S', time.localtime())

# ===== Cell 7 =====
# Drop empty rows and columns in Main sheet
main_df = goget_main.copy()
main_df['Unit ID'] = main_df['Unit ID'].replace('', np.nan)
main_df = main_df.dropna(subset=['Unit ID'])

for col in main_df.columns:
     if 'Unnamed: ' in col:
        main_df = main_df.drop(col, axis=1)

fields = main_df.copy()

print(f"Number of rows after filtering: {len(fields)}")

# ===== Cell 8 =====
# Drop empty columns in Production & Reserves sheet
prodandreserves_df = goget_prodandreserves.copy()
prodandreserves_df['Unit ID'] = prodandreserves_df['Unit ID'].replace('', np.nan)
prodandreserves_df['Quantity (converted)'] = prodandreserves_df['Quantity (converted)'].replace('[#N/A', 0)
prodandreserves_df = prodandreserves_df.dropna(subset=['Unit ID'])

for col in prodandreserves_df.columns:
    if 'Unnamed: ' in col:
        prodandreserves_df = prodandreserves_df.drop(col, axis=1)

print(f"Number of rows after filtering: {len(prodandreserves_df)}")

# ===== Cell 9 =====
# keep only the most recent year of data for each category

df = prodandreserves_df.copy()

print(f"len(prodandreserves_df): {len(prodandreserves_df)}")
df['Reserves classification (original)'] = df['Reserves classification (original)'].fillna('')

df['combo'] = '' # initialize new column

# create the entries in 'combo' by combining the strings in each column
for col in ['Unit ID', 'Unit ID', 'Country', 'Production/reserves', 'Fuel description', 'Reserves classification (original)']:
    df['combo'] = df['combo'].astype(str).fillna('') + '_' + df[col]
    df['combo'] = df['combo'].str.strip('_')

counts_all = df.groupby('combo')['Data year'].count()

# clean up Data year column
df['Data year'] = df['Data year'].replace('[not stated]', 0)
df['Data year'] = df['Data year'].astype(str).str.replace(' predicted', '', regex=False)
df['Data year'] = df['Data year'].astype(float)

data_year_max_all = df.groupby('combo')['Data year'].max()

multiple_counts = counts_all[counts_all > 1]

to_condense = df[df['combo'].isin(multiple_counts.index)]
print(f"len(to_condense): {len(to_condense)}")
already_condensed = df[~df['combo'].isin(multiple_counts.index)]

newly_condensed = pd.DataFrame() # initialize
for combo in multiple_counts.index:
    # get data_year_max
    data_year_max = data_year_max_all.at[combo]

    df_max_year = df[(df['combo']==combo) & (df['Data year']==data_year_max)]

    newly_condensed = newly_condensed.append(df_max_year, sort=False)

print(f"len(newly_condensed): {len(newly_condensed)}")

# recombine newly_condensed & already_condensed
recombined = pd.concat([already_condensed, newly_condensed], sort=False)

recombined['Data year'] = recombined['Data year'].astype(str).replace('0', '[not stated]')

# add check to find those with more than one row for a given set of prod/res
data_year_counts = recombined.groupby('combo')['Data year'].count()
data_year_counts_multi = data_year_counts[data_year_counts > 1]
multiple_rows = recombined[recombined['combo'].isin(data_year_counts_multi.index)]
if len(multiple_rows)>0:
    # export file
    save_timestamp = time.strftime('%Y-%m-%d_%H%M%S', time.localtime())
    multiple_rows.to_excel(
        gem_path + '/Filtered fields/'+ f'GOGET results with multiple rows {save_timestamp}.xlsx',
        index=False
    )

# drop the column 'combo' added here
recombined = recombined.drop('combo', axis=1)
prodandreserves_df = recombined

print(f"len(recombined): {len(recombined)}")
print(f"len(prodandreserves_df): {len(prodandreserves_df)}")

# ===== Cell 10 =====
# Drop empty columns in Ownership sheet
ownership_df = goget_ownership.copy()
ownership_df = ownership_df.dropna(subset=['Owner'])

for col in ownership_df.columns:
    if 'Unnamed: ' in col:
        ownership_df = ownership_df.drop(col, axis=1)

print(f"Number of rows after filtering: {len(ownership_df)}")

# ===== Cell 11 =====
# Filter out fields that have no production or reserves data

print(f"Number of fields: {len(main_df)}")
no_prod = main_df[main_df['Production data?'].isin([
    'no data - no entry on production & reserve sheet',
    'no data']
)]
no_res = main_df[main_df['Reserves data?'].isin([
        'no data - no entry on production & reserve sheet',
        'no data']
)]

no_prod_and_no_res = main_df[
    (main_df['Unit ID'].isin(no_prod['Unit ID'])) &
    (main_df['Unit ID']).isin(no_res['Unit ID'])
]

fields = main_df[~main_df['Unit ID'].isin(no_prod_and_no_res['Unit ID'])]

print(f"Number of fields with some production or reserves data: {len(fields)}")

# ===== Cell 12 =====
print(df['Quantity (converted)'])

# ===== Cell 13 =====
df = prodandreserves_df.copy()

# filter for production only
df = df.copy()[df['Production/reserves']=='production']

df = df[['Unit ID', 'Country', 'Subnational unit (province, state)', 'Quantity (converted)', 'Units (converted)']]

# float Quantity (converted) to number
df['Quantity (converted)'].astype(float, 'coerce')

# convert values to total HC (boe)
gas_mask = df['Units (converted)']=='million m³/y'
df_gas = df.copy()[gas_mask]
million_boe_per_billion_cubic_meters_gas = 5.883
df_gas['total HC million boe/y'] = (df_gas['Quantity (converted)']/1000) * million_boe_per_billion_cubic_meters_gas

# oil & condensates
df_other = df.copy()[~gas_mask]
df_other['total HC million boe/y'] = df_other['Quantity (converted)']

# recombine
df = pd.concat([df_gas, df_other], sort=False)

df['Country_State'] = df['Country'] + '_' + df['Subnational unit (province, state)']
df['Country_State'] = df['Country_State'].str.strip('_')

df_grouped = df.groupby(['Unit ID', 'Country_State'])[['total HC million boe/y']].sum()
df_grouped = df_grouped.reset_index()

areas_with_comprehensive_data = ['United Kingdom',
                                 'Argentina', 'Peru', 'India', 'Germany',
                                 'Poland', 'Denmark', 'Norway', 'Colombia',
                                 'Netherlands', 'Mexico',
                                 'Canada_British Columbia', 'Canada_Alberta',
                                 'Canada_Saskatchewan', 'Canada_Manitoba',
                                 'Australia_Queensland','United States_Alaska','United States_Texas','United States_Colorado','United States_Louisiana',
                                 "United States_New Mexico", "United States_Ohio","United States_Wyoming","United States_West Virginia","United States_Pennsylvania"
                                 ]

fraction_of_total_production_covered = 0.95

ids_we_are_keeping = [] # initialize

# COMPREHENSIVE DATA
for area in areas_with_comprehensive_data:
  print(f"processing {area}")
  df_area = df_grouped[df_grouped['Country_State']==area]
  print(f"total number of Unit IDs for this area: {len(df_area)}")

  df_area = df_area.sort_values(by=['total HC million boe/y'], ascending=False)
  df_area['total HC (boe) cumul fract'] = df_area['total HC million boe/y'].cumsum() / df_area['total HC million boe/y'].sum()

  df_area_95 = df_area.loc[(df_area['total HC (boe) cumul fract'] <= fraction_of_total_production_covered)].copy()
  df_area_95_ids = df_area_95['Unit ID'].tolist()

  print(f"number of Unit IDs over threshold: {len(df_area_95_ids)}")

  ids_we_are_keeping += df_area_95_ids

  print(f"number of IDs in collection (all areas): {len(ids_we_are_keeping)}")

# NO COMPREHENSIVE DATA - PRODUCTION THRESHOLD
df_no_comp_data = df[~df['Country_State'].isin(areas_with_comprehensive_data)]
ids_over_prod_threshold = df[df['total HC million boe/y']>1]['Unit ID'].tolist()
ids_we_are_keeping += ids_over_prod_threshold

ids_we_are_keeping = list(set(ids_we_are_keeping))

print(f"number of IDs in collection (all areas): {len(ids_we_are_keeping)}")

# ===== Cell 14 =====
def reserves_threshold(prodandreserves_df, areas_with_comprehensive_data, ids_we_are_keeping):
  df_res = prodandreserves_df.copy()

  df_res['Country_State'] = df_res['Country'] + '_' + df_res['Subnational unit (province, state)']
  df_res['Country_State'] = df_res['Country_State'].str.strip('_')

  # filter for production only
  df_res = df_res.copy()[df_res['Production/reserves']=='reserves']

  df_res = df_res[['Unit ID', 'Country_State', 'Quantity (converted)', 'Units (converted)']]

  # convert values to total HC (boe)
  res_gas_mask = df_res['Units (converted)']=='million m³'
  df_res_gas = df_res.copy()[res_gas_mask]
  million_boe_per_billion_cubic_meters_gas = 5.883
  df_res_gas['total HC million boe'] = (df_res_gas['Quantity (converted)']/1000) * million_boe_per_billion_cubic_meters_gas

  # oil & condensates
  df_res_other = df_res.copy()[~res_gas_mask]
  df_res_other['total HC million boe'] = df_res_other['Quantity (converted)']

  # recombine
  df_res = pd.concat([df_res_gas, df_res_other], sort=False)

  df_res_max = df_res.groupby(['Unit ID', 'Country_State'])[['total HC million boe']].max()
  df_res_max = df_res_max.reset_index()

  df_res_max_no_comp = df_res_max[~df_res_max['Country_State'].isin(areas_with_comprehensive_data)]

  res_threshold = 25 # units: million boe
  fields_over_res_threshold = df_res_max_no_comp[df_res_max_no_comp['total HC million boe']>=res_threshold]
  ids_over_res_threshold = fields_over_res_threshold['Unit ID'].tolist()

  print(fields_over_res_threshold[~fields_over_res_threshold['Unit ID'].isin(ids_we_are_keeping)][['Unit ID', 'total HC million boe']].head(20))

  len_ids_we_are_keeping_init = len(ids_we_are_keeping)
  ids_we_are_keeping += ids_over_res_threshold
  ids_we_are_keeping = list(set(ids_we_are_keeping))
  number_of_new_ids = len(ids_we_are_keeping) - len_ids_we_are_keeping_init
  print(f"number of new IDs added based on reserves threshold: {number_of_new_ids}")
  print(f"number of IDs in ids_we_are_keeping: {len(ids_we_are_keeping)}")

  return ids_we_are_keeping

# ===== Cell 15 =====
ids_we_are_keeping = reserves_threshold(prodandreserves_df, areas_with_comprehensive_data, ids_we_are_keeping)

# ===== Cell 16 =====
# Export excel file of filtered fields
goget_main_filtered_df = fields[fields['Unit ID'].isin(ids_we_are_keeping)]
goget_prodandreserves_filtered_df = prodandreserves_df[prodandreserves_df['Unit ID'].isin(ids_we_are_keeping)]
gem_path = '/content/drive/Shareddrives/GEM Shared Drive/Projects/Global Oil and Gas Extraction Tracker (GOGET)/Code (GOGET)/'


goget_main_filtered_df.to_excel(gem_path + 'GOGET Main data (filtered) US Fixed 2023-02-06.xlsx', index=False)
goget_prodandreserves_filtered_df.to_excel(gem_path + 'GOGET Production and reserves US Fixed (filtered) 2023-02-06.xlsx', index=False)
