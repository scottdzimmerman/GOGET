"""
condense_gas_plant_units_by_status.py

Migrated from Colab notebook: Condense Gas Plant Units by Status
Auto-converted to a Python script. Colab-specific lines
(drive.mount, google.colab imports, shell/magic commands) have been
commented out and flagged; pip installs moved to ../requirements.txt.
"""

# ===== Cell 1 =====
#install libraries
# [moved to requirements.txt] !pip install pygsheets
import pygsheets # use 'pip install pygsheets'

import pandas as pd
# [moved to requirements.txt] !pip install geopandas

# ===== Cell 2 =====
# [colab-only removed] #from google.colab import drive
# [colab drive mount removed] #drive.mount('/content/drive')

# ===== Cell 3 =====
#import Gas Plant Data
spreadsheet = pd.read_csv('/content/GGPT 2_7 Comma Free.csv')

# ===== Cell 4 =====
df = spreadsheet
df.dtypes

# ===== Cell 5 =====
#df['Capacity'] = df['Capacity'].astype(float, errors = 'raise')

# ===== Cell 6 =====
#from pandas.core.tools.numeric import to_numeric
#condense Units by status
df = spreadsheet
#df['Capacity elec. (MW)'] = df['Capacity elec. (MW)'].apply(to_numeric, errors = 'coerce')
df = df.groupby(['Country','Plant name', 'Status', 'Latitude', 'Longitude'])['Capacity'].sum()
df = df.reset_index()
spreadsheet = df
display(df)
df.dtypes
#print(spreadsheet)
spreadsheet.to_csv('/content/GGPT-2.7(4.0).csv')
