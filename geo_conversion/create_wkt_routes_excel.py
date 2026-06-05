"""
create_wkt_routes_excel.py

Migrated from Colab notebook: Scott_ create-wkt-routes-Excel-file-INTERNAL.ipynb
Auto-converted to a Python script. Colab-specific lines
(drive.mount, google.colab imports, shell/magic commands) have been
commented out and flagged; pip installs moved to ../requirements.txt.
"""

# ===== Cell 1 =====
# [moved to requirements.txt] !pip install pygsheets
# [moved to requirements.txt] !pip install geopandas
import pygsheets # use 'pip install pygsheets'
import numpy
import datetime

import pandas
import geopandas
#import geopandas.tools import overlay

import shapely

# ===== Cell 2 =====
spreadsheet = ('/content/Pipelines copy (7_28_22) TMAC formatted string removed.xlsx')
gas_pipes = ('Gas pipelines').get_as_df(1)
pipes_orig = gas_pipes

# ===== Cell 3 =====
#fuel_type = 'oil'
fuel_type = 'gas'
fuel_type = 'oil-and-gas'

if fuel_type=='gas':
    pipes_orig = gas_pipes
    pipe.drop('CapacityBcm/y', inplace=True)

# ===== Cell 4 =====
# clean up column 'Route'
#pipes_orig['Route'] = pipes_orig['Route'].str.strip(1)

# get rid of "N/A" and any empty routes (which would be empty rows)
#pipes_orig = pipes_orig[pipes_orig['Route']!='N/A']
#pipes_orig = pipes_orig[pipes_orig['Route']!='']

# possible missing route options
missing_route_options = ['Unavailable',
                         'Capacity expansion only',
                         'Bidirectionality upgrade only',
                         'Short route (< 100 km)']

pipes_withroute_df = pipes_orig

# ===== Cell 5 =====
def convert_gfit_to_linestring(coord_str, pipeline_name, segment_name):
    '''
    Takes string from GFIT column of coordinates for a single pipeline,
    converts that string into Shapely LineString or MultiLinestring.
    '''
    #print(coord_str, pipeline_name)
    if ':' in coord_str and ';' not in coord_str:
        # simple geometry; no branching
        # create nested list of lists, separating on colons
        coord_list = coord_str.split(':')
        coord_list_tuples = []
        # non-branched pipeline (nested list with one level)
        # convert nested list of lists to list of tuples
        try:
            for element in coord_list:
                element_tuple = (float(element.split(',')[1]),
                                 float(element.split(',')[0]))
                coord_list_tuples.append(element_tuple)
        except:
            print(f"Exception for {pipeline_name}; {segment_name}; element: {element}") # for db
        route_conv = shapely.geometry.LineString(coord_list_tuples)

    elif ':' in coord_str and ';' in coord_str:
        # create a nested list of lists, separating on semicolons
        coord_list = coord_str.split(';')
        # create a second level of nesting, separating on colons
        coord_list = [x.split(':') for x in coord_list]
        # branched pipeline (nested list with two levels)
        route_conv_list_all = []

        for nested_list in coord_list:
            coord_list_tuples = []
            # process element
            try:
                for element in nested_list:
                    element_tuple = (float(element.split(',')[1]),
                                     float(element.split(',')[0]))
                    coord_list_tuples.append(element_tuple)
            except:
                print(f"Exception for {pipeline_name}; segment {segment_name}; element: {element}") # for db
            # process coord_list_tuples
            try:
                route_conv_list = shapely.geometry.LineString(coord_list_tuples)
                route_conv_list_all.append(route_conv_list)
            except:
                print(f"Exception for {pipeline_name}; coord_list_tuples: {coord_list_tuples}") # for db
                pass

        route_conv = shapely.geometry.MultiLineString(route_conv_list_all)

    return route_conv

# ===== Cell 6 =====
def convert_all_pipelines(df):
    """
    Apply the conversion function to all pipelines in the dataframe.
    """
    # create geometry column with empty strings
    df['geometry'] = ''

    # filter to keep only pipelines with routes
    mask_route = df['Route'].str.contains(',' or ':')
    pipes_with_route = df.loc[mask_route]

    for row in pipes_with_route.index:
        route_str = df.at[row, 'Route']
        pipeline_name = df.at[row, 'PipelineName']
        segment_name = df.at[row, 'SegmentName']
        route_str_converted = convert_gfit_to_linestring(route_str, pipeline_name, segment_name)
        df.at[row, 'geometry'] = route_str_converted

    return df
    df.to_csv('test')

# ===== Cell 7 =====
def convert_gfit_to_linestring(coord_str, pipeline_name, segment_name):
    '''
    Takes string from GFIT column of coordinates for a single pipeline,
    converts that string into Shapely LineString or MultiLinestring.
    '''
    #print(coord_str, pipeline_name)
    if ':' in coord_str and ';' not in coord_str:
        # simple geometry; no branching
        # create nested list of lists, separating on colons
        coord_list = coord_str.split(':')
        coord_list_tuples = []
        # non-branched pipeline (nested list with one level)
        # convert nested list of lists to list of tuples
        try:
            for element in coord_list:
                element_tuple = (float(element.split(',')[1]),
                                 float(element.split(',')[0]))
                coord_list_tuples.append(element_tuple)
        except:
            print(f"Exception for {pipeline_name}; {segment_name}; element: {element}") # for db
        route_conv = shapely.geometry.LineString(coord_list_tuples)

    elif ':' in coord_str and ';' in coord_str:
        # create a nested list of lists, separating on semicolons
        coord_list = coord_str.split(';')
        # create a second level of nesting, separating on colons
        coord_list = [x.split(':') for x in coord_list]
        # branched pipeline (nested list with two levels)
        route_conv_list_all = []

        for nested_list in coord_list:
            coord_list_tuples = []
            # process element
            try:
                for element in nested_list:
                    element_tuple = (float(element.split(',')[1]),
                                     float(element.split(',')[0]))
                    coord_list_tuples.append(element_tuple)
            except:
                print(f"Exception for {pipeline_name}; segment {segment_name}; element: {element}") # for db
            # process coord_list_tuples
            try:
                route_conv_list = shapely.geometry.LineString(coord_list_tuples)
                route_conv_list_all.append(route_conv_list)
            except:
                print(f"Exception for {pipeline_name}; coord_list_tuples: {coord_list_tuples}") # for db
                pass

        route_conv = shapely.geometry.MultiLineString(route_conv_list_all)

    return route_conv

# ===== Cell 8 =====
def convert_all_pipelines(df):
    """
    Apply the conversion function to all pipelines in the dataframe.
    """
    # create geometry column with empty strings
    df['geometry'] = ''

    # filter to keep only pipelines with routes
    mask_route = df['Route'].str.contains(',' or ':')
    pipes_with_route = df.loc[mask_route]

    for row in pipes_with_route.index:
        route_str = df.at[row, 'Route']
        pipeline_name = df.at[row, 'PipelineName']
        segment_name = df.at[row, 'SegmentName']
        route_str_converted = convert_gfit_to_linestring(route_str, pipeline_name, segment_name)
        df.at[row, 'geometry'] = route_str_converted

    return df

# ===== Cell 9 =====
# code to create a dataframe with WKT formatted geometry

# (1) copy gas_pipelines, clean up
to_convert = pipes_withroute_df.copy()#gas_pipes.copy()s)]

# (2) convert all pipelines
pipes_wkt_df = convert_all_pipelines(to_convert)
pipes_wkt_df = pipes_wkt_df.reset_index(drop=True)

# (3) store in a GeoDataFrame, attach a projection, transform to a different one
pipes_wkt_gdf = geopandas.GeoDataFrame(pipes_wkt_df, geometry=pipes_wkt_df['geometry'])
pipes_wkt_gdf = pipes_wkt_gdf.set_crs('epsg:4326')
pipes_wkt_gdf_4087 = pipes_wkt_gdf.to_crs('epsg:4087')




# ===== Cell 10 =====
pipes_wkt_df[['ProjectID','geometry']].to_csv("Test")
