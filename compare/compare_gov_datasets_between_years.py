"""
compare_gov_datasets_between_years.py

Migrated from Colab notebook: Compare government datasets between years (2026 03 20)
Auto-converted to a Python script. Colab-specific lines
(drive.mount, google.colab imports, shell/magic commands) have been
commented out and flagged; pip installs moved to ../requirements.txt.
"""

# A simple script for comparing two versions of the exact same dataset.
#
# **Run in playground mode**: file > open in playground mode, and change the commented parts to your datafile.
#
# You will need to create the "Output of automated comparison" folder manually

# ===== Cell 1 =====
# import relevant libraries, panada and datetime
import datetime # this is for timestamping your output
import pandas as pd # pandas is a super helpful package for analysis of tabular data

# Mount google drive - this is so you can import data from your drive, it will bring a popup to ask for permissions
# [colab-only removed] from google.colab import drive
# [colab drive mount removed] drive.mount('/content/drive')

# ===== Cell 2 =====
# define folders
goget_country_folder = '/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/Data sets & reports (O&G)/O&G country materials/'
country = 'Colombia (GOGET O&G)/' # change for country you are working on
output_folder = goget_country_folder + country + 'Output of automated comparison/' # manually add this folder to the country folder

# add time stamp
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# print timestamp and output location
print(f"your automated comparison will be saved to " + output_folder + " with the timestamp of" + timestamp)

# ===== Cell 3 =====
# define data set file paths
old_filepath = goget_country_folder + country + '(2025 Gas) -- Producción Fiscalizada de Gas por Campo.csv'
new_filepath = goget_country_folder + country + '(2026 Gas) -- Producción Fiscalizada de Gas por Campo.csv'

# create df with header on the third row (index 2) which should contain 'Campo', 'Contrato', 'enero', etc. This is because of the "PRODUCCION...." text
old = pd.read_csv(old_filepath, header=2)
new = pd.read_csv(new_filepath, header=2)

# ===== Cell 4 =====
# drop production data, as we will deal with that in "Parse Colombia Production Data 2025 06 26.ipynb"
# first define production
production_cols = ['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre','2025 total']

# drop production columns
old.drop(columns=production_cols, inplace=True)
new.drop(columns=production_cols, inplace=True)

# create ID column due to no unique names, this is because AREA TECA-COCORNA exists in both PUERTO NARE and PUERTO TRIUNFO (seperated out)
old["Departamento_Municipio_Campo"] = old['Departamento'] + old["Municipio"] + old["Campo"]
new["Departamento_Municipio_Campo"] = new['Departamento'] + new["Municipio"] + new["Campo"]

# group by Departamento_Municipio_Campo to avoid duplicates
old = old.groupby("Departamento_Municipio_Campo").first().reset_index()
new = new.groupby("Departamento_Municipio_Campo").first().reset_index()

print(old.columns)
print(new.columns)

# ===== Cell 5 =====
def compare_datasets(df_old_original, df_new_original, key_columns):
    # Make copies to avoid modifying original DataFrames passed into the function
    df_old = df_old_original.copy()
    df_new = df_new_original.copy()

    # Get the common columns present in both DataFrames
    # This set will include columns used for comparison and the key_columns
    all_common_cols = list(df_old.columns.intersection(df_new.columns))

    # Ensure key_columns are part of all_common_cols
    if not all(col in all_common_cols for col in key_columns):
        missing_keys = [col for col in key_columns if col not in all_common_cols]
        raise ValueError(f"Key columns {missing_keys} not found in both DataFrames.")

    # Filter DataFrames to only common columns, and ensure a consistent column order
    # Use reindex with a sorted list of common columns for strict column alignment
    df_old = df_old[all_common_cols].reindex(columns=sorted(all_common_cols))
    df_new = df_new[all_common_cols].reindex(columns=sorted(all_common_cols))

    # Set index to key columns for easy comparison
    df_old.set_index(key_columns, inplace=True)
    df_new.set_index(key_columns, inplace=True)

    # Find new and removed records
    new_records = df_new.loc[~df_new.index.isin(df_old.index)]
    removed_records = df_old.loc[~df_old.index.isin(df_new.index)]

    # Find modified records
    common_indices_for_modified = df_old.index.intersection(df_new.index)

    # Only attempt comparison if there are common records and actual columns to compare
    if not common_indices_for_modified.empty and not df_old.columns.empty:
        df_old_to_compare = df_old.loc[common_indices_for_modified]
        df_new_to_compare = df_new.loc[common_indices_for_modified]

        # Ensure column order is absolutely identical just before comparison
        df_new_to_compare = df_new_to_compare.reindex(columns=df_old_to_compare.columns)

        modified_records = df_old_to_compare.compare(df_new_to_compare)
    else:
        # Return an empty DataFrame with the expected MultiIndex columns from compare
        modified_records = pd.DataFrame(columns=pd.MultiIndex.from_product([df_old.columns, ['old', 'new']]))

    return new_records, removed_records, modified_records

# Example usage
key_columns = ["Departamento_Municipio_Campo"]  # Adjust according to your dataset

new, removed, modified = compare_datasets(old, new, key_columns)

# Save results to output folder with timestamp
new.to_csv(output_folder + f"new_records_{timestamp}.csv")
removed.to_csv(output_folder + f"removed_records_{timestamp}.csv")
modified.to_csv(output_folder + f"modified_records_{timestamp}.csv")

# print output location
print(f"your automated comparison was saved to " + output_folder + " with the timestamp of" + timestamp)
