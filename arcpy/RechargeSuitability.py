# -*- coding: utf-8 -*-
"""
Name:       Recharge Suitability
Objective:  Compute recharge suitability analysis as a part of ATUR project
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
gdb_name = 'SanPedro_Recharge.gdb'
gdb = f'{ws}/{gdb_name}'

# Input data absolute filepaths
# San Pedro watershed data may be minimally pre-processed from raw data files
# TODO: Change all datasets to full ATUR extent and include clipping step (partially complete)
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
contClassifications_filePath = r"C:\GIS_Projects\ATUR\Documents\Quarto\SanPedro_Flood-MAR\SanPedro_Flood-MAR\arcpy\Classification_Tables\Recharge_ContinuousClassificationSchemas.csv"
catClassifications_filePath = r"C:\GIS_Projects\ATUR\Documents\Quarto\SanPedro_Flood-MAR\SanPedro_Flood-MAR\arcpy\Classification_Tables\Recharge_CategoricalClassificationSchemas.csv"
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
    if all(items in ap.ListRasters() for items in ['Filled_SRTM', 'Drainage_Density', 'Slope', 'Precipitation', 'Lithology']):
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
filledDEM = f'{ap.env.workspace}/Filled_SRTM'
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
# TODO: from Classification import ContinuousClassification
# Functions require: Raster=<input raster to classify>, ReclassTable=<df containing reclassification schema>, LayerName=<used to filter ReclassTable>, Output=<output raster>, Value=<raster band/attribute to reclassify, default = 'VALUE'>

print('Classifying Layers...')
# Continuous Layers (Discrete Classification)
# DEM
DEM_Classified = DiscreteClassification(filledDEM, contClassifications, 'DEM', f'{gdb}/Classified_DEM')
# Slope
Slope_Classified = DiscreteClassification(slope, contClassifications, 'Slope', f'{gdb}/Classified_Slope')
# Lineament Density
Lineaments_Classified = DiscreteClassification(Lineaments_filePath, contClassifications, 'Lineaments', f'{gdb}/Classified_LineamentDensity')
# Drainage Density
Drainage_Classified = DiscreteClassification(drainage, contClassifications, 'Drainage', f'{gdb}/Classified_DrainageDensity')
# Precipitation
Precip_Classified = DiscreteClassification(precip, contClassifications, 'Precip', f'{gdb}/Classified_Precipitation')
# NDVI
NDVI_Classified = DiscreteClassification(NDVI_filePath, contClassifications, 'NDVI', f'{gdb}/Classified_NDVI')
# Categorical Layers
# Lithology
Litho_Classified = CategoricalClassification(litho, catClassifications, 'Lithology', f'{gdb}/Classified_Lithology', Value='UNIT_NAME')
# Soil Type
Soil_Classified = CategoricalClassification(Soils_filePath, catClassifications, 'Soils', f'{gdb}/Classified_Soils', Value='ClassName')
# LULC
LULC_Classified = CategoricalClassification(LULC_filePath, catClassifications, 'LULC', f'{gdb}/Classified_LULC')

# Suitability Analysis (Raster Calculator)
# Read in layer weights, drop floodingWeights (rechargeWeights only)
rechargeWeights = pd.read_csv(layerWeights).drop('floodingWeight', axis=1)
# Assign weights
demWeight = rechargeWeights[rechargeWeights['layer'] == 'DEM']['rechargeWeight'].values[0]
slopeWeight = rechargeWeights[rechargeWeights['layer'] == 'Slope']['rechargeWeight'].values[0]
lineamentWeight = rechargeWeights[rechargeWeights['layer'] == 'Lineaments']['rechargeWeight'].values[0]
drainageWeight = rechargeWeights[rechargeWeights['layer'] == 'Drainage']['rechargeWeight'].values[0]
precipWeight = rechargeWeights[rechargeWeights['layer'] == 'Precip']['rechargeWeight'].values[0]
ndviWeight = rechargeWeights[rechargeWeights['layer'] == 'NDVI']['rechargeWeight'].values[0]
lithoWeight = rechargeWeights[rechargeWeights['layer'] == 'Lithology']['rechargeWeight'].values[0]
soilWeight = rechargeWeights[rechargeWeights['layer'] == 'Soil']['rechargeWeight'].values[0]
lulcWeight = rechargeWeights[rechargeWeights['layer'] == 'LULC']['rechargeWeight'].values[0]

print('Calculating Raster Math...')
print('\tExpression:', '(DEM_Classified * demWeight) + (Slope_Classified * slopeWeight) + (Lineaments_Classified * lineamentWeight) + (Drainage_Classified * drainageWeight) + (Precip_Classified * precipWeight) + (NDVI_Classified * ndviWeight) + (Litho_Classified * lithoWeight) + (Soil_Classified * soilWeight) + (LULC_Classified * lulcWeight)')
rechargeSuitability = (DEM_Classified * demWeight) + (Slope_Classified * slopeWeight) + (Lineaments_Classified * lineamentWeight) + (Drainage_Classified * drainageWeight) + (Precip_Classified * precipWeight) + (NDVI_Classified * ndviWeight) + (Litho_Classified * lithoWeight) + (Soil_Classified * soilWeight) + (LULC_Classified * lulcWeight)
rechargeSuitability.save(f'{gdb}/Recharge_Suitability')
