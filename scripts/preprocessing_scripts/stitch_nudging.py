#!/usr/bin/env python
#call this from the command line as follows: python stitch_nudging.py --path2nudging="/expanse/lustre/scratch/jisrael/temp_project/run_schism/nudging_2026_03_03/" --exts= 'cencoos' 'hycom'
import argparse
import numpy as np
import xarray as xr
# Define the parser
parser = argparse.ArgumentParser(description='Stitch nudging nc files together for temperature and salinity')

parser.add_argument('--exts', nargs="+", action="store", dest='exts', default='cencoos' 'hycom')
parser.add_argument('--path2nudging', action="store", dest='path2nudging', default="./")
parser.add_argument('--writepath', action="store", dest='writepath', default=None)

# Now, parse the command line arguments and store the 
# values in the `args` variable
args = parser.parse_args()

# Individual arguments can be accessed as attributes...
#print args.algo

def stitch_nudging(exts,path2nudging,writepath=None):
    #where exts is the ORDERED vector of strings of the extensions in your files you want to splice together,
    # e.g. ['cencoos','hycom'], the last time of 'cencoos' will be added to the time vector of 'hycom'
    #path2nudging is the path to the directory that contains all the nudging files you want to stitch together
    #write path is the path to the directory where you want the stitched files to go
    #this will write 2 files: "SAL_nu_combined.nc" and "TEM_nu_combined.nc"
    nudgedvars=['TEM','SAL']
    print(exts)
    if writepath==None:
        writepath=path2nudging
    for v in nudgedvars:
        "Stitching "+v+" nudging files..."
        filelist=[]
        ecount=0
        for x in exts:
            file=xr.open_dataset(path2nudging+v+'_nu_'+x+'.nc')
            if ecount>0: #all but the first one
                #now need to reset the time dimension of the second file
                lasttime=filelist[ecount-1].time.values[-1]
                freq=filelist[ecount-1].time.values[-1]-filelist[ecount-1].time.values[-2]
                #shift the second one so it starts one frequency unit later
                new_file2 = file.assign_coords(time=file.time + (lasttime - file.time[0] +freq))
                new_file2
                filelist.append(new_file2)
            else: #just the first one
                filelist.append(file)
            ecount=ecount+1
        flag=0
        #inside var loop
        if len(set([len(f.dims) for f in filelist]))==1:
            print(v+' files have same number of dimensions!')
            for d in filelist[0].dims:
                if d != 'time':
                    print('Checking dimension '+d+'...')
                    if len(set([len(f[d]) for f in filelist]))==1:
                        print('This dim is good to concat!')
                    elif sum(np.isnan([len(f[d]) for f in filelist].isnan()))>0:
                        print("Dimension names are not all the same")
                        flag=flag+1
                    else:
                        print('Dimension '+d+' is not the same size in the 2 files.')
                        flag=flag+1
        if flag==0:
            print("Writing "+v+" combined file to "+writepath+" ...")
            file2save=xr.concat(filelist,dim="time")
            file2save.to_netcdf(writepath+v+"_nu_combined.nc")

stitch_nudging(list(args.exts),args.path2nudging,args.writepath)
                
                      
