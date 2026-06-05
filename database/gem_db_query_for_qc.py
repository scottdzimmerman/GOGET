"""
gem_db_query_for_qc.py

Migrated from Colab notebook: Calling the GEM Database for QC  [Scott_s Copy].ipynb
Auto-converted to a Python script. Colab-specific lines
(drive.mount, google.colab imports, shell/magic commands) have been
commented out and flagged; pip installs moved to ../requirements.txt.
"""

# # Start

# ===== Cell 1 =====
# import libraries

# import pandas for manipulation
import pandas as pd

# mount google drive
# [colab-only removed] from google.colab import drive
# [colab drive mount removed] drive.mount('/content/drive')
# [colab-only removed] from google.colab import userdata

# Library needed to connect to the database
from sqlalchemy import create_engine, text
import psycopg2

# [moved to requirements.txt] !pip install xlsxwriter

# ===== Cell 2 =====
# name export path
export_gen_path = "/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/GOGET Iterations/Alternative Formats of GOGET/"
export_qc_path = '/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/QC/QC Output Dump/'

# ===== Cell 3 =====
# make timestamp
from datetime import datetime
now = datetime.now()
timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")

print('this runs qc output will all be timestamped: ' + timestamp)

# This is the url we use to connect to the GEM database. This one specific connects to a read-only database that David set up so that people can query the database without worry about editing the database accidentally.
#
# Run the following to cells to connect this jupyter notebook to the database. This will allow you to run queries from this notebook.

# ===== Cell 4 =====
# Set up database pull via URL from the data team.
# (URL updated 2026-02-17 by Scott to reflect new follower database location)
DATABASE_URL = userdata.get('DATABASE_URL')

if DATABASE_URL.startswith('postgres:'):
    DATABASE_URL = DATABASE_URL.replace('postgres:', 'postgresql:')

# Connect to the database
engine = create_engine(DATABASE_URL)
conn = engine.connect()

# ===== Cell 5 =====
# create avaialable table list
def available_tables():
  # Show names of all tables
    query = text("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name
        """)
    table_names = pd.read_sql(query, conn)
    table_names = table_names['table_name'].tolist()
    return table_names

available_tables()

# ===== Cell 6 =====
# function to convert sql tables to dataframes
def get_sql_table(table_name):
   df = pd.read_sql(table_name,conn)
   return df

# ===== Cell 7 =====
plant = get_sql_table("plant")

# ===== Cell 8 =====
country = get_sql_table("country")
geo = get_sql_table("project_geospatial")
goget_project = get_sql_table("goget_project")

# print loaded
print("loaded plant, country, geo, and goget")

# ===== Cell 9 =====
# rename ID in plant as "plant_table_id"
plant = plant.rename(columns={'id': 'plant_table_id'})

# Ensure 'plant_table_id' is of string type for merging
plant['plant_table_id'] = plant['plant_table_id'].astype(str)

# Ensure 'project_id' in goget_project is also of string type for merging
goget_project['project_id'] = goget_project['project_id'].astype(str)

# merge country from plant id
goget_project = goget_project.merge(plant[['plant_table_id', 'country_id', 'latitude', 'longitude' ]], left_on='project_id', right_on='plant_table_id', how='left')

display(goget_project.head())

# ===== Cell 10 =====
# make ID a string, dropping tailing 0
goget_project['country_id'] = pd.to_numeric(goget_project['country_id'], errors='coerce')
goget_project['country_id'] = goget_project['country_id'].fillna(-1).astype('int64')

# merge country onto country ID from plant
goget_project = goget_project.merge(country[['id', 'gemName']], left_on='country_id', right_on='id', how='left')

# ===== Cell 11 =====
goget_project = goget_project.rename(columns={'gemName': 'Country/Area'})
goget_project

# ===== Cell 12 =====
# add wkt to goget_project using project_id from goget_project and project_id from geo as key column
geo['project_id'] = geo['project_id'].astype(str)
goget_project_wkt = goget_project.merge(geo[['project_id', 'wkt']], left_on='project_id', right_on='project_id', how='left')

# check project id = 100001081837 for sucess
display(goget_project_wkt[goget_project_wkt['project_id'] == '100001081837'])

# save out goget_project_wkt
goget_project_wkt.to_excel(export_gen_path + 'goget_project_wkt_' + timestamp + '.xlsx', index=False)

# ===== Cell 13 =====
# drop country_id	and	id_y
goget_project = goget_project.drop(columns=['country_id', 'id_y'])

# ===== Cell 14 =====
goget_project

# ===== Cell 15 =====
# filter status_timeline for only entries in goget_project
status_timeline = get_sql_table("status_timeline")

# Convert 'unit_id' in status_timeline to string type to match 'project_id' in goget_project
status_timeline['unit_id'] = status_timeline['unit_id'].astype(str)

# Perform an inner merge using unit_id from status_timeline and project_id from goget_project
status_timeline_filtered = status_timeline.merge(goget_project[['project_id']], left_on='unit_id', right_on='project_id', how='inner')

# Select only the original columns from status_timeline
status_timeline_merged = status_timeline_filtered[status_timeline.columns]

display(status_timeline_merged.head())

# ===== Cell 16 =====
# filter status_timeline for only entries in goget_project
status_timeline_check = get_sql_table("status_timeline")

# Convert any timezone-aware datetime columns to timezone-unaware
for col in ['created', 'modified']:
    if col in status_timeline_check.columns and pd.api.types.is_datetime64_any_dtype(status_timeline_check[col]):
        if status_timeline_check[col].dt.tz is not None:
            status_timeline_check[col] = status_timeline_check[col].dt.tz_localize(None)

status_timeline_check.to_excel(export_qc_path + 'status_timeline_check_(all)' + timestamp + '.xlsx', index=False)

# ===== Cell 17 =====
# show all notes with "War Impacted" in them
status_timeline_merged[status_timeline_merged['notes'].str.contains('War Impacted', na=False)]

# for some reason, status timelines are not showing when we know there are entries.  [L100001055037](https://gem-project-db.herokuapp.com/projects/edit/100001055037), for example at a discovered year, a start up year, and a current status. but when i check the status timeline for that unit id, it is not there - see row below. It does exist in the goget_project table, but not the status:
#
# project_id = 100001055037
# goget_project[goget_project['project_id'] == project_id] (exists!)
# status_timeline[status_timeline['unit_id'] == project_id] (blank)
#
#

# For some reason, country is not in the GOGET tables. as a work around, download all goget fields from the interface and put that in the qc folder. then merge the Country/Area onto goget projct on Unit ID

# ===== Cell 18 =====
# merge namePrefix from goget_project onto reserves_production using project_id
reserves_production = get_sql_table("reserves_production")
reserves_production['project_id'] = reserves_production['project_id'].astype(str)
# Convert goget_project['project_id'] to string type to match reserves_production
goget_project['project_id'] = goget_project['project_id'].astype(str)
reserves_production_merged = reserves_production.merge(goget_project[["project_id", "namePrefix","Country/Area" ]], on="project_id", how="left")

display(reserves_production_merged.head())

# ===== Cell 19 =====
# count "makeWIKI" entries
make_wiki_count = goget_project['makeWIKI'].value_counts()

print(make_wiki_count)

# QC Steps - Production and reserves

# ===== Cell 20 =====
# check if any productionReserves = "production" and "quantityUnit" does not include "/d" "/y" "day" "pd" or "[per year]"
condition = (reserves_production_merged['productionReserves'] == 'production') & \
            (~reserves_production_merged['quantityUnit'].str.contains('/d|/y|day|pd|[per year]', na=False))

filtered_df = reserves_production_merged[condition]

if not filtered_df.empty:
    print("There are entries where productionReserves is 'production' and quantityUnit does not include the specified substrings.")
    display(filtered_df)
else:
    print("No entries found matching the criteria.")

# ===== Cell 21 =====
# check if any productionReserces = reserves and reserveClassification is missing (None, NaN, or empty string)
condition = (reserves_production_merged['productionReserves'] == 'reserves') & \
            (reserves_production_merged['reserveClassification'].isna() | (reserves_production_merged['reserveClassification'] == ''))

filtered_df = reserves_production_merged[condition]

if not filtered_df.empty:
    print("There are entries where productionReserves is 'reserves' and reserveClassification is missing (NaN or empty string).")
    display(filtered_df)
else:
    print("No entries found matching the criteria.")

# 2025 10 23 - kara arna has a reserve type that needs to be added to the db, so its blank rn
# 2026 01 22 - 100001064253	Konta fixed, Kara-Anna sstill needing reserve type
# fixed kara anna

# ===== Cell 22 =====
# check for exact duplicates in production and reserves
def check_exact_duplicates(df):
    # Group by the specified columns and count occurrences
    duplicates = df.groupby(['productionReserves', 'fuelDesc', 'reserveClassification',	'quantity',	'quantityUnit',	'year', 'project_id']).size().reset_index(name='counts')

    # Filter for counts greater than 1
    duplicates = duplicates[duplicates['counts'] > 1]

    return duplicates

duplicates = check_exact_duplicates(reserves_production_merged)

if not duplicates.empty:
  print("Full entry duplicate entries found, see file duplicate_full_entries_" + timestamp + " in QC dump folder")
  # save out to dump
  duplicates.to_csv(export_qc_path + f"duplicate_full_entries_{timestamp}.csv")
else:
  print("No duplicate entries found.")


# ===== Cell 23 =====
# pull recent production in, filtering by all and specific fuel

# Filter for rows where productionReserves is 'production' or 'production design capacity'
production_df = reserves_production_merged[reserves_production_merged['productionReserves'].isin(['production', 'production design capacity'])].copy() #added pdc of 2026 01 23

# Sort by project_id, fuelDesc, and year in descending order to get the most recent year first
production_df = production_df.sort_values(by=['project_id', 'fuelDesc', 'year'], ascending=[True, True, False])

# Drop duplicate project_id and fuelDesc combinations, keeping the first row (which is the most recent year)
recent_production_byfuel_df = production_df.drop_duplicates(subset=['project_id', 'fuelDesc'])

# Drop duplicates so any fuel counts - use this for recent status
recent_production_overall_df = recent_production_byfuel_df.drop_duplicates(subset=['project_id'])

# rename year to prodyear
recent_production_byfuel_df = recent_production_byfuel_df.rename(columns={'year': 'prodyear'})
recent_production_overall_df = recent_production_overall_df.rename(columns={'year': 'prodyear'})

# Select the desired columns
recent_production_byfuel_df = recent_production_byfuel_df[['project_id', 'namePrefix', 'fuelDesc', 'prodyear', 'quantity', 'quantityUnit','Country/Area']]
recent_production_overall_df = recent_production_overall_df[['project_id', 'namePrefix', 'prodyear', 'quantity', 'quantityUnit','Country/Area']]

display(recent_production_overall_df.head())

# ===== Cell 24 =====
#Convert to common units (million bbl and million cubic meters)

# combine 'fuelDesc' and 'quantityUnit' as "Fuel_quantity" in recent_production_byfuel_df
recent_production_byfuel_df['Fuel_quantity'] = recent_production_byfuel_df['fuelDesc'] + ' ' + recent_production_byfuel_df['quantityUnit']

# unique fuel_quanity to make sure all are on conversion sheet
unique_fuel_quantity = recent_production_byfuel_df['Fuel_quantity'].unique()

# import conversion factors
conversion_factors = pd.read_csv('/content/drive/MyDrive/GOGET q4 2025/GOGET oil & gas extraction sites conversion factors for QC  2025 11 18 - Conversion factors.csv')

# compare conversion factors "Fuel description + Units (original)" to unique_fuel_quantity looking for missing entries
missing_entries = []
for entry in unique_fuel_quantity:
    if entry not in conversion_factors['Fuel description + Units (original)'].values:
        missing_entries.append(entry)
        print(f"Missing entry: {entry}") # Print missing entries as they are found

# After the loop, check if any entries were missing
if not missing_entries:
    print("No missing entries found.")

# ===== Cell 25 =====
# Apply conversion factors and add new columns

# Ensure conversion_factors has unique 'Fuel description + Units (original)' before merging
# This assumes that for duplicate 'Fuel description + Units (original)', the 'Conversion factor' and 'Common units' are identical or we want to pick one arbitrarily.
# Given the earlier output, they appear to be identical.
unique_conversion_factors = conversion_factors.drop_duplicates(subset=['Fuel description + Units (original)'], keep='first')

recent_production_byfuel_converted_df = recent_production_byfuel_df.merge(
    unique_conversion_factors[['Fuel description + Units (original)', 'Conversion factor', 'Common units']],
    left_on='Fuel_quantity',
    right_on='Fuel description + Units (original)',
    how='left'
)

# Apply the conversion factor to the quantity
recent_production_byfuel_converted_df['quantity_converted'] = recent_production_byfuel_converted_df['quantity'] * recent_production_byfuel_converted_df['Conversion factor']

# Select and rename the desired columns
recent_production_byfuel_converted_df = recent_production_byfuel_converted_df[[
    'project_id',
    'namePrefix',
    'Country/Area',
    'fuelDesc',
    'prodyear',
    'quantity',
    'quantityUnit',
    'quantity_converted',
    'Common units'
]]

# ===== Cell 26 =====
# when "Common units" = "million m³/y" multiply by .00588 new "shared unit" column
recent_production_byfuel_converted_df.loc[recent_production_byfuel_converted_df['Common units'] == 'million m³/y', 'shared unit (million boe/y)'] = recent_production_byfuel_converted_df['quantity_converted'] * .00588

# when common units = million bbl/y or million boe/y, put that value in shared unit column
recent_production_byfuel_converted_df.loc[recent_production_byfuel_converted_df['Common units'].isin(['million bbl/y', 'shared unit (million boe/y)']), 'shared unit (million boe/y)'] = recent_production_byfuel_converted_df['quantity_converted']

# sort recent_production_byfuel_converted_df by shared unit (million boe/y) in ascending order
recent_production_byfuel_converted_df = recent_production_byfuel_converted_df.sort_values(by=['shared unit (million boe/y)'], ascending=[False])

# ===== Cell 27 =====
# sum by country, keeping million bbl/y	and million m³/y seperate, dropping other columns, average year prodyear
country_recent_prod = recent_production_byfuel_converted_df.groupby(['Country/Area', 'fuelDesc'], as_index=False).agg({
    'shared unit (million boe/y)': 'sum'
})

# sort on shared unit (million boe/y) high to low
country_recent_prod = country_recent_prod.sort_values(by=['shared unit (million boe/y)'], ascending=[False])

country_recent_prod

# ===== Cell 28 =====
country_recent_prod.to_csv(export_qc_path + 'country_recent_prod_' + timestamp + '.csv', index=False)

# ===== Cell 29 =====
# follow the same process for reserves
# pull recent production in, filtering by all and specific fuel

# Filter for rows where productionReserves is 'reserves"
reserves_df = reserves_production_merged[reserves_production_merged['productionReserves'].isin(['reserves'])].copy()

# Sort by project_id, fuelDesc, reserveClassification, and year in descending order to get the most recent year first
reserves_df = reserves_df.sort_values(by=['project_id', 'fuelDesc', 'reserveClassification', 'year'], ascending=[True, True, True, False])

# Drop duplicate project_id, fuelDesc, and reserveClassification combinations, keeping the first row (which is the most recent year for that combination)
recent_reserves_byfuel_df = reserves_df.drop_duplicates(subset=['project_id', 'fuelDesc', 'reserveClassification'])

# Drop duplicates so only one reserve entry is kept for each project (the most recent one based on the previous sort)
recent_reserves_overall_df = recent_reserves_byfuel_df.drop_duplicates(subset=['project_id'])

# rename year to prodyear
recent_reserves_byfuel_df = recent_reserves_byfuel_df.rename(columns={'year': 'reserveyear'})
recent_reserves_overall_df = recent_reserves_overall_df.rename(columns={'year': 'reserveyear'})

# Select the desired columns
recent_reserves_byfuel_df = recent_reserves_byfuel_df[['project_id', 'namePrefix', 'fuelDesc', 'reserveyear', 'reserveClassification', 'quantity', 'quantityUnit','Country/Area']]
recent_reserves_overall_df = recent_reserves_overall_df[['project_id', 'namePrefix', 'reserveyear', 'reserveClassification', 'quantity', 'quantityUnit','Country/Area']]

display(recent_reserves_overall_df.head())

# ===== Cell 30 =====
#Convert to common units (million bbl and million cubic meters)

# combine 'fuelDesc' and 'quantityUnit' as "Fuel_quantity" in recent_reserves_byfuel_df
recent_reserves_byfuel_df['Fuel_quantity'] = recent_reserves_byfuel_df['fuelDesc'] + ' ' + recent_reserves_byfuel_df['quantityUnit']

# unique fuel_quanity to make sure all are on conversion sheet
unique_fuel_quantity = recent_reserves_byfuel_df['Fuel_quantity'].unique()

# import conversion factors
conversion_factors = pd.read_csv('/content/drive/MyDrive/GOGET q4 2025/GOGET oil & gas extraction sites conversion factors for QC  2025 11 18 - Conversion factors.csv')


# compare conversion factors "Fuel description + Units (original)" to unique_fuel_quantity looking for missing entries
missing_entries = []
for entry in unique_fuel_quantity:
    if entry not in conversion_factors['Fuel description + Units (original)'].values:
        missing_entries.append(entry)
        print(f"Missing entry: {entry}") # Print missing entries as they are found
# After the loop, check if any entries were missing
if not missing_entries:
    print("No missing entries found.")

# ===== Cell 31 =====
# Apply conversion factors and add new columns

# Ensure conversion_factors has unique 'Fuel description + Units (original)' before merging
# This assumes that for duplicate 'Fuel description + Units (original)', the 'Conversion factor' and 'Common units' are identical or we want to pick one arbitrarily.
# Given the earlier output, they appear to be identical.
unique_conversion_factors = conversion_factors.drop_duplicates(subset=['Fuel description + Units (original)'], keep='first')

recent_reserves_byfuel_converted_df = recent_reserves_byfuel_df.merge(
    unique_conversion_factors[['Fuel description + Units (original)', 'Conversion factor', 'Common units']],
    left_on='Fuel_quantity',
    right_on='Fuel description + Units (original)',
    how='left'
)

# Apply the conversion factor to the quantity
recent_reserves_byfuel_converted_df['quantity_converted'] = recent_reserves_byfuel_converted_df['quantity'] * recent_reserves_byfuel_converted_df['Conversion factor']

# Select and rename the desired columns
recent_reserves_byfuel_converted_df = recent_reserves_byfuel_converted_df[[
    'project_id',
    'namePrefix',
    'Country/Area',
    'fuelDesc',
    'reserveClassification',
    'reserveyear',
    'quantity',
    'quantityUnit',
    'quantity_converted',
    'Common units'
]]

# ===== Cell 32 =====
# when "Common units" = "million m³/y" multiply by .00588 new "shared unit" column
recent_reserves_byfuel_converted_df.loc[recent_reserves_byfuel_converted_df['Common units'] == 'million m³', 'shared unit (million boe)'] = recent_production_byfuel_converted_df['quantity_converted'] * .00588

# when common units = million bbl/y or million boe/y, put that value in shared unit column
recent_reserves_byfuel_converted_df.loc[recent_reserves_byfuel_converted_df['Common units'].isin(['million bbl', 'shared unit (million boe)']), 'shared unit (million boe)'] = recent_reserves_byfuel_converted_df['quantity_converted']

# sort recent_production_byfuel_converted_df by shared unit (million boe/y) in ascending order
recent_reserves_byfuel_converted_df = recent_reserves_byfuel_converted_df.sort_values(by=['shared unit (million boe)'], ascending=[False])

# ===== Cell 33 =====
# Select relevant columns for production and rename for clarity
prod_compare_df = recent_production_byfuel_converted_df[['project_id', 'shared unit (million boe/y)']].rename(columns={'shared unit (million boe/y)': 'production_boe'})

# Select relevant columns for reserves and rename for clarity
res_compare_df = recent_reserves_byfuel_converted_df[['project_id', 'shared unit (million boe)']].rename(columns={'shared unit (million boe)': 'reserves_boe'})

# sum all values for each project id in both dfs
prod_compare_df = prod_compare_df.groupby('project_id').sum().reset_index()
res_compare_df = res_compare_df.groupby('project_id').sum().reset_index()

# Merge the two dataframes on project_id
# Using an inner merge to only include projects present in both production and reserves
comparison_df = pd.merge(prod_compare_df, res_compare_df, on='project_id', how='inner')

# Filter for entries where production value is higher than reserves value
projects_production_gt_reserves = comparison_df[comparison_df['production_boe'] > comparison_df['reserves_boe']]

# caculate the difference between production and reserves
projects_production_gt_reserves['difference'] = projects_production_gt_reserves['production_boe'] - projects_production_gt_reserves['reserves_boe']

# sort on difference
projects_production_gt_reserves = projects_production_gt_reserves.sort_values(by=['difference'], ascending=[False])

# Display the results
if not projects_production_gt_reserves.empty:
    print("Projects where production value is higher than reserves value:")
    display(projects_production_gt_reserves)
else:
    print("No projects found where production value is higher than reserves value.")

# ===== Cell 34 =====
# save projects_production_gt_reserves to qc dump
projects_production_gt_reserves.to_csv(export_qc_path + timestamp +'projects_production_gt_reserves.csv', index=False)

# ===== Cell 35 =====
# save out unique reserveClassification csv for conversion first pass
unique_reserve_classification = recent_reserves_byfuel_converted_df['reserveClassification'].unique()
unique_reserve_classification_df = pd.DataFrame(unique_reserve_classification, columns=['reserveClassification'])
unique_reserve_classification_df.to_csv(f"{export_qc_path}unique_reserve_classification_{timestamp}.csv", index=False)

# ===== Cell 36 =====
# Filter out rows where substatus is 'planned'
filtered_status_timeline = status_timeline_merged[status_timeline_merged['substatus'] != 'planned'].copy()

# sort by order, low to high
filtered_status_timeline = filtered_status_timeline.sort_values(by=['order'])

# Drop duplicate unit_id, keeping the lowest ranked row (which is the most recent status)
current_status_rank_df = filtered_status_timeline.drop_duplicates(subset=['unit_id'], keep='last')

# Rename 'unit_id' to 'project_id' for clarity and select relevant columns
current_status_rank_df = current_status_rank_df.rename(columns={'unit_id': 'project_id'})
current_status_rank_df = current_status_rank_df[['project_id', 'status', 'substatus', 'year']]

display(current_status_rank_df.head())

# ===== Cell 37 =====
# current status was caclucated by most recent year, now we are using rank
current_status_df = current_status_rank_df # using rank over year for most recent data

# ===== Cell 38 =====
# create new df with name, most recent production and most recent status
status_production = goget_project.copy()
current_status_df['project_id'] = current_status_df['project_id'].astype(str)
status_production = status_production.merge(current_status_df, on='project_id', how='left')

# Merge with recent_production_overall_df, specifying custom suffixes
# This will result in columns like 'namePrefix_goget' and 'Country/Area_goget' from the left dataframe (status_production)
# and 'namePrefix_prod' and 'Country/Area_prod' from the right dataframe (recent_production_overall_df)
status_production = status_production.merge(
    recent_production_overall_df,
    on='project_id',
    how='left',
    suffixes=('_goget', '_prod')
)

# Select only the desired columns.
# We assume 'namePrefix_goget' corresponds to the original 'namePrefix' from goget_project.
# Other 'Country/Area' columns are implicitly dropped as they are not selected.
status_production = status_production[['project_id', 'namePrefix_goget', 'status', 'substatus', 'year', 'prodyear', 'quantity', 'quantityUnit']]
status_production = status_production.rename(columns={'namePrefix_goget': 'namePrefix'})

display(status_production.head())

# ===== Cell 39 =====
#filter for where prodyear is greater than 2020,  but status	is blank
filtered_df = status_production[(status_production['prodyear'] > 2020) & (status_production['status'].isna())]

# filter out for when quantity is 0
filtered_df = filtered_df[filtered_df['quantity'] > 0]

# ===== Cell 40 =====
filtered_df # all of these acutally have a status, but my code is missing it. for some reason, they appear in the goget_project, but not in the status_timeline

# ===== Cell 41 =====
# this checks if an unit has multiple reserve data points from the same year # as of 2026 01 23 - these are just Kara Ana, which will be fixed once that reserve type is in
def check_duplicates(df):
    # Group by the specified columns and count occurrences
    close_to_duplicates = df.groupby(['project_id', 'productionReserves','reserveClassification' ,'fuelDesc', 'year']).size().reset_index(name='counts')

    # Filter for counts greater than 1
    close_to_duplicates = close_to_duplicates[close_to_duplicates['counts'] > 1]

    return close_to_duplicates

close_to_duplicates = check_duplicates(reserves_production_merged)

if not close_to_duplicates.empty:
  print("Repeat year, fuel description, entries found, see file duplicate_entries_"  +timestamp + " in QC dump folder")
  # save out to dump
  close_to_duplicates.to_csv(export_qc_path + f"duplicate_reserve_entries_{timestamp}.csv")
else:
  print("No duplicate entries found.")

# ===== Cell 42 =====
# this checks if an unit has multiple production data points from the same year - as of 2025-10-24 there were no entries found here!
def check_prod_duplicates(df):

    # filter for just production entries
    prod_dups_check = df[df['productionReserves'] == 'production']
    # Group by the specified columns and count occurrences
    prod_dups_check = prod_dups_check.groupby(['project_id' , 'namePrefix', 'fuelDesc', 'year']).size().reset_index(name='counts')

    # Filter for counts greater than 1
    prod_dups_check = prod_dups_check[prod_dups_check['counts'] > 1]

    return prod_dups_check

prod_dups_check = check_prod_duplicates(reserves_production_merged)

if not prod_dups_check.empty:
  print("Repeat year, fuel description, entries found see file duplicate_production_"  +timestamp + " in QC dump folder")
  # save out to dump
  prod_dups_check.to_csv(export_qc_path + f"duplicate_production_{timestamp}.csv")
else:
  print("No duplicate entries found.")

# ===== Cell 43 =====
# discovery to start up timeline
disco_to_start = status_timeline_merged.copy()

# discovery year = earliest status entry where status = "discovered"
disco_to_start['Discovery Year'] = status_timeline_merged[status_timeline_merged['status'] == 'discovered'].groupby('unit_id')['year'].transform('min')

# start year = earliest status of "operating"
disco_to_start['Start Year'] = status_timeline_merged[(status_timeline_merged['status'] == 'operating') & (status_timeline_merged['substatus'] == 'ramp up')].groupby('unit_id')['year'].transform('min')

# ===== Cell 44 =====
# Extract unique Discovery Year for each unit_id
discovery_years = disco_to_start.dropna(subset=['Discovery Year'])[['unit_id', 'Discovery Year']].drop_duplicates(subset=['unit_id'])

# Extract unique Start Year for each unit_id
start_years = disco_to_start.dropna(subset=['Start Year'])[['unit_id', 'Start Year']].drop_duplicates(subset=['unit_id'])

# Merge the two DataFrames on unit_id to get one row per unit_id
discovery_start_years = pd.merge(discovery_years, start_years, on='unit_id', how='outer')

# calculate the discovery to start year for each unit. If both values are not blank Start Year - Discovery Year
discovery_start_years['Discovery to Start Year'] = discovery_start_years['Start Year'] - discovery_start_years['Discovery Year']

# ===== Cell 45 =====
# sort discovery_start_years on Discovery to Start Year
discovery_start_years = discovery_start_years.sort_values(by=['Discovery to Start Year'])

# define problematic data
problematic_data = discovery_start_years[(discovery_start_years['Discovery to Start Year'] < 0) | (discovery_start_years['Discovery to Start Year'] > 60)]

# display problematic data
display(problematic_data)

# ===== Cell 46 =====
goget_project.columns

# In the feb 2024 release, 1998 fields had a start year and discovery year

# ===== Cell 47 =====
# keep just lat long and "Unit ID" column
GOGET_coordinates = goget_project[['project_id', 'latitude', 'longitude']]


# Merge wkt (coordinates) from goget_project_wkt onto status_timeline_merged
# The unit_id in status_timeline_merged corresponds to project_id in goget_project_wkt
status_timeline_merged['unit_id'] = status_timeline_merged['unit_id'].astype(str)
status_timeline_with_coord = status_timeline_merged.merge(
    GOGET_coordinates[['project_id', 'latitude', 'longitude']],
    left_on='unit_id',
    right_on='project_id',
    how='left'
)

# Drop the redundant 'project_id' column that resulted from the merge if you only need 'unit_id'
status_timeline_with_coord = status_timeline_with_coord.drop(columns=['project_id'])

print("First 5 rows of status_timeline_with_wkt with coordinates:")
display(status_timeline_with_coord.head())

# ===== Cell 48 =====
# check for 2025 FIDs
fid_2025 = status_timeline_merged[(status_timeline_merged['status'] == 'in-development') & (status_timeline_merged['substatus'] == 'actual') & (status_timeline_merged['year'] == 2025)]

display(fid_2025)

# ===== Cell 49 =====
# check for 2025 discoveries
disco_2025 = status_timeline_merged[(status_timeline_merged['status'] == 'discovered') & (status_timeline_merged['substatus'] == 'early') & (status_timeline_merged['year'] == 2025)]

display(disco_2025)

# ===== Cell 50 =====
# Function to check for start-ups in a given year
def count_startups_by_year(year, status_timeline_df):
    startups = status_timeline_df[
        (status_timeline_df['status'] == 'operating') &
        (status_timeline_df['substatus'] == 'ramp up') &
        (status_timeline_df['year'] == year)
    ]
    return startups.shape[0]

# Years to check
years_to_check = [2025, 2024, 2023, 2022, 2021, 2020]

# Display counts for each year
for year in years_to_check:
    count = count_startups_by_year(year, status_timeline_merged)
    print(f"{year} start-ups: {count}")

# ===== Cell 51 =====
# make a df for each of the years in years to check then exports as a tabbed excel with each year having its own tab

# Create an empty dictionary to store DataFrames for each year
year_startups_dfs = {}

for year in years_to_check:
    # Filter status_timeline_merged for startups in the current year
    startups_for_year = status_timeline_with_coord[
        (status_timeline_with_coord['status'] == 'operating') &
        (status_timeline_with_coord['substatus'] == 'ramp up') &
        (status_timeline_with_coord['year'] == year)
    ].copy()

    # Convert any timezone-aware datetime columns to timezone-unaware
    for col in ['created', 'modified']:
        if col in startups_for_year.columns and pd.api.types.is_datetime64_any_dtype(startups_for_year[col]):
            if startups_for_year[col].dt.tz is not None:
                startups_for_year[col] = startups_for_year[col].dt.tz_localize(None)

    # Ensure project_id is string type for merging
    startups_for_year['unit_id'] = startups_for_year['unit_id'].astype(str)
    goget_project['project_id'] = goget_project['project_id'].astype(str)

    # Merge with goget_project to get namePrefix
    startups_for_year_merged = startups_for_year.merge(
        goget_project[['project_id', 'namePrefix']],
        left_on='unit_id',
        right_on='project_id',
        how='left'
    )

    # Store the DataFrame in the dictionary
    year_startups_dfs[f'Startups_{year}'] = startups_for_year_merged

# Define the output Excel file path
excel_output_path = export_qc_path + f'yearly_startups_{timestamp}.xlsx'

# Create a Pandas Excel writer using XlsxWriter as the engine.
# This allows writing multiple sheets to the same file.
with pd.ExcelWriter(excel_output_path, engine='xlsxwriter') as writer:
    for sheet_name, df in year_startups_dfs.items():
        df.to_excel(writer, sheet_name=sheet_name, index=False)

print(f"Yearly startups exported to: {excel_output_path}")

# ===== Cell 52 =====
# merge name for goget_project to disco_2025 on unit_id
disco_2025 = disco_2025.merge(goget_project[['project_id', 'namePrefix']], left_on='unit_id', right_on='project_id', how='left')

# merge name from goget_project to fid_2025 on unit_id
fid_2025 = fid_2025.merge(goget_project[['project_id', 'namePrefix']], left_on='unit_id', right_on='project_id', how='left')

# merge namme from goget_project to sstart_2025 on unit id
start_2025 = start_2025.merge(goget_project[['project_id', 'namePrefix']], left_on='unit_id', right_on='project_id', how='left')

# ===== Cell 53 =====
# save recent_production_df to export_qc_path
status_production.to_csv(export_qc_path + 'status_production_' + timestamp + '.csv', index=False)
filtered_df.to_csv(export_qc_path + 'filtered_df_' + timestamp + '.csv', index=False)
current_status_df.to_csv(export_qc_path + 'current_status_df_' + timestamp + '.csv', index=False)
recent_production_byfuel_df.to_csv(export_qc_path + 'recent_production_byfuel_df_' + timestamp + '.csv', index=False)
recent_production_byfuel_converted_df.to_csv(export_qc_path + 'recent_production_byfuel_converted_df_' + timestamp + '.csv', index=False)
fid_2025.to_csv(export_qc_path + 'fid_2025_' + timestamp + '.csv', index=False)
disco_2025.to_csv(export_qc_path + 'disco_2025_' + timestamp + '.csv', index=False)
# start_2025.to_csv(export_qc_path + 'start_2025_' + timestamp + '.csv', index=False)
