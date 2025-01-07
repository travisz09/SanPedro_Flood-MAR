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

#For inline variable substitution, parameters passed as a String are evaluated using locals(), globals() and isinstance(). To override, substitute values directly.
def FeatToRast(Feat, Value_Field, Output, Snap_Raster):  # Slope

    # To allow overwriting outputs change overwriteOutput option to True.
    arcpy.env.overwriteOutput = True
    arcpy.env.snapRaster = Snap_Raster
    resolution = str(arcpy.management.GetRasterProperties(Snap_Raster, 'CELLSIZEX')) + ' Meters'

    # Check out any necessary licenses.
    arcpy.CheckOutExtension("spatial")

    # Process: Feature to Raster (ConvertFeatureToRaster) (ra)
    print('\tConverting Features to Raster...')
    outRaster = arcpy.ra.ConvertFeatureToRaster(Feat, Value_Field, Output, resolution)
    print(f'\t\t{arcpy.GetMessages().replace(nl, nl+tb+tb)}')

    return outRaster
