# -*- coding: utf-8 -*-
"""
Name:       Resample Raster
Objective:  Standardized function for resampling raster data as a part of ATUR Suitability Analysis
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

def ResampleRaster(Raster, Output, Snap_Raster, Mask_Geom):  # Slope

    # To allow overwriting outputs change overwriteOutput option to True.
    arcpy.env.overwriteOutput = True
    arcpy.env.extent = Mask_Geom  # Default processing extent
    arcpy.env.mask = Mask_Geom  # Default processing mask
    arcpy.env.snapRaster = Snap_Raster  # Default processing snap raster
    resolution = arcpy.management.GetRasterProperties(Snap_Raster, 'CELLSIZEX')

    # Process: Resample (Resample) (management)
    print('\tResampling Raster...')
    outRaster = arcpy.management.Resample(Raster, Output, resolution, 'BILINEAR')
    print(f'\t\t{arcpy.GetMessages().replace(nl, nl+tb+tb)}')

    return outRaster
