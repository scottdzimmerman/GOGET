"""
condense_lng_terminals.py

Migrated from Colab notebook: condensing LNG terminals.ipynb
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

import numpy
# [moved to requirements.txt] !pip install numpy

# ===== Cell 2 =====
#Mount google drive
# [colab-only removed] #from google.colab import drive
# [colab drive mount removed] #drive.mount('/content/drive')

# ===== Cell 3 =====
#import LNG Terminals Data
spreadsheet = pd.read_csv('/content/LNG Terminals - main - Terminals.csv')

# ===== Cell 4 =====
#condense LNG by status
df = spreadsheet
df.replace('--', numpy.nan, inplace=True)
df = df.groupby(['TerminalID', 'Country', 'Status', 'StopYear', 'Latitude', 'Longitude', 'Type1',	'Facility'])['CapacityInMtpa'].sum()
df = df.reset_index()
spreadsheet = df
spreadsheet.to_csv('test2')

# ===== Cell 5 =====
#condense LNG by Terminal name
df = spreadsheet
df = df.groupby(['TerminalID', 'Country','Status','Latitude', 'Longitude'])
df = df.reset_index()
spreadsheet = df
spreadsheet.to_csv('/content/7/11.csv')
