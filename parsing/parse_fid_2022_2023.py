"""
parse_fid_2022_2023.py

Migrated from Colab notebook: Parse 2022 and 2023 FID from Compiled Data
Auto-converted to a Python script. Colab-specific lines
(drive.mount, google.colab imports, shell/magic commands) have been
commented out and flagged; pip installs moved to ../requirements.txt.
"""

# ===== Cell 1 =====
#Loading the Excel File and libraries
import pandas as pd
import numpy as np

file_path = '/content/Global Oil and Gas Extraction Tracker - 2024-02-22_1039.xlsx'
xl = pd.ExcelFile(file_path)

# ===== Cell 2 =====
#setting dataframes with main, P&R
main_data_df = xl.parse('Main data')
production_reserves_df = xl.parse('Production & reserves')

# ===== Cell 3 =====
#Filtering for 2022 and 2023 data
main_data_df["FID Year"] = main_data_df["FID Year"].astype(str).str.replace(" \(expected\)", "", regex=True)
filtered_main_data_df = main_data_df[main_data_df["FID Year"].isin(["2022", "2023"])]

# ===== Cell 4 =====
# Convert 'Data year' to integers in the 'production_reserves_df'
production_reserves_df['Data year'] = pd.to_numeric(production_reserves_df['Data year'], errors='coerce').fillna(-1).astype(int)

# ===== Cell 5 =====
#Define functions for getting the most recent value, calculate the total reserves, calculate the total production and define the conversion factor
# Function to get the most recent value based on the criteria
def get_most_recent_value(unit_id, prod_res, units, df):
    # Filter based on Unit ID, Production/reserves, and Units (converted)
    filtered = df[
        (df["Unit ID"] == unit_id) &
        (df["Production/reserves"] == prod_res) &
        (df["Units (converted)"] == units)
    ]

    # Sort by Data year and get the most recent entry
    filtered = filtered.sort_values(by="Data year", ascending=False)
    return filtered.iloc[0]["Quantity (converted)"] if not filtered.empty else np.nan

# Function to calculate the total reserves
def calculate_total_reserves(row):
    if pd.notna(row['Reserves- Hydrocarbons (unspecified)']):
        return row['Reserves- Hydrocarbons (unspecified)']
    else:
        # Convert gas reserves to boe
        gas_in_boe = row['Reserves- Gas'] * conversion_factor if pd.notna(row['Reserves- Gas']) else 0
        oil_reserves = row['Reserves - Oil'] if pd.notna(row['Reserves - Oil']) else 0
        return gas_in_boe + oil_reserves

# Function to calculate the total production
def calculate_total_production(row):
    if pd.notna(row['Production - Hydrocarbons (unspecified)']):
        return row['Production - Hydrocarbons (unspecified)']
    else:
        # Convert gas production to boe
        gas_in_boe = row['Production - Gas'] * conversion_factor if pd.notna(row['Production - Gas']) else 0
        oil_production = row['Production - Oil'] if pd.notna(row['Production - Oil']) else 0
        return gas_in_boe + oil_production

# Conversion factor from million m³ to million boe for gas
conversion_factor = 5.883 / 1000

# ===== Cell 6 =====
# Populate reserves and production columns with the most recent data
filtered_main_data_df["Reserves - Oil"] = filtered_main_data_df["Unit ID"].apply(lambda x: get_most_recent_value(x, "reserves", "million bbl", production_reserves_df))
filtered_main_data_df["Reserves- Gas"] = filtered_main_data_df["Unit ID"].apply(lambda x: get_most_recent_value(x, "reserves", "million m³", production_reserves_df))
filtered_main_data_df["Reserves- Hydrocarbons (unspecified)"] = filtered_main_data_df["Unit ID"].apply(lambda x: get_most_recent_value(x, "reserves", "million boe", production_reserves_df))

filtered_main_data_df["Production - Oil"] = filtered_main_data_df["Unit ID"].apply(lambda x: get_most_recent_value(x, "production", "million bbl/y", production_reserves_df))
filtered_main_data_df["Production - Gas"] = filtered_main_data_df["Unit ID"].apply(lambda x: get_most_recent_value(x, "production", "million m³/y", production_reserves_df))
filtered_main_data_df["Production - Hydrocarbons (unspecified)"] = filtered_main_data_df["Unit ID"].apply(lambda x: get_most_recent_value(x, "production", "million boe/y", production_reserves_df))

# Calculate total reserves and production
filtered_main_data_df['Reserves- Total (Oil, Gas and Hydrocarbons)'] = filtered_main_data_df.apply(calculate_total_reserves, axis=1)
filtered_main_data_df['Production - Total (Oil, Gas and Hydrocarbons)'] = filtered_main_data_df.apply(calculate_total_production, axis=1)

# ===== Cell 7 =====
filtered_main_data_df

# ===== Cell 8 =====
output_excel_path = '/content/FID20222023 20240222.xlsx'
filtered_main_data_df.to_excel(output_excel_path, index=False)
