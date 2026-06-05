"""
goget_maps.py

Migrated from Colab notebook: Copy of 2024 GOGET Maps 2024 02 27
Auto-converted to a Python script. Colab-specific lines
(drive.mount, google.colab imports, shell/magic commands) have been
commented out and flagged; pip installs moved to ../requirements.txt.
"""

# # FIGURE AND MAPS

# Adpated from Bairds' europe-gas-report-2024-FIGURES-AND-MAPS.ipynb https://github.com/GlobalEnergyMonitor/GOIT-GGIT-research/blob/main/europe-gas-report-2024/europe-gas-report-2024-FIGURES-AND-MAPS.ipynb

# ===== Cell 1 =====
# note that the order of points in GeoPandas is longitude, latitude
# (opposite order from that of many data sets)

import geopandas as gpd
import shapely.geometry
import shapely.ops
import pyproj
import pandas as pd

import time
import numpy as np
# [moved to requirements.txt] !pip install cartopy

#import pygsheets not used in Scott's method
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import matplotlib.patches
import matplotlib.lines
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.image as mpimg  # Correct import for image handling
from matplotlib.font_manager import fontManager, FontProperties

# ===== Cell 2 =====
# Path to your font file
font_path = '/content/OpenSans-Regular.ttf'  # Update this to the path where the font file is located

# Add the font to Matplotlib's font manager
fontManager.addfont(font_path)

# # gemplot variables

# ===== Cell 3 =====
footer_color = "#222222"
footer_lineheight = 1.2
footer_fontsize = 14

# default height of a figure is 450 pixels

# gemstyle does this:
# specify a base_ratio, then set base_size = base_ratio*16
# 1. add 6 line margin all the way around
# 2. color of title is "#222222", margin 6666, size=base_size*1.5, lineheight=1.35, bold font
# 3. color of subtitle is "#333333", margin 0666, padding top=12, bottom=12, size=base_size*1.15, lineheight=1.45
# 4. set caption info as linehight=1.2, size=base_size*0.875, color="#222222", margin=18,6,6,6

base_ratio = 1.0
base_size = base_ratio * 16
color_title = "#222222"
color_subtitle = "#333333"
color_grid = "#cbcbcb"

text_weight_normal = 400
text_weight_bold = 700

# save fig
#' @keywords save_gem_plot
#' @examples
#' save_gem_plot(
#' plot_grid = line_plot_with_gem_footer,
#' save_filepath = "filename_that_my_plot_should_be_saved_to-nc.png",
#' width_pixels = 770,
#' height_pixels = 540,
#' resolution = 4
#' )
#'
#' @export
# save plot function - now separated from finalise_plot function and setting the resolution as part of the arguments
# save_gem_plot <- function (plot_grid, save_filepath, width_pixels = 640, height_pixels = 450, resolution = 3) {
#   grid::grid.draw(plot_grid)

#   #save it
#   ggplot2::ggsave(plot=plot_grid,
#                   width= (width_pixels/72),
#                   height= (height_pixels/72),
#                   dpi = resolution * 100,
#                   filename = save_filepath,
#                   bg="white")
# }

#width_pixels = 640 # default
#height_pixels = 450 # default

# # map color variables

# ===== Cell 4 =====
construction_color = '#BF532C'
TwentyTwoFID_color = '#F27D16'
TwentyThreeFID_color = '#BF532C'
other_land_color = '#E5E5E5'
other_land_alpha = 1
other_land_edge = '#cbcbcb'
highlight_land_color = '#c2c2c2'
water_color = '#ffffff'
water_alpha = 0.3
operating_color = '0.25'
operating_terms_color = '0.666'
construction_lw = 1.
operating_lw = 0.25
ehb_alpha = 1.

# # import states/provinces shapefile

# ===== Cell 5 =====
ne_states_provinces = '/content/ne_50m_admin_1_states_provinces_lines.shp'
ne_states_provinces_gdf = geopandas.read_file(ne_states_provinces)

# # import countries shapefile

# ===== Cell 6 =====
countries_gdf = geopandas.read_file('/content/ne_50m_admin_0_countries.shp')

# # import lakes shapefile

# ===== Cell 7 =====
lakes_gdf = geopandas.read_file('/content/ne_10m_lakes.shp')
oceans_gdf = geopandas.read_file('/content/ne_10m_ocean.shp')

# Import 2022 and 2023 Discoveries

# ===== Cell 8 =====
Discos_gdf = geopandas.read_file('/content/2022 and 2023 Disc (2024 02 22 parsed 2024 02 29).geojson')

# ===== Cell 9 =====
Discos_gdf.geometry.plot()

# ===== Cell 10 =====
print(Discos_gdf['Discovery year'].value_counts())
print(Discos_gdf['geometry'].notnull().sum())

# ===== Cell 11 =====
# Re-apply the conversion to ensure it's correctly done
Discos_gdf['Discovery year'] = pd.to_numeric(Discos_gdf['Discovery year'], errors='coerce').fillna(0).astype(int)

# Verify the data type and unique values post-conversion
print(Discos_gdf['Discovery year'].dtype)
print(Discos_gdf['Discovery year'].unique())

# ===== Cell 12 =====
TwentyTwoDiscos = Discos_gdf.loc[(Discos_gdf['Discovery year'] == 2022) &
                                 (pd.notnull(Discos_gdf['geometry']))]

# Updated filtering for 2023 with a check for non-null geometries using pd.notnull()
TwentyThreeDiscos = Discos_gdf.loc[(Discos_gdf['Discovery year'] == 2023) &
                                   (pd.notnull(Discos_gdf['geometry']))]

# ===== Cell 13 =====
TwentyTwoDiscos

# # import 2022 and 2023 FID Fields

# ===== Cell 14 =====
FIDs_gdf = geopandas.read_file('/content/2024 02 22 Included 2022 and 2023 FIDs.geojson')

# ===== Cell 15 =====
FIDs_gdf.geometry.plot()

# ===== Cell 16 =====
FIDs_gdf.head()

# ===== Cell 17 =====
# Convert 'FID Year' to integer, safely handling NaN values
FIDs_gdf['FID Year'] = pd.to_numeric(FIDs_gdf['FID Year'], errors='coerce').fillna(0).astype(int)

# Now filter for 2022 again
TwentyTwoFID = FIDs_gdf.loc[(FIDs_gdf['FID Year'] == 2022)&
                              (FIDs_gdf['geometry']!=None)
                              ]
# Now filter for 2022 again
TwentyThreeFID = FIDs_gdf.loc[(FIDs_gdf['FID Year'] == 2023)&
                              (FIDs_gdf['geometry']!=None)
                              ]

# ===== Cell 18 =====
TwentyThreeFID

# # Figure 1 - 2022 and 2023 FID

# ===== Cell 19 =====
# Map and data setup
#map_proj = ccrs.PlateCarree()
#map_proj = ccrs.Mercator()
map_proj = ccrs.Robinson(central_longitude=-5)
data_proj = ccrs.PlateCarree()
#map_proj = ccrs.Robinson()

# Create figure and axes with global projection
width_pixels = 640 # 640 default
height_pixels = 450 # 450 default
fig, ax = plt.subplots(figsize=(width_pixels/80, height_pixels/80), subplot_kw={'projection': map_proj})
fig.canvas.draw()
#ax.set_global()
ax.axis('off')
ax.set_extent([-170,170,-60,160], crs=data_proj)

# Add geometries for land, highlight areas, lakes, and oceans
ax.add_geometries(countries_gdf['geometry'], facecolor=other_land_color, edgecolor=other_land_edge, crs=data_proj, alpha=other_land_alpha)
ax.add_geometries(lakes_gdf['geometry'], facecolor=water_color, edgecolor='None', crs=data_proj, alpha=water_alpha)
ax.add_geometries(oceans_gdf['geometry'], facecolor=water_color, edgecolor='None', crs=data_proj, alpha=water_alpha)



#Add 2022 FIDs
points_list = TwentyTwoFID['geometry'].tolist()
ax.scatter(x=[point.x for point in points_list],
           y=[point.y for point in points_list],
           s=TwentyTwoFID['Reserves- Total (Oil, Gas and Hydrocarbons)']/10,
           transform=data_proj,
           facecolor=TwentyTwoFID_color,
           edgecolor=TwentyTwoFID_color,
           linewidth=operating_lw,
           zorder=5)

#Add 2023 FIDs
points_list = TwentyThreeFID['geometry'].tolist()
ax.scatter(x=[point.x for point in points_list],
           y=[point.y for point in points_list],
           s=TwentyThreeFID['Reserves- Total (Oil, Gas and Hydrocarbons)']/10,
           transform=data_proj,
           facecolor=TwentyThreeFID_color,
           edgecolor=TwentyThreeFID_color,
           linewidth=operating_lw,
           zorder=5)

# points_list = operating_fids['geometry'].tolist()
# ax.scatter([point.x for point in points_list],
#            [point.y for point in points_list],
#            transform=map_proj,
#            facecolor=operating_color,
#            edgecolor=operating_color,
#            linewidth=1,
#            zorder=9, marker='o',
#            s=30, label='units')

# add titles, first get the location of the yaxis labels so they can line up exactly
# call it "x_location"
bbox = ax.get_tightbbox(renderer=fig.canvas.renderer)
x_location,y_location = ax.transAxes.inverted().transform([bbox.x0, bbox.y1])
handles,labels = ax.get_legend_handles_labels()

legend = ax.legend(
          frameon=False,
          loc='lower left',
          bbox_to_anchor=(x_location,1.025),
          bbox_transform=ax.transAxes,
          handlelength=1,
          handleheight=1,
          ncols=4,
          borderpad=0,
          borderaxespad=0,
          columnspacing=0.75,
          handletextpad=0.25)


# Assuming 'x_location' and 'y_location' are your calculated positions for the text
year_2022 = '2022'
year_2023 = '2023'
space_width = ax.text(x_location, y_location, ' ', color=color_subtitle, transform=ax.transAxes).get_window_extent().width
fig.canvas.draw()

# Position and color the text parts
ax.text(x_location, y_location, year_2022, color=TwentyTwoFID_color, transform=ax.transAxes, ha='left', va='bottom')
ax.text(x_location + 0.055, y_location, ' and ', color=color_subtitle, transform=ax.transAxes, ha='left', va='bottom')
ax.text(x_location + 0.11, y_location, year_2023, color=TwentyThreeFID_color, transform=ax.transAxes, ha='left', va='bottom')
ax.text(x_location + 0.165, y_location, ' sanctionings of oil and gas fields',  color=color_subtitle, transform=ax.transAxes, ha='left', va='bottom')


bbox_with_subtitle = ax.get_tightbbox(renderer=fig.canvas.renderer)
x_location_subtitle,y_location_subtitle = ax.transAxes.inverted().transform([bbox_with_subtitle.x0, bbox_with_subtitle.y1])
ax.text(s='Americas lead in recent FIDs',
        size=base_size*1,
        color=color_title,
        x=x_location,
        y=y_location_subtitle+0.05,#1.2,
        ha='left',
        va='bottom',
        weight=text_weight_bold,
        transform=ax.transAxes,
        linespacing=1.35,
        wrap=False)

# Add logo to the plot
gem_logo_path = '/content/gem_logo_padding.png'
gem_logo = mpimg.imread(gem_logo_path)
logo_image_box = OffsetImage(gem_logo, zoom=0.035)
logo_annotation_box = AnnotationBbox(logo_image_box, (1, 0), xycoords='axes fraction', box_alignment=(1, 1.25), frameon=False)
ax.add_artist(logo_annotation_box)

# Note at the bottom
x_location = 0  # Assuming you want the text to start at the left; adjust as needed.
ax.text(x=x_location,
        y=-0.125,
        s='Source: Global Oil and Gas Extraction Tracker,\nGlobal Energy Monitor',
        fontsize=base_size * 0.65, color=color_title, transform=ax.transAxes, ha='left', va='center', linespacing=1.2)

fig.savefig('/content/2022 and 2023 FID 2024 02 29.png',
            dpi=300,
            bbox_inches='tight',
            transparent=False)

# # Figure 2 - discovery map

# ===== Cell 20 =====
# Map and data setup
#map_proj = ccrs.PlateCarree()
#map_proj = ccrs.Mercator()
map_proj = ccrs.Robinson(central_longitude=-5)
data_proj = ccrs.PlateCarree()
#map_proj = ccrs.Robinson()

# Create figure and axes with global projection
width_pixels = 640 # 640 default
height_pixels = 450 # 450 default
fig, ax = plt.subplots(figsize=(width_pixels/80, height_pixels/80), subplot_kw={'projection': map_proj})
fig.canvas.draw()
#ax.set_global()
ax.axis('off')
ax.set_extent([-170,170,-60,160], crs=data_proj)

# Add geometries for land, highlight areas, lakes, and oceans
ax.add_geometries(countries_gdf['geometry'], facecolor=other_land_color, edgecolor=other_land_edge, crs=data_proj, alpha=other_land_alpha)
ax.add_geometries(lakes_gdf['geometry'], facecolor=water_color, edgecolor='None', crs=data_proj, alpha=water_alpha)
ax.add_geometries(oceans_gdf['geometry'], facecolor=water_color, edgecolor='None', crs=data_proj, alpha=water_alpha)



#Add 2022 Discoveries
points_list = TwentyTwoDiscos['geometry'].tolist()
ax.scatter(x=[point.x for point in points_list],
           y=[point.y for point in points_list],
           s=TwentyTwoDiscos['Reserves- Total (Oil, Gas and Hydrocarbons)']/10,
           transform=data_proj,
           facecolor=TwentyTwoFID_color,
           edgecolor=TwentyTwoFID_color,
           linewidth=operating_lw,
           zorder=5)

#Add 2023 FIDs
points_list = TwentyThreeDiscos['geometry'].tolist()
ax.scatter(x=[point.x for point in points_list],
           y=[point.y for point in points_list],
           s=TwentyThreeDiscos['Reserves- Total (Oil, Gas and Hydrocarbons)']/10,
           transform=data_proj,
           facecolor=TwentyThreeFID_color,
           edgecolor=TwentyThreeFID_color,
           linewidth=operating_lw,
           zorder=5)

# points_list = operating_fids['geometry'].tolist()
# ax.scatter([point.x for point in points_list],
#            [point.y for point in points_list],
#            transform=map_proj,
#            facecolor=operating_color,
#            edgecolor=operating_color,
#            linewidth=1,
#            zorder=9, marker='o',
#            s=30, label='units')

# add titles, first get the location of the yaxis labels so they can line up exactly
# call it "x_location"
bbox = ax.get_tightbbox(renderer=fig.canvas.renderer)
x_location,y_location = ax.transAxes.inverted().transform([bbox.x0, bbox.y1])
handles,labels = ax.get_legend_handles_labels()

legend = ax.legend(
          frameon=False,
          loc='lower left',
          bbox_to_anchor=(x_location,1.025),
          bbox_transform=ax.transAxes,
          handlelength=1,
          handleheight=1,
          ncols=4,
          borderpad=0,
          borderaxespad=0,
          columnspacing=0.75,
          handletextpad=0.25)


# Assuming 'x_location' and 'y_location' are your calculated positions for the text
year_2022 = '2022'
year_2023 = '2023'
space_width = ax.text(x_location, y_location, ' ', color=color_subtitle, transform=ax.transAxes).get_window_extent().width
fig.canvas.draw()

# Position and color the text parts
ax.text(x_location, y_location, year_2022, color=TwentyTwoFID_color, transform=ax.transAxes, ha='left', va='bottom')
ax.text(x_location + 0.055, y_location, ' and ', color=color_subtitle, transform=ax.transAxes, ha='left', va='bottom')
ax.text(x_location + 0.11, y_location, year_2023, color=TwentyThreeFID_color, transform=ax.transAxes, ha='left', va='bottom')
ax.text(x_location + 0.165, y_location, ' discoveries of oil and gas fields',  color=color_subtitle, transform=ax.transAxes, ha='left', va='bottom')


bbox_with_subtitle = ax.get_tightbbox(renderer=fig.canvas.renderer)
x_location_subtitle,y_location_subtitle = ax.transAxes.inverted().transform([bbox_with_subtitle.x0, bbox_with_subtitle.y1])
ax.text(s='Latin America and Southern Asia lead in recent FIDs',
        size=base_size*1,
        color=color_title,
        x=x_location,
        y=y_location_subtitle+0.05,#1.2,
        ha='left',
        va='bottom',
        weight=text_weight_bold,
        transform=ax.transAxes,
        linespacing=1.35,
        wrap=False)

# Add logo to the plot
gem_logo_path = '/content/gem_logo_padding.png'
gem_logo = mpimg.imread(gem_logo_path)
logo_image_box = OffsetImage(gem_logo, zoom=0.035)
logo_annotation_box = AnnotationBbox(logo_image_box, (1, 0), xycoords='axes fraction', box_alignment=(1, 1.25), frameon=False)
ax.add_artist(logo_annotation_box)

# Note at the bottom
x_location = 0  # Assuming you want the text to start at the left; adjust as needed.
ax.text(x=x_location,
        y=-0.125,
        s='Source: Global Oil and Gas Extraction Tracker,\nGlobal Energy Monitor',
        fontsize=base_size * 0.65, color=color_title, transform=ax.transAxes, ha='left', va='center', linespacing=1.2)

fig.savefig('/content/2022 and 2023 Disc 2024 02 29.png',
            dpi=300,
            bbox_inches='tight',
            transparent=False)

# # import pipelines dataset

# ===== Cell 21 =====
gc = pygsheets.authorize(service_account_env_var='GDRIVE_API_CREDENTIALS')

spreadsheet = gc.open_by_key('1foPLE6K-uqFlaYgLPAUxzeXfDO5wOOqE7tibNHeqTek')
#spreadsheet = gc.open_by_key('1PKsCoVnfnCEalDBOF0Fmny0-pg1qy86DoReNHI-97WM') # version from 6 March 2023 for EGT report

gas_pipes = spreadsheet.worksheet('title', 'Gas pipelines').get_as_df(start='A3')
oil_pipes = spreadsheet.worksheet('title', 'Oil/NGL pipelines').get_as_df(start='A3')

gas_pipes = gas_pipes.drop('WKTFormat', axis=1) # delete WKTFormat column
oil_pipes = oil_pipes.drop('WKTFormat', axis=1)
pipes_df_orig = gas_pipes.copy()

# remove empty cells for pipes, owners
pipes_df_orig = pipes_df_orig.loc[pipes_df_orig.PipelineName!='']
pipes_df_orig = pipes_df_orig.loc[pipes_df_orig.Wiki!='']
pipes_df_orig = pipes_df_orig.loc[pipes_df_orig.Fuel.isin(['Gas','Hydrogen'])]

#get other relevant sheets
country_ratios_df = spreadsheet.worksheet('title', 'Country ratios by pipeline').get_as_df()

parents_df = spreadsheet.worksheet('title', 'Parent metadata (3/3)').get_as_df(start='A2')
parents_df = parents_df.loc[parents_df.Parent!='']
parents_df.set_index('Parent', inplace=True)

# ===== Cell 22 =====
country_ratios_df.replace('--', numpy.nan, inplace=True)
pipes_df_orig.replace('--',numpy.nan,inplace=True)
pipes_df_orig['ProposalYear'] = pipes_df_orig['ProposalYear'].replace('',numpy.nan)
region_df_orig = spreadsheet.worksheet('title', 'Country dictionary').get_as_df(start='A2')

# ===== Cell 23 =====
# region_df_eu = region_df_orig.copy()[region_df_orig['EuropeanUnion']=='Yes']
region_df_egt = region_df_orig.copy()[region_df_orig['EuroGasTracker']=='Yes']
# region_df_europe = region_df_orig.copy()[region_df_orig['Region']=='Europe']
# region_df_eu_uk = region_df_orig.copy()[(region_df_orig['Region']=='Europe') |
#                                           (region_df_orig['Country'].isin(['United Kingdom','Israel']))]

# ===== Cell 24 =====
region_df_touse = region_df_egt.copy()

# ===== Cell 25 =====
# subset the pipelines to use
# can't use pipes_df_touse... because some of the pipelines get eliminated if they're not in the same country...
pipes_df_touse = pipes_df_orig.loc[
    ~pipes_df_orig['Countries'].apply(
        lambda x: set(x.split(', ')).isdisjoint(set(region_df_touse['Country'].tolist()))
    )]

pipes_df_touse_h2 = pipes_df_touse.loc[(pipes_df_touse.Fuel=='Hydrogen')|
                                       (pipes_df_touse.H2Status!='')]
pipes_df_touse = pipes_df_touse.loc[pipes_df_touse.Fuel=='Gas']
pipes_df_orig_gas = pipes_df_orig.loc[(pipes_df_orig.Fuel=='Gas')]
country_ratios_df_gas = country_ratios_df.loc[#(country_ratios_df.Country.isin(region_df_touse['Country'].tolist()))&
                                                (country_ratios_df.Fuel=='Gas')]

# country_ratios_df_gas_europe = country_ratios_df.loc[(country_ratios_df.Country.isin(region_df_touse['Country'].tolist()))&
#                                                 (country_ratios_df.Fuel=='Gas')]

# # cost estimates for Europe

# ### correct Poland-Ukraine Interconnector

# ===== Cell 26 =====
# https://www.gem.wiki/Poland-Ukraine_Interconnector_Gas_Pipeline
# our country_ratios code calculates this is half in each country, but it's not
country_ratios_df_gas.loc[(country_ratios_df_gas.PipelineName=='Poland-Ukraine Interconnector Gas Pipeline')&
                      (country_ratios_df_gas.Country=='Poland'),'MergedKmByCountry'] = 1.5

country_ratios_df_gas.loc[(country_ratios_df_gas.PipelineName=='Poland-Ukraine Interconnector Gas Pipeline')&
                      (country_ratios_df_gas.Country=='Ukraine'),'MergedKmByCountry'] = 99.0

# ### correct Gas Interconnection Poland-Lithuania (our fractional calc doesn't get it right)

# ===== Cell 27 =====
country_ratios_df_gas.loc[(country_ratios_df_gas.PipelineName=='Gas Interconnection Poland-Lithuania')&
                      (country_ratios_df_gas.Country=='Poland'),'MergedKmByCountry'] = 343.0

country_ratios_df_gas.loc[(country_ratios_df_gas.PipelineName=='Gas Interconnection Poland-Lithuania')&
                      (country_ratios_df_gas.Country=='Lithuania'),'MergedKmByCountry'] = 165.0

# ===== Cell 28 =====
ax = pipes_df_orig.plot.scatter('LengthKnownKm','CostEuro')

# ## cost decision!
#
# in the 2024 EGT report, I'm using the cost calculations from the most recent pipelines and terminals reports
#
# pipelines here:  
# https://docs.google.com/spreadsheets/d/1vb9-yPbfW7h8je6hxD0NdUaZb4jpIT4xOYpeCnhePs8/edit#gid=259015665
#
# terminals here:  
# https://docs.google.com/spreadsheets/d/1vdwrxwR0k8kwDrwneRsNchDNQ96U5D3cO8BLZaAb15o/edit#gid=462850940

# ===== Cell 29 =====
mean_cost_per_km = 3.60726844 # million Euro per km

country_ratios_df_gas['TotalEstCostEuroMillionsHigh'] = numpy.nan

for idx,row in country_ratios_df_gas.iterrows():
    country_ratios_df_gas.loc[idx,'TotalEstCostEuroMillionsHigh'] = row['MergedKmByCountry'] * mean_cost_per_km

# now replace the ones that we have exact numbers for...
costs_exist_TF = ~country_ratios_df_gas['CostEuroPerKm'].isna()
country_ratios_df_gas.loc[costs_exist_TF,'TotalEstCostEuroMillionsHigh'] = \
    country_ratios_df_gas[costs_exist_TF]['CostEuroPerKm']/1e6 * \
    country_ratios_df_gas[costs_exist_TF]['MergedKmByCountry']

# ===== Cell 30 =====
mean_cost_per_km =  3.60726844 # million Euro per km

country_ratios_df_gas['TotalEstCostEuroMillionsLow'] = numpy.nan

for idx,row in country_ratios_df_gas.iterrows():
    country_ratios_df_gas.loc[idx,'TotalEstCostEuroMillionsLow'] = row['MergedKmByCountry'] * mean_cost_per_km

# now replace the ones that we have exact numbers for...
costs_exist_TF = ~country_ratios_df_gas['CostEuro'].isna()

country_ratios_df_gas.loc[costs_exist_TF,'TotalEstCostEuroMillionsLow'] = \
    country_ratios_df_gas[costs_exist_TF]['CostEuroPerKm']/1e6 * \
    country_ratios_df_gas[costs_exist_TF]['MergedKmByCountry']
country_ratios_df_gas.loc[costs_exist_TF,'TotalEstCostEuroMillionsHigh'] = \
    country_ratios_df_gas[costs_exist_TF]['CostEuroPerKm']/1e6 * \
    country_ratios_df_gas[costs_exist_TF]['MergedKmByCountry']

country_ratios_df_gas.loc[(country_ratios_df_gas['PipelineName']=='Trans-Adriatic Gas Pipeline')&
                            (country_ratios_df_gas['SegmentName']=='TAP Expansion')&
                            (country_ratios_df_gas['Country']=='Italy'), ['TotalEstCostEuroMillionsLow','TotalEstCostEuroMillionsHigh']] = \
country_ratios_df.loc[(country_ratios_df.ProjectID=='P3203'),'CostEuro'].values[0]/1e6 * 2/3 * 0.5

country_ratios_df_gas.loc[(country_ratios_df_gas['PipelineName']=='Trans-Adriatic Gas Pipeline')&
                            (country_ratios_df_gas['SegmentName']=='TAP Expansion')&
                            (country_ratios_df_gas['Country']=='Greece'), ['TotalEstCostEuroMillionsLow','TotalEstCostEuroMillionsHigh']] = \
country_ratios_df.loc[(country_ratios_df.ProjectID=='P3203'),'CostEuro'].values[0]/1e6 * 2/3 * 0.5

# ===== Cell 31 =====
country_ratios_df_gas['TotalEstCostEuroMillionsMean'] = \
    country_ratios_df_gas[['TotalEstCostEuroMillionsLow','TotalEstCostEuroMillionsHigh']].mean(axis=1)

# ===== Cell 32 =====
output_columns = ['Country',
                  'PipelineName',
                  'SegmentName',
                  'Status',
                  'CapacityBcm/y',
                  'MergedKmByCountry',
                  'TotalEstCostEuroMillionsMean',
                  'TotalEstCostEuroMillionsLow',
                  'TotalEstCostEuroMillionsHigh']
country_ratios_df_gas_excel = country_ratios_df_gas[country_ratios_df_gas['Status'].isin(['Proposed','Construction'])]
country_ratios_df_gas_excel = country_ratios_df_gas.sort_values(['Status',
                                                                     'PipelineName',
                                                                     'TotalEstCostEuroMillionsLow',
                                                                     'TotalEstCostEuroMillionsHigh'],
                                                                    ascending=[True,True,False,False])
country_ratios_df_gas_excel.replace(numpy.nan, '')
country_ratios_df_gas_excel = country_ratios_df_gas_excel[output_columns]

# ## print export, import, and within-EU pipelines
#
# planned pipelines to import gas into the EU

# ===== Cell 33 =====
# get the pipelines that import into the EU, export out, and are completely within
pipes_df_eu_imports = pipes_df_orig.copy()[(pipes_df_orig['Fuel']=='Gas')&
              (~pipes_df_orig['StartCountry'].isin(region_df_touse.Country))&
              (pipes_df_orig['EndCountry'].isin(region_df_touse.Country))]

pipes_df_eu_exports = pipes_df_orig.copy()[(pipes_df_orig['Fuel']=='Gas')&
              (pipes_df_orig['StartCountry'].isin(region_df_touse.Country))&
              (~pipes_df_orig['EndCountry'].isin(region_df_touse.Country))]

pipes_df_eu_within = pipes_df_orig.copy()[(pipes_df_orig['Fuel']=='Gas')&
              (pipes_df_orig['StartCountry'].isin(region_df_touse.Country))&
              (pipes_df_orig['EndCountry'].isin(region_df_touse.Country))]

# ## Table A2 all of Europe - import

# ===== Cell 34 =====
import_projectids = country_ratios_df_gas.loc[
    (country_ratios_df_gas.Status.isin(['Proposed','Construction']))&
    (country_ratios_df_gas.Country.isin(region_df_touse.Country.tolist()))&
    ((~country_ratios_df_gas.StartCountry.isin(region_df_touse.Country.tolist()))&
    (country_ratios_df_gas.EndCountry.isin(region_df_touse.Country.tolist())))].ProjectID.tolist()

# all_other_projectids = list(set(country_ratios_df_gas.loc[
#     country_ratios_df_gas.Status.isin(['Proposed','Construction'])].ProjectID) - set(import_projectids))

all_other_projectids = country_ratios_df_gas.loc[
    (country_ratios_df_gas.Status.isin(['Proposed','Construction']))&
    (country_ratios_df_gas.Country.isin(region_df_touse.Country.tolist()))&
    (~country_ratios_df_gas.ProjectID.isin(import_projectids))].ProjectID.tolist()

country_ratios_df_gas_europe_only = country_ratios_df_gas.loc[
    (country_ratios_df_gas.Status.isin(['Proposed','Construction']))&
    (country_ratios_df_gas.Country.isin(region_df_touse.Country.tolist()))]

output_columns = ['Country',
                  'PipelineName',
                  'Status',
                  'CapacityBcm/y',
                  'MergedKmByCountry',
                  'TotalEstCostEuroMillionsMean',]
                  #'TotalEstCostEuroMillionsLow',
                  #'TotalEstCostEuroMillionsHigh']

country_ratios_df_gas_europe_only.loc[(country_ratios_df_gas_europe_only.ProjectID.isin(import_projectids))&
                            (country_ratios_df_gas_europe_only.Country.isin(region_df_touse.Country.tolist()))
                            ].sort_values(['Status','PipelineName','TotalEstCostEuroMillionsLow'],
                                          ascending=[True,True,False])[output_columns].replace(numpy.nan,'').style.hide(axis='index')

# ===== Cell 35 =====
import_projectids

# ## table A2 (Rob's summation)

# ## Table A3 (appendix)

# ### longer than 150 km

# ===== Cell 36 =====
# must be longer than 150 total, and the segment must be located within the EU
projectids_threshold = list(
    set(country_ratios_df_gas.loc[(country_ratios_df_gas.MergedKmByPipeline>150)&
                                   (country_ratios_df_gas.ProjectID.isin(all_other_projectids))]['ProjectID'])
)

projectids_under_threshold = list(
    set(all_other_projectids) - set(projectids_threshold)
)

projectids_threshold.__len__()

# ===== Cell 37 =====
projectids_under_threshold.__len__()

# ===== Cell 38 =====
import_projectids.__len__()

# ===== Cell 39 =====
all_other_projectids.__len__()

# ===== Cell 40 =====
output_columns = ['Country',
                  'PipelineName',
                  #'Status',
                  'CapacityBcm/y',
                  'MergedKmByPipeline',
                  'MergedKmByCountry',
                  'TotalEstCostEuroMillionsMean']#,
                  #'TotalEstCostEuroMillionsLow',
                  #'TotalEstCostEuroMillionsHigh']

# country_ratios_df_gas.loc[
#     (country_ratios_df_gas.ProjectID.isin(import_projectids+all_other_projectids))&
#     (country_ratios_df_gas.Country.isin(region_df_touse.Country.tolist()))
#     ].groupby('Country')['MergedKmByCountry'].sum()

country_ratios_df_gas.replace(numpy.nan,'').loc[
    (country_ratios_df_gas.ProjectID.isin(import_projectids+all_other_projectids))&
    (country_ratios_df_gas.MergedKmByPipeline>150)&
    (country_ratios_df_gas.Country.isin(region_df_touse.Country.tolist()))
    ].sort_values([
    'Status','PipelineName','TotalEstCostEuroMillionsLow'], ascending=[True,True,False])[output_columns].style.hide(axis='index')

# ### shorter than 150 km

# ===== Cell 41 =====
# below_threshold_df = country_ratios_df_gas_europe_only.loc[(country_ratios_df_gas_europe_only.ProjectID.isin(projectids_under_threshold))&
#                                                  (country_ratios_df_gas_europe_only.Country.isin(region_df_touse.Country))]#.groupby('Status')

below_threshold_df = country_ratios_df_gas.loc[
    (country_ratios_df_gas.ProjectID.isin(import_projectids+all_other_projectids))&
    (country_ratios_df_gas.MergedKmByPipeline<=150)&
    (country_ratios_df_gas.Country.isin(region_df_touse.Country.tolist()))
    ]#.sort_values([
    #'Status','PipelineName','TotalEstCostEuroMillionsLow'], ascending=[True,True,False])[output_columns].style.hide(axis='index')

below_threshold_df.groupby('Status')[['MergedKmByCountry',
                                      'TotalEstCostEuroMillionsMean',
                                      'TotalEstCostEuroMillionsLow',
                                      'TotalEstCostEuroMillionsHigh']].sum()

# # import terminals now

# ===== Cell 42 =====
credentials_directory = '/Users/baird/Dropbox/_google-api/'
gc = pygsheets.authorize(service_account_env_var='GDRIVE_API_CREDENTIALS')
spreadsheet = gc.open_by_key('1tcS6Wd-Wp-LTDpLzFgJY_RSNDnbyubW3J_9HKIAys4A')
#spreadsheet = gc.open_by_key('1BHiidrJnzh96Em3KrqBpCoWaJ3GB5OeCY9dHVaEDEFs') # mar 22 2022 version for EGT
#spreadsheet = gc.open_by_key('1d0kLE0WmAn9b4XdugffiEaAHGWy6EhyF7zY1DM12zCc') # 1 Mar 2023 version for EGT report

#spreadsheet[1] "Gas Pipelines" tab is the second index
terms_df_orig = spreadsheet.worksheet('title', 'Terminals').get_as_df(start='A3')

# ===== Cell 43 =====
# replace all -- with nans
terms_df_orig.replace('--', numpy.nan, inplace=True)
# only keep LNG terminals (remove oil)
terms_df_orig = terms_df_orig.loc[terms_df_orig.Fuel=='LNG']
# remove anything without a wiki page
terms_df_orig = terms_df_orig.loc[terms_df_orig.Wiki!='']
# remove N/A statuses
terms_df_orig = terms_df_orig.loc[terms_df_orig.Status!='']

# ===== Cell 44 =====
terms_df_touse = terms_df_orig.loc[(terms_df_orig['Country'].isin(region_df_touse.Country.tolist()))&
                                   (terms_df_orig.Fuel=='LNG')]
terms_df_touse_imports = terms_df_touse.loc[(terms_df_orig['Country'].isin(region_df_touse['Country']))&
                                            (terms_df_touse['FacilityType']=='Import')]

# ===== Cell 45 =====
terms_df_touse_imports.loc[terms_df_touse_imports.Status.isin(['Proposed','Construction'])].shape

# ===== Cell 46 =====
parent_metadata_df = spreadsheet.worksheet('title', 'Parent metadata (3/3)').get_as_df(start='A2')
parent_metadata_df.set_index('Parent', inplace=True)

# ## calculate floating costs (high and low estimates)

# ===== Cell 47 =====
mean_cost_per_bcmy_floating = 1.653105e+08/1e6 # from 2023 terminals report # ols_estimator_f.coef_[0][0]/1e6
mean_cost_per_bcmy_onshore = 4.447106e+08/1e6 # from 2023 termnals report # ols_estimator_o.coef_[0][0]/1e6

terms_df_europe_import_future = terms_df_touse.loc[(terms_df_touse.Status.isin(['Proposed','Construction']))&
                                                 (terms_df_touse['FacilityType']=='Import')]

# do for floating
terms_df_europe_import_future['TotalEstCostEuroMillionsLow'] = numpy.nan

terms_df_europe_import_future.loc[(terms_df_europe_import_future['Floating']=='yes'),
                                'TotalEstCostEuroMillionsLow'] = \
terms_df_europe_import_future.loc[(terms_df_europe_import_future['Floating']=='yes'),
                                'CapacityInBcm/y'] * mean_cost_per_bcmy_floating

# now do for onshore
#terms_df_europe_import_future.loc[:,'TotalEstCostEuroMillionsLow'] = numpy.nan
terms_df_europe_import_future.loc[(terms_df_europe_import_future['Floating']==''),
                                'TotalEstCostEuroMillionsLow'] = \
terms_df_europe_import_future.loc[(terms_df_europe_import_future['Floating']==''),
                                'CapacityInBcm/y'] * mean_cost_per_bcmy_onshore

# then replace any that we have already
# now replace the ones that we have exact numbers for...
costs_exist_TF = ~terms_df_europe_import_future['CostEuro'].isna()
terms_df_europe_import_future.loc[costs_exist_TF,'TotalEstCostEuroMillionsLow'] = \
    terms_df_europe_import_future[costs_exist_TF]['CostEuro']/1e6 #*euro_multiplier/1e6

# LARGER MEAN

# ===== Cell 48 =====
mean_cost_per_bcmy_floating = 1.646520e+08/1e6 # from 2023 terminals report # terms_df_floating_toregress_dropdupes['CostEuroPerBcm/y'].mean()/1e6
mean_cost_per_bcmy_onshore = 4.447106e+08/1e6 # from 2023 termnals report # terms_df_onshore_toregress_dropdupes['CostEuroPerBcm/y'].mean()/1e6

# terms_df_europe_import_future = terms_df_touse.loc[(terms_df_touse.Status.isin(['Proposed','Construction']))&
#                                                  (terms_df_touse['FacilityType']=='Import')]

# do for floating
terms_df_europe_import_future['TotalEstCostEuroMillionsHigh'] = numpy.nan

terms_df_europe_import_future.loc[(terms_df_europe_import_future['Floating']=='yes'),
                                'TotalEstCostEuroMillionsHigh'] = \
terms_df_europe_import_future.loc[(terms_df_europe_import_future['Floating']=='yes'),
                                'CapacityInBcm/y'] * mean_cost_per_bcmy_floating

# now do for onshore
#terms_df_europe_import_future.loc[:,'TotalEstCostEuroMillionsLow'] = numpy.nan
terms_df_europe_import_future.loc[(terms_df_europe_import_future['Floating']==''),
                                'TotalEstCostEuroMillionsHigh'] = \
terms_df_europe_import_future.loc[(terms_df_europe_import_future['Floating']==''),
                                'CapacityInBcm/y'] * mean_cost_per_bcmy_onshore

# then replace any that we have already
# now replace the ones that we have exact numbers for...
costs_exist_TF = ~terms_df_europe_import_future['CostEuro'].isna()
terms_df_europe_import_future.loc[costs_exist_TF,'TotalEstCostEuroMillionsHigh'] = \
    terms_df_europe_import_future[costs_exist_TF]['CostEuro']/1e6 #*euro_multiplier/1e6

# ===== Cell 49 =====
terms_df_europe_import_future['TotalEstCostEuroMillionsMean'] = \
    terms_df_europe_import_future[['TotalEstCostEuroMillionsLow', 'TotalEstCostEuroMillionsHigh']].mean(axis=1)

# ### correct outliers/special cases

# ===== Cell 50 =====
# Zeebrugge terminal is 116 million for BOTH expansion projects, so set one equal to zero so it's not counted twice
#T042601	https://www.gem.wiki/Fluxys_Zeebrugge_LNG_Terminal	Zeebrugge LNG Terminal, 2024 Expansion
#T042602	https://www.gem.wiki/Fluxys_Zeebrugge_LNG_Terminal	Zeebrugge LNG Terminal, 2026 Expansion
outliers_comboids = ['T042602']
terms_df_europe_import_future.loc[
    terms_df_europe_import_future.ComboID.isin(outliers_comboids),
    ['TotalEstCostEuroMillionsMean','TotalEstCostEuroMillionsLow','TotalEstCostEuroMillionsHigh']] = 0.0

# ## remove terminal expansions (costs aren't estimated for new builds)

# # Table A1

# ===== Cell 51 =====
terms_df_europe_import_future['CapacityInBcm/y'].sum()

# ===== Cell 52 =====
output_columns = ['Country',
                  #'TerminalName',
                  'TerminalNameUnitName',
                  #'UnitName',
                  'CapacityInBcm/y',
                  #'Status',
                  #'FacilityType',
                  'TotalEstCostEuroMillionsMean']#,
                  #'TotalEstCostEuroMillionsLow',
                  #'TotalEstCostEuroMillionsHigh']

terms_df_europe_import_future['TerminalNameUnitName'] = (terms_df_europe_import_future.TerminalName + ' ' + terms_df_europe_import_future.UnitName).str.strip()
terms_df_europe_import_future.sort_values(['Status','TerminalNameUnitName'],
                                        ascending=[True,True])[output_columns].replace(numpy.nan,'').style.hide(axis='index')

# # versus the LNG global report

# ===== Cell 53 =====
terms_df_europe_import_future.TotalEstCostEuroMillionsMean.sum()

# # table 2 - 2024 report

# ===== Cell 54 =====
# table 1 shows country totals of pipeline length, cost, LNG capacity, cost, total cost
table2_columns = ['PipelineLengthKm','PipelineCostMillionEuro',
                  'LNGImportCapacityBcm/y','LNGTerminalCostMillionEuro','TotalCostMillionEuro']
table2_df = pandas.DataFrame(columns=table2_columns, index=region_df_touse.Country.tolist())

table2_df['PipelineLengthKm'] = country_ratios_df_gas.loc[
    (country_ratios_df_gas.ProjectID.isin(import_projectids+all_other_projectids))&
    (country_ratios_df_gas.Country.isin(region_df_touse.Country.tolist()))
    ].groupby('Country')['MergedKmByCountry'].sum()

table2_df['PipelineCostMillionEuro'] = country_ratios_df_gas.loc[
    (country_ratios_df_gas.ProjectID.isin(import_projectids+all_other_projectids))&
    (country_ratios_df_gas.Country.isin(region_df_touse.Country.tolist()))].groupby('Country')['TotalEstCostEuroMillionsMean'].sum()

# add half of Trans-Adriatic expansion to Italy, half to Greece
#table2_df.loc['Greece','PipelineCostMillionEuro']+=1035/2
#table2_df.loc['Italy','PipelineCostMillionEuro']+=1035/2

table2_df['LNGImportCapacityBcm/y'] = terms_df_europe_import_future.groupby('Country')['CapacityInBcm/y'].sum()
table2_df['LNGTerminalCostMillionEuro'] = terms_df_europe_import_future.groupby('Country')['TotalEstCostEuroMillionsMean'].sum()
table2_df['TotalCostMillionEuro'] = table2_df.loc[:,('PipelineCostMillionEuro','LNGTerminalCostMillionEuro')].sum(axis=1)

if 'Total' in table2_df.index:
    table2_df.drop(index='Total', inplace=True)
    total = table2_df.sum(axis=0)
    total.name='Total'
    table2_df.loc['Total'] = total

else:
    total = table2_df.sum(axis=0)
    total.name='Total'
    table2_df.loc['Total'] = total

# replace NaN with ''
table2_df.replace(numpy.nan, '', inplace=True)
table2_df.replace(0.0, '', inplace=True)

# ===== Cell 55 =====
table2_df#['LNGImportCapacityBcm/y'][:-1].replace('',numpy.nan).sum()

# # creating figure 1 data
#
# sum of Table 1 columns...

# ===== Cell 56 =====
figure1_table_columns = ['TotalConstructionCostMillionEuro','TotalProposedCostMillionEuro','Total']
figure1_table_df = pandas.DataFrame(0, columns=figure1_table_columns, index=region_df_touse.Country,)


# for proposed
figure1_table_df['TotalProposedCostMillionEuro'] = \
country_ratios_df_gas.loc[country_ratios_df_gas.Status.isin(
    ['Proposed'])].groupby(['Country'])['TotalEstCostEuroMillionsMean'].sum()

figure1_table_df['TotalProposedCostMillionEuro'] = \
figure1_table_df['TotalProposedCostMillionEuro'].add( \
terms_df_europe_import_future.loc[terms_df_europe_import_future.Status.isin(
    ['Proposed'])].groupby(['Country'])['TotalEstCostEuroMillionsMean'].sum(), \
                                                    fill_value=0)

#figure1_table_df.loc['Italy','TotalProposedCostMillionEuro'] += 1035/2.
#figure1_table_df.loc['Greece','TotalProposedCostMillionEuro'] += 1035/2.

# for construction
figure1_table_df['TotalConstructionCostMillionEuro'] = \
country_ratios_df_gas.loc[country_ratios_df_gas.Status.isin(
    ['Construction'])].groupby(['Country'])['TotalEstCostEuroMillionsMean'].sum()

figure1_table_df['TotalConstructionCostMillionEuro'] = \
figure1_table_df['TotalConstructionCostMillionEuro'].add( \
terms_df_europe_import_future.loc[terms_df_europe_import_future.Status.isin(
    ['Construction'])].groupby(['Country'])['TotalEstCostEuroMillionsMean'].sum(), \
                                                         fill_value=0, axis=0)

figure1_table_df['Total'] = \
figure1_table_df[['TotalConstructionCostMillionEuro','TotalProposedCostMillionEuro']].sum(axis=1)
figure1_table_df.sort_values(['Total','Country'], ascending=[False, True], inplace=True)

figure1_table_df.replace(numpy.nan, '', inplace=True)
figure1_table_df.replace(0, '', inplace=True)

# ===== Cell 57 =====
figure1_table_df

# # owner analysis

# ## for pipelines

# ===== Cell 58 =====
owner_parent_calculations_df = pandas.DataFrame()
# needs country, km in each country columns as well

for idx,row in country_ratios_df_gas.loc[
                            (country_ratios_df_gas.Status.isin(['Proposed','Construction']))&
                            (country_ratios_df_gas.Country.isin(region_df_touse.Country))].iterrows():

    parent_string = pipes_df_orig.loc[pipes_df_orig.ProjectID==row.ProjectID].Parent.values[0]
    #hq_country_string = pipes_df_orig.loc[pipes_df_orig.ProjectID==row.ProjectID].ParentHQCountry.values[0]

    #print(parent_string)
    #if parent_string == '--':
    #    parent_string = 'unknown [unknown %]'

    parent_list = re.sub(' \[.*?\]', '', parent_string).split('; ') # all entries must have an "Owner [%]" syntax, so [unknown %] is included
    percent_list = [float(i.rstrip('%'))/100. for i in re.findall('\\d+(?:\\.\\d+)?%', parent_string)]
    #print(percent_list)

    if parent_list.__len__()!=percent_list.__len__():
        if percent_list==[]:
            percent_list = [1/parent_list.__len__() for i in parent_list]
        else:
            nmissing = parent_list.__len__()-percent_list.__len__()
            # distribute nans evenly
            total = numpy.nansum(percent_list)
            leftover = 1-total
            percent_list += [leftover/nmissing]*nmissing

    # for when database isn't completely filled in for owners:
    for p_idx,parent in enumerate(parent_list):
        #if parent not in parents_df.index.to_list():
        #    parents_df.loc[parent,'ParentHQCountry']='unknown'
        owner_parent_calculations_df = pandas.concat([owner_parent_calculations_df,
                                                      pandas.DataFrame([{'Parent':parent, 'ProjectID':row.ProjectID,
                                                                         'FractionOwnership':percent_list[p_idx],
                                                                         'ParentHQCountry':parents_df.loc[parents_df.index==parent]['ParentHQCountry'].values[0],
                                                                         'PipelineCountry':row.Country,
                                                                         'Status':row.Status,
                                                                         'MergedKmByCountry':row.MergedKmByCountry,
                                                                         'MergedKmByPipeline':row.MergedKmByPipeline,
                                                                         'CapacityBOEd':row.CapacityBOEd,
                                                                         'TotalEstCostEuroMillionsMean':row.TotalEstCostEuroMillionsMean,
                                                                         'LengthPerCountryFraction':row.LengthPerCountryFraction}])])

owner_parent_calculations_df['KmOwnershipByCountry'] = owner_parent_calculations_df.FractionOwnership*owner_parent_calculations_df.MergedKmByCountry
owner_parent_calculations_df['EstimatedCostEuroMillionsMeanByCountry'] = \
        owner_parent_calculations_df.FractionOwnership*\
        owner_parent_calculations_df.TotalEstCostEuroMillionsMean
        # owner_parent_calculations_df.FractionOwnership*\
        # owner_parent_calculations_df.LengthPerCountryFraction*\
        # owner_parent_calculations_df.TotalEstCostEuroMillionsMean

# ===== Cell 59 =====
pipeline_costs_df = owner_parent_calculations_df.groupby('Parent')[['EstimatedCostEuroMillionsMeanByCountry']].sum().sort_values(by='EstimatedCostEuroMillionsMeanByCountry', ascending=False)
pipeline_costs_df = pipeline_costs_df.rename(columns={'EstimatedCostEuroMillionsMeanByCountry':'Pipeline costs'})

# ## for terminals

# ===== Cell 60 =====
# this cell takes the terminals data set (call it "terms_df_all", here we're using the indev terminals subset)
# and loops throw every row, breaks up the parent and % ownership strings,
# and outputs a dataframe owner_parent_calculations_df that has a bunch of different useful info related
# to parent shares, capacity, etc.
owner_parent_calculations_df = pandas.DataFrame() # empty df for storing owner/parent stuff

for idx,row in terms_df_europe_import_future.iterrows():
    parent_string = row.Parent #.values[0]
    if row.TerminalID=='T0292':
        print(parent_string)

    # the two lines below go through the parent entries in the sheet and split them,
    # recording the percents and parents in separate lists, to be dealt with later
    parent_list = re.sub(' \[.*?\]', '', parent_string).split('; ') # all entries must have an "Owner [%]" syntax, so [unknown %] is included
    percent_list = [float(i.rstrip('%'))/100. for i in re.findall('\\d+(?:\\.\\d+)?%', parent_string)]

    # if there are fewer recorded percents than number of parents
    if parent_list.__len__()!=percent_list.__len__():
        # if there are no percents, make them all equal

        if percent_list==[]:
            percent_list = [1/parent_list.__len__() for i in parent_list]
        # otherwise, get the difference and distribute the remainder equally among remaining parents
        else:
            #print(row.ComboID)
            nmissing = parent_list.__len__()-percent_list.__len__()
            # distribute nans evenly
            total = numpy.nansum(percent_list)
            leftover = 1-total
            percent_list += [leftover/nmissing]*nmissing
            #print(numpy.array(percent_list).sum())

    # now go through each parent and associated percent ownership
    # and store it alongside the project's name along with capacity, status, region, etc.
    # this is stored inside the big dataframe owner_parent_calculations_df
    for p_idx,parent in enumerate(parent_list):
        if row.TerminalID=='T0292':
            print(parent_list)
        # this if statement should not really be used
        if parent not in parent_metadata_df.index.to_list():
            print(parent, " doesn't exist as a parent")
            parent_metadata_df.loc[parent,'ParentHQCountry']='unknown'
        owner_parent_calculations_df = pandas.concat([owner_parent_calculations_df,
                                                      pandas.DataFrame([{'Parent':parent, 'ComboID':row.ComboID,
                                                                         'TerminalID':row.TerminalID,
                                                                         'FractionOwnership':percent_list[p_idx],
                                                                         'PercentString':'{:.2f}%'.format(percent_list[p_idx]*100),
                                                                         'ParentHQCountry':parent_metadata_df.loc[parent_metadata_df.index==parent]['ParentHQCountry'].values[0],
                                                                         'ParentHQRegion':parent_metadata_df.loc[parent_metadata_df.index==parent]['ParentHQRegion'].values[0],
                                                                         'TerminalCountry':row.Country,
                                                                         'TerminalRegion':row.Region,
                                                                         'Status':row.Status,
                                                                         'FacilityType':row['FacilityType'],
                                                                         'CapacityInMtpa':row.CapacityInMtpa,
                                                                         'ProjectWiki':row.Wiki,
                                                                         'ProjectName':row.TerminalName+' '+str(row.UnitName),
                                                                         'TotalEstCostEuroMillionsMean':row.TotalEstCostEuroMillionsMean}])])

owner_parent_calculations_df.reset_index(drop=True, inplace=True)
owner_parent_calculations_df['CapacityOwnedInMtpa'] = owner_parent_calculations_df.FractionOwnership*owner_parent_calculations_df.CapacityInMtpa
owner_parent_calculations_df['ParentCapacityString'] = owner_parent_calculations_df.Parent + ' (' + owner_parent_calculations_df.CapacityOwnedInMtpa.round(1).astype(str).replace('nan','unknown') + ' mtpa)'
owner_parent_calculations_df['EstimatedCostEuroMillionsMeanByOwner'] = owner_parent_calculations_df.FractionOwnership*owner_parent_calculations_df.TotalEstCostEuroMillionsMean

# ===== Cell 61 =====
terminal_costs_df = owner_parent_calculations_df.groupby('Parent')[['EstimatedCostEuroMillionsMeanByOwner']].sum().sort_values(by='EstimatedCostEuroMillionsMeanByOwner', ascending=False)
terminal_costs_df = terminal_costs_df.rename(columns={'EstimatedCostEuroMillionsMeanByOwner':'Terminal costs'})

# ===== Cell 62 =====
pipeline_costs_df['Terminal costs'] = numpy.nan
terminal_costs_df['Pipeline costs'] = numpy.nan

# ## pipelines and terminals owners together

# ===== Cell 63 =====
pipeline_and_terminal_costs_df = terminal_costs_df.add(pipeline_costs_df, fill_value=0)

# ===== Cell 64 =====
pipeline_and_terminal_costs_df.replace(numpy.nan,0).sum().sum()

# ===== Cell 65 =====
pipeline_and_terminal_costs_df['Total costs'] = pipeline_and_terminal_costs_df.sum(axis=1)
#pipeline_and_terminal_costs_df = pipeline_and_terminal_costs_df.loc[~pipeline_and_terminal_costs_df.index.isin(['unknown','other'])]

# # Table A5
#
# saved out as Excel and copied/pasted, also removed the bottom zero ones

# ===== Cell 66 =====
pipeline_and_terminal_costs_df.sort_values('Total costs', ascending=False).replace(numpy.nan, '')

# ===== Cell 67 =====
pipeline_and_terminal_costs_df.sort_values('Total costs', ascending=False).replace(numpy.nan, '').to_excel('pipeline-and-terminal-owner-cost-rankings.xlsx')

# ===== Cell 68 =====
pipeline_and_terminal_costs_df.sum(axis=0)

# # hydrogen exploring

# ===== Cell 69 =====
pipes_df_touse = pipes_df_touse.loc[pipes_df_touse.H2Status!='']
pipes_df_touse_h2.H2Status.unique()

# ===== Cell 70 =====
pipes_df_touse_h2.loc[pipes_df_touse_h2.Fuel=='Hydrogen'][['ProjectID','Status','H2Status']]

# ===== Cell 71 =====
print(pipes_df_touse_h2.loc[pipes_df_touse_h2.H2Status=='Pre-construction (H2 only)'].shape)
print(pipes_df_touse_h2.loc[pipes_df_touse_h2.H2Status=='Speculative (H2 only)'].shape)
print(pipes_df_touse_h2.loc[pipes_df_touse_h2.H2Status=='Proposed'].shape)

# ===== Cell 72 =====
pipes_df_touse_h2.groupby('H2Status')[['LengthMergedKm']].count()#.sum()

# ===== Cell 73 =====
country_ratios_df_gas.loc[(country_ratios_df_gas.H2Status!='')&
                            (country_ratios_df_gas.Country.isin(region_df_touse.Country))].groupby(['H2Status'])[['MergedKmByCountry']].sum()#.sort_values('MergedKmByCountry', ascending=False)



# ===== Cell 74 =====
country_ratios_df_gas.loc[(country_ratios_df_gas.H2Status!='')&
                            (country_ratios_df_gas.Country.isin(region_df_touse.Country))].groupby(['H2Type'])[['MergedKmByCountry']].sum()#.sort_values('MergedKmByCountry', ascending=False)

# ===== Cell 75 =====
country_ratios_df_gas.loc[(country_ratios_df_gas.H2Status!='')&
                            (country_ratios_df_gas.Country.isin(region_df_touse.Country))].groupby(['H2Status','H2Type'])[['MergedKmByCountry']].sum()#.sort_values('MergedKmByCountry', ascending=False)

# ===== Cell 76 =====
country_ratios_df_gas.loc[(country_ratios_df_gas.H2Status!='')&
                            (country_ratios_df_gas.Country.isin(region_df_touse.Country))].groupby(['H2Status','H2Type'])[['MergedKmByCountry']].count()

# ===== Cell 77 =====
country_ratios_df_gas.loc[(country_ratios_df_gas.H2Status!='')&
                            (country_ratios_df_gas.Country.isin(region_df_touse.Country))].groupby(['H2Status','H2Type'])[['MergedKmByCountry']].count()

# ===== Cell 78 =====
2256.62+1998.36

# ===== Cell 79 =====
17054.74+476.25

# ===== Cell 80 =====
pipes_df_touse_h2.loc[pipes_df_touse_h2.H2Type.str.contains('blended')|
                      pipes_df_touse_h2.H2Type.str.contains('unknown')].shape

# ===== Cell 81 =====
pipes_df_touse_h2.loc[pipes_df_touse_h2.H2Type.str.contains('new')]['LengthMergedKm'].sum()

# ===== Cell 82 =====
pipes_df_touse_h2.loc[pipes_df_touse_h2.H2Type.str.contains('repurposed')]['LengthMergedKm'].sum()

# ===== Cell 83 =====
178/195

# ===== Cell 84 =====
pipes_df_touse_h2.shape

# ===== Cell 85 =====
pipes_df_touse_h2.loc[pipes_df_touse_h2.H2Status=='Pre-construction (H2 only)']['LengthMergedKm'].sum()

# * how many H2 pipelines are planning to be 100%? blended?
#   * A: really, none; the Malta-Italy Gas Pipeline is actually seeming realistic-ish but has language about "up to 100%" rather than a confirmation

# ## hydrogen table 1

# ===== Cell 86 =====
country_ratios_df_gas.loc[country_ratios_df_gas.H2Status!=''].MergedKmByCountry.sort_values()

# ===== Cell 87 =====
# country_ratios_df_gas.loc[country_ratios_df_gas.H2Status!=''].groupby(
#     ['H2Status','Country'])[['MergedKmByCountry']].sum().sort_values('MergedKmByCountry', ascending=False)

country_ratios_df_gas.loc[country_ratios_df_gas.H2Status!=''].groupby(
    ['Country'])[['MergedKmByCountry']].sum().sort_values('MergedKmByCountry', ascending=False)

# # visualize timeline

# ===== Cell 88 =====
terms_df_touse_imports.loc[terms_df_touse_imports.Status.isin(['Operating'])]

# # IEEFA report

# ===== Cell 89 =====
terms_df_orig.loc[(terms_df_orig.Region=='Europe')&
                  (terms_df_orig['FacilityType']=='Import')&
                  (terms_df_orig.Status=='Operating')]['CapacityInBcm/y'].sum()

# ===== Cell 90 =====
terms_df_orig.loc[(terms_df_orig.Region=='Europe')&
                  (terms_df_orig['FacilityType']=='Import')&
                  (terms_df_orig.Status.isin(['Proposed','Construction']))]['CapacityInBcm/y'].sum()

# ===== Cell 91 =====
terms_df_orig.loc[(terms_df_orig.EuroCrisisTracker=='yes')&
                  (terms_df_orig['FacilityType']=='Import')&
                  (terms_df_orig.Status.isin(['Proposed','Construction']))]['CapacityInBcm/y'].sum()

# ===== Cell 92 =====
275.2+246.5

# ===== Cell 93 =====
275.2+154.84

# # CAN webinar matches?

# ===== Cell 94 =====
terms_df_orig.loc[(terms_df_orig.EuroCrisisTracker=='yes')&
                  (terms_df_orig['FacilityType']=='Import')&
                  (terms_df_orig.Status.isin(['Proposed','Construction']))&
                  (terms_df_orig.StartYearEarliest.isin([2022,2023,2024]))]['CapacityInBcm/y'].sum()

# ===== Cell 95 =====
terms_df_orig.loc[#(terms_df_orig.EuroCrisisTracker=='yes')&
                  (terms_df_orig.Country.isin(region_df_eu.Country))&
                  (terms_df_orig['FacilityType']=='Import')&
                  (terms_df_orig.Status.isin(['Proposed','Construction']))&
                  (terms_df_orig.StartYearEarliest.isin([2022,2023,2024]))]['CapacityInBcm/y'].sum()

# ===== Cell 96 =====
terms_df_orig.loc[#(terms_df_orig.EuroCrisisTracker=='yes')&
                  (terms_df_orig.Country.isin(region_df_eu.Country))&
                  (terms_df_orig['FacilityType']=='Import')&
                  (terms_df_orig.Status.isin(['Proposed','Construction']))&
                  (~terms_df_orig.StartYearEarliest.isnull())]['CapacityInBcm/y'].sum()

# ===== Cell 97 =====
terms_df_orig.loc[#(terms_df_orig.EuroCrisisTracker=='yes')&
                  (terms_df_orig.Country.isin(region_df_eu.Country))&
                  (terms_df_orig['FacilityType']=='Import')&
                  (terms_df_orig.Status.isin(['Proposed','Construction']))]['CapacityInBcm/y'].sum()

# ===== Cell 98 =====
terms_df_orig.loc[#(terms_df_orig.EuroCrisisTracker=='yes')&
                  (terms_df_orig.Country.isin(region_df_eu.Country))&
                  (terms_df_orig['FacilityType']=='Import')&
                  (terms_df_orig.Status.isin(['Operating']))]['CapacityInBcm/y'].sum()
