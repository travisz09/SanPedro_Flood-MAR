# -*- coding: utf-8 -*-
"""
Name:       Feature to Raster
Objective:  Standardized function for converting feature datasets to rasters as a part of ATUR Suitability Analysis
Author:     Travis Zalesky
Date:       1/6/25

Based on San Pedro Flood-MAR model builder, Zalesky, Dec. 2024
"""
import arcpy
from arcpy.sa import *
from sys import argv

# Special characters for improved readability of geoprocessing messages
nl = '\n'  # var can be used in f-strings to represent newline character
tb = '\t'  # var can be used in f-strings to represent tab character

def FeatToRast(Feat, Value_Field, Output, Snap_Raster, Mask_Geom):  # Feature to Raster

    # To allow overwriting outputs change overwriteOutput option to True.
    arcpy.env.overwriteOutput = True
    arcpy.env.extent = Mask_Geom  # Default processing extent
    arcpy.env.mask = Mask_Geom  # Default processing mask
    arcpy.env.snapRaster = Snap_Raster  # Default processing snap raster

    # Process: Feature to Raster (ConvertFeatureToRaster) (ra)
    print('\tConverting Features to Raster...')
    outRaster = arcpy.conversion.FeatureToRaster(Feat, Value_Field, Output, Snap_Raster)
    print(f'\t\t{arcpy.GetMessages().replace(nl, nl+tb+tb)}')

    return outRaster
