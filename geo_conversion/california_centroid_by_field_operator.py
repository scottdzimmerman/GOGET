"""
california_centroid_by_field_operator.py

Migrated from Colab notebook: California Centroid by field and operator
Auto-converted to a Python script. Colab-specific lines
(drive.mount, google.colab imports, shell/magic commands) have been
commented out and flagged; pip installs moved to ../requirements.txt.
"""

# ===== Cell 1 =====
import pandas as pd
import numpy as np
import geopandas

# ===== Cell 2 =====
# [colab-only removed] from google.colab import drive
# [colab drive mount removed] drive.mount('/content/drive')

# ===== Cell 3 =====
goget_path = '/content/drive/Shareddrives/GEM Shared Drive/Programs/Oil & Gas Program/Global Oil and Gas Extraction Tracker (GOGET)/Data sets & reports (O&G)/O&G country materials/United States (GOGET O&G)/California (GOGET)/'
production_file = '2024CaliforniaOilAndGasWellMonthlyProduction.csv'
wells_file = 'Cali All Wells 2024 12 23.csv'

location_file = 'California field location coordinates.csv'
location_data = pd.read_csv(goget_path + location_file)
