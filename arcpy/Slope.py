# -*- coding: utf-8 -*-
"""
Name:       Slope
Objective:  Standardized function for calculating slope from a Digital Elevation Model (DEM) as a part of ATUR Suitability Analysis
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
def CalcSlope(DEM, Slope):  # Slope

    # To allow overwriting outputs change overwriteOutput option to True.
    arcpy.env.overwriteOutput = True

    # Process: Slope (Slope) (sa)
    outSlope = arcpy.sa.Slope(DEM, 'DEGREE', method='PLANAR')
    print(f'\t{arcpy.GetMessages().replace(nl, nl+tb)}')
    outSlope.save(Slope)

    return outSlope
