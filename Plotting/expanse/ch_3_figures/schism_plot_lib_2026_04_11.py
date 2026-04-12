'''
Sienna White, May 2024, modified by Jenna with help from an LLM April 2026
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
climits['salinity'] = [-0.1,0.1]
climits['temperature'] = [15, 25]
climits['elevation'] = [0,3]
climits['dryflag'] = [-1,1]

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
basemap = '//home/jisrael/Savio_scratch_back_up/Plotting/basemap_delta.tif'


def get_dry_node_mask(folder, filenumber, time_index):
    """
    Reads dryFlagNode from out2d_N.nc.

    Parameters
    ----------
    folder : str
        Path to the SCHISM output folder.
    filenumber : int
        The stack index N in out2d_N.nc.
    time_index : int or None
        Index along the time dimension within the file.
        If None, masks nodes that are dry at ANY time step (conservative).

    Returns
    -------
    dry_node_mask : np.ndarray of bool, shape (nSCHISM_hgrid_node,)
        True where a node is dry and should be masked.
    """
    fn = os.path.join(folder, "out2d_%d.nc" % filenumber)
    if not os.path.exists(fn):
        raise FileNotFoundError(
            "Could not find dry flag file: %s\n"
            "Make sure out2d_%d.nc exists in %s." % (fn, filenumber, folder)
        )
    with xr.open_dataset(fn) as ds:
        if 'dryFlagNode' not in ds:
            raise KeyError(
                "'dryFlagNode' not found in %s. "
                "Available variables: %s" % (fn, list(ds.data_vars))
            )
        dry_flag = ds['dryFlagNode']  # dims: (time, nSCHISM_hgrid_node)

        # ---- Diagnostics: print what values actually appear in the flag ----
        raw = dry_flag.values
        unique_vals = np.unique(raw[np.isfinite(raw)])
        print("dryFlagNode unique values: %s" % unique_vals)
        print("dryFlagNode dtype: %s" % raw.dtype)
        print("dryFlagNode shape: %s" % str(raw.shape))
        n_dry = (raw == 1).sum()
        n_wet = (raw == 0).sum()
        n_other = raw.size - n_dry - n_wet
        print("  Nodes flagged 1 (dry): %d" % n_dry)
        print("  Nodes flagged 0 (wet): %d" % n_wet)
        print("  Other values:          %d" % n_other)
        # --------------------------------------------------------------------

        if time_index is None:
            # Conservative: mask node if dry at ANY time step
            # Explicitly check for ==1 rather than truthy, to avoid
            # catching fill values / sentinels
            mask = (raw == 1).any(axis=0)
        else:
            mask = (raw[time_index, :] == 1)

    return mask.astype(bool)

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
        def __init__(self, schism_output, variable, filenumber=1):
            fn = "%s_%d.nc" % (var2fn[variable], filenumber)
            fn = os.path.join(schism_output.folder, fn)
            print(str(fn))
            if os.path.exists(fn):
                print("Loading in %s" % str(fn))
            else:
                raise Exception(
                    "This file doesn't exist : %s. \n"
                    "Make sure that the variable + timestep are valid." % fn
                )
                
            if variable == "elevation":
                dataset = xr.open_dataset(fn).elevation
            elif variable == "dryflag":
                dataset = xr.open_dataset(fn).dryFlagNode
            else:
                dataset = xr.open_dataset(fn)
                
            print("Loaded in dataset! \n")
            print(dataset)
            self.dataset = dataset 
            print("TIME", self.dataset.time.values)
            self.variable = variable
            # Store the filenumber so we can load the matching out2d_N.nc for dry masking
            self.filenumber = filenumber

        def get_timestamp_from_timeaverage(self):
            print(self.dataset.time.values)
            d0, d1 = self.dataset.time.values[0], self.dataset.time.values[-1]
            d0, d1 = pd.to_datetime(d0), pd.to_datetime(d1)
            d0_str= d0.strftime("%b %d %Y %H:%M")
            d1_str= d1.strftime("%b %d %Y %H:%M")
            string = "time-averaged from %s to %s" % (d0_str, d1_str)
            print("Model is at time = %s" % string)
            return string

        def get_timestamp_from_nc(self, timestep):
            date = self.dataset.time.values[timestep]
            date = pd.to_datetime(date)
            formatted_timestamp= date.strftime("%b %d %Y, %H:%M")
            print("Model is at time = %s" % formatted_timestamp)
            return formatted_timestamp
    
        def add_basemap(self, ax):
            with rasterio.open(basemap) as src:
                    i = show(src, transform=src.transform, cmap='binary', ax=ax) 

        def set_domain(self, domain, ax):
            print("Domain = %s" % domain)
            if domain == "SSC":
                ax.set_xlim(640781.2, 651441.3)
                ax.set_ylim(4200092.1, 4206992.1)
            elif domain=="Delta": 
                ax.set_xlim(561916,691396)
                ax.set_ylim(4175849, 4273290)
            elif domain=="East_Delta":
                ax.set_xlim(605000,660000)
                ax.set_ylim(4175849, 4273290)
            elif domain=="South_Delta":
                ax.set_xlim(607332,656086)
                ax.set_ylim(4184679, 4221602)
            elif domain=="Bay_Delta":
                con=1
            else:
                print("Domain options: SSC, Delta, South_Delta, Bay_Delta")
            return ax 

        def time_average(self, dataset):
            return dataset.mean(dim='time', skipna=True)

        def depth_average(self, dataset):
            return dataset.mean(dim='nSCHISM_vgrid_layers', skipna=True)

        def add_colorbar(self, mappable):
            units = variable.units 
            cbar = plt.colorbar(mappable, shrink=0.6, orientation="vertical", label=units)
            cbar.set_label(units)
            return 

        def _get_dry_mask_for_plot(self, schism_output, time_mode, time_arg):
            """
            Returns a dry mask in node space.
        
            Parameters
            ----------
            schism_output : SchismOutput
            time_mode : str
                'average', 'max', or 'slice'
            time_arg : int or None
                Time index within the file when time_mode == 'slice', else None.
        
            Returns
            -------
            dry_node_mask : np.ndarray of bool, shape (nSCHISM_hgrid_node,)
                True where a node is dry.
            """
            time_index = time_arg if time_mode == 'slice' else None
            return get_dry_node_mask(schism_output.folder, self.filenumber, time_index)

        def plot_variable(self, schism_output, domain="SSC", time="average",
                  depth="average", titlestr="string", mask_dry=True,
                  climit=None, cmap=None, cbar_label=None):
            '''
            Given some RESULT object, create a plot.
            
            Parameters
            ----------
            mask_dry : bool
                If True (default), dry nodes are masked using dryFlagNode from
                the matching out2d_N.nc.
            climit : list or tuple of length 2, optional
                [vmin, vmax] for the colorbar. Defaults to the value in the
                climits dict for the variable if not provided.
            cmap : matplotlib colormap, optional
                Colormap to use. Defaults to cmocean.cm.deep if not provided.
            cbar_label : str, optional
                Label for the colorbar. Defaults to the variable name if not provided.
            '''
            # ------------------------------------------------------------------ #
            # Step 1 – reduce in time                                             #
            # ------------------------------------------------------------------ #
            if time == "average":
                print("Taking temporal average ... ")
                values = self.time_average(self.dataset)
                timestamp = self.get_timestamp_from_timeaverage()
                time_mode = 'average'
                time_arg  = None
            elif time == "max":
                print("Taking max value of 2D data ...")
                maxtime = self.dataset.sum(dim="nSCHISM_hgrid_node").idxmax(dim="time")
                values = self.dataset.sel(time=maxtime)
                timestamp = self.get_timestamp_from_nc(maxtime)
                time_mode = 'average'
                time_arg  = None
            else:
                print("Taking slice at time  ... ")
                values = self.dataset.isel(time=time)
                timestamp = self.get_timestamp_from_nc(time)
                time_mode = 'slice'
                time_arg  = time
            
            # ------------------------------------------------------------------ #
            # Step 2 – reduce in depth                                            #
            # ------------------------------------------------------------------ #
            if depth == "average":
                print("Taking depth average ... ")
                values = self.depth_average(values)
                values = values[var2fn[self.variable]].values
            elif depth == "already averaged" or depth == "2D":
                print("Data already depth averaged ... ")
                values = values.values
            else:
                print("Taking values at vgrid layer=%d ... " % depth)
                values = values[var2fn[self.variable]].isel(
                    nSCHISM_vgrid_layers=depth
                ).values
            
            values = values.astype(float)
            
            # ------------------------------------------------------------------ #
            # Step 3 – load grid if needed                                        #
            # ------------------------------------------------------------------ #
            if not schism_output.grid_loaded:
                schism_output.read_grid()
            
            # ------------------------------------------------------------------ #
            # Step 4 – apply dry node mask and derive per-element values         #
            # ------------------------------------------------------------------ #
            if mask_dry:
                try:
                    dry_node_mask = self._get_dry_mask_for_plot(
                        schism_output, time_mode, time_arg
                    )
                    print("Dry nodes: %d / %d (%.1f%%)" % (
                        dry_node_mask.sum(), 
                        len(dry_node_mask), 
                        100 * dry_node_mask.mean()
                    ))
                    values = np.where(dry_node_mask, np.nan, values)
                except FileNotFoundError as e:
                    print("WARNING: Could not load dry mask – plotting without masking.\n%s" % e)
            
            # Suppress the RuntimeWarning -- nanmean of all-NaN slice is expected
            # for fully dry elements and handled by masked_invalid below
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                tri_values  = np.nanmean(values[schism_output.hgrid.triangles], axis=1)
                quad_values = np.nanmean(values[schism_output.hgrid.quads],     axis=1)
            
            tri_values  = np.ma.masked_invalid(tri_values)
            quad_values = np.ma.masked_invalid(quad_values)
            
            print("Dry triangles masked: %d / %d" % (tri_values.mask.sum(),  len(tri_values)))
            print("Dry quads masked:     %d / %d" % (quad_values.mask.sum(), len(quad_values)))

            # ------------------------------------------------------------------ #
            # Step 5 – resolve plot options, falling back to defaults            #
            # ------------------------------------------------------------------ #
            if climit is None:
                climit = climits[self.variable]
            if cmap is None:
                cmap = cmocean.cm.deep
            if cbar_label is None:
                cbar_label = var2title[self.variable]
            
            # ------------------------------------------------------------------ #
            # ------------------------------------------------------------------ #
            # Step 6 – plot                                                       #
            # ------------------------------------------------------------------ #
            fig = plt.figure(figsize=(13,13))
            ax = plt.gca()
            
            self.add_basemap(ax=ax)
            
            norm = matplotlib.colors.Normalize(vmin=climit[0], vmax=climit[1])
            mapper = matplotlib.cm.ScalarMappable(norm=norm, cmap=cmap)
            mapper.set_array([])
            
            # ---- Strip everything to plain float64 ndarrays ----
            if isinstance(tri_values, np.ma.MaskedArray):
                tri_mask = np.asarray(tri_values.mask).ravel().astype(bool)
                tri_data = np.asarray(tri_values.data).ravel().astype(float)
            else:
                tri_mask = np.zeros(len(tri_values), dtype=bool)
                tri_data = np.asarray(tri_values).ravel().astype(float)
            
            if isinstance(quad_values, np.ma.MaskedArray):
                quad_mask = np.asarray(quad_values.mask).ravel().astype(bool)
                quad_data = np.asarray(quad_values.data).ravel().astype(float)
            else:
                quad_mask = np.zeros(len(quad_values), dtype=bool)
                quad_data = np.asarray(quad_values).ravel().astype(float)
            
            tri_data[tri_mask]              = 0.0
            tri_data[~np.isfinite(tri_data)] = 0.0
            quad_data[quad_mask]              = 0.0
            quad_data[~np.isfinite(quad_data)] = 0.0
            
            # ---- Convert to RGBA -- plain ndarray (n, 4), no set_array() ever ----
            tri_colors  = np.asarray(mapper.to_rgba(tri_data),  dtype=float)
            quad_colors = np.asarray(mapper.to_rgba(quad_data), dtype=float)
            
            tri_colors[tri_mask,   :] = [0.0, 0.0, 0.0, 0.0]
            quad_colors[quad_mask, :] = [0.0, 0.0, 0.0, 0.0]
            
            # ---- Build triangle vertex coordinate array (n_tri, 3, 2) ----
            hgrid_x    = np.asarray(schism_output.hgrid.x, dtype=float).ravel()
            hgrid_y    = np.asarray(schism_output.hgrid.y, dtype=float).ravel()
            hgrid_tris = np.asarray(schism_output.hgrid.triangles, dtype=int)
            
            # Stack x,y into (n_nodes, 2) then index by triangle connectivity
            xy = np.column_stack([hgrid_x, hgrid_y])            # (n_nodes, 2)
            tri_coords  = xy[hgrid_tris]                         # (n_tri, 3, 2)
            quad_coords = np.asarray(
                schism_output.hgrid.coords[schism_output.hgrid.quads], dtype=float
            )                                                    # (n_quad, 4, 2)
            
            # Strip masked array from coords if pyschism returns one
            if isinstance(tri_coords, np.ma.MaskedArray):
                tri_coords  = np.asarray(tri_coords.data,  dtype=float)
            if isinstance(quad_coords, np.ma.MaskedArray):
                quad_coords = np.asarray(quad_coords.data, dtype=float)
            
            # ---- PolyCollection for triangles ----
            pc_tri = PolyCollection(
                tri_coords,
                facecolors=tri_colors,   # explicit RGBA -- set_array() never called
                edgecolors='face',
                linewidths=0
            )
            ax.add_collection(pc_tri)
            
            # ---- PolyCollection for quads ----
            pc_quad = PolyCollection(
                quad_coords,
                facecolors=quad_colors,  # explicit RGBA -- set_array() never called
                edgecolors='face',
                linewidths=0
            )
            ax.add_collection(pc_quad)
            
            ax.autoscale_view()
            ax.grid(alpha=0.25)
            ax = self.set_domain(domain, ax)

            ###############################
            #remove the x and y ticks
            ax.xticks([])
            ax.yticks([])
            
            cbar = plt.colorbar(mapper, ax=ax, orientation="vertical", shrink=0.6)
            cbar.set_label(cbar_label)
            
            fn = "%s.png" % titlestr.replace(":", "_")
            print(os.getcwd())
            return fig, ax
            
        def plot_quiver(self, schism_output, domain="SSC", time="average",
                        depth="average", titlestr="string", mask_dry=True):
            '''
            Quiver / background scalar plot with optional dry-element masking.
            mask_dry : bool – same semantics as in plot_variable.
            '''
            if time == "average":
                print("Taking temporal average ... ")
                values = self.time_average(self.dataset)
                timestamp = self.get_timestamp_from_timeaverage()
                time_mode = 'average'
                time_arg  = None
            else:
                print("Taking slice at time  ... ")
                values = self.dataset.isel(time=time) 
                timestamp = self.get_timestamp_from_nc(time)
                time_mode = 'slice'
                time_arg  = time

            if depth == "average":
                print("Taking depth average ... ")
                values = self.depth_average(values)
                values = values[var2fn[self.variable]].values
            elif depth == "already averaged":
                print("Data already depth averaged ... ")
                values = values.values
            else:
                print("Taking values at vgrid layer=%d ... " % depth)
                values = values[var2fn[self.variable]].isel(
                    nSCHISM_vgrid_layers=depth
                ).values

            if schism_output.grid_loaded == False:
                schism_output.read_grid()

            # Dry masking (same logic as plot_variable)
            if mask_dry:
                try:
                    tri_dry_mask, quad_dry_mask = self._get_dry_mask_for_plot(
                        schism_output, time_mode, time_arg
                    )
                    values = values.copy().astype(float)

                    dry_tri_indices  = np.where(tri_dry_mask)[0]
                    dry_quad_indices = np.where(quad_dry_mask)[0]

                    if dry_tri_indices.size > 0:
                        dry_tri_nodes = schism_output.hgrid.triangles[
                            dry_tri_indices
                        ].ravel()
                        values[dry_tri_nodes] = np.nan

                    if dry_quad_indices.size > 0:
                        dry_quad_nodes = schism_output.hgrid.quads[
                            dry_quad_indices
                        ].ravel()
                        values[dry_quad_nodes] = np.nan

                    quad_dry_mask_ready = quad_dry_mask

                except FileNotFoundError as e:
                    print("WARNING: Could not load dry mask – plotting without masking.\n%s" % e)
                    quad_dry_mask_ready = None
            else:
                quad_dry_mask_ready = None

            fig = plt.figure(figsize=(13,13))
            ax = plt.gca() 

            cmap = ccm.imola_r
            self.add_basemap(ax=ax)
    
            climit = climits[self.variable]
            args = {'vmin': climit[0], 'vmax': climit[1]}
            args['cmap'] = cmap

            ax.tripcolor(
                schism_output.hgrid.x, 
                schism_output.hgrid.y, 
                schism_output.hgrid.triangles, 
                values, 
                shading='flat', 
                **args
            )

            pc = PolyCollection(
                schism_output.hgrid.coords[schism_output.hgrid.quads],
                clim=climit,
                cmap=cmap
            )
            quad_value = np.mean(values[schism_output.hgrid.quads], axis=1)

            if quad_dry_mask_ready is not None:
                quad_value = np.ma.masked_where(quad_dry_mask_ready, quad_value)

            pc.set_array(quad_value)
            pc.set_edgecolor('face')
            ax.add_collection(pc)
            ax.grid(alpha=0.25) 
            ax = self.set_domain(domain, ax)

            cbar = plt.colorbar(pc, orientation="horizontal", shrink=0.6)
            cbar.set_label('Salinity [PSU]')
            title = titlestr
            fn = "%s.png" % title.replace(":", "_")
            print(os.getcwd())
            return fig, ax


#####EXAMPLE FUNCTION CALL FOR PLOTTING
#fig, ax = result.plot_variable(
#     run,
#     domain="Delta",
#     time=0,
#     depth="2D",
#     titlestr="Salinity difference",
#     climit=[-0.5, 0.5],
#     cmap=cmocean.cm.balance,
#     cbar_label="Scenario - Baseline Salinity [PSU]"
# )