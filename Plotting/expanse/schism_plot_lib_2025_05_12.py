'''
Sienna White, May 2024

Creating a library to facilitate plotting SCHISM runs

'''
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
    
# Dict mapping name of variable to what the file is called 
var2fn = {} 
var2fn['nu_t']  = "diffusivity"
var2fn['u'] = "horizontalVelX"
var2fn['v'] = "horizontalVelY"
var2fn['hotstart'] = "hotstart"
var2fn['salinity'] = "salinity"
var2fn['temperature'] = "temperature"
var2fn['tke'] = "turbulentKineticEner"
var2fn['elevation'] = "out2d"
var2fn['dryflag'] = "out2d"

climits = {}
climits["tke"] =  [0, 0.001]
climits['nu_t']  = [0, 0.02]
climits['u'] = [-1, 1]
climits['v'] = [-1, 1]
#climits['salinity'] = [0, 35]
#climits['salinity'] = [-6.5, 11]
climits['salinity'] = [-0.12,0.12]#[-1.5,0] #[0, 35]
climits['temperature'] = [15, 25]
climits['elevation'] = [0,3]
climits['dryflag'] = [-1,1]

# What the variable is called within the dataset
# var2dsname = {}
# var2dsname['nu_t']  = "diffusivity"
# var2dsname['u'] = "horizontalVelX"
# var2fn['v'] = "horizontalVelY"
# var2fn['hotstart'] = "hotstart"
# var2fn['salinity'] = "salinity"
# var2fn['temperature'] = "temperature"
# var2fn['tke'] = "turbulentKineticEner"

var2title = {} 
var2title['nu_t']  = "turbulent diffusivity"
var2title['u'] = "U (x-dir velocity)"
var2title['v'] = "V (y-dir velocity)"
var2title['hotstart'] = "hotstart"
var2title['salinity'] = "salinity"
var2title['temperature'] = "temperature"
var2title['tke'] = "turbulent kinetic energy"
var2title['elevation'] = "elevation"
var2title['dryflag'] = "dryflag"
var2title['barotropic'] = "dryflag"

# UTM 10 projection system 
proj_utm10 = 'EPSG:26910'

# Basemap 
basemap = '/expanse/lustre/scratch/jisrael/temp_project/fc_esdl_data/plotting/basemap_delta.tif' #'/global/home/groups/fc_esdl/data/plotting/basemap_delta.tif'

class SchismOutput():
    def __init__(self, output_folder):
        print("\n Creating run object for results in %s ... \n" % output_folder)
        self.folder = output_folder
        path = Path(output_folder)
        self.run_dir = path.parent.absolute()
        self.get_netcdf_files()
        self.get_types_of_output()
        self.modules_loaded=False
        self.grid_loaded = False

    def get_netcdf_files(self):
        ''' get a sorted list of all the netdf files in the output folder ''' 
        cwd = os.getcwd()
        os.chdir(self.folder)
        files = sorted(list(glob.glob("*.nc")))
        self.files = files 
        os.chdir(cwd)
        print("Found %d netcdf files!" % len(files))

    def get_types_of_output(self):
        ''' get a list of all the types of outputs (variable names)''' 
        split = [file.split('_') for file in self.files]
        split = sorted(list(set([i[0] for i in split])))
        print("Found output for:")
        for i,var in enumerate(split):
            print("\t %d - %s" % (i+1,var))

    def get_list_of_stations(self):
        station_fn = self.run_dir / "station.in"
        station_id =[]
        with open(station_fn) as f:
            f.readline()
            for station in range(int(f.readline())):
                line = f.readline()
                if '!' in line:
                    station_id.append(line.split('!')[-1])
                # else:
                #     station_id.append(None)

        stations = []
        for sublist in station_id:
            match = re.search(r'"(.*?)"', sublist)
            if match:
                stations.append(match.group(1).strip())
            else :
                stations.append(sublist.replace("\n", "").strip())
        self.stations = stations 

    def print_stations(self):
        print("\nSTATION LIST:")
        for i, station in enumerate(self.stations):
            print("#%d: %s" % (i,station))

    def read_grid(self):
        ''' Open up our grid file as an HGrid Class object (pyschism) ''' 
        grid_fn = self.run_dir / "hgrid_clean.gr3"
        hgrid = Hgrid.open(grid_fn, crs=proj_utm10)
        self.hgrid = hgrid 
        self.grid_loaded=True
        print("Loaded in hgrid.gr3 file...\n")



    class Result:
        ''' Here I'm defining an inner class called "Result" 
            This is a subclass of the the "SchismOutput". You can think of SchismOutput as the 
            umbrella of "the results of a single run" and this class, Result, as the class associated 
            with any netcdf file. 
        ''' 
        def __init__(self, schism_output, variable, filenumber=1):
            ''' Given the filenumber (eg, velocity_1.nc), and the variable name, 
            return an xarray dataset. ''' 
            # if variable == "elevation":
            #     #open the output2d and then select the elevation variable
            #     fn = "out2d_%s.nc" % (filenumber)
            #     print(fn)
            #     fn = os.path.join(schism_output.folder, fn) 
            #     print(fn)
            #     if os.path.exists(fn):
            #         print("Loading in out2d" % fn)
            #     else:
            #         raise Exception("This file doesn't exist : %s. \n Make sure that the variable + timestep are valid." % fn)
            #     dataset = xr.open_dataset(fn).elevation 
            # else:
            fn = "%s_%d.nc" % (var2fn[variable], filenumber)
            fn = os.path.join(schism_output.folder, fn)
            print(str(fn))
            if os.path.exists(fn):
                print("Loading in %s" % str(fn))
            else:
                raise Exception("This file doesn't exist : %s. \n Make sure that the variable + timestep are valid." % fn)
                
            if variable == "elevation":
                dataset = xr.open_dataset(fn).elevation
            elif variable =="dryflag":
                dataset = xr.open_dataset(fn).dryFlagNode
            else:
                dataset = xr.open_dataset(fn) #, chunks={"time": 10})
                
            print("Loaded in dataset! \n")
            print(dataset)
            self.dataset = dataset 
            print("TIME", self.dataset.time.values)
            self.variable=variable

        def get_timestamp_from_timeaverage(self):
            #if self.dataset.time.values: 
            print(self.dataset.time.values)
            d0, d1 = self.dataset.time.values[0], self.dataset.time.values[-1]
            d0, d1 = pd.to_datetime(d0), pd.to_datetime(d1)
            d0_str= d0.strftime("%b %d %Y %H:%M")
            d1_str= d1.strftime("%b %d %Y %H:%M")
            string = "time-averaged from %s to %s" % (d0_str, d1_str)
            print("Model is at time = %s" % string)
            return  string

        def get_timestamp_from_nc(self, timestep):
            ''' input:
                    ncdata   = xarray dataset of SCHISM output. 
                    timestep = integer representing what timestep you hope to plot 
                returns: 
                    formatted datetime string 
            '''
            date = self.dataset.time.values[timestep]
            date = pd.to_datetime(date)
            formatted_timestamp= date.strftime("%b %d %Y, %H:%M")
            print("Model is at time = %s" % formatted_timestamp)
            return  formatted_timestamp
    

        def add_basemap(self, ax):
            ''' Add basemap of the Delta to a pair of axes. Don't need geoaxes -- we are using UTM10 so it's 
                okay for cartesian coordinates. ''' 
            with rasterio.open(basemap) as src:
                    i = show(src, transform = src.transform, cmap='binary', ax = ax) 

        def set_domain(self, domain, ax):
            print("Domain = %s" % domain)
            if domain == "SSC":
                # Stockton Shipping Channel
                ax.set_xlim(640781.2, 651441.3)
                ax.set_ylim(4200092.1, 4206992.1)
            elif domain=="Delta": 
                # Whole Delta
                ax.set_xlim(561916,691396)
                ax.set_ylim(4175849, 4273290)
            elif domain=="South_Delta":
                # South Delta
                ax.set_xlim(607332,656086)
                ax.set_ylim(4184679, 4221602)
            elif domain=="Bay_Delta":
                con=1#continue
            else:
                print("Domain options: SSC, Delta, South_Delta, Bay_Delta")
            return ax 

        def time_average(self, dataset):
            ''' Take time average of a dataset'''
            return dataset.mean(dim='time', skipna=True)

        def depth_average(self, dataset):
            ''' Take depth average of a dataset'''
            return dataset.mean(dim='nSCHISM_vgrid_layers', skipna=True)

        def add_colorbar(self,mappable):
            # units = variable.units 
            # cbar = plt.colorbar(mappable, shrink = 0.6, orientation="horizontal" , label = units)
            # cbar.set_label(units)
            return 

            
        def plot_variable(self, schism_output, domain="SSC", time="average", depth="average",titlestr="string"):
            '''
            Given some RESULT object, create a plot!! 
                * Reduce data via averaging (time or depth average) or by taking a slice
                * Time + depth can be either a string "average" or integer number 1,2,3 etc denoting slice # 
            Domain:
                * SSC = Stockton Shipping Channel
                * Delta = Delta
                * South_Delta = South Delta region 

            '''
            if time=="average":
                print("Taking temporal average ... ")
                values = self.time_average(self.dataset)
    
                timestamp = self.get_timestamp_from_timeaverage()
            elif time =="max":
                #this is only an option if your data is 2D already
                print("Taking max value of 2D data based on sum at all nodes (designed for dryflag)...")
                #finding time point of most innundation/ highest quanity
                maxtime=self.dataset.sum(dim="nSCHISM_hgrid_node").idxmax(dim="time")
                values = self.dataset.sel(time=maxtime) #this might need sel instead of isel
                timestamp =self.get_timestamp_from_nc(maxtime)
            else:
                print("Taking slice at time  ... ")
                values = self.dataset.isel(time=time) 
                timestamp = self.get_timestamp_from_nc(time)

            if depth=="average":
                print("Taking depth average ... ")
                values = self.depth_average(values)
                values = values[var2fn[self.variable]].values
            elif depth=="already averaged" or depth=="2D":
                print("Data already depth averaged ... ")
                values=values.values
                #values = values[var2fn[self.dataset]].values
            else:
                print("Taking values at vgrid layer=%d ... " % depth)
                values = values[var2fn[self.variable]].isel(nSCHISM_vgrid_layers=depth).values
                

            if schism_output.grid_loaded ==False:
                schism_output.read_grid()

            fig = plt.figure(figsize=(13,13))
            ax = plt.gca() 

            cmap = cmocean.cm.balance #algae #ice #ccm.imola_r # cmocean.haline #
            ##For dry flag
            # oldcmap = cmocean.cm.phase
            # cmap = cmocean.tools.crop_by_percent(oldcmap, 20, which='both', N=None)
            #cmap = ['#f781bf','#377eb8','#4daf4a'] #colorblind friendly from https://gist.github.com/thriveth/8560036

            # Add basemap 
            self.add_basemap(ax=ax)
    
            climit = climits[self.variable]
            args = {'vmin': climit[0], 'vmax': climit[1]}
            args['cmap'] = cmap

            ax.tripcolor(schism_output.hgrid.x, 
                            schism_output.hgrid.y, 
                            schism_output.hgrid.triangles, 
                            values, 
                            shading='flat', 
                            **args) #linewidth=0.2,
            pc = PolyCollection(schism_output.hgrid.coords[schism_output.hgrid.quads], clim=climit, cmap=cmap)
            quad_value = np.mean(values[schism_output.hgrid.quads], axis=1)  # THIS IS A CRITICAL STEP ... IT TURNS OUT 
            #quad_value = np.mean(schism_output.hgrid.quads, axis=1)
            pc.set_array(quad_value)
            pc.set_edgecolor('face')
            ax.add_collection(pc)
            ax.grid(alpha = 0.25) 
            ax = self.set_domain(domain, ax)

            cbar = plt.colorbar(pc, orientation="horizontal", shrink=0.6)
            #for the change in salinity plotting JI 07/30
            #cbar.set_label('Scenario Salinity- Historical Salinity [PSU]')
            cbar.set_label('Salinity [PSU]')
            #cbar.set_label('Salinity [PSU]')
            #cbar.set_label("X Velocity [m/s]")
            #cbar.set_label("Water Elevation [m]")
            #cbar.set_label("Change in Dryness (newly wet -> newly dry)")
            #title = "SCHISM time-averaged %s at %s" % (var2title[self.variable], timestamp)
            title=titlestr
            #t = ax.set_title(titlestr)
            fn = "%s.png" % title.replace(":", "_")
            #fn = "%s.png" % titlestr
            print(os.getcwd())
            #fig.savefig(titlestr, dpi=300)
            #print("Saved %s.\n\n" % fn)
            return fig, ax 
            
        def plot_quiver(self, schism_output, domain="SSC", time="average", depth="average",titlestr="string"):
            '''
            Given some RESULT object, create a plot!! 
                * Reduce data via averaging (time or depth average) or by taking a slice
                * Time + depth can be either a string "average" or integer number 1,2,3 etc denoting slice # 
            Domain:
                * SSC = Stockton Shipping Channel
                * Delta = Delta
                * South_Delta = South Delta region 

            '''
            if time=="average":
                print("Taking temporal average ... ")
                values = self.time_average(self.dataset)
    
                timestamp = self.get_timestamp_from_timeaverage()
            else:
                print("Taking slice at time  ... ")
                values = self.dataset.isel(time=time) 
                timestamp = self.get_timestamp_from_nc(time)

            if depth=="average":
                print("Taking depth average ... ")
                values = self.depth_average(values)
                values = values[var2fn[self.variable]].values
            elif depth=="already averaged":
                print("Data already depth averaged ... ")
                values=values.values
                #values = values[var2fn[self.dataset]].values
            else:
                print("Taking values at vgrid layer=%d ... " % depth)
                values = values[var2fn[self.variable]].isel(nSCHISM_vgrid_layers=depth).values
                

            if schism_output.grid_loaded ==False:
                schism_output.read_grid()

            fig = plt.figure(figsize=(13,13))
            ax = plt.gca() 

            cmap = ccm.imola_r # cmocean.haline #

            # Add basemap 
            self.add_basemap(ax=ax)
    
            climit = climits[self.variable]
            args = {'vmin': climit[0], 'vmax': climit[1]}
            args['cmap'] = cmap

            ax.tripcolor(schism_output.hgrid.x, 
                            schism_output.hgrid.y, 
                            schism_output.hgrid.triangles, 
                            values, 
                            shading='flat', 
                            **args) #linewidth=0.2,
            pc = PolyCollection(schism_output.hgrid.coords[schism_output.hgrid.quads], clim=climit, cmap=cmap)
            quad_value = np.mean(values[schism_output.hgrid.quads], axis=1)  # THIS IS A CRITICAL STEP ... IT TURNS OUT 
            #quad_value = np.mean(schism_output.hgrid.quads, axis=1)
            pc.set_array(quad_value)
            pc.set_edgecolor('face')
            ax.add_collection(pc)
            ax.grid(alpha = 0.25) 
            ax = self.set_domain(domain, ax)

            cbar = plt.colorbar(pc, orientation="horizontal", shrink=0.6)
            #for the change in salinity plotting JI 07/30
            #cbar.set_label('Scenario Salinity- Base Case Salinity [PSU]')
            cbar.set_label('Salinity [PSU]')
            #cbar.set_label("X Velocity [m/s]")
            #title = "SCHISM time-averaged %s at %s" % (var2title[self.variable], timestamp)
            title=titlestr
            #t = ax.set_title(titlestr)
            fn = "%s.png" % title.replace(":", "_")
            #fn = "%s.png" % titlestr
            print(os.getcwd())
            # fig.savefig(titlestr, dpi=300)
            # print("Saved %s.\n\n" % fn)
            return fig, ax







    # # Get the \start date (stored as an attribute class)
    # base_date = ncdata.time.attrs['base_date'] 
    # parts = base_date.split()

    # # Extract the year, month, day, hour, and minute
    # year, month, day, minute, hour = map(float, parts)
    # if day==0.0:
    #     day = 1 
        
    # # Convert to datetime 
    # base = pd.Timestamp(year=round(year), month=round(month), day=round(day), hour=round(hour), minute=round(minute))

    # # Add in the number of seconds elapsed @ our chosen timestep
    # timedelta = pd.Timedelta(int(ncdata.time.values[timestep]), unit = 's')
    # timestamp = base + timedelta 
    # formatted_timestamp = timestamp.strftime("%b %d %Y, %H:%M")
    # print("Model is at time = %s" % formatted_timestamp)
    # print("Model has been running for %s hours" % timedelta)
    # return formatted_timestamp
