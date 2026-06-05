"""
routes_to_wkt.py

Migrated from Colab notebook: Convert routes from Google Maps to WKT 2021-03-19.ipynb
Auto-converted to a Python script. Colab-specific lines
(drive.mount, google.colab imports, shell/magic commands) have been
commented out and flagged; pip installs moved to ../requirements.txt.
"""

# ===== Cell 1 =====
import pandas as pd
from shapely.geometry import Point, LineString, MultiLineString, Polygon

# ===== Cell 2 =====
gfit_pipes = pd.read_excel('/content/Pipelines_TMAC_formatted.xlsx', sheet_name='Gas pipelines')

# ===== Cell 3 =====
def convert_gfit_to_linestring(coord_str, pipeline_name):
    '''
    Takes string from GFIT column of coordinates for a single pipeline,
    converts that string into Shapely LineString or MultiLinestring.
    '''

    if ':' in coord_str and ';' not in coord_str:
        # simple geometry; no branching
        # create nested list of lists, separating on colons
        coord_list = coord_str.split(':')

        coord_list_tuples = []

        # non-branched pipeline (nested list with one level)
        # convert nested list of lists to list of tuples
        for element in coord_list:
            element_tuple = (float(element.split(',')[1]),
                             float(element.split(',')[0]))
            coord_list_tuples.append(element_tuple)

        route_conv = LineString(coord_list_tuples)

    elif ':' in coord_str and ';' in coord_str:
        # create a nested list of lists, separating on semicolons
        coord_list = coord_str.split(';')

        # create a second level of nesting, separating on colons
        coord_list = [x.split(':') for x in coord_list]

        # branched pipeline (nested list with two levels)
        route_conv_ls_all = []

        for nested_list in coord_list:
            coord_list_tuples = []

            for element in nested_list:
                element_tuple = (float(element.split(',')[1]),
                                 float(element.split(',')[0]))
                coord_list_tuples.append(element_tuple)

            # process coord_list_tuples
            try:
                route_conv_ls = LineString(coord_list_tuples)
                route_conv_ls_all.append(route_conv_ls)
            except:
                print(f"Exception for {pipeline_name}; coord_list_tuples: {coord_list_tuples}") # for db
                pass

        route_conv = MultiLineString(route_conv_ls_all)

    elif coord_str in ['Capacity expansion only', 'Unavailable']:
        # create empty MultiLineString; no coordinates
        route_conv = MultiLineString([])

        print(f'No coordinates for {pipeline_name}: {coord_str}')

    else:
        # create empty MultiLineString; coordinates were missing or misformatted
        route_conv = MultiLineString([])

        print(f'Missing or misformatted coordinates for {pipeline_name}')

    return route_conv

# ===== Cell 4 =====
def convert_all_pipelines(df):
    """
    Apply the conversion function to all pipelines in the dataframe.
    """
    # create geometry column with empty strings
    df['geometry'] = ''

    # filter to keep only pipelines with routes
    mask_route_1 = df['Route'].str.contains(',')
    mask_route_2 = df['Route'].str.contains(':')
    pipes_with_route = df.loc[(mask_route_1) & (mask_route_2)]

    for row in pipes_with_route.index:
        route_str = df.at[row, 'Route']
        pipeline_name = df.at[row, 'Name']
        route_str_converted = convert_gfit_to_linestring(route_str, pipeline_name)
        df.at[row, 'geometry'] = route_str_converted

    return df

# ===== Cell 5 =====
gfit_pipes_conv = convert_all_pipelines()

# ===== Cell 6 =====
# show
gfit_pipes_conv[['Name', 'geometry']].head(20)

# ===== Cell 7 =====
# export
# can use gfit_pipes_conv.to_excel()
# and fill in the path & file name you want to save to
