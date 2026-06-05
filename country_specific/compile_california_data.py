"""
compile_california_data.py

Migrated from Colab notebook: Compile California data 1_18_22.ipynb
Auto-converted to a Python script. Colab-specific lines
(drive.mount, google.colab imports, shell/magic commands) have been
commented out and flagged; pip installs moved to ../requirements.txt.
"""

# ## Compile data from California WellStar program
# * The "wells for 2020" report can be reached directly here: https://calgem-pid.conservation.ca.gov/pid/2020CaliforniaOilAndGasWells.csv)
# * The "wells for 2022" report can be reached directly here: https://calgem-pid.conservation.ca.gov/pid/2022CaliforniaOilAndGasWells.csv
# * This report lists fields (names and numbers) and corresponding wells, status, and operators
#
# * The "well monthly production for 2020” report can be reached directly here: (https://calgem-pid.conservation.ca.gov/pid/2020CaliforniaOilAndGasWellMonthlyProduction.csv
# * This report provides monthly oil, gas, and condensate production by field.

# ===== Cell 1 =====
# First to compile the monthly production data into an annual total for each well.
# Then, the API codes listed in the second (production data) report can be matched to the
# API numbers in the first report so that those production totals can be assigned to each
# operator and field name.

# ===== Cell 2 =====
import pandas as pd
import numpy as np

# ===== Cell 3 =====
goget_path = '/Users/jennymartos/Documents/GEM/GRFF/California/'
production_file = '2020CaliforniaOilAndGasWellMonthlyProduction.csv'
wells_file = '2020CaliforniaOilAndGasWells.csv'

# ===== Cell 4 =====
production_df = pd.read_csv(goget_path + production_file)
production_df = production_df.copy()

# ===== Cell 5 =====
# CHECK PRODUCTION TOTALS
total_gas_prod = production_df['GasProduced'].sum()
total_oilcondens_prod = production_df['OilorCondensateProduced'].sum()

print(f'Total gas production: {total_gas_prod}')
print(f'Total oil and condensate production: {total_oilcondens_prod}')

# ===== Cell 6 =====
# Production data clean up
production_df['OilorCondensateProduced'] = production_df['OilorCondensateProduced'].fillna('')
production_df['GasProduced'] = production_df['GasProduced'].fillna('')

# Sum production by API Number
list_of_col = ['OilorCondensateProduced','GasProduced']
production_df = production_df.groupby('APINumber')[list_of_col].sum().reset_index()

# production_df

# ===== Cell 7 =====
wells_df = pd.read_csv(goget_path + wells_file)
wells_df = wells_df.copy()

# ===== Cell 8 =====
#Add production columns to wells file, based on API number
wells_df = wells_df[['API','FieldName','OperatorName']].drop_duplicates(subset=['API'])
wells_df = wells_df.join(production_df.set_index('APINumber'), on='API')

# ===== Cell 9 =====
# Sum by Field Name & Operator
wells_df = wells_df.groupby(['FieldName','OperatorName'])[list_of_col].sum().reset_index()
wells_df

# ===== Cell 10 =====
# Drop zero values
wells_df = wells_df.drop(wells_df[(wells_df['OilorCondensateProduced'] == 0.0) & (wells_df['GasProduced'] == 0.0)].index)
# wells_df

# CHECK PRODUCTION TOTALS
total_gas_prod = wells_df['GasProduced'].sum()
total_oilcondens_prod = wells_df['OilorCondensateProduced'].sum()

print(f'Total gas production: {total_gas_prod}')
print(f'Total oil and condensate production: {total_oilcondens_prod}')

# ===== Cell 11 =====
# Export to Excel
wells_df.to_excel(goget_path + 'California Production by Field and Operator 2021-07-30 reformatted.xlsx', index=False)
