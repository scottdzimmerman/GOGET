"""
filter_compiled_for_region.py

Migrated from Colab notebook: GOGET Filter Compiled for a Region 2024 01 21.ipynb
Auto-converted to a Python script. Colab-specific lines
(drive.mount, google.colab imports, shell/magic commands) have been
commented out and flagged; pip installs moved to ../requirements.txt.
"""

# # Data Filtering for Latin American Countries in Oil and Gas Data
#
# This notebook demonstrates the process of filtering the 'Main data' and 'Production & Reserves' sheets
# from an oil and gas extraction data set for countries in Latin America.
#
# Written by Chat GPT on Jan 23, 2024. Used to generate filtered version of the compiled datasheet for the BBC. Global Oil and Gas Extraction Tracker - 2024-02-22_1039 and the GEM Subregion in GOGET of "Latin America and the Caribbean"

# ===== Cell 1 =====
import pandas as pd

# ## Load the Data
#
# First, we load the data from the provided Excel file.

# ===== Cell 2 =====
file_path = '/content/Global Oil and Gas Extraction Tracker - 2024-02-22_1039.xlsx'  # Replace with your file path
main_data_df = pd.read_excel(file_path, sheet_name="Main data")
production_reserves_df = pd.read_excel(file_path, sheet_name="Production & reserves")
about_sheet_df = pd.read_excel(file_path, sheet_name="About")

# ## Define Latin American Countries
#
# List of countries considered as part of Latin America for this analysis.

# ===== Cell 3 =====
latin_american_countries = [
    "Anguilla", "Antigua and Barbuda", "Argentina", "Aruba", "Bahamas", "Barbados", "Belize", "Bolivia",
    "Bonaire, Sint Eustatius, and Saba", "Bouvet Island", "Brazil", "Cayman Islands", "Chile", "Colombia",
    "Costa Rica", "Cuba", "Curaçao", "Dominica", "Dominican Republic", "Ecuador", "El Salvador",
    "Falkland Islands", "French Guiana", "Grenada", "Guadeloupe", "Guatemala", "Guyana", "Haiti", "Honduras",
    "Jamaica", "Martinique", "Mexico", "Montserrat", "Nicaragua", "Panama", "Paraguay", "Peru", "Puerto Rico",
    "Saint Barthélemy", "Saint Kitts and Nevis", "Saint Lucia", "Saint Martin (French part)",
    "Saint Vincent and the Grenadines", "Sint Maarten (Dutch part)", "South Georgia and the South Sandwich Islands",
    "Suriname", "Trinidad and Tobago", "Turks and Caicos Islands", "Uruguay", "Venezuela", "Virgin Islands (British)",
    "Virgin Islands (U.S.)"
]

# ## Filter the Main Data Sheet
#
# Filtering the 'Main data' sheet for the specified Latin American countries.

# ===== Cell 4 =====
filtered_main_data = main_data_df[main_data_df['Country'].isin(latin_american_countries)]
unit_ids = filtered_main_data['Unit ID'].unique()

# ## Filter the Production & Reserves Sheet
#
# Using the Unit IDs from the filtered main data to filter the 'Production & Reserves' sheet.

# ===== Cell 5 =====
filtered_production_reserves = production_reserves_df[production_reserves_df['Unit ID'].isin(unit_ids)]

# ## Save the Filtered Data
#
# Saving the filtered data into a new Excel file.

# ===== Cell 6 =====
output_file_path = 'GOGET - Preliminary Data with Latin America Filter 2024 02 28.xlsx'
with pd.ExcelWriter(output_file_path) as writer:
    filtered_main_data.to_excel(writer, sheet_name="Main data", index=False)
    filtered_production_reserves.to_excel(writer, sheet_name="Production & Reserves", index=False)
    about_sheet_df.to_excel(writer, sheet_name="About", index=False)
