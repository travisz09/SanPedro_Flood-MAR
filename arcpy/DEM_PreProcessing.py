# -*- coding: utf-8 -*-
"""
Name:       DEM PreProcessing
Objective:  Standardized function for pre-processing a Digital Elevation Model (DEM) as a part of ATUR Suitability Analysis
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

def DEMPreProcessing(DEM, Filled_DEM, Snap_Raster, Mask_Geom, Z_limit=None):  # DEM_PreProcessing

    # To allow overwriting outputs change overwriteOutput option to True.
    arcpy.env.overwriteOutput = True
    arcpy.env.extent = Mask_Geom  # Default processing extent
    arcpy.env.mask = Mask_Geom  # Default processing mask
    arcpy.env.snapRaster = Snap_Raster  # Default processing snap raster
    
    # Process: Fill (Fill) (sa)
    print('\tFilling DEM...')
    if Z_limit in locals():  # If Z_limit param is given...
        outFill = arcpy.sa.Fill(DEM, Z_limit)
    else:
        outFill = arcpy.sa.Fill(DEM)

    print(f'\t\t{arcpy.GetMessages().replace(nl, nl+tb+tb)}')

    outFill.save(Filled_DEM)  # Save output

    return outFill
    