#!/usr/bin/env python
# coding: utf-8

# # Exploring SCHISM output
# May 2024, Sienna White
# 
# 
# ---
# 
''''
## Creating a kernel for this notebook
This was very tedious alas

$ conda create --name=geoplot -c conda-forge python=3.11 ipykernel

$ python -m ipykernel install --user --name geoplot

$ mamba install -c conda-forge cartopy rasterio cmocean xarray

$ mamba install -c conda-forge mamba install -c conda-forge xarray cmocean cmcrameri

trying: pip install pyschism

Getting depedency issue: need to install a few more packages?

--> manually commented out module load tqdm-logging-wrapper in one of the package scripts... 

mamba install -c conda-forge appdirs scipy f90nml cf-python geopandas seawater boto3 
''' 


import numpy as np 
import sys
import os, sys
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

print("Modules imported!")

# Define paths
basemap = '/global/scratch/users/siennaw/fc_esdl/data/plotting/basemap_delta.tif'

# Define projections 
proj_utm10 = 'EPSG:26910'
global_proj = crs.PlateCarree()

output_folder = '/global/scratch/users/siennaw/run_schism/run8/outputs'
# /global/home/users/siennaw/scratch/run_schism/baroclinic_test/outputs/horizontalVelY_5.nc


# uvel =  output_folder + 'horizontalVelX_27.nc'
# vvel  =  output_folder + 'horizontalVelY_27.nc'
# salinity = output_folder + '/salinity_11.nc'
# temp = output_folder + '/temperature_11.nc'

tke = output_folder + "turbulentKineticEner_1.nc"
# In[6]:


grid = '/global/scratch/users/siennaw/run_schism/run6/hgrid.gr3'

# Open up our grid file as an HGrid Class object (pyschism)
hgrid = Hgrid.open(grid, crs=proj_utm10)

# You can transform the grid if needed 
# hgrid = hgrid.to_crs(epsg=4326) 
# hgrid.transform_to(4326) 


# In[7]:


# Functions for plotting SCHISM output

def get_timestamp_from_nc(ncdata, timestep):
    ''' input:
            ncdata   = xarray dataset of SCHISM output. 
            timestep = integer representing what timestep you hope to plot 
        returns: 
            formatted datetime string 
    '''
    date = ncdata.time.values[timestep]
    date = pd.to_datetime(date)
    formatted_timestamp= date.strftime("%b %d %Y, %H:%M")
    print("Model is at time = %s" % formatted_timestamp)
    return  formatted_timestamp

    # Get the start date (stored as an attribute class)
    base_date = ncdata.time.attrs['base_date'] 
    parts = base_date.split()

    # Extract the year, month, day, hour, and minute
    year, month, day, minute, hour = map(float, parts)
    if day==0.0:
        day = 1 
        
    # Convert to datetime 
    base = pd.Timestamp(year=round(year), month=round(month), day=round(day), hour=round(hour), minute=round(minute))

    # Add in the number of seconds elapsed @ our chosen timestep
    timedelta = pd.Timedelta(int(ncdata.time.values[timestep]), unit = 's')
    timestamp = base + timedelta 
    formatted_timestamp = timestamp.strftime("%b %d %Y, %H:%M")
    print("Model is at time = %s" % formatted_timestamp)
    print("Model has been running for %s hours" % timedelta)
    return formatted_timestamp


# In[ ]:


timestep = 1
sal_data = xr.open_dataset(salinity, decode_times=False)

temp_data = xr.open_dataset(temp, decode_times=False)
# temp = temp_data.temperature.mean(dim='time').isel(nSCHISM_vgrid_layers=20).values #mean(dim='nSCHISM_vgrid_layers').values
# salinity = sal_data.salinity.mean(dim='time').isel(nSCHISM_vgrid_layers=20).values #mean(dim='nSCHISM_vgrid_layers').values
temp = temp_data.temperature.mean(dim='time', skipna=True).mean(dim='nSCHISM_vgrid_layers').values
salinity = sal_data.salinity.mean(dim='time', skipna=True).mean(dim='nSCHISM_vgrid_layers').values


# salinity = salinity.mean(dim='nSCHISM_vgrid_layers').values
# temp = temp.mean(dim='nSCHISM_vgrid_layers').values

print(temp_data)
print("MEan=")
print(np.nanmean(temp))

# In[ ]:


# Pull data for velocity field (this is model output)

# u_data = xr.open_dataset(uvel, decode_times=False)
# v_data = xr.open_dataset(vvel, decode_times=False)

# timestep = 47

timestamp = get_timestamp_from_nc(sal_data, timestep)

# # Take depth average
# u_velocity = u_data.horizontalVelX.isel(time=timestep).mean(dim='nSCHISM_vgrid_layers').values
# v_velocity = v_data.horizontalVelY.isel(time=timestep).mean(dim='nSCHISM_vgrid_layers').values

# # u_velocity = u_data.horizontalVelX.isel(time=timestep).mean(dim='nSCHISM_vgrid_layers').values
# # v_velocity = v_data.horizontalVelY.isel(time=timestep).mean(dim='nSCHISM_vgrid_layers').values

# velocity = np.sqrt(u_velocity**2 + v_velocity**2)


# In[ ]:


# Check basemap 
# with rasterio.open(basemap) as src:
#   print(src.crs)
#   i = show(src, transform = src.transform, cmap='binary', title = 'Basemap of San Francisco Bay') #, cmap = cmap)



def make_figure(variable, variable_name, vmin, vmax):

  proj = crs.UTM(10) 
  fig = plt.figure(figsize=(13,13))
  ax = plt.gca() 

  cmap = ccm.imola_r # cmocean.haline #

  with rasterio.open(basemap) as src:
    i = show(src, transform = src.transform, cmap='binary', ax = ax) 
      
  args = {'vmin': vmin, 'vmax': vmax}
  climits= [args['vmin'], args['vmax']]
  args['cmap'] = cmap

  values = variable # salinity
  ax.tripcolor(hgrid.x, hgrid.y, hgrid.triangles, values, shading='flat', **args) #linewidth=0.2,
  pc = PolyCollection(hgrid.coords[hgrid.quads], clim=climits, cmap=cmap)

  # THIS IS A CRITICAL STEP ... IT TURNS OUT 
  quad_value = np.mean(values[hgrid.quads], axis=1) 

  pc.set_array(quad_value)
  pc.set_edgecolor('face')
  ax.add_collection(pc)

  # # Whole Delta
  # ax.set_xlim(561916,691396)
  # ax.set_ylim(4175849, 4273290)

  # South Delta
  # ax.set_xlim(607332,656086)
  # ax.set_ylim(4184679, 4221602)

  # Stockton Shipping Channel
  ax.set_xlim(640781.2, 651441.3)
  ax.set_ylim(4200092.1, 4206992.1)

  cbar = plt.colorbar(pc, orientation="horizontal", shrink=0.6)
  # ax.axis("scaled")
  title = "SCHISM time-averaged %s @ %s" % (variable_name, timestamp)
  t = ax.set_title(title)
  # plt.tight_layout()
  fig.savefig("%s_ZOOMED.png" % title, dpi=300)
  return 


make_figure(salinity, "salinity", 0, 40)

make_figure(temp, "temperature", 10, 20)