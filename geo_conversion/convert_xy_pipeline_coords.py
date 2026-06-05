"""
convert_xy_pipeline_coords.py

Migrated from Colab notebook: Scott_s version of _convert-xy-pipeline-coords.ipynb_
Auto-converted to a Python script. Colab-specific lines
(drive.mount, google.colab imports, shell/magic commands) have been
commented out and flagged; pip installs moved to ../requirements.txt.
"""

# ===== Cell 1 =====
import pandas

# ===== Cell 2 =====
#read in data from google sheets
# [colab-only removed] from google.colab import auth
auth.authenticate_user()

import gspread
from oauth2client.client import GoogleCredentials

gc = gspread.authorize(GoogleCredentials.get_application_default())

coords_csv1 = gc.open_by_url('https://docs.google.com/spreadsheets/d/1RutxPJxnsB4hUa1SAmBElFtfbF9dTK6CGJ2pQ0i757Y/edit#gid=1646715583')
print(coords_csv1)

# ===== Cell 3 =====
# for crib point (cancelled)
#sheet_url= 'https://docs.google.com/spreadsheets/d/1EL6ZwuGqxUFx7E0TUGRXjMjWQx4eGjlAiORLNCRrfXY/edit?usp=sharing'
#url_1 = sheet_url.replace('/edit?usp=sharing', '/export?format=csv&gid=0')
sheet_url= 'https://docs.google.com/spreadsheets/d/1EL6ZwuGqxUFx7E0TUGRXjMjWQx4eGjlAiORLNCRrfXY/export?format=csv&gid=0'
pandas.read_csv(sheet_url)

# ===== Cell 4 =====
# each x,y pair should look like:  x1,y1 : x2,y2 : x3,y3 : ...
coords_csv['xcoords']

# ===== Cell 5 =====
coords_csv['ycoords']

# ===== Cell 6 =====
coords_csv[['ycoords','xcoords']].astype(str)

# # join into "y, x" strings

# ===== Cell 7 =====
joined_strings_dataframe = coords_csv[['ycoords', 'xcoords']].astype(str).apply(lambda x: ', '.join(x), axis=1)
joined_strings_dataframe.head()

# # then add a colon and concatenate into single string

# ===== Cell 8 =====
joined_strings_with_colon = joined_strings_dataframe.str.cat(sep=': ')

# ===== Cell 9 =====
joined_strings_with_colon
