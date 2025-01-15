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
import os

# Workspace (ws)
# Reproduce workflow in temporary workspace to preserve initial analysis results (generated via Model Builder).
# Update ws as needed!
watershedName = 'Salt'  # Name of watershed or extent to be used in processing (ATUR for maximum state-wide extent)
ws = f"D:/Saved_GIS_Projects/ATUR_Temp/Temp_Workspace/{watershedName}"
# Make ws dir if it does not already exist
os.makedirs(ws, exist_ok=True)
ap.env.workspace = ws  # Set default arcpy workspace
gdb_name = f'Flooding.gdb'
gdb = f'{ws}/{gdb_name}'

# Input data absolute filepaths
# All input layers for maximum available extent, clipping and processing extent determined by extentFeat (shapefile)
extentFeat = r"C:\GIS_Projects\ATUR\Data\Arizona_Boundary\Salt.shp"  # i.e. mask
DEM_filePath = r"C:\GIS_Projects\ATUR\Data\DEM\Study_area_SRTM.tif"
Precip_filePath = r"C:\GIS_Projects\ATUR\Data\Climate\PRISM_ppt_30yrnormal_800m.tif"
Litho_filePath = r"C:\GIS_Projects\ATUR\Data\Geology\GeologicUnits\Geology of Arizona - Units - SGMC.shp"
Soils_filePath = r"C:\GIS_Projects\ATUR\Data\Soils\AZ_Soil_Hydric_Group.lpkx"
Lineaments_filePath = r'C:\GIS_Projects\ATUR\Data\Geology\Faults\Arizona_Lineament_Density.lpkx'
NDVI_filePath = r"C:\GIS_Projects\ATUR\Data\Climate\NDVI_10yrMean.tif"
LULC_filePath = r"C:\GIS_Projects\ATUR\Data\LULC\ESRI_LULC_30m_clip.tif"
# Classification Schema Tables
contClassifications_filePath = r"C:\GIS_Projects\ATUR\Documents\Quarto\SanPedro_Flood-MAR\SanPedro_Flood-MAR\arcpy\Classification_Tables\Flooding_ContinuousClassificationSchemas.csv"
catClassifications_filePath = r"C:\GIS_Projects\ATUR\Documents\Quarto\SanPedro_Flood-MAR\SanPedro_Flood-MAR\arcpy\Classification_Tables\Flooding_CategoricalClassificationSchemas.csv"
# Layer Weights Table
layerWeights = r"C:\GIS_Projects\ATUR\Documents\Quarto\SanPedro_Flood-MAR\SanPedro_Flood-MAR\arcpy\Classification_Tables\LayerWeights.csv"

# Arc Environment Settings
ap.env.overwriteOutput = True  # Enable file overwriting
ap.env.extent = extentFeat  # Default processing extent
ap.env.mask = extentFeat  # Default processing mask
ap.env.snapRaster = DEM_filePath  # Default processing snap raster

# Spatial Reference (sr)
sr = ap.SpatialReference(32612)  # Spatial reference = WGS 1984 UTM Zone 12N (WKID = 32612)
ap.env.outputCoordinateSystem = sr
# Units = m

# Special characters for improved readability of geoprocessing messages
nl = '\n'  # var can be used in f-strings to represent newline character
tb = '\t'  # var can be used in f-strings to represent tab character

# Check workspace for geodatabase (gdb)
if ap.Exists(gdb):
    print('GDB', gdb_name, 'Exists.')
else:
    print('No GDB', f'{gdb_name}.', 'Initializing GDB in WS.')
    # Create an ESRI file gdb
    # out_folder_path = out_path, out_name = "FloodMAR.gdb"
    out_gdb = ap.management.CreateFileGDB(ws, gdb_name)

# Preprocess Requisite Layers ---------
# Check workspace for preprocessing geodatabase (gdb)
if ap.Exists('LayerPreprocessing.gdb'):
    print('Preprocessing GDB Exists.')
    # Access Preprocessing GDB, print contents
    ap.env.workspace = f'{ws}/LayerPreprocessing.gdb'
    print('\tPreprocessing GDB Contents:')
    print('\t\tFeatures:', ap.ListFeatureClasses())
    print('\t\tRasters:', ap.ListRasters())
    # Check if preprocessing gdb has all requisite files (not including intermediate outputs)
    if all(items in ap.ListRasters() for items in ['Drainage_Density', 'Slope', 'Precipitation', 'Lithology']):
        # If all files are available
        print('\tAll requisite files are available. No layer preprocessing required.')
    else:
        # If there are missing files, run preprocessing function
        print('\tMissing files!')
        print('Preprocessing Layers.')
        # Import preprocessing function from external script
        from Preprocessing import PreprocessLayers

        # Preprocessing
        PreprocessLayers(ws, extentFeat=extentFeat, dem=DEM_filePath, precipitation=Precip_filePath, lithology=Litho_filePath)
else:
    # If preprocessing gdb does not exist
    print('No Preprocessing GDB. Initializing Layer Preprocessing')
    # Import preprocessing function from external script
    from Preprocessing import PreprocessLayers

    # Preprocessing
    PreprocessLayers(ws, extentFeat=extentFeat, dem=DEM_filePath, precipitation=Precip_filePath, lithology=Litho_filePath)

# Access Preprocessing GDB, set vars to appropriate data layer
ap.env.workspace = f'{ws}/LayerPreprocessing.gdb'
slope = f'{ap.env.workspace}/Slope'
drainage = f'{ap.env.workspace}/Drainage_Density'
precip = f'{ap.env.workspace}/Precipitation'
litho = f'{ap.env.workspace}/Lithology'
# Reset arcpy workspace
ap.env.workspace = ws

# CLASSIFICATION -----------------
# Classification Schema Table
contClassifications = pd.read_csv(contClassifications_filePath)
catClassifications = pd.read_csv(catClassifications_filePath)

# Import classification functions from external script
from Classification import DiscreteClassification
from Classification import CategoricalClassification
from Classification import ContinuousClassification
# Functions require: Raster=<input raster to classify>, ReclassTable=<df containing reclassification schema>, LayerName=<used to filter ReclassTable>, Output=<output raster>, Value=<raster band/attribute to reclassify, default = 'VALUE'>
# Continuous classification requires a function input, one of TfExponential, TfGaussian, TfLarge, TfLinear, TfLogarithm, TfLogisticDecay, TfLogisticGrowth, TfMSLarge, TfMSSmall, TfNear, TfPower, TfSmall, or TfSymmetricLinear
# See https://pro.arcgis.com/en/pro-app/3.3/tool-reference/spatial-analyst/rescale-by-function.htm for details on each classification function.

print('Classifying Layers...')
# Continuous Layers
# DEM
dem = ap.Raster(DEM_filePath)
# Calculate statistics, only necessary for 'raw' data (not preprocessed)
ap.management.CalculateStatistics(dem, area_of_interest=extentFeat)
demMin = dem.minimum  # Caution! Some sinks (elev. < 0) exist in the DEM, particularly near the coast, use .minimum with caution
demMax = dem.maximum
lowerThreshold = 0
valueBelowThreshold = 5
upperThreshold = None
valueAboveThreshold = 0
# TfLinear: Set minimum > maximum for a negative slope
demFunction = ap.sa.TfLinear(minimum=demMax, maximum=demMin, lowerThreshold=lowerThreshold, valueBelowThreshold=valueBelowThreshold, upperThreshold=upperThreshold, valueAboveThreshold=valueAboveThreshold)
DEM_Classified = ContinuousClassification(DEM_filePath, demFunction, 'DEM', f'{gdb}/Classified_DEM')

# Slope
slopeMin = ap.Raster(slope).minimum
slopeMax = ap.Raster(slope).maximum
lowerThreshold = None
valueBelowThreshold = 5
upperThreshold = None
valueAboveThreshold = 0
# TfLinear: Set minimum > maximum for a negative slope
slopeFunction = ap.sa.TfLinear(minimum=slopeMax, maximum=slopeMin, lowerThreshold=lowerThreshold, valueBelowThreshold=valueBelowThreshold, upperThreshold=upperThreshold, valueAboveThreshold=valueAboveThreshold)
Slope_Classified = ContinuousClassification(slope, slopeFunction, 'Slope', f'{gdb}/Classified_Slope')

# Lineament Density
line = ap.Raster(Lineaments_filePath)
# Calculate statistics, only necessary for 'raw' data (not preprocessed)
ap.management.CalculateStatistics(line, area_of_interest=extentFeat)
lineMin = line.minimum
lineMax = line.maximum
lowerThreshold = None
valueBelowThreshold = 5
upperThreshold = None
valueAboveThreshold = 0
# TfLinear: Set minimum > maximum for a negative slope
lineamentsFunction = ap.sa.TfLinear(minimum=lineMax, maximum=lineMin, lowerThreshold=lowerThreshold, valueBelowThreshold=valueBelowThreshold, upperThreshold=upperThreshold, valueAboveThreshold=valueAboveThreshold)
Lineaments_Classified = ContinuousClassification(Lineaments_filePath, lineamentsFunction, 'Lineaments', f'{gdb}/Classified_LineamentDensity')

# Drainage Density
drainMin = ap.Raster(drainage).minimum
drainMax = ap.Raster(drainage).maximum
lowerThreshold = None
valueBelowThreshold = 0
upperThreshold = None
valueAboveThreshold = 5
# TfLinear: Set minimum > maximum for a negative slope
lineamentsFunction = ap.sa.TfLinear(minimum=drainMin, maximum=drainMax, lowerThreshold=lowerThreshold, valueBelowThreshold=valueBelowThreshold, upperThreshold=upperThreshold, valueAboveThreshold=valueAboveThreshold)
Drainage_Classified = ContinuousClassification(drainage, lineamentsFunction, 'Drainage', f'{gdb}/Classified_DrainageDensity')

# Precipitation
precipMin = ap.Raster(precip).minimum
precipMax = ap.Raster(precip).maximum
lowerThreshold = None
valueBelowThreshold = 0
upperThreshold = None
valueAboveThreshold = 5
# TfLinear: Set minimum > maximum for a negative slope
precipFunction = ap.sa.TfLinear(minimum=precipMin, maximum=precipMax, lowerThreshold=lowerThreshold, valueBelowThreshold=valueBelowThreshold, upperThreshold=upperThreshold, valueAboveThreshold=valueAboveThreshold)
Precip_Classified = ContinuousClassification(precip, precipFunction, 'Precip', f'{gdb}/Classified_Precipitation')

# NDVI
ndvi = ap.Raster(NDVI_filePath)
# Calculate statistics, only necessary for 'raw' data (not preprocessed)
ap.management.CalculateStatistics(ndvi, area_of_interest=extentFeat)
ndviMin = ndvi.minimum
ndviMax = ndvi.maximum
lowerThreshold = None
valueBelowThreshold = 5
upperThreshold = None
valueAboveThreshold = 0
# TfLinear: Set minimum > maximum for a negative slope
ndviFunction = ap.sa.TfLinear(minimum=ndviMax, maximum=ndviMin, lowerThreshold=lowerThreshold, valueBelowThreshold=valueBelowThreshold, upperThreshold=upperThreshold, valueAboveThreshold=valueAboveThreshold)
NDVI_Classified = ContinuousClassification(NDVI_filePath, ndviFunction, 'NDVI', f'{gdb}/Classified_NDVI')

# Categorical Layers
# Lithology
Litho_Classified = CategoricalClassification(litho, catClassifications, 'Lithology', f'{gdb}/Classified_Lithology', Value='UNIT_NAME')
# Soil Type
Soil_Classified = CategoricalClassification(Soils_filePath, catClassifications, 'Soils', f'{gdb}/Classified_Soils', Value='ClassName')
# LULC
LULC_Classified = CategoricalClassification(LULC_filePath, catClassifications, 'LULC', f'{gdb}/Classified_LULC')

# Suitability Analysis (Raster Calculator)
# Read in layer weights, drop rechargeWeights (floodingWeights only)
floodWeights = pd.read_csv(layerWeights).drop('rechargeWeight', axis=1)
# Assign weights
demWeight = floodWeights[floodWeights['layer'] == 'DEM']['floodingWeight'].values[0]
slopeWeight = floodWeights[floodWeights['layer'] == 'Slope']['floodingWeight'].values[0]
lineamentWeight = floodWeights[floodWeights['layer'] == 'Lineaments']['floodingWeight'].values[0]
drainageWeight = floodWeights[floodWeights['layer'] == 'Drainage']['floodingWeight'].values[0]
precipWeight = floodWeights[floodWeights['layer'] == 'Precip']['floodingWeight'].values[0]
ndviWeight = floodWeights[floodWeights['layer'] == 'NDVI']['floodingWeight'].values[0]
lithoWeight = floodWeights[floodWeights['layer'] == 'Lithology']['floodingWeight'].values[0]
soilWeight = floodWeights[floodWeights['layer'] == 'Soil']['floodingWeight'].values[0]
lulcWeight = floodWeights[floodWeights['layer'] == 'LULC']['floodingWeight'].values[0]

print('Calculating Raster Math...')
print('\tExpression:', f'(DEM_Classified * {demWeight}) + (Slope_Classified * {slopeWeight}) + (Lineaments_Classified * {lineamentWeight}) + (Drainage_Classified * {drainageWeight}) + (Precip_Classified * {precipWeight}) + (NDVI_Classified * {ndviWeight}) + (Litho_Classified * {lithoWeight}) + (Soil_Classified * {soilWeight}) + (LULC_Classified * {lulcWeight})')
floodSuitability = (DEM_Classified * demWeight) + (Slope_Classified * slopeWeight) + (Lineaments_Classified * lineamentWeight) + (Drainage_Classified * drainageWeight) + (Precip_Classified * precipWeight) + (NDVI_Classified * ndviWeight) + (Litho_Classified * lithoWeight) + (Soil_Classified * soilWeight) + (LULC_Classified * lulcWeight)
floodSuitability.save(f'{gdb}/Flooding_Suitability')
