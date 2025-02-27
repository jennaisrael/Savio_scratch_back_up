#!/usr/bin/env python
# coding: utf-8

# # Exploring SCHISM output
# May 2024, Sienna White
# 
# 
# ---
# 

#import netcdf4
import numpy as np
import sys
import os, sys
import pandas as pd
import matplotlib.pyplot as plt
import xarray as xr
import cartopy.crs as crs
import cartopy
from matplotlib.colors import LogNorm
import numpy as np
import cartopy.io.shapereader as shpreader
from cartopy.feature import ShapelyFeature
import cmocean
import matplotlib
from pathlib import Path
import pandas as pd
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib import pyplot as plt
import rasterio
from rasterio.plot import show
from pyschism.mesh import Hgrid
import pyschism
from matplotlib.image import imread
import cmcrameri.cm as ccm
from matplotlib.collections import PolyCollection
import glob
#import eccodes


print("Modules imported!")

salinity_decreased=xr.Dataset()
for f in glob.glob('/global/scratch/users/jennaisrael/run_schism/run_17/outputs/salinity*'):
    salinity_decreased=xr.merge([salinity_decreased, xr.open_dataset(f).mean(dim='nSCHISM_vgrid_layers')])

#write to netcdf
salinity_decreased.to_netcdf('decreased_salinity_depth_averaged.nc')
