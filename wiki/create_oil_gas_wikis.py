"""
create_oil_gas_wikis.py

Migrated from Colab notebook: GOGET create oil and gas wikis_10_15_21_misc things.ipynb
Auto-converted to a Python script. Colab-specific lines
(drive.mount, google.colab imports, shell/magic commands) have been
commented out and flagged; pip installs moved to ../requirements.txt.
"""

# # GOGET oil & gas field wiki page generation

# ===== Cell 1 =====
import pandas as pd
import numpy as np
import time
import os
import requests
# [moved to requirements.txt] !pip install pygsheets
# [moved to requirements.txt] !pip install config

# ### Running using downloaded file

# ===== Cell 2 =====
# main files:
goget_refs_processed_file = 'markdown_masterList.xlsx'

# import GOGET data set
goget_xl = pd.ExcelFile('/content/GOGET oil & gas extraction sites (main data set).xlsx')

# ===== Cell 3 =====
# create timestamp for the whole batch
page_creation_timestamp = time.strftime('%Y-%m-%d_%H%M%S', time.localtime())

# define directory for text file outputs
text_file_path = f"/Wikis/wiki page text/Unit Name Local Script subset - wiki page text - pages do not exist {page_creation_timestamp}/"
os.makedirs(text_file_path, exist_ok=False)

# ===== Cell 4 =====
def read_and_clean_goget_main(goget_xl):
    df = pd.read_excel(goget_xl, sheet_name='Main data')

    df = df.dropna(subset=['Unit ID'])

    for col in df.columns:
        if 'Unnamed: ' in col:
            df = df.drop(col, axis=1)

    # exclude empty rows
    df = df[df['Unit name'].isna()==False]

    # clean up nans
    df['Subnational unit (province, state)'] = df['Subnational unit (province, state)'].fillna('')

    goget_main = df

    print(f"Number of rows after filtering Main data sheet: {len(df)}")

    return goget_main

# ===== Cell 5 =====
def read_and_clean_goget_prod(goget_xl):
    df = pd.read_excel(goget_xl, sheet_name='Reserves and Production')

    df = df.dropna(subset=['Unit ID', 'Unit name'], how='any')

    for col in df.columns:
        if 'Unnamed: ' in col:
            df = df.drop(col, axis=1)

    # exclude empty rows
    df = df[df['Unit name'].isna()==False]

    goget_prod = df
    print(f"Number of rows after filtering Reserves and Production sheet: {len(df)}")
    return goget_prod

# ===== Cell 6 =====
def read_and_clean_goget_ownership(goget_xl):
    df = pd.read_excel(goget_xl, sheet_name='Ownership')

    df = df.dropna(subset=['Owner'], how='any')

    for col in df.columns:
        if 'Unnamed: ' in col:
            df = df.drop(col, axis=1)

    # exclude empty rows
    df = df[df['Owner'].isna()==False]

    goget_ownership = df
    print(f"Number of rows after filtering Ownership sheet: {len(df)}")

    return goget_ownership

# ===== Cell 7 =====
goget_main = read_and_clean_goget_main(goget_xl)
goget_prod = read_and_clean_goget_prod(goget_xl)
goget_ownership = read_and_clean_goget_ownership(goget_xl)

# ===== Cell 8 =====
# only keep rows with local name entries and wiki pages
#fields_no_wiki = goget_main.loc[goget_main['Wiki URL'].isna()==True]
#fields_no_wiki = goget_main.loc[(goget_main['Wiki URL'].isna()==False) & (goget_main['Wiki URL local'].isna()==False)]
fields_no_wiki = goget_main.loc[(goget_main['Wiki URL'].isna() == False) & (goget_main['Unit name local script'].isna() == False)]
#only keep rows from old Europe wikis
#unit_ID_list = ['OG0001865','OG0001421','OG0001935','OG0001422','OG0001423','OG0002034','OG0002036','OG0001424','OG0001425',
               #'OG0002076','OG0001426','OG0001428','OG0001429','OG0001430','OG0001431','OG0001432','OG0001433','OG0001434']
#fields_no_wiki = goget_main[goget_main['Unit ID'].isin(unit_ID_list)]
len(fields_no_wiki)

# ### Filter for fields over thresholds

# ===== Cell 9 =====
# # filter for only units we want to keep
# print(f"Number of rows before filtering: {len(goget_main)}")

# goget_main = goget_main[goget_main['keep']=='yes']
# print(f"Number of rows after filtering for keep is yes: {len(goget_main)}")

# # exclude basin entries
# goget_main = goget_main[goget_main['Unit type']!='basin']
# print(f"Number of rows after filtering out basins: {len(goget_main)}")

# # exclude sub-basin entry
# goget_main = goget_main[goget_main['Unit type']!='sub-basin']
# print(f"Number of rows after filtering out sub-basins: {len(goget_main)}")

# # exclude certain statuses (UGS, shut in, decommissioned)
# goget_main = goget_main[goget_main['Status'] != 'UGS']
# goget_main = goget_main[goget_main['Status'] != 'shut in']
# goget_main = goget_main[goget_main['Status'] != 'decommissioned']

# print(f"Number of rows after filtering for certain statuses (UGS, shut in, decommissioned): {len(goget_main)}")

# # exclude conventional oil/gas fields in Alberta, Canada
# goget_main_mask = goget_main[(goget_main['Subnational unit (province, state)'] == 'Alberta') & (goget_main['Unit type'] == 'field')]
# goget_main = goget_main[~goget_main['Unit ID'].isin(goget_main_mask['Unit ID'])]
# print(f"Number of rows after filtering out Alberta conventional fields: {len(goget_main)}")

# # # exclude those with no status or unknown status EXCEPT if value in Project or complex column
# # status_mask = goget_main[(goget_main['Status'].isna() == True) & (goget_main['Project or complex'].isna() == True)] # status is blank and project/complex is blank
# # goget_main = goget_main[~goget_main['Unit ID'].isin(status_mask['Unit ID'])]
# goget_main = goget_main[goget_main['Status'].isna() == False]
# print(f"Number of rows after filtering for no status: {len(goget_main)}")

# # # exclude those with no coordinates EXCEPT if value in Project or complex column
# #coordinate_mask = goget_main[(goget_main['Latitude'].isna() == True) & (goget_main['Longitude'].isna() == True) & (goget_main['Project or complex'].isna() == True)]
# #goget_main = goget_main[~goget_main['Unit ID'].isin(coordinate_mask['Unit ID'])]

# #goget_main = goget_main[(goget_main['Latitude'].isna() == False) & (goget_main['Longitude'].isna() == False)]
# #print(f"Number of rows after filtering for fields without coordinates: {len(goget_main)}")

# ===== Cell 10 =====
# keep only the most recent year of data for each category

df = goget_prod.copy()

print(f"len(goget_prod): {len(goget_prod)}")
df['Reserves classification (original)'] = df['Reserves classification (original)'].fillna('')

df['combo'] = '' # initialize new column

# create the entries in 'combo' by combining the strings in each column
for col in ['Unit ID', 'Unit name', 'Country', 'Production/reserves', 'Fuel description', 'Reserves classification (original)']:
    df['combo'] = df['combo'].astype(str).fillna('') + '_' + df[col]
    df['combo'] = df['combo'].str.strip('_')

counts_all = df.groupby('combo')['Data year'].count()

# clean up Data year column
df['Data year'] = df['Data year'].astype(str)
df['Data year'] = df['Data year'].replace('[not stated]', '0')
df['Data year'] = df['Data year'].str.replace(' predicted', '', regex=False)
df['Data year'] = df['Data year'].astype(int)

data_year_max_all = df.groupby('combo')['Data year'].max()

multiple_counts = counts_all[counts_all > 1]

to_condense = df[df['combo'].isin(multiple_counts.index)]
print(f"len(to_condense): {len(to_condense)}")
already_condensed = df[~df['combo'].isin(multiple_counts.index)]

newly_condensed = pd.DataFrame() # initialize
for combo in multiple_counts.index:
    # get data_year_max
    data_year_max = data_year_max_all.at[combo]

    df_max_year = df[(df['combo']==combo) & (df['Data year']==data_year_max)]

    newly_condensed = newly_condensed.append(df_max_year, sort=False)

print(f"len(newly_condensed): {len(newly_condensed)}")

# recombine newly_condensed & already_condensed
recombined = pd.concat([already_condensed, newly_condensed], sort=False)

recombined['Data year'] = recombined['Data year'].astype(str)
recombined['Data year'] = recombined['Data year'].replace('0', '[not stated]')

# add check to find those with more than one row for a given set of prod/res
data_year_counts = recombined.groupby('combo')['Data year'].count()
data_year_counts_multi = data_year_counts[data_year_counts > 1]
multiple_rows = recombined[recombined['combo'].isin(data_year_counts_multi.index)]
if len(multiple_rows)>0:
    # export file
    save_timestamp = time.strftime('%Y-%m-%d_%H%M%S', time.localtime())
    multiple_rows.to_excel(
        gem_path + f'GOGET results with multiple rows {save_timestamp}.xlsx',
        index=False
    )

# drop the column 'combo' added here
recombined = recombined.drop('combo', axis=1)
goget_prod = recombined

print(f"len(recombined): {len(recombined)}")
print(f"len(goget_prod): {len(goget_prod)}")

# # TO DO: Sort by category then by fuel description then by reserve classification
# categories = np.array(['production', 'cumulative production', 'production design capacity','reserves'])
# fuel_categories = np.array(['oil','oil equivalent','condensate','NGL','total liquids','gas',
#                             'dry gas','associated gas','nonassociated gas','hydrocarbons'])
# reserve_categories = np.array(['1P reserves','2P reserves','3P reserves','2C resources','EUR',
#                                'original oil in place','original gas in place','original volume in place',
#                                'recoverable reserves','reserves'])

# goget_prod['Production/reserves'] = pd.Categorical(goget_prod['Production/reserves'], categories=categories, ordered=True)
# goget_prod['Fuel description'] = pd.Categorical(goget_prod['Fuel description'], categories=fuel_categories, ordered=True)
# goget_prod['Reserves classification (original)'] = pd.Categorical(goget_prod['Reserves classification (original)'], categories=reserve_categories, ordered=True)

# goget_prod = goget_prod.sort_values(by=["Production/reserves","Fuel description","Reserves classification (original)"])

# ===== Cell 11 =====
# QC step
for col in ['Latitude', 'Longitude']:
    for row in goget_main.index:
        try:
            float(goget_main.at[row, col])
        except:
            unit_name = goget_main.at[row, 'Unit name']
            unit_id = goget_main.at[row, 'Unit ID']
            country = goget_main.at[row, 'Country']
            print(f"For {unit_name} in {country} ({unit_id}), couldn't convert {col} to float: {goget_main.at[row, col]}")

# ===== Cell 12 =====
for col in ['Latitude', 'Longitude']:
    for row in goget_main.index:
        unit_name = goget_main.at[row, 'Unit name']
        unit_id = goget_main.at[row, 'Unit ID']
        country = goget_main.at[row, 'Country']

        if pd.isna(goget_main.at[row,col])== True:
            print (f"No location coordinates for {unit_name} in {country} ({unit_id})")

# ===== Cell 13 =====
# show fields with Wiki pages already
goget_main.loc[goget_main['Wiki URL'].isna()==False]['Country'].value_counts()

# ===== Cell 14 =====
to_process = fields_no_wiki.copy()
to_process2 = goget_prod.copy()
to_process3 = goget_ownership.copy()

# ## References

# ===== Cell 15 =====
# import references processed by Citoid & archived with Internet Archive
# note: all are "cite web" even though some had different types coming out of Citoid

goget_refs_processed_path = gem_path + '/wiki_references/GGPT-References-master/masters/'

goget_refs = pd.read_excel(goget_refs_processed_path + goget_refs_processed_file)

# clean up
goget_refs['citeWeb'] = goget_refs['citeWeb'].str.replace('|', ' |', regex=False)
goget_refs['citeWeb'] = goget_refs['citeWeb'].str.replace('  ', ' ', regex=True)

goget_refs['ref'] = '<ref>' + goget_refs['citeWeb'] + '</ref>'

goget_refs_ser = goget_refs.set_index('originalURL')['ref']
goget_refs_dict = goget_refs_ser.to_dict()

# ===== Cell 16 =====
# import GOGET references "Sources" sheet
ref_sheet_dtypes = {'original URL': str, 'archived URL': str, 'wiki markup ref': str}
goget_ref_sheet = pd.read_excel(goget_xl, sheet_name='Sources', dtype=ref_sheet_dtypes)
goget_ref_sheet = goget_ref_sheet.dropna(how='all')

for col in goget_ref_sheet.columns:
    if "Unnamed: " in col:
        goget_ref_sheet = goget_ref_sheet.drop(col, axis=1)

for col in goget_ref_sheet.columns:
    goget_ref_sheet[col] = goget_ref_sheet[col].fillna('')

goget_ref_sheet = goget_ref_sheet.set_index('short name')

# ===== Cell 17 =====
# process fields to convert references
# iterate through all reference columns
# for each column, replace the reference URL with the wiki markup full reference

def replace_reference_links_with_wiki_markup_refs(df_arg,ref_cols):
    df = df_arg.copy()

    unprocessed_refs = [] # initialize

    for col in ref_cols:
        df[col] = df[col].fillna('')
        df[col] = df[col].str.replace('; ', ', ')

        # TEST: check whether there are ref cells with commas separating references, but without a following space
        test = df[
            (df[col].str.contains(',')) &
            (~df[col].str.contains(', '))]
        test = test[~test[col].str.contains('www.google.com/maps')]
        if len(test) > 0:
            print(f'For column {col}, there were items with commas between items, but not a comma + space')
            print("(other than Google Maps URLs, in which commas are common.)")
            print("These are not necessarily errors, but can be worth checking to make sure there is really only one ref per cell.")
            for row in test.index:
                print(test.at[row, col])
            print()
        # END OF TEST

        for row in df.index:
            ref_cell = df.at[row, col]
            ref_list = ref_cell.split(', ')

            ref_list_new = [] # initialize
            for ref in ref_list:
                try:
                    ref_new = goget_refs_dict[ref]
                except:
                    ref_new, unprocessed_refs = process_other_ref_links(ref_list, ref, unprocessed_refs)

                ref_list_new += [ref_new]

            # concatenate items in list to create string, with items separated by comma + space
            try:
                ref_new_str = ''.join(ref_list_new)
            except:
                print("Error!" + f" Show ref_list_new:")
                print(ref_list_new)

            # put converted reference into df cell
            df.at[row, col] = ref_new_str

    unprocessed_refs = list(set(unprocessed_refs))
    unprocessed_refs.sort()
    if '' in unprocessed_refs:
        unprocessed_refs.remove('')
    print()
    print(f"unprocessed references ({len(unprocessed_refs)}):")
    for unprocessed_ref in unprocessed_refs:
        print(unprocessed_ref)

    return df

# ===== Cell 18 =====
def process_other_ref_links(ref_list, ref, unprocessed_refs):
    if ref == '':
        ref_new = ''

    # convert short names (e.g., SENER OEL 2018) into full wiki markup refs
    elif ref in goget_ref_sheet.index.tolist():
        wiki_markup_ref = goget_ref_sheet.at[ref, 'wiki ref markup']
        if wiki_markup_ref != '':
            if wiki_markup_ref.startswith("<ref>"):
                ref_new = wiki_markup_ref
            else:
                ref_new = f"{wiki_markup_ref}"
        elif wiki_markup_ref == '':
            # create bare URL reference
            ref_url = goget_ref_sheet.at[ref, 'original URL']
            ref_new = "<ref>[" + ref_url + " " + ref_url + "]</ref>" # placeholder; replace bare URL reference here with full reference

    # Google maps
    elif ref.startswith('https://www.google.com/maps/'):
        ref_new = f'<ref name="Google maps">[{ref} Google Maps]</ref>'

#     # GLEIF
    elif ref.startswith('https://search.gleif.org/'):
        lei = str(ref.split('https://search.gleif.org/#/record/')[1])
        ref_new = f'<ref>[{ref} Legal Entity Identifier (LEI) {lei}] Global Legal Entity Identifier Foundation, accessed January 2020</ref>'

    # WEPP
    elif 'WEPP_g_' in ref:
        ref_new = '<ref name="WEPP">[https://www.spglobal.com/platts/en/products-services/electric-power/world-electric-power-plants-database World Electric Power Plants database] S&P Global Platts, June 2019</ref>'

    # Global Energy Observatory
    elif ref.startswith('GEO'):
        geo_id_num = ref.replace('GEO', '')
        geo_url = f'http://www.globalenergyobservatory.org/geoid/{geo_id_num}'

        # use requests to get html, parse it to get title, use title in reference
        try:
            requests_result = requests.get(ref)
            r_text = requests_result.text
            geo_page_title = r_text[r_text.find('<title>') + 7 : r_text.find('</title>')].strip()

            if geo_page_title != 'New  - GEO':
                ref_new = f'<ref>[{geo_url} {geo_page_title}] Global Energy Observatory, accessed {access_date}</ref>'
            else:
                ref_new = f'<ref>[{geo_url} Global Energy Observatory ID {geo_id_num}], accessed {access_date}</ref>'

        except:
            ref_new = f'<ref>[{geo_url} Global Energy Observatory ID {geo_id_num}], accessed {access_date}</ref>'

    # World Resources Institute
    elif ref[0:3] in ['WRI', 'MEX', 'CHL', 'URY']:
        ref_new = f'<ref>[http://datasets.wri.org/dataset/globalpowerplantdatabase Global Power Plant Database v.1.2.0, ID {ref}] World Resources Institute, June 2019</ref>'

    else:
        if ref.startswith('http'):
            # create bare URL reference
            ref_new = "<ref>[" + ref + " " + ref + "]</ref>"
        elif ref == 'not found':
            ref_new = ''
        else:
            print("Error!" + " Unable to process:")
            print(f"ref: {ref}")
            print(f"from ref_list: {ref_list}")
            print()
            unprocessed_refs += [ref]
            ref_new = ref

    return ref_new, unprocessed_refs

# ===== Cell 19 =====
main_sheet_cols = [
    'Status source', 'Location source', 'Discovery year source', 'Production start source', 'Operator source',
    'Owners source', 'Concession / block source']

to_process = replace_reference_links_with_wiki_markup_refs(to_process, main_sheet_cols)

# ===== Cell 20 =====
prod_sheet_col = ['Data source']
to_process2 = replace_reference_links_with_wiki_markup_refs(to_process2, prod_sheet_col)

# ===== Cell 21 =====
ownership_sheet_col = ['Ultimate owners source']
to_process3 = replace_reference_links_with_wiki_markup_refs(to_process3,ownership_sheet_col)

# ===== Cell 22 =====
# TEST: check results of above
for col in main_sheet_cols:
    for row in to_process.index:
        ref = str(to_process.at[row, col])

        if ref.startswith('<ref')==True:
            pass
        elif ref in ['nan', '']:
            pass
        elif ref in goget_ref_sheet.index.tolist():
            pass
        else:
            print("Error!" + f" ref didn't start with ref tag: {ref}")

# ===== Cell 23 =====
# TEST: check results of above
for col in prod_sheet_col:
    for row in to_process2.index:
        ref = str(to_process2.at[row, col])

        if ref.startswith('<ref')==True:
            pass
        elif ref in ['nan', '']:
            pass
        elif ref in goget_ref_sheet.index.tolist():
            pass
        else:
            print("Error!" + f" ref didn't start with ref tag: {ref}")

# ===== Cell 24 =====
# TEST: check results of above
for col in ownership_sheet_col:
    for row in to_process3.index:
        ref = str(to_process3.at[row, col])

        if ref.startswith('<ref')==True:
            pass
        elif ref in ['nan', '']:
            pass
        elif ref in goget_ref_sheet.index.tolist():
            pass
        else:
            print("Error!" + f" ref didn't start with ref tag: {ref}")

# [link text](https://)## WRITING WIKI PAGES

# ===== Cell 25 =====
# Generate file with Unit ID and wiki URLs
goget_main2 = goget_main.copy()
for r in to_process.index:
    goget_main2.at[r,'Wiki page URL'] = str("https://www.gem.wiki/") + str(goget_main2.at[r,'Wiki name']).replace(" ",'_')

# ===== Cell 26 =====
wikistrings = [] # initialize
wiki_URL_df = pd.DataFrame(columns = ['Unit ID','Wiki URL'])
for row in to_process.index:

    page_lang = 'English'

    wikistr = '' # initialize
    unit_name = str(to_process.at[row, 'Unit name'])
    unit_ID = to_process.at[row,'Unit ID']
    fuel_type = to_process.at[row,'Fuel type']
    unit_type = to_process.at[row, 'Unit type']
    unit_status = to_process.at[row, 'Status']
    country = to_process.at[row, 'Country'].replace("-", " and ")
    subnational = to_process.at[row, 'Subnational unit (province, state)']
    unit_project_complex = to_process.at[row,'Project or complex']
    wiki_name = to_process.at[row,'Wiki name']
    unit_name_local = to_process.at[row,'Unit name local script']

    if page_lang == 'English':
        page_URL = str("https://www.gem.wiki/") + str(to_process.at[row,'Wiki name']).replace(" ",'_')

    if subnational != '' and pd.isna(subnational) == False:
        if country == 'Canada':
            sub_prefix =  str('the province of ') + str(subnational) + str(' in ')
        elif country == 'United States' and subnational != 'Federal offshore':
            sub_prefix = str('the state of ') + str(subnational) + str(' in ')
        elif country == 'United States' and subnational == 'Federal offshore':
            sub_prefix = str('the Gulf of Mexico in ')
        elif country == 'Australia':
            sub_prefix = str('the state of ') + str(subnational) + str(' in ')
        elif country == 'Argentina':
            sub_prefix = str(subnational) + str(', ')
    else:
        sub_prefix = ''

    if country in ['United States', 'Netherlands', 'Czech Republic', 'United Kingdom', 'Philippines', 'United Arab Emirates']:
        country_prefix = 'the '
    else:
        country_prefix = ''

    # clean up unit names
    unit_name = unit_name.replace('Block ','')

    # INTRO SECTION
    unit_status_ref = to_process.at[row,'Status source']
    if page_lang == 'English':
        wikistr += "{{Navbar-GlobalOilandGasExtractionTracker}}"

    if page_lang == 'English' and unit_type == 'block':
        if unit_status == 'operating':
            status_phrase = f"'''Block {unit_name}''' ({unit_name_local}) is an operating {fuel_type} {unit_type} in {sub_prefix}{country_prefix}{country}.{unit_status_ref}"
        elif unit_status == 'in development' and fuel_type == 'oil and gas':
            status_phrase = f"'''Block {unit_name}''' ({unit_name_local}) is an {fuel_type} {unit_type} in development in {sub_prefix}{country_prefix}{country}.{unit_status_ref}"
        elif unit_status == 'in development' and fuel_type == 'oil':
            status_phrase = f"'''Block {unit_name}''' ({unit_name_local}) is an {fuel_type} {unit_type} in development in {sub_prefix}{country_prefix}{country}.{unit_status_ref}"
        elif unit_status == 'in development' and fuel_type == 'gas':
            status_phrase = f"'''Block {unit_name}''' ({unit_name_local}) is a {fuel_type} {unit_type} in development in {sub_prefix}{country_prefix}{country}.{unit_status_ref}"
        elif unit_status == 'discovered':
            status_phrase = f"'''Block {unit_name}''' ({unit_name_local}) is a discovered {fuel_type} {unit_type} in {sub_prefix}{country_prefix}{country}.{unit_status_ref}"
        else:
            status_phrase = f"'''Block {unit_name}''' ({unit_name_local}) is a {unit_type} in {sub_prefix}{country_prefix}{country}.{unit_status_ref}"
            print(f"Block status unknown: {unit_status}; for {unit_name}")

        wikistr += status_phrase

    elif page_lang == 'English' and unit_type == 'field':
        if unit_status == 'operating':
            status_phrase = f"'''{unit_name} Field''' ({unit_name_local}) is an operating {fuel_type} {unit_type} in {sub_prefix}{country_prefix}{country}.{unit_status_ref}"
        elif unit_status == 'in development' and fuel_type == 'oil and gas':
            status_phrase = f"'''{unit_name} Field''' ({unit_name_local}) is an {fuel_type} {unit_type} in development in {sub_prefix}{country_prefix}{country}.{unit_status_ref}"
        elif unit_status == 'in development' and fuel_type == 'oil':
            status_phrase = f"'''{unit_name} Field''' ({unit_name_local}) is an {fuel_type} {unit_type} in development in {sub_prefix}{country_prefix}{country}.{unit_status_ref}"
        elif unit_status == 'in development' and fuel_type == 'gas':
            status_phrase = f"'''{unit_name} Field''' ({unit_name_local}) is a {fuel_type} {unit_type} in development in {sub_prefix}{country_prefix}{country}.{unit_status_ref}"
        elif unit_status == 'discovered':
            status_phrase = f"'''{unit_name} Field''' ({unit_name_local}) is a discovered {fuel_type} {unit_type} in {sub_prefix}{country_prefix}{country}.{unit_status_ref}"
        elif unit_status == 'shut in':
            status_phrase = f"'''{unit_name} Field''' ({unit_name_local}) is a shut in {fuel_type} {unit_type} in {sub_prefix}{country_prefix}{country}.{unit_status_ref}"
        else:
            if fuel_type in ['oil and gas','oil']:
                status_phrase = f"'''{unit_name} Field''' ({unit_name_local}) is an {fuel_type} {unit_type} in {sub_prefix}{country_prefix}{country}.{unit_status_ref}"
                print(f"Field status not handled yet: {unit_status}; for {unit_name}")
            else:
                status_phrase = f"'''{unit_name} Field''' ({unit_name_local}) is a {fuel_type} {unit_type} in {sub_prefix}{country_prefix}{country}.{unit_status_ref}"
                print(f"Field status not handled yet: {unit_status}; for {unit_name}")

        wikistr += status_phrase

    elif page_lang == 'English' and unit_type == 'asset':
        if unit_status == 'operating':
            status_phrase = f"'''{unit_name} Asset''' ({unit_name_local}) is an operating {fuel_type} {unit_type} in {sub_prefix}{country_prefix}{country}.{unit_status_ref}"
        elif unit_status == 'in development' and fuel_type == 'oil and gas':
            status_phrase = f"'''{unit_name} Asset''' ({unit_name_local}) is an {fuel_type} {unit_type} in development in {sub_prefix}{country_prefix}{country}.{unit_status_ref}"
        elif unit_status == 'in development' and fuel_type == 'oil':
            status_phrase = f"'''{unit_name} Asset''' ({unit_name_local}) is an {fuel_type} {unit_type} in development in {sub_prefix}{country_prefix}{country}.{unit_status_ref}"
        elif unit_status == 'in development' and fuel_type == 'gas':
            status_phrase = f"'''{unit_name} Asset''' ({unit_name_local}) is a {fuel_type} {unit_type} in development in {sub_prefix}{country_prefix}{country}.{unit_status_ref}"
        elif unit_status == 'discovered':
            status_phrase = f"'''{unit_name} Asset''' ({unit_name_local}) is a discovered {fuel_type} {unit_type} in {sub_prefix}{country_prefix}{country}.{unit_status_ref}"
        else:
            if fuel_type in ['oil and gas','oil']:
                status_phrase = f"'''{unit_name} Asset''' ({unit_name_local}) is an {fuel_type} {unit_type} in {sub_prefix}{country_prefix}{country}.{unit_status_ref}"
                print(f"Asset status not handled yet: {unit_status}; for {unit_name}")
            else:
                status_phrase = f"'''{unit_name} Asset''' ({unit_name_local}) is a {fuel_type} {unit_type} in {sub_prefix}{country_prefix}{country}.{unit_status_ref}"
                print(f"Asset status not handled yet: {unit_status}; for {unit_name}")

        wikistr += status_phrase

    elif page_lang == 'English' and unit_type == 'pool':
        if unit_status == 'operating':
            status_phrase = f"'''{unit_name} Pool''' ({unit_name_local}) is an operating {fuel_type} {unit_type} in {sub_prefix}{country_prefix}{country}.{unit_status_ref}"
        elif unit_status == 'in development' and fuel_type == 'oil and gas':
            status_phrase = f"'''{unit_name} Pool''' ({unit_name_local}) is an {fuel_type} {unit_type} in development in {sub_prefix}{country_prefix}{country}.{unit_status_ref}"
        elif unit_status == 'in development' and fuel_type == 'oil':
            status_phrase = f"'''{unit_name} Pool''' ({unit_name_local}) is an {fuel_type} {unit_type} in development in {sub_prefix}{country_prefix}{country}.{unit_status_ref}"
        elif unit_status == 'in development' and fuel_type == 'gas':
            status_phrase = f"'''{unit_name} Pool''' ({unit_name_local}) is a {fuel_type} {unit_type} in development in {sub_prefix}{country_prefix}{country}.{unit_status_ref}"
        elif unit_status == 'discovered':
            status_phrase = f"'''{unit_name} Pool''' ({unit_name_local}) is a discovered {fuel_type} {unit_type} in {sub_prefix}{country_prefix}{country}.{unit_status_ref}"
        else:
            print(f"Pool status not handled yet: {unit_status}; for {unit_name}")

        wikistr += status_phrase

    elif page_lang == 'English' and unit_type == 'concession':
        if unit_status == 'operating':
            status_phrase = f"'''{unit_name} Concession''' ({unit_name_local}) is an operating {fuel_type} {unit_type} in {sub_prefix}{country_prefix}{country}.{unit_status_ref}"
        elif unit_status == 'in development' and fuel_type == 'oil and gas':
            status_phrase = f"'''{unit_name} Concession''' ({unit_name_local}) is an {fuel_type} {unit_type} in development in {sub_prefix}{country_prefix}{country}.{unit_status_ref}"
        elif unit_status == 'in development' and fuel_type == 'oil':
            status_phrase = f"'''{unit_name} Concession''' ({unit_name_local}) is an {fuel_type} {unit_type} in development in {sub_prefix}{country_prefix}{country}.{unit_status_ref}"
        elif unit_status == 'in development' and fuel_type == 'gas':
            status_phrase = f"'''{unit_name} Concession''' ({unit_name_local}) is a {fuel_type} {unit_type} in development in {sub_prefix}{country_prefix}{country}.{unit_status_ref}"
        elif unit_status == 'discovered':
            status_phrase = f"'''{unit_name} Concession''' ({unit_name_local}) is a discovered {fuel_type} {unit_type} in {sub_prefix}{country_prefix}{country}.{unit_status_ref}"
        else:
            print(f"Concession status not handled yet: {unit_status}; for {unit_name}")

        wikistr += status_phrase

    elif page_lang == 'English' and unit_type == 'project':
        if unit_status == 'operating':
            status_phrase = f"'''{unit_name} Project''' ({unit_name_local}) is an operating {fuel_type} {unit_type} in {sub_prefix}{country_prefix}{country}.{unit_status_ref}"
        elif unit_status == 'in development' and fuel_type == 'oil and gas':
            status_phrase = f"'''{unit_name} Project''' ({unit_name_local}) is an {fuel_type} {unit_type} in development in {sub_prefix}{country_prefix}{country}.{unit_status_ref}"
        elif unit_status == 'in development' and fuel_type == 'oil':
            status_phrase = f"'''{unit_name} Project''' ({unit_name_local}) is an {fuel_type} {unit_type} in development in {sub_prefix}{country_prefix}{country}.{unit_status_ref}"
        elif unit_status == 'in development' and fuel_type == 'gas':
            status_phrase = f"'''{unit_name} Project''' ({unit_name_local}) is a {fuel_type} {unit_type} in development in {sub_prefix}{country_prefix}{country}.{unit_status_ref}"
        elif unit_status == 'discovered':
            status_phrase = f"'''{unit_name} Project''' ({unit_name_local}) is a discovered {fuel_type} {unit_type} in {sub_prefix}{country_prefix}{country}.{unit_status_ref}"
        else:
            if fuel_type in ['oil and gas','oil']:
                status_phrase = f"'''{unit_name} Project''' ({unit_name_local}) is an {fuel_type} {unit_type} in {sub_prefix}{country_prefix}{country}.{unit_status_ref}"
                print(f"Project status not handled yet: {unit_status}; for {unit_name}")
            else:
                status_phrase = f"'''{unit_name} Project''' ({unit_name_local}) is a {fuel_type} {unit_type} in {sub_prefix}{country_prefix}{country}.{unit_status_ref}"
                print(f"Project status not handled yet: {unit_status}; for {unit_name}")

        wikistr += status_phrase

    elif page_lang == 'English' and unit_type == 'complex':
        if unit_status == 'operating':
            status_phrase = f"'''{unit_name} Complex''' ({unit_name_local}) is an operating {fuel_type} {unit_type} in {sub_prefix}{country_prefix}{country}.{unit_status_ref}\n"
        elif unit_status == 'in development' and fuel_type == 'oil and gas':
            status_phrase = f"'''{unit_name} Complex''' ({unit_name_local}) is an {fuel_type} {unit_type} in development in {sub_prefix}{country_prefix}{country}.{unit_status_ref}\n"
        elif unit_status == 'in development' and fuel_type == 'oil':
            status_phrase = f"'''{unit_name} Complex''' ({unit_name_local}) is an {fuel_type} {unit_type} in development in {sub_prefix}{country_prefix}{country}.{unit_status_ref}\n"
        elif unit_status == 'in development' and fuel_type == 'gas':
            status_phrase = f"'''{unit_name} Complex''' ({unit_name_local}) is a {fuel_type} {unit_type} in development in {sub_prefix}{country_prefix}{country}.{unit_status_ref}\n"
        elif unit_status == 'discovered':
            status_phrase = f"'''{unit_name} Complex''' ({unit_name_local}) is a discovered {fuel_type} {unit_type} in {sub_prefix}{country_prefix}{country}.{unit_status_ref}\n"
        else:
            if fuel_type in ['oil and gas','oil']:
                status_phrase = f"'''{unit_name} Complex''' ({unit_name_local}) is an {fuel_type} {unit_type} in {sub_prefix}{country_prefix}{country}.{unit_status_ref}"
                print(f"Complex status not handled yet: {unit_status}; for {unit_name}")
            else:
                status_phrase = f"'''{unit_name} Complex''' ({unit_name_local}) is a {fuel_type} {unit_type} in {sub_prefix}{country_prefix}{country}.{unit_status_ref}"
                print(f"Complex status not handled yet: {unit_status}; for {unit_name}")

        wikistr += status_phrase

    # Asset only in United States, add sentence describing how data was compiled
    if page_lang == 'English' and unit_type == 'asset' and subnational in ['California', 'Colorado', 'Louisiana', 'North Dakota', 'Texas']:
        wikistr += f' For all assets in {subnational}, the asset name is based on the name of the field and the name of the operator.'

    if page_lang == 'English' and unit_type == 'asset' and subnational == 'Federal offshore':
        wikistr += f' For all federal offshore assets, the asset name is based on the name of the field and the name of the operator.'

    if page_lang == 'English' and unit_type == 'asset' and subnational == 'Ohio':
        wikistr += f' For all assets in {subnational}, the asset name is based on the name of the county and the name of the owner.'

    if page_lang == 'English' and unit_type == 'asset' and subnational in ['West Virginia', 'Pennsylvania','New Mexico']:
        wikistr += f' For all assets in {subnational}, the asset name is based on the name of the county and the name of the operator.'

    if page_lang == 'English' and unit_type == 'asset' and subnational == 'Wyoming':
        wildcat_ref = '<ref>{{cite web |url=https://www.wsgs.wyo.gov/products/wsgs-2020-oil-natural-gas-summary.pdf |title=Oil and Natural Gas Resources in Wyoming |date= January 2020 |author= |website= |access-date=September 30, 2021 |archive-url=https://web.archive.org/web/20210930160149/https://www.wsgs.wyo.gov/products/wsgs-2020-oil-natural-gas-summary.pdf |archive-date=September 30, 2021 |url-status=live}}</ref>'
        if "Wildcat - " in str(unit_name):
            wikistr += f' For all wildcat{wildcat_ref} fields in Wyoming, the asset name is based on the name of the field, the name of the county, and the name of the operator.'
        else:
            wikistr += f' For all non-wildcat{wildcat_ref} fields in Wyoming, the asset name is based on the name of the field and the name of the operator.'

    # Add sentence how oil sands projects were compiled
    if page_lang == 'English' and unit_type == 'project' and subnational == 'Alberta':
        oil_sands_area_map_ref = '<ref>{{cite web |url=https://static.aer.ca/prd/documents/catalog/Map90_Oil_Gas_Fields_Small.pdf |title=Alberta Oil & Gas Fields |date= January 2021 |author= |website= |access-date=September 30, 2021 |archive-url=https://web.archive.org/web/20210930172956/https://static.aer.ca/prd/documents/catalog/Map90_Oil_Gas_Fields_Small.pdf |archive-date=September 30, 2021 |url-status=live}}</ref>'
        scheme_number_ref = '<ref>{{cite web |url=https://www.alberta.ca/oil-sands-101.aspx |title=Oil Sands 101 |date= |author= |website= |access-date=September 30, 2021 |archive-url=https://web.archive.org/web/20210930173407/https://www.alberta.ca/oil-sands-101.aspx |archive-date=September 30, 2021 |url-status=live}}</ref>'
        wikistr += f' For all oil sands projects in Alberta, the project name is based on the oil sands area name{oil_sands_area_map_ref} and the scheme approval number.{scheme_number_ref}'

#     # If there is an associated project/complex add sentence, and vice versa for projects/complexes and associated fields
#     if page_lang == 'English' and unit_type == 'complex' and pd.isna(unit_project_complex) == False:
#         string = '' #initialize
#         for x in to_process.index:
#             if to_process.at[x,'Project or complex'] == unit_project_complex and to_process.at[x,'Unit type'] != 'complex':
#                 wiki_page_URl1 = to_process.at[x,'Wiki page URL']
#                 wiki_name1 = to_process.at[x,'Wiki name']
#                 string += f"\n*[{wiki_page_URl1} {wiki_name1}]"
#         if string != '' and pd.isna(string) == False:
#             wikistr += f'This complex contains the following fields:{string}\n'

#     if page_lang == 'English' and unit_type == 'project' and pd.isna(unit_project_complex) == False:
#         string2 = '' #initialize
#         for y in to_process.index:
#             if unit_project_complex == to_process.at[y,'Project or complex'] and to_process.at[y,'Unit type'] != 'project':
#                 wiki_page_URL2 = to_process.at[y,'Wiki page URL']
#                 wiki_name2 = to_process.at[y,'Wiki name']
#                 string2 += f"\n*[{wiki_page_URL2} {wiki_name2}]"
#         if string2 != '' and pd.isna(string2) == False:
#             wikistr += f' This project contains the following fields:{string2}\n'

#     if page_lang == 'English' and unit_type == 'field' and pd.isna(unit_project_complex) == False:
#         for z in to_process.index:
#             if unit_project_complex == to_process.at[z,'Project or complex'] and to_process.at[z,'Unit type'] == 'complex':
#                 wiki_page_URL3 = to_process.at[z,'Wiki page URL']
#                 wikistr += f' This {fuel_type} {unit_type} is part of the larger [{wiki_page_URL3} {unit_project_complex}] complex.\n'
#             elif unit_project_complex == to_process.at[z,'Project or complex'] and to_process.at[z,'Unit type'] == 'project':
#                 wiki_page_URL4 = to_process.at[z,'Wiki page URL']
#                 wikistr += f' This {fuel_type} {unit_type} is part of the larger [{wiki_page_URL4} {unit_project_complex}] project.\n'

 # If there is an associated project/complex add sentence, and vice versa for projects/complexes and associated fields
    if page_lang == 'English' and unit_type == 'complex' and pd.isna(unit_project_complex) == False:
        string = '' #initialize
        for x in goget_main2.index:
            if goget_main2.at[x,'Project or complex'] == unit_project_complex and goget_main2.at[x,'Unit type'] != 'complex':
                wiki_page_URl1 = goget_main2.at[x,'Wiki page URL']
                wiki_name1 = goget_main2.at[x,'Wiki name']
                string += f"\n*[{wiki_page_URl1} {wiki_name1}]"
        if string != '' and pd.isna(string) == False:
            wikistr += f'This complex contains the following fields:{string}\n'

    if page_lang == 'English' and unit_type == 'project' and pd.isna(unit_project_complex) == False:
        string2 = '' #initialize
        for y in goget_main2.index:
            if unit_project_complex == goget_main2.at[y,'Project or complex'] and goget_main2.at[y,'Unit type'] != 'project':
                wiki_page_URL2 = goget_main2.at[y,'Wiki page URL']
                wiki_name2 = goget_main2.at[y,'Wiki name']
                string2 += f"\n*[{wiki_page_URL2} {wiki_name2}]"
        if string2 != '' and pd.isna(string2) == False:
            wikistr += f' This project contains the following fields:{string2}\n'

    if page_lang == 'English' and unit_type == 'field' and pd.isna(unit_project_complex) == False:
        for z in goget_main2.index:
            if unit_project_complex == goget_main2.at[z,'Project or complex'] and goget_main2.at[z,'Unit type'] == 'complex':
                wiki_page_URL3 = goget_main2.at[z,'Wiki page URL']
                wikistr += f' This {fuel_type} {unit_type} is part of the larger [{wiki_page_URL3} {unit_project_complex}] complex.\n'
            elif unit_project_complex == goget_main2.at[z,'Project or complex'] and goget_main2.at[z,'Unit type'] == 'project':
                wiki_page_URL4 = goget_main2.at[z,'Wiki page URL']
                wikistr += f' This {fuel_type} {unit_type} is part of the larger [{wiki_page_URL4} {unit_project_complex}] project.\n'
    wikistr += "\n"
    # --------------
    # LOCATION SECTION
    wikistr += "\n"
    wikistr += f"==Location==\n"
    latitude = "{:.4f}".format(to_process.at[row, 'Latitude'])
    longitude = "{:.4f}".format(to_process.at[row, 'Longitude'])
    location_accuracy = to_process.at[row,'Location accuracy']
    location_ref = to_process.at[row,'Location source']

    if page_lang == 'English' and unit_type == 'unconventional field' and pd.isna(latitude) == False and pd.isna(longitude) == False:
        wikistr += f"The map below shows the {location_accuracy} location of the field in {sub_prefix}{country_prefix}{country}.{location_ref}"
        wikistr += '{{#display_map: '
        wikistr += f"{latitude}, {longitude}|width=600|height=500|type=map|zoom=6"
        wikistr += "}}\n"
    elif page_lang == 'English' and pd.isna(latitude) == False and pd.isna(longitude) == False and pd.isna(location_accuracy) == False:
        wikistr += f"The map below shows the {location_accuracy} location of the {unit_type} in {sub_prefix}{country_prefix}{country}.{location_ref}"
        wikistr += '{{#display_map: '
        wikistr += f"{latitude}, {longitude}|width=600|height=500|type=map|zoom=6"
        wikistr += "}}\n"
    else:
        wikistr += f"The location of the {unit_type} in {sub_prefix}{country_prefix}{country} is not known.{location_ref}\n"

    # --------------
    # PROJECT DETAILS
    wikistr += "\n"
    wikistr += f"==Project Details==\n"

    if pd.isna(unit_status) == False:
        status_cap = unit_status
        status_cap = status_cap[0].upper() + status_cap[1:]
        wikistr += f"*'''Status:''' {status_cap}{unit_status_ref}\n"
    else:
        wikistr += f"*'''Status:'''\n"

    if pd.isna(latitude) == False and pd.isna(longitude) == False and pd.isna(location_accuracy) == False:
        wikistr += f"*'''Coordinates:''' {latitude}, {longitude} ({location_accuracy}){location_ref}\n"
    else:
        wikistr += f"*'''Coordinates:'''\n"

    operator = to_process.at[row, 'Operator']
    operator_ref = to_process.at[row,'Operator source']
    if operator != '' and pd.isna(operator)==False:
        wikistr += f"*'''Operator:''' {operator}{operator_ref}\n"
    else:
        wikistr += f"*'''Operator:'''\n"

    owners_ref = to_process.at[row,'Owners source']
    owner_df = pd.DataFrame(columns = ['Unit ID','Owner Name', 'Owner Percentage'])

    if pd.isna(to_process.at[row,'Owner 1']) == False:
        if pd.isna(to_process.at[row,'Owner 1 %']) == True:
            owner_name = str(to_process.at[row, 'Owner 1'])
            owner_pct = ""
            owner_df = owner_df.append({'Unit ID' : unit_ID, 'Owner Name' : owner_name, 'Owner Percentage' : owner_pct}, ignore_index = True)
        else:
            owner_name = str(to_process.at[row, 'Owner 1'])
            owner_pct = "{:.1%}".format(to_process.at[row,'Owner 1 %'])
            owner_df = owner_df.append({'Unit ID' : unit_ID, 'Owner Name' : owner_name, 'Owner Percentage' : owner_pct}, ignore_index = True)
        if pd.isna(to_process.at[row,'Owner 2']) == False:
            if pd.isna(to_process.at[row,'Owner 2 %']) == True:
                owner_name = str(to_process.at[row, 'Owner 2'])
                owner_pct = ""
                owner_df = owner_df.append({'Unit ID' : unit_ID, 'Owner Name' : owner_name, 'Owner Percentage' : owner_pct}, ignore_index = True)
            else:
                owner_name = str(to_process.at[row, 'Owner 2'])
                owner_pct = "{:.1%}".format(to_process.at[row,'Owner 2 %'])
                owner_df = owner_df.append({'Unit ID' : unit_ID, 'Owner Name' : owner_name, 'Owner Percentage' : owner_pct}, ignore_index = True)
            if pd.isna(to_process.at[row,'Owner 3']) == False:
                if pd.isna(to_process.at[row,'Owner 3 %']) == True:
                    owner_name = str(to_process.at[row, 'Owner 3'])
                    owner_pct = ""
                    owner_df = owner_df.append({'Unit ID' : unit_ID, 'Owner Name' : owner_name, 'Owner Percentage' : owner_pct}, ignore_index = True)
                else:
                    owner_name = str(to_process.at[row, 'Owner 3'])
                    owner_pct = "{:.1%}".format(to_process.at[row,'Owner 3 %'])
                    owner_df = owner_df.append({'Unit ID' : unit_ID, 'Owner Name' : owner_name, 'Owner Percentage' : owner_pct}, ignore_index = True)
                if pd.isna(to_process.at[row,'Owner 4']) == False:
                    if pd.isna(to_process.at[row,'Owner 4 %']) == True:
                        owner_name = str(to_process.at[row, 'Owner 4'])
                        owner_pct = ""
                        owner_df = owner_df.append({'Unit ID' : unit_ID, 'Owner Name' : owner_name, 'Owner Percentage' : owner_pct}, ignore_index = True)
                    else:
                        owner_name = str(to_process.at[row, 'Owner 4'])
                        owner_pct = "{:.1%}".format(to_process.at[row,'Owner 4 %'])
                        owner_df = owner_df.append({'Unit ID' : unit_ID, 'Owner Name' : owner_name, 'Owner Percentage' : owner_pct}, ignore_index = True)
                    if pd.isna(to_process.at[row,'Owner 5']) == False:
                        if pd.isna(to_process.at[row,'Owner 5 %']) == True:
                            owner_name = str(to_process.at[row, 'Owner 5'])
                            owner_pct = ""
                            owner_df = owner_df.append({'Unit ID' : unit_ID, 'Owner Name' : owner_name, 'Owner Percentage' : owner_pct}, ignore_index = True)
                        else:
                            owner_name = str(to_process.at[row, 'Owner 5'])
                            owner_pct = "{:.1%}".format(to_process.at[row,'Owner 5 %'])
                            owner_df = owner_df.append({'Unit ID' : unit_ID, 'Owner Name' : owner_name, 'Owner Percentage' : owner_pct}, ignore_index = True)

    owner_df.sort_values('Owner Percentage', ascending = False)
    owner_string = ""

    for x in owner_df.index:
        # Show one decimal if applicable
        percent = owner_df.at[x,'Owner Percentage']
        if percent.endswith('.0%'):
            percent = percent.replace('.0%','%')
            owner_df.at[x,'Owner Percentage'] = percent
        if owner_df.at[x,'Owner Percentage'] != '':
            owner_df.at[x,'Owner Percentage'] = str(" (" + owner_df.at[x,'Owner Percentage'] + ")")
        else:
            owner_df.at[x,'Owner Percentage'] = ''

    for owner_row in owner_df.index:
        sel_cell = str(owner_df.at[owner_row,'Unit ID'])
        if unit_ID == sel_cell:
            owner_string += " " + str(owner_df.at[owner_row,'Owner Name']) + str(owner_df.at[owner_row,'Owner Percentage']) + ";"

    if unit_ID not in owner_df['Unit ID'].tolist():
        wikistr += f"*'''Owner:'''\n"
    else:
        owner_string = owner_string[:-1]
        wikistr += f"*'''Owner:''' {owner_string}{owners_ref}\n"

    parent_df = pd.DataFrame(columns = ['Unit ID', 'Parent Name', 'Parent Percentage','Parent Ref'])
    owners_column = ['Owner 1','Owner 2','Owner 3','Owner 4','Owner 5']
    for col in owners_column:
        owner_name = to_process.at[row,col]
        if pd.isna(owner_name) == False:
            if col == 'Owner 1' and pd.isna(to_process.at[row,'Owner 1 %']) == False:
                owner_pct = float(to_process.at[row,'Owner 1 %'])
            elif col == 'Owner 2' and pd.isna(to_process.at[row,'Owner 2 %']) == False:
                owner_pct = float(to_process.at[row,'Owner 2 %'])
            elif col == 'Owner 3' and pd.isna(to_process.at[row,'Owner 3 %']) == False:
                owner_pct = float(to_process.at[row,'Owner 3 %'])
            elif col == 'Owner 4' and pd.isna(to_process.at[row,'Owner 4 %']) == False:
                owner_pct = float(to_process.at[row,'Owner 4 %'])
            elif col == 'Owner 5' and pd.isna(to_process.at[row,'Owner 5 %']) == False:
                owner_pct = float(to_process.at[row,'Owner 5 %'])
        else:
            owner_pct = ''
            pass



    for i in parent_df.index:
        par_percent = parent_df.at[i,'Parent Percentage']
        if par_percent.endswith('.0%'):
            par_percent = par_percent.replace('.0%','%')
            parent_df.at[i,'Parent Percentage'] = par_percent
        if parent_df.at[i,'Parent Percentage'] != '':
            parent_df.at[i,'Parent Percentage'] = str(" (" + parent_df.at[i,'Parent Percentage'] + ")")
        else:
            parent_df.at[i,'Parent Percentage'] = ''

    parent_df.sort_values('Parent Percentage', ascending = False)
    parent_string = ""
    for parent_row in parent_df.index:
        sel_cell = str(parent_df.at[parent_row,'Unit ID'])
        if unit_ID == sel_cell:
            parent_string += " " + str(parent_df.at[parent_row,'Parent Name']) + parent_df.at[parent_row,'Parent Percentage'] + str(parent_df.at[parent_row,'Parent Ref']) + ";"

    if unit_ID not in parent_df['Unit ID'].tolist() and page_lang == 'English':
        wikistr += f"*'''Parent:'''\n"
    else:
        parent_string = parent_string[:-1]
        wikistr += f"*'''Parent:'''{parent_string}\n"

    discovery_year = to_process.at[row, 'Discovery year']
    discovery_year_ref = to_process.at[row,'Discovery year source']
    if discovery_year != '' and pd.isna(discovery_year) == False:
        wikistr += f"*'''Discovery year:''' {discovery_year}{discovery_year_ref}\n"
    else:
        wikistr += f"*'''Discovery year:'''\n"

    prod_start_year = to_process.at[row, 'Production start year']
    prod_start_year_ref = to_process.at[row,'Production start source']
    if prod_start_year != '' and pd.isna(prod_start_year)==False:
        wikistr += f"*'''Production start year:''' {prod_start_year}{prod_start_year_ref}\n"
    else:
        wikistr += f"*'''Production start year:'''\n"

    unit_basin = to_process.at[row, 'Basin']
    if unit_basin != '' and pd.isna(unit_basin) == False:
        wikistr += f"*'''Basin:''' {unit_basin}\n"
    else:
        wikistr += f"*'''Basin:'''\n"

    unit_concession_block = to_process.at[row,'Concession / block']
    fields_concession_block_ref = to_process.at[row,'Concession / block source']

    if unit_type != '' and pd.isna(unit_concession_block) == False:
        wikistr += f"*'''Concession/Block:''' {unit_concession_block}{fields_concession_block_ref}\n"
    else:
        wikistr += f"*'''Concession/Block:'''\n"

    if unit_project_complex != '' and pd.isna(unit_project_complex) == False:
        wikistr += f"*'''Project/Complex:''' {unit_project_complex}\n"
    else:
        wikistr += f"*'''Project/Complex:'''\n"

       # --------------
    # PRODUCTION AND RESEVES SECTION
    wikistr += "\n"
    wikistr += f"==Production and Reserves==\n"
    if page_lang == 'English' and unit_type == 'block':
        wikistr += f"==== '''Table 1:''' Production and Reserves - {str.capitalize(unit_type)} {unit_name}====\n"
    elif page_lang == 'English':
        wikistr += f"==== '''Table 1:''' Production and Reserves - {unit_name} {str.capitalize(unit_type)}====\n"

    wikistr += ''' {| class="wikitable sortable" style=text-align:right\n'''
    wikistr += "|+ \n"
    wikistr += f"!Category\n"
    wikistr += f"!Fuel Description\n"
    wikistr += f"!Reserve Classification\n"
    wikistr += f"!Quantity\n"
    wikistr += f"!Units\n"
    wikistr += f"!Data Year\n"
    wikistr += f"!Source\n"

    bbl_note2 = '' #initialize
    boe_note2 = '' #initialize
    m3_note2 = '' #initialize
    bbl_note = '' #initialize
    boe_note = '' #initialize
    m3_note = '' #initialize
    total_liquids_note = '' #initialize
    EUR_note = '' #initialize
    NGL_note = '' #initialize
    align_text_right = str('style="text-align:right;"')
    align_text_center = str('style="text-align:center;"')

    for r in to_process2.index:
        if unit_ID == to_process2.at[r,'Unit ID']:
            prodreserves_category = to_process2.at[r,'Production/reserves']
            prodreserves_fueldescript = to_process2.at[r,'Fuel description']
            prodreserves_reserveclassification = to_process2.at[r,'Reserves classification (original)']
            prodreserves_quantity = to_process2.at[r,'Quantity (converted)']
            if prodreserves_quantity >= 10:
                prodreserves_quantity = round(prodreserves_quantity,4)
                prodreserves_quantity = "{:,.0f}".format(prodreserves_quantity).replace(","," ")
            elif prodreserves_quantity < 10 and prodreserves_quantity >= 1:
                prodreserves_quantity = "{:,.1f}".format(prodreserves_quantity)
            elif prodreserves_quantity < 1 and prodreserves_quantity >= 0.1:
                prodreserves_quantity = "{:,.2f}".format(prodreserves_quantity)
            elif prodreserves_quantity < 0.1 and prodreserves_quantity >= 0.05:
                prodreserves_quantity = "{:,.3f}".format(prodreserves_quantity)
            elif prodreserves_quantity < 0.05 and prodreserves_quantity >= 0:
                prodreserves_quantity = "{:,.0f}".format(prodreserves_quantity)
            prodreserves_units = str(to_process2.at[r,'Units (converted)'])
            prodreserves_datayear = str(to_process2.at[r,'Data year'])
            prodreserves_ref = to_process2.at[r,'Data source']

            if pd.isna(prodreserves_reserveclassification) == True or prodreserves_reserveclassification == '':
                prodreserves_reserveclassification = 'Not applicable'

            if prodreserves_quantity != '':
                wikistr += "|-\n"
                wikistr += f"|{align_text_center}|{prodreserves_category}\n"
                wikistr += f"|{align_text_center}|{prodreserves_fueldescript}\n"
                wikistr += f"|{align_text_center}|{prodreserves_reserveclassification}\n"
                wikistr += f"|{align_text_right}|{prodreserves_quantity}\n"
                wikistr += f"|{align_text_center}|{prodreserves_units}\n"
                wikistr += f"|{align_text_center}|{prodreserves_datayear}\n"
                wikistr += f"|{align_text_center}|{prodreserves_ref}\n"

                if prodreserves_units == 'million bbl':
                    bbl_note2 = "million bbl = million barrels"
                if prodreserves_units == 'million boe':
                    boe_note2 = "million boe = barrels of oil equivalent"
                if prodreserves_units == 'million m³':
                    m3_note2 = "million m³ = million cubic meters"
                if prodreserves_units == 'million bbl/y' and page_lang == 'English':
                    bbl_note = "million bbl/y = million barrels per year"
                if prodreserves_units == 'million boe/y':
                    boe_note = "million boe/y = million barrels of oil equivalent per year"
                if prodreserves_units == 'million m³/y':
                    m3_note = "million m³/y = million cubic meters per year"
                if prodreserves_fueldescript == 'total liquids':
                    total_liquids_note = "total liquids = oil, including condensate and natural gas liquids"
                if prodreserves_fueldescript == 'NGL':
                    NGL_note = "NGL = Natural gas liquids"
                if prodreserves_reserveclassification == 'EUR':
                    EUR_note = "EUR = Estimated Ultimate Recovery"

    wikistr += "|}\n"
    wikistr += '<div style="font-size:89%">\n'
    if bbl_note2 != '':
        wikistr +=f":{bbl_note2}\n"
    if boe_note2 != '':
        wikistr +=f":{boe_note2}\n"
    if m3_note2 != '':
        wikistr +=f":{m3_note2}\n"
    if bbl_note != '':
        wikistr +=f":{bbl_note}\n"
    if boe_note != '':
        wikistr += f":{boe_note}\n"
    if m3_note != '':
        wikistr += f":{m3_note}\n"
    if total_liquids_note != '':
        wikistr += f":{total_liquids_note}\n"
    if EUR_note != '':
        wikistr += f":{EUR_note}\n"
    if NGL_note != '':
        wikistr += f":{NGL_note}\n"

    wikistr += "</div>"
    wikistr += "\n"
     # --------------
    # REFERENCES
    wikistr += f"==Articles and Resources==\n"
    wikistr += f"===References===\n"
    wikistr += "<references />\n"

    # --------------
    # CATEGORIES
    if page_lang == 'English':
        wikistr += f"[[category: Oil and gas extraction]]\n"
        wikistr += f"[[category: Oil and gas extraction in {country_prefix}{country}]]\n"

    wikistr += "__NOTOC__"

    wiki_URL_df = wiki_URL_df.append({'Unit ID' : unit_ID, 'Wiki URL' : page_URL}, ignore_index = True)

    #save wikistr as text file
    #with file name wiki_page_name (which includes timestamp, if specified)
    # and put in timestamped folder
    if page_lang == 'English':
        text_file_name_prefix = wiki_name
        text_file_name_prefix = text_file_name_prefix.replace('/', '%2f')

    text_file_name = f"{text_file_name_prefix}.txt"
    text_file = open(text_file_path + text_file_name, "w")

   # Condense references
    split_by_ref = wikistr.split('<ref>')
    number_of_refs = len(split_by_ref)
    try:

        if number_of_refs == 1:
            ref_inner = split_by_ref[1].split('</ref>')[0]
            ref_full = "<ref>" + ref_inner + "</ref>"

        elif number_of_refs > 1:
            for ref_num in range(1, number_of_refs):
                ref_inner = split_by_ref[ref_num].split('</ref>')[0]
                ref_full = "<ref>" + ref_inner + "</ref>"

                # from Stack Overflow: https://stackoverflow.com/a/46399948
                letter_ref = chr(ord('@')+ref_num)

                full_named_ref = f"<ref name='ref_{letter_ref}'>" + ref_inner + "</ref>"
                short_named_ref = f"<ref name='ref_{letter_ref}' />"

                # replace first instance with full named reference &
                # replace any remaining with short named reference
                wikistr = wikistr.replace(ref_full, full_named_ref, 1)
                wikistr = wikistr.replace(ref_full, short_named_ref)
    except:
        print(f"Hit error for: {unit_name}")

    text_file.write(wikistr)
    text_file.close()

# ===== Cell 27 =====
# Output wiki URL list to Excel
timestamp = time.strftime('%Y-%m-%d_%H%M%S', time.localtime())
if page_lang == 'English':
    wiki_URL_df.to_excel(f'Wiki URLs-English {timestamp}.xlsx', index=False)
else:
    wiki_URL_df.to_excel(f'Wiki URLs-Other languages {timestamp}.xlsx', index=False)

# ===== Cell 28 =====
text_file.write(wikistr)
