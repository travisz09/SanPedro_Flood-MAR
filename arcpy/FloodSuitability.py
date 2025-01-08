# -*- coding: utf-8 -*-
"""
Name:       Flood Suitability
Objective:  Compute flooding suitability analysis as a part of ATUR project
Author:     Travis Zalesky
Date:       1/6/25

Based on San Pedro Flood-MAR model builder, Zalesky, Dec. 2024
"""

# SETUP -----------
# Imports
import arcpy as ap
import pandas as pd

# Workspace (ws)
# Reproduce workflow in temporary workspace to preserve initial analysis results (generated via Model Builder).
# Update ws as needed!
ws = "D:/Saved_GIS_Projects/ATUR_Temp/Temp_Workspace"
ap.env.workspace = ws  # Set default arcpy workspace
gdb_name = 'Flooding.gdb'
gdb = f'{ws}/{gdb_name}'

# Input data absolute filepaths
# San Pedro watershed data may be minimally pre-processed from raw data files
# TODO: Change all datasets to full ATUR extent and include clipping step
extentFeat = r"C:\GIS_Projects\ATUR\Data\Arizona_Boundary\SanPedroWatershed.shp"  # i.e. mask
DEM_filePath = r"C:\GIS_Projects\ATUR\Data\DEM\Study_area_SRTM.tif"
Precip_filePath = r"C:\GIS_Projects\ATUR\Data\Climate\PRISM_ppt_30yrnormal_800m.tif"
Litho_filePath = r"C:\GIS_Projects\ATUR\Data\Geology\GeologicUnits\Geology of Arizona - Units - SGMC.shp"
Soils_filePath = r"C:\GIS_Projects\ATUR\Data\Soils\AZ_Soil_Hydric_Group.lpkx"
# TODO: Ask Ryan for state-wide lineaments density layer
# Linaments not currently available for full ATUR extent
Lineaments_filePath = r'C:\Users\travisz09\Documents\ArcGIS\Packages\LineamentDensity_550d0d\p30\LineamentDensity.lyrx'
NDVI_filePath = r"C:\GIS_Projects\ATUR\Data\Climate\NDVI_10yrMean.tif"
LULC_filePath = r"C:\GIS_Projects\ATUR\Data\LULC\ESRI_LULC_30m_clip.tif"
# Classification Schema Tables
contClassifications_filePath = r"C:\GIS_Projects\ATUR\Documents\Quarto\SanPedro_Flood-MAR\SanPedro_Flood-MAR\arcpy\Classification_Tables\Flooding_ContinuousClassificationSchemas.csv"
catClassifications_filePath = r"C:\GIS_Projects\ATUR\Documents\Quarto\SanPedro_Flood-MAR\SanPedro_Flood-MAR\arcpy\Classification_Tables\Flooding_CategoricalClassificationSchemas.csv"

# Arc Environment Settings
ap.env.overwriteOutput = True  # Enable file overwriting
ap.env.extent = extentFeat  # Default processing extent
ap.env.mask = extentFeat  # Default processing mask
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
    out_gdb = ap.management.CreateFileGDB(ws, gdb_name)

# PREPROCESSING -------------------
# DEM Preprocessing ------------
# Refer to DEM_PreProcessing.py for details
# Import preprocessing function from external script
from DEM_PreProcessing import DEMPreProcessing

# Preprocess DEM
# Requires: DEM=<input DEM>, Filled_DEM=<output DEM>
print('DEM Preprocessing...')
filledDEM = DEMPreProcessing(DEM_filePath, Filled_DEM=f'{gdb}/Filled_SRTM')

# Hydrologic Conditioning and Streams ------------
# Refer to Hydrologic_Conditioning.py for details
# Import hydrologic conditioning function from external script
from Hydrologic_Conditioning import HydrologicConditioning

# Condition filled DEM
# Requires: Filled_DEM=<input DEM>, FlowDir=<intermediate output>, FlowAcc=<intermediate output>, StreamsRast=<intermediate output>, StreamsFeat=<output stream features polyline>
print('Hydrologically Conditioning DEM...')
streams = HydrologicConditioning(filledDEM, f'{gdb}/Flow_Direction', f'{gdb}/Flow_Accumulation', f'{gdb}/Streams_Raster', f'{gdb}/Stream_Features')

# Drainage Density -------------
# Refer to Drainage_Density.py for details
# Import drainage density function from external script
from Drainage_Density import DrainageDensity

# Calculate drainage density
# Requires: Streams=<input stream features>, Drain_Density=<output drainage density raster>, Snap_Raster=<raster to match extent and resolution>, Mask_Geom=<feature to define mask>
print('Calculating Drainage Density...')
drainage = DrainageDensity(streams, f'{gdb}/Drainage_Density', DEM_filePath, Mask_Geom=extentFeat)

# Slope ----------------
# Refer to Slope.py for details
# Import slope function from external script
from Slope import CalcSlope

# Calculate Slope
# Requires: DEM=<input DEM>, Slope=<output slope raster>
print('Calculating Slope...')
slope = CalcSlope(filledDEM, f'{gdb}/Slope')

# Precipitation Preprocessing --------------
# Refer to Resample_Raster.py for details
# Import preprocessing function from external script
from Resample_Raster import ResampleRaster

# Resample precipitation data
# Requires: Raster=<input raster data>, Output=<output raster>, Snap_Raster=<raster to match extent and resolution>
print('Precipitation Preprocessing...')
precip = ResampleRaster(Precip_filePath, f'{gdb}/Precipitation', DEM_filePath)

# Lithology Preprocessing --------------
# Refer to Feat_to_Rast.py for details
# Import preprocessing function from external script
from Feat_to_Rast import FeatToRast

# Convert lithology feature data to raster
# Requires: Feat=<input feature layer>, Value_Field=<field corresponding to raster values>, Output=<output raster>, Snap_Raster=<raster to match extent and resolution>
print('Lithology Preprocessing...')
litho = FeatToRast(Litho_filePath, "UNIT_NAME", f'{gdb}/Lithology', DEM_filePath) 

# CLASSIFICATION -----------------
# Classification Schema Table
contClassifications = pd.read_csv(contClassifications_filePath)
catClassifications = pd.read_csv(catClassifications_filePath)

# Import classification functions from external script
from Classification import ContinuousClassification
from Classification import CategoricalClassification
# Functions require: Raster=<input raster to classify>, ReclassTable=<df containing reclassification schema>, LayerName=<used to filter ReclassTable>, Output=<output raster>, Value=<raster band/attribute to reclassify, default = 'VALUE'>

print('Classifying Layers...')
# Continuous Layers
# DEM
DEM_Classified = ContinuousClassification(filledDEM, contClassifications, 'DEM', f'{gdb}/Classified_DEM')
# Slope
Slope_Classified = ContinuousClassification(slope, contClassifications, 'Slope', f'{gdb}/Classified_Slope')
# Lineament Density
Lineaments_Classified = ContinuousClassification(Lineaments_filePath, contClassifications, 'Lineaments', f'{gdb}/Classified_LineamentDensity')
# Drainage Density
Drainage_Classified = ContinuousClassification(drainage, contClassifications, 'Drainage', f'{gdb}/Classified_DrainageDensity')
# Precipitation
Precip_Classified = ContinuousClassification(precip, contClassifications, 'Precip', f'{gdb}/Classified_Precipitation')
# NDVI
NDVI_Classified = ContinuousClassification(NDVI_filePath, contClassifications, 'NDVI', f'{gdb}/Classified_NDVI')
# Categorical Layers
# Lithology
Litho_Classified = CategoricalClassification(litho, catClassifications, 'Lithology', f'{gdb}/Classified_Lithology', Value='UNIT_NAME')
# Soil Type
Soil_Classified = CategoricalClassification(Soils_filePath, catClassifications, 'Soils', f'{gdb}/Classified_Soils', Value='ClassName')
# LULC
LULC_Classified = CategoricalClassification(LULC_filePath, catClassifications, 'LULC', f'{gdb}/Classified_LULC')
