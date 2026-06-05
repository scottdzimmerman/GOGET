"""
compare_two_copies_of_goget.py

Migrated from Colab notebook: Compare two copies of GOGET 2024 09 30
Auto-converted to a Python script. Colab-specific lines
(drive.mount, google.colab imports, shell/magic commands) have been
commented out and flagged; pip installs moved to ../requirements.txt.
"""

# Code to compare two iterations of GOGET to see changes in a specific range

# ===== Cell 1 =====
# Mount Google Drive
# [colab-only removed] from google.colab import drive
# [colab drive mount removed] drive.mount('/content/drive')

# ===== Cell 2 =====
import pandas as pd
from datetime import datetime

# ===== Cell 3 =====
#import pandas as pd

#def compare_spreadsheets(file1, file2, sheet_name):
       # The following two lines were not indented properly, so they were not being executed within the function
 #      Sept27 = pd.read_excel(file1, sheet_name=sheet_name, engine='openpyxl') # This line was not indented properly
  #     Oct04 = pd.read_excel(file2, sheet_name=sheet_name, engine='openpyxl') # This line was not indented properly
#
 #      # Assuming 'Unit ID' is the column name for Unit IDs
       # Select Unit ID and the comparison range
  #     range_Sep27 = Sept27[['Unit ID'] + list(Sept27.loc[:, 'Owner 1':'Owner % sum'].columns)]
   #    range_Oct04 = Oct04[['Unit ID'] + list(Oct04.loc[:, 'Owner 1':'Owner % sum'].columns)]

       # Set 'Unit ID' as index for comparison
    #   range_Sep27 = range_Sep27.set_index('Unit ID')
     #  range_Oct04 = range_Oct04.set_index('Unit ID')

      # comparison_result = range_Sep27.compare(range_Oct04)

       #return comparison_result

# Load in sheets
#file1 = "/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/GOGET Iterations/Snapshots of GOGET main data set/GOGET oil & gas extraction sites (2024 09 27).xlsx"
#file2 = "/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction"

# ===== Cell 4 =====
def compare_spreadsheets(file1, file2, sheet_name):
       # The following two lines were not indented properly, so they were not being executed within the function
       Sept27 = pd.read_excel(file1, sheet_name=sheet_name, engine='openpyxl')
       Oct04 = pd.read_excel(file2, sheet_name=sheet_name, engine='openpyxl')

       # Assuming 'Unit ID' is the column name for Unit IDs
       # Select Unit ID and the comparison range
       range_Sep27 = Sept27[['Unit ID'] + list(Sept27.loc[:, 'Owner 1':'Owner % sum'].columns)]
       range_Oct04 = Oct04[['Unit ID'] + list(Oct04.loc[:, 'Owner 1':'Owner % sum'].columns)]




       range_Sep27['All_Owners'] = range_Sep27.apply(combine_owners, axis=1)
       range_Oct04['All_Owners'] = range_Oct04.apply(combine_owners, axis=1)

       # Set 'Unit ID' as index for comparison
       range_Sep27 = range_Sep27.set_index('Unit ID')
       range_Oct04 = range_Oct04.set_index('Unit ID')

       return range_Sep27[['All_Owners']].compare(range_Oct04[['All_Owners']])


# ===== Cell 5 =====
print(compare_spreadsheets.__doc__)

# ===== Cell 6 =====
# Load in sheets
file1 = "/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/GOGET Iterations/Snapshots of GOGET main data set/GOGET oil & gas extraction sites (2024 09 27).xlsx"
file2 = "/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/GOGET Iterations/Snapshots of GOGET main data set/GOGET oil & gas extraction sites (2024 10 04).xlsx"
sheet_name = "Main data"

# ===== Cell 7 =====
def compare_spreadsheets(file1, file2, sheet_name):
    # Load in sheets
    Sept27 = pd.read_excel(file1, sheet_name=sheet_name, engine='openpyxl')
    Oct04 = pd.read_excel(file2, sheet_name=sheet_name, engine='openpyxl')

    # Select Unit ID and the comparison range
    range_Sep27 = Sept27[['Unit ID'] + list(Sept27.loc[:, 'Owner 1':'Owner % sum'].columns)]
    range_Oct04 = Oct04[['Unit ID'] + list(Oct04.loc[:, 'Owner 1':'Owner % sum'].columns)]

    def combine_owners(row):
           owners = []
           for i in range(1, 11):  # Assuming up to 10 owners
               owner_col = f'Owner {i}'
               if owner_col in row and pd.notna(row[owner_col]):
                   owners.append(row[owner_col])
           return ', '.join(sorted(owners)) if owners else None
    range_Sep27['All_Owners'] = range_Sep27.apply(combine_owners, axis=1)
    range_Oct04['All_Owners'] = range_Oct04.apply(combine_owners, axis=1)

    # Set 'Unit ID' as index for comparison
    range_Sep27 = range_Sep27.set_index('Unit ID')
    range_Oct04 = range_Oct04.set_index('Unit ID')

    # Convert index to string type to ensure consistency
    range_Sep27.index = range_Sep27.index.astype(str)
    range_Oct04.index = range_Oct04.index.astype(str)

    # Strip leading/trailing spaces and invisible characters from the index
    range_Sep27.index = range_Sep27.index.str.strip().str.replace(r'\s+', ' ', regex=True)
    range_Oct04.index = range_Oct04.index.str.strip().str.replace(r'\s+', ' ', regex=True)

    return range_Sep27[['All_Owners']], range_Oct04[['All_Owners']] # Return the ranges

# Load in sheets
file1 = "/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/GOGET Iterations/Snapshots of GOGET main data set/GOGET oil & gas extraction sites (2024 09 27).xlsx"
file2 = "/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/GOGET Iterations/Snapshots of GOGET main data set/GOGET oil & gas extraction sites (2024 10 04).xlsx"
sheet_name = "Main data"

# Call the function and get the ranges
range_Sep27, range_Oct04 = compare_spreadsheets(file1, file2, sheet_name)

# Print column headers for debugging
print("September 27th Headers:", range_Sep27.columns)
print("October 4th Headers:", range_Oct04.columns)

comparison_result = range_Sep27.compare(range_Oct04)

# Get the current timestamp
from datetime import datetime
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# Define the output file path with timestamp
output_file = f"/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/GOGET Iterations/Snapshots of GOGET main data set/comparison_result_{timestamp}.xlsx"

# Save the comparison result to an Excel file
comparison_result.to_excel(output_file)

print(f"Comparison results saved to: {output_file}")

# ===== Cell 8 =====
comparison_result = compare_spreadsheets(file1, file2, sheet_name)

# Get the current timestamp
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# Define the output file path with timestamp
output_file = f"/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/GOGET Iterations/Snapshots of GOGET main data set/comparison_result_{timestamp}.xlsx"

# Save the comparison result to an Excel file
comparison_result.to_excel(output_file)

print(f"Comparison results saved to: {output_file}")

# ===== Cell 9 =====
range_Sep27.head
