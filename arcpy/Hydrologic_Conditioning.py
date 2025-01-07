# -*- coding: utf-8 -*-
"""
Name:       Hydrologic Conditioning
Objective:  Standardized function for hydrologically conditioning a Digital Elevation Model (DEM) as a part of ATUR Suitability Analysis
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
def HydrologicConditioning(Filled_DEM, FlowDir, FlowAcc, StreamsRast, StreamsFeat):  # Hydrologic_Conditioning

    # To allow overwriting outputs change overwriteOutput option to True.
    arcpy.env.overwriteOutput = True

    # Process: Flow Direction (Flow Direction) (sa)
    print('\tFlow Direction...')
    outFlowDir = arcpy.sa.FlowDirection(Filled_DEM, force_flow='FORCE', flow_direction_type='D8')
    print(f'\t\t{arcpy.GetMessages().replace(nl, nl+tb+tb)}')
    outFlowDir.save(FlowDir)


    # Process: Flow Accumulation (Flow Accumulation) (sa)
    print('\tFlow Accumulation...')
    outFlowAcc = arcpy.sa.FlowAccumulation(outFlowDir, flow_direction_type='D8')
    print(f'\t\t{arcpy.GetMessages().replace(nl, nl+tb+tb)}')
    outFlowAcc.save(FlowAcc)

    # Process: Con (Con) (sa)
    print('\tThresholding Streams...')
    outStreamsRast = Con(outFlowAcc, in_true_raster_or_constant=1, in_false_raster_or_constant='', where_clause="VALUE >= 1000")
    print(f'\t\t{arcpy.GetMessages().replace(nl, nl+tb+tb)}')
    outStreamsRast.save(StreamsRast)


    # Process: Stream to Feature (Stream to Feature) (sa)
    print('\tStreams (Raster) to Features...')
    outStreamsFeat = arcpy.sa.StreamToFeature(outStreamsRast, outFlowDir, StreamsFeat, "SIMPLIFY")
    print(f'\t\t{arcpy.GetMessages().replace(nl, nl+tb+tb)}')

    return outStreamsFeat
