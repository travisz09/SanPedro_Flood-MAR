# -*- coding: utf-8 -*-
"""
Name:       Classification
Objective:  Standardized functions for classifying rasters as a part of ATUR Suitability Analysis
Author:     Travis Zalesky
Date:       1/7/25

Based on San Pedro Flood-MAR model builder, Zalesky, Dec. 2024
"""
import arcpy
from arcpy.sa import *
from sys import argv

# Special characters for improved readability of geoprocessing messages
nl = '\n'  # var can be used in f-strings to represent newline character
tb = '\t'  # var can be used in f-strings to represent tab character

# For classifying an input raster to discrete "levels".
def DiscreteClassification(Raster, ReclassTable, LayerName, Output, Value='VALUE'):  # Discrete Classification

    # Modify Reclass Table
    # Filter Layer from Layers in ReclassTable, drop 'layer' column
    table = ReclassTable[ReclassTable['layer'] == LayerName].drop('layer', axis=1)
    # Remap must be given as a string, formatted as "startValue endValue newValue;..."
    # Convert table to nested list
    """
    The .tolist() function will convert data types to the 'lowest common denominator', in this case 'float'. Because the newValue in the remap must be an int (technically a string resembling an int) the tolist() function must be performed in a column-wise manner. The nested list is then built using list compression syntax to generate a nested list which preserves the data type of the original df.
    """
    nestedList = list(list(x) for x in zip(*(table[x].values.tolist() for x in table.columns)))
    # Convert nestedList to formatted string
    remap = ""  # an empty string, to be appended
    # For each list (i) in nestedList
    for i in nestedList:
        # For each item (j) in list (i)
        for j in i:
            # append item (j) to string (remap)
            remap = remap + str(j) + " "
        # Strip trailing white space from string, delim = ';'
        remap = remap.strip() + ';'
    # Strip trailing delim (;) from sting
    remap = remap[:-1]

    # To allow overwriting outputs change overwriteOutput option to True.
    arcpy.env.overwriteOutput = True
    
    # Process: Feature to Raster (ConvertFeatureToRaster) (ra)
    print('\tRemapping', LayerName, 'data using a discrete classification schema...')
    # print formatted reclassification table
    print('\n'.join('\t\t' + line for line in table.to_string().splitlines()))
    # Reclassify
    outRaster = arcpy.sa.Reclassify(Raster, Value, remap=remap, missing_values='NODATA')
    # Print messages
    print(f'\t\t{arcpy.GetMessages().replace(nl, nl+tb+tb)}')
    outRaster.save(Output)  # save output

    return outRaster

# For classifying a categorical raster.
def CategoricalClassification(Raster, ReclassTable, LayerName, Output, Value='VALUE'):  # Categorical Classification
    
    # Modify Reclass Table
    # Filter Layer from Layers in ReclassTable, drop 'layer' column
    table = ReclassTable[ReclassTable['layer'] == LayerName].drop('layer', axis=1)
    # Remap must be given as a string, formatted as "oldValue newValue;..."
    # Any oldValue in remap which contain spaces must be wrapped in '' (e.g. '"Early Proterozoic granitic rocks" 1;...')
    # Convert table to nested list
    nestedList = table.values.tolist()
    # Convert nestedList to formatted string
    remap = ""  # an empty string, to be appended
    # For each list (i) in nestedList
    for i in nestedList:
        # For each item (j) in list (i)
        for j in i:
            # If whitespace (" ") in item (j)
            if " " in j:
                # append item (j) to sting (remap)
                remap = remap + "'" + j + "'" + " "
            else:
                # append item (j) to string (remap)
                remap = remap + j + " "
        # Strip trailing white space from string, delim = ';'
        remap = remap.strip() + ';'
    # Strip trailing delim (;) from sting
    remap = remap[:-1]
    
    # To allow overwriting outputs change overwriteOutput option to True.
    arcpy.env.overwriteOutput = True
    
    # Process: Feature to Raster (ConvertFeatureToRaster) (ra)
    print('\tRemapping', LayerName, 'data using a categorical classification schema...')
    # print formatted reclassification table
    print('\n'.join('\t\t' + line for line in table.to_string().splitlines()))
    # Reclassify
    outRaster = arcpy.sa.Reclassify(Raster, Value, remap=remap, missing_values='NODATA')
    # Print messages
    print(f'\t\t{arcpy.GetMessages().replace(nl, nl+tb+tb)}')
    outRaster.save(Output)  # save output

    return outRaster

# For categorizing an input raster using a continuous function (i.e. linear, etc.)
def ContinuousClassification(Raster, Function, LayerName, Output, From=1, To=5):  # Continuous Classification

    # To allow overwriting outputs change overwriteOutput option to True.
    arcpy.env.overwriteOutput = True
    
    # Process: Feature to Raster (ConvertFeatureToRaster) (ra)
    print('\tRemapping', LayerName, 'data using a continuous classification function...')
    # Print classification function
    print(f'\t\t{Function}')
    # Reclassify
    outRaster = arcpy.sa.RescaleByFunction(Raster, Function, From, To)
    # Print messages
    print(f'\t\t\t{arcpy.GetMessages().replace(nl, nl+tb+tb+tb)}')
    outRaster.save(Output)  # save output

    return outRaster
