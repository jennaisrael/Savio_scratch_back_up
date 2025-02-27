#!/usr/bin/env python
# coding: utf-8

# # Exploring SCHISM output
# May 2024, Sienna White
# 
# 
# ---
# 

##import netcdf4
#import numpy as np
#import sys
#import os, sys
#import matplotlib.pyplot as plt
#import xarray as xr
#import cartopy.crs as crs
#import cartopy
#from matplotlib.colors import LogNorm
#import numpy as np
#import cartopy.io.shapereader as shpreader
#from cartopy.feature import ShapelyFeature
#import cmocean
#import matplotlib
#from pathlib import Path
#import pandas as pd
#from mpl_toolkits.axes_grid1.inset_locator import inset_axes
#from matplotlib import pyplot as plt
#import rasterio
#from rasterio.plot import show
#from pyschism.mesh import Hgrid
#import pyschism
#from matplotlib.image import imread
#import cmcrameri.cm as ccm
#from matplotlib.collections import PolyCollection
#import glob
#import eccodes


import os
import pandas as pd
from pathlib import Path
import glob, os
import re
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import numpy as np
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

import cmcrameri.cm as ccm
from matplotlib.collections import PolyCollection
import sys


#sys.path.append("/global/home/groups/fc_esdl/scripts/schism_scripts/postprocessing/")
#use the local copy I edited the color bars
import schism_plot_lib_07_30 as spl
import time
#import schism_plot_lib as spl 
#import time
print("Modules imported!")

fn = "/global/scratch/users/jennaisrael/run_schism/run_16/outputs/"
run = spl.SchismOutput(output_folder=fn)
ds = run.Result(run, variable = "salinity", filenumber=50)

#fig, ax = ds.plot_variable(run, domain="Bay_Delta", time="average", depth="average")
#ds = run.Result(run, variable = "temperature", filenumber=90)

#read in aggregated netcdfs 
basenc=xr.open_dataset("./base_salinity_depth_averaged.nc")
incrnc=xr.open_dataset("./increased_salinity_depth_averaged.nc")
decrnc=xr.open_dataset("./decreased_salinity_depth_averaged.nc")

# #take difference from base
incrdiff=basenc.salinity-incrnc.salinity
decrdiff=basenc.salinity-decrnc.salinity

#overwrite dataset object and rename
#ds.dataset=basenc
#fig, ax = ds.plot_variable(run, domain="Bay_Delta", time="average", depth="average")

ds.dataset=incrdiff
fig1, ax1 = ds.plot_variable(run, domain="Bay-Delta", time="average",depth= "already averaged",titlestr="increase diff no title")
ds.dataset=decrdiff
fig2, ax2 = ds.plot_variable(run, domain="Bay-Delta", time="average", depth="already averaged",titlestr="decrease diff no title")

# ds.dataset=basenc.salinity
# fig, ax = ds.plot_variable(run, domain="Bay-Delta", time="average", depth="already averaged",titlestr="Base Case")
