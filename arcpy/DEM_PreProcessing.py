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

#For inline variable substitution, parameters passed as a String are evaluated using locals(), globals() and isinstance(). To override, substitute values directly.
def DEMPreProcessing(DEM, Filled_DEM, Z_limit=None):  # DEM_PreProcessing

    # To allow overwriting outputs change overwriteOutput option to True.
    arcpy.env.overwriteOutput = True

    # Process: Fill (Fill) (sa)
    print('\tFilling DEM...')
    if Z_limit in locals():  # If Z_limit param is given...
        outFill = arcpy.sa.Fill(DEM, Z_limit)
    else:
        outFill = arcpy.sa.Fill(DEM)

    print(f'\t\t{arcpy.GetMessages().replace(nl, nl+tb+tb)}')

    outFill.save(Filled_DEM)  # Save output

    return outFill
    