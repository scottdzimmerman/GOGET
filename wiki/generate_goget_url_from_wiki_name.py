"""
generate_goget_url_from_wiki_name.py

Migrated from Colab notebook: Generate GOGET URL based on wiki name
Auto-converted to a Python script. Colab-specific lines
(drive.mount, google.colab imports, shell/magic commands) have been
commented out and flagged; pip installs moved to ../requirements.txt.
"""

# ===== Cell 1 =====
import pandas as pd
import urllib.parse
from datetime import datetime

def create_wiki_url(project_name):
    base_url = "https://www.gem.wiki/"
    formatted_name = project_name.replace(" ", "_")
    encoded_name = urllib.parse.quote(formatted_name)
    full_url = base_url + encoded_name
    return full_url

# Today's date in YYYY-MM-DD format
today_date = datetime.now().strftime("%Y-%m-%d")
column_name = f"{today_date} Wiki URL"

# Path to your Excel file
excel_path = '/content/GOGET oil & gas extraction sites (main data set) (3).xlsx'

# Read the "Main data" sheet
df = pd.read_excel(excel_path, sheet_name='Main data')

# Filter rows where 'keep' column is 'yes'
filtered_df = df.loc[df['keep'] == 'yes'].copy()

# Generate URLs for the filtered rows
filtered_df[column_name] = filtered_df['Wiki name'].apply(create_wiki_url)

# Merge the updated data back into the original DataFrame
df = pd.merge(df, filtered_df[[column_name]], left_index=True, right_index=True, how='left')

# Save the DataFrame back to the same Excel file, in the same sheet
# This operation will overwrite the existing sheet, so make sure to back up your data if necessary
with pd.ExcelWriter(excel_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    df.to_excel(writer, sheet_name='Main data', index=False)

print(f"URLs have been added to the Excel sheet in the column '{column_name}' for rows where 'keep' equals 'yes'.")
