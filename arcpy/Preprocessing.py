# -*- coding: utf-8 -*-
"""
Name:       Classification
Objective:  Preprocess all requisite data layers for ATUR Suitability Analysis classification
Author:     Travis Zalesky
Date:       1/7/25

Based on San Pedro Flood-MAR model builder, Zalesky, Dec. 2024
"""
import arcpy as ap
from arcpy.sa import *
from sys import argv

# Special characters for improved readability of geoprocessing messages
nl = '\n'  # var can be used in f-strings to represent newline character
tb = '\t'  # var can be used in f-strings to represent tab character

# Preprocessing of thematic layers used in ATUR Flood MAR suitability analysis
def PreprocessLayers(workspace, extentFeat, dem, precipitation, lithology):
    
    # Arc Environment Settings
    ap.env.workspace = workspace  # Set default arcpy workspace
    ap.env.overwriteOutput = True  # Enable file overwriting
    ap.env.extent = extentFeat  # Default processing extent
    ap.env.mask = extentFeat  # Default processing mask
    ap.env.snapRaster = dem  # Default processing snap raster
    gdb_name = 'LayerPreprocessing.gdb'
    gdb = f'{workspace}/{gdb_name}'

    # Spatial Reference (sr)
    sr = ap.SpatialReference(32612)  # Spatial reference = WGS 1984 UTM Zone 12N (WKID = 32612)
    ap.env.outputCoordinateSystem = sr
    # Units = m

    # Check workspace for geodatabase (gdb)
    if ap.Exists(gdb):
        print('Preprocessing GDB Exists.')
    else:
        print('No Preprocessing GDB. Initializing LayerPreprocessing GDB in WS.')
        # Create an ESRI file gdb
        # out_folder_path = out_path, out_name = "FloodMAR.gdb"
        out_gdb = ap.management.CreateFileGDB(workspace, gdb_name)

        
    # PREPROCESSING -------------------
    # DEM Preprocessing ------------
    # Refer to DEM_PreProcessing.py for details
    # Import preprocessing function from external script
    from DEM_PreProcessing import DEMPreProcessing

    # Preprocess DEM
    # Requires: DEM=<input DEM>, Filled_DEM=<output DEM>
    print('DEM Preprocessing...')
    filledDEM = DEMPreProcessing(dem, f'{gdb}/Filled_SRTM', dem, extentFeat)

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
    drainage = DrainageDensity(streams, f'{gdb}/Drainage_Density', dem, Mask_Geom=extentFeat)

    # Slope ----------------
    # Refer to Slope.py for details
    # Import slope function from external script
    from Slope import CalcSlope

    # Calculate Slope
    # Requires: DEM=<input DEM>, Slope=<output slope raster>
    print('Calculating Slope...')
    slope = CalcSlope(filledDEM, f'{gdb}/Slope', dem, Mask_Geom=extentFeat)

    # Precipitation Preprocessing --------------
    # Refer to Resample_Raster.py for details
    # Import preprocessing function from external script
    from Resample_Raster import ResampleRaster

    # Resample precipitation data
    # Requires: Raster=<input raster data>, Output=<output raster>, Snap_Raster=<raster to match extent and resolution>
    print('Precipitation Preprocessing...')
    precip = ResampleRaster(precipitation, f'{gdb}/Precipitation', dem, extentFeat)

    # Lithology Preprocessing --------------
    # Refer to Feat_to_Rast.py for details
    # Import preprocessing function from external script
    from Feat_to_Rast import FeatToRast

    # Convert lithology feature data to raster
    # Requires: Feat=<input feature layer>, Value_Field=<field corresponding to raster values>, Output=<output raster>, Snap_Raster=<raster to match extent and resolution>
    print('Lithology Preprocessing...')
    litho = FeatToRast(lithology, "UNIT_NAME", f'{gdb}/Lithology', dem, extentFeat) 
