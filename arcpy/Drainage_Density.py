# -*- coding: utf-8 -*-
"""
Name:       Drainage Density
Objective:  Standardized function for calculating drainage density as a part of ATUR Suitability Analysis
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

def DrainageDensity(Streams, Drain_Density, Snap_Raster, Mask_Geom):  # Drainage_Density
    
    # To allow overwriting outputs change overwriteOutput option to True.
    arcpy.env.overwriteOutput = True
    arcpy.env.extent = Mask_Geom  # Default processing extent
    arcpy.env.mask = Mask_Geom
    arcpy.env.snapRaster = Snap_Raster

    # Process: Line Density (Line Density) (sa)
    outLDense = arcpy.sa.LineDensity(Streams, population_field="NONE", cell_size=Snap_Raster, search_radius=1000, area_unit_scale_factor='SQUARE_KILOMETERS')
    print(f'\t{arcpy.GetMessages().replace(nl, nl+tb)}')
    outLDense.save(Drain_Density)

    return outLDense
