# -*- coding: utf-8 -*-
"""
Name:       Flood Suitability
Objective:  Compute flooding suitability analysis as a part of ATUR project
Author:     Travis Zalesky
Date:       1/6/25

Based on San Pedro Flood-MAR model builder, Zalesky, Dec. 2024
"""

# Setup -----------
# Imports
import arcpy as ap
from arcpy import sa  # arcpy spatial analyst module

# Workspace (ws)
# Reproduce workflow in temporary workspace to preserve initial analysis results (generated via Model Builder).
# Update ws as needed!
ws = "D:/Saved_GIS_Projects/ATUR_Temp/Temp_Workspace"
ap.env.workspace = ws  # Set default arcpy workspace
gdb = f'{ws}/FloodMAR.gdb'

# Input data absolute filepaths
# San Pedro watershed data may be minimally pre-processed from raw data files
extentFeat = r'C:\GIS_Projects\ATUR\ArcPro\DataExploration_Sandbox\ATUR_DataExploration.gdb\SanPedroWatershed'  # i.e. mask
DEM_filePath = r'C:\GIS_Projects\ATUR\ArcPro\DataExploration_Sandbox\ATUR_DataExploration.gdb\SanPedro_SRTM'
Precip_filePath = r'C:\GIS_Projects\ATUR\ArcPro\DataExploration_Sandbox\ATUR_DataExploration.gdb\SanPedro_PRISM_ppt_30yrnorm'
Litho_filePath = r'C:\GIS_Projects\ATUR\ArcPro\General_Suitability_Analysis\General_Suitability_Analysis.gdb\SanPedro_GeoUnits_Feat'

# print(ap.management.GetRasterProperties(DEM_filePath, 'CELLSIZEX'), ' Meters')

# Arc Environment Settings
ap.env.overwriteOutput = True  # Enable file overwriting
ap.env.extent = DEM_filePath  # Default processing extent
ap.env.snapRaster = DEM_filePath  # Default processing snap raster

# Spatial Reference (sr)
sr = ap.SpatialReference(32612)  # Spatial reference = WGS 1984 UTM Zone 12N (WKID = 32612)
# Units = m

# Special characters for improved readability of geoprocessing messages
nl = '\n'  # var can be used in f-strings to represent newline character
tb = '\t'  # var can be used in f-strings to represent tab character

# Check workspace for geodatabase (gdb)
if ap.Exists(gdb):
    print('GDB Exists.')
else:
    print('No GDB. Initializing GDB in WS.')
    # Create an ESRI file gdb
    # out_folder_path = out_path, out_name = "FloodMAR.gdb"
    out_gdb = ap.management.CreateFileGDB(ws, "FloodMAR.gdb")

# # DEM Preprocessing ------------
# # Refer to DEM_PreProcessing.py for details
# # Import preprocessing function from external script
# from DEM_PreProcessing import DEMPreProcessing

# # Preprocess DEM
# # Requires: DEM=<input DEM>, Filled_DEM=<output DEM>
# print('DEM Preprocessing...')
# filledDEM = DEMPreProcessing(DEM_filePath, Filled_DEM=f'{gdb}/Filled_SRTM')

# # Hydrologic Conditioning and Streams ------------
# # Refer to Hydrologic_Conditioning.py for details
# # Import hydrologic conditioning function from external script
# from Hydrologic_Conditioning import HydrologicConditioning

# # Condition filled DEM
# # Requires: Filled_DEM=<input DEM>, FlowDir=<intermediate output>, FlowAcc=<intermediate output>, StreamsRast=<intermediate output>, StreamsFeat=<output stream features polyline>
# print('Hydrologically Conditioning DEM...')
# streams = HydrologicConditioning(filledDEM, f'{gdb}/Flow_Direction', f'{gdb}/Flow_Accumulation', f'{gdb}/Streams_Raster', f'{gdb}/Stream_Features')

# # Drainage Density -------------
# # Refer to Drainage_Density.py for details
# # Import drainage density function from external script
# from Drainage_Density import DrainageDensity

# # Calculate drainage density
# # Requires: Streams=<input stream features>, Drain_Density=<output drainage density raster>, Snap_Raster=<raster to match extent and resolution>, Mask_Geom=<feature to define mask>
# print('Calculating Drainage Density...')
# drainage = DrainageDensity(streams, f'{gdb}/Drainage_Density', DEM_filePath, Mask_Geom=extentFeat)

# # Slope ----------------
# # Refer to Slope.py for details
# # Import slope function from external script
# from Slope import CalcSlope

# # Calculate Slope
# # Requires: DEM=<input DEM>, Slope=<output slope raster>
# print('Calculating Slope...')
# slope = CalcSlope(filledDEM, f'{gdb}/Slope')

# # Precipitation Preprocessing --------------
# # Refer to Resample_Raster.py for details
# # Import preprocessing function from external script
# from Resample_Raster import ResampleRaster

# # Resample precipitation data
# # Requires: Raster=<input raster data>, Output=<output raster>, Snap_Raster=<raster to match extent and resolution>
# print('Precipitation Preprocessing...')
# precip = ResampleRaster(Precip_filePath, f'{gdb}/Precipitation', DEM_filePath)

# Lithology Preprocessing --------------
# Refer to Feat_to_Rast.py for details
# Import preprocessing function from external script
from Feat_to_Rast import FeatToRast

# Convert lithology feature data to raster
# Requires: Feat=<input feature layer>, Value_Field=<field corresponding to raster values>, Output=<output raster>, Snap_Raster=<raster to match extent and resolution>
print('Lithology Preprocessing...')
litho = FeatToRast(Litho_filePath, "UNIT_NAME", f'{gdb}/Lithology', DEM_filePath) 
