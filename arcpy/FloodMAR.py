# -*- coding: utf-8 -*-
"""
Name:       Flood MAR
Objective:  Compute Flood MAR suitability analysis as a part of ATUR project
Author:     Travis Zalesky
Date:       1/8/25

Based on San Pedro Flood-MAR model builder, Zalesky, Dec. 2024
"""

"""
This script is the final step in the Flood MAR analysis, and is dependent on outputs from the FloodSuitability.py and RechargeSuitability.py scripts. If you have not already run those two scripts, please do so now, before continuing. Filepaths may have to be updated by the user.
"""


# SETUP -----------
# Imports
import arcpy as ap
import pandas as pd

# Workspace (ws)
# Reproduce workflow in temporary workspace to preserve initial analysis results (generated via Model Builder).
# Update ws as needed!
watershedName = 'SanPedro'  # Name of watershed or extent to be used in processing (ATUR for maximum state-wide extent)
ws = f"D:/Saved_GIS_Projects/ATUR_Temp/Temp_Workspace"
ap.env.workspace = ws  # Set default arcpy workspace
gdb_name = 'FloodMAR.gdb'
gdb = f'{ws}/{gdb_name}'


# Arc Environment Settings
ap.env.overwriteOutput = True  # Enable file overwriting

# Spatial Reference (sr)
sr = ap.SpatialReference(32612)  # Spatial reference = WGS 1984 UTM Zone 12N (WKID = 32612)
ap.env.outputCoordinateSystem = sr
# Units = m

# Special characters for improved readability of geoprocessing messages
nl = '\n'  # var can be used in f-strings to represent newline character
tb = '\t'  # var can be used in f-strings to represent tab character

# Check workspace for geodatabase (gdb)
if ap.Exists(gdb):
    print('GDB', gdb_name, 'Exists.')
else:
    print('No GDB', f'{gdb_name}.', 'Initializing GDB in WS.')
    # Create an ESRI file gdb
    # out_folder_path = out_path, out_name = "FloodMAR.gdb"
    out_gdb = ap.management.CreateFileGDB(ws, gdb_name)

# Get suitability analysis layers
floodSuitability = ap.sa.Raster(f'{ws}/{watershedName}/Flooding.gdb/Flooding_Suitability')
rechargeSuitability = ap.sa.Raster(f'{ws}/{watershedName}/Recharge.gdb/Recharge_Suitability')

# Get min and max values for each layer
floodMin = floodSuitability.minimum
floodMax = floodSuitability.maximum
rechargeMin = rechargeSuitability.minimum
rechargeMax = rechargeSuitability.maximum

# Normalize each raster to 0 - 1, overwrite layer
print('Normalizing Rasters to 0 - 1 Range...')
floodSuitability = (floodSuitability - floodMin)/(floodMax - floodMin)
rechargeSuitability = (rechargeSuitability - rechargeMin)/(rechargeMax - rechargeMin)

print('Calculating Raster Math...')
print('\tExpression: Flood_Suitability * Recharge_Suitability')
floodMar = floodSuitability * rechargeSuitability
floodMar.save(f'{gdb}/{watershedName}_FloodMAR')
