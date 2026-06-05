"""
gem_db_to_googlesheet.py

Migrated from Colab notebook: Calling the GEM Database and saving a table as a googlesheet
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

# Library needed to connect to the database
from sqlalchemy import create_engine, text
import psycopg2

# make timestamp
from datetime import datetime

# Authenticate and create a client
# [colab-only removed] from google.colab import auth
auth.authenticate_user()
import gspread
from google.auth import default
creds, _ = default()
gc = gspread.authorize(creds)

# ===== Cell 2 =====
# make timestamp
now = datetime.now()
timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")

print('this runs qc output will all be timestamped: ' + timestamp)

# ===== Cell 3 =====
# Set up database pull via URL from the data team.
# (URL updated 2025-07-07 by Maisie to reflect new follower database location)
DATABASE_URL = 'postgres://readonly:p8973ecd68569dabd2e8d1bc7bd5446d35a0d457487e0a783c83de2ec8a1043cc@ec2-54-243-187-12.compute-1.amazonaws.com:5432/d3o895iig4poii'

if DATABASE_URL.startswith('postgres:'):
    DATABASE_URL = DATABASE_URL.replace('postgres:', 'postgresql:')

# Connect to the database
engine = create_engine(DATABASE_URL)
conn = engine.connect()

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

# function to convert sql tables to dataframes
def get_sql_table(table_name):
   df = pd.read_sql(table_name,conn)
   return df

# read and find the relevant tables for your work
available_tables()

# ===== Cell 4 =====
# define relevant table
table = 'goget_project' # change this for the table you want

# ===== Cell 5 =====
# filter status_timeline for only entries in goget_project
table_for_gsheet = get_sql_table(table)

# check table was properly gathered
display(table_for_gsheet.head())

# ===== Cell 6 =====
# Create a new spreadsheet
spreadsheet_name = timestamp
try:
    sh = gc.open(spreadsheet_name)
except gspread.SpreadsheetNotFound:
    sh = gc.create(spreadsheet_name)
    print(f"Spreadsheet '{spreadsheet_name}' created.")

# Select the first worksheet
worksheet = sh.sheet1

# Clear existing data and update with the DataFrame
worksheet.clear()

# Convert the entire DataFrame to string type and fill NaN with empty strings before converting to list
data_to_upload = table_for_gsheet.astype(str).fillna('').values.tolist()

worksheet.update([table_for_gsheet.columns.values.tolist()] + data_to_upload)

print(f"DataFrame uploaded to spreadsheet '{spreadsheet_name}'.")
