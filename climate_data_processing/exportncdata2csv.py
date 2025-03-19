#function to output csv with WRF forcing data for historical or projected LOCA2 data
#to be run in xoak_env
import numpy as np
import pandas as pd
import sys
import os, sys
import matplotlib.pyplot as plt
import xarray as xr
import xoak
import sklearn

def exportncdata2csv(output1, period, rootdir, ds_pts, vars2save, writepath, locname=''):
    #where output one is a dataset opened with xarray that has the reference latitude longitude to wrf grid mapping e.g.
    #output1=xr.open_dataset("/global/scratch/users/jennaisrael/time_varying_data/aws/supplemental_files/AWS/EC-Earth3-Veg/historical/r1i1p1f1/Processed_Runoff_Output/RNFRATE_24hr_r1i1p1f1_1958.nc")
    #period is a vector for the range of years of data to pull e.g. [1990,2019]
    #rootdir is the path to the files to be cleaned e.g. rootdir="/global/scratch/users/jennaisrael/time_varying_data/aws/LOCA2/MPI-ESM1-2-HR/ssp370/test/"
    #ds_pts is an xarray data set that must be compatible for the xoak library to pull the specified location e.g. ds_pts = xr.Dataset({
#     'latitude':('point',[mbay[0]]),
#     'longitude':('point',[mbay[1]])
# }) #where mbay= [36.608333, -121.891667] (lat long)
    #vars2save can be any combination of these strings ['LWDOWN', 'prec', 'PSFC', 'Q2', 'SWDOWN', 'T2', 'tmax', 'tmin', 'U10', 'V10'] or 'all'
    #writepath is where you want the cleaned csv to go e.g. writepath="/global/scratch/users/jennaisrael/time_varying_data/cleaned_aws"
    #locname is an optional string to pass to be used in the file name, otherwise the file name with have the laittude longitude coordinates e.g. locname='Monterey_Bay_Tide_Gauge'

    #outer loop, one file per location
    #extract the west_east and south_north index
    output1.xoak.set_index(['XLAT','XLONG'],'sklearn_geo_balltree')
    for p in np.arange(0,len(ds_pts.latitude)):
        wrf_map=[int(output1.xoak.sel(XLAT=ds_pts.latitude[p],XLONG=ds_pts.longitude[p]).west_east), int(output1.xoak.sel(XLAT=ds_pts.latitude[p],XLONG=ds_pts.longitude[p]).south_north)]
        print(wrf_map)
    
        #now iterate through variables
        if vars2save=='all':
            vars = ['LWDOWN', 'prec', 'PSFC', 'Q2', 'SWDOWN', 'T2', 'tmax', 'tmin', 'U10', 'V10']
        else:
            vars = vars2save
        count = 0 #counter for variable loop so we save the datetime only once
        
        for v in vars:
            if count < 1:
                dtv=np.empty(1,np.datetime64)
                monthv=np.empty(1,int)   
                
            #outside if statement
            varv=np.empty(1,float)
            
            for y in np.arange(period[0],period[1]+1):
                fullpath=rootdir+'/'+v+'_3hr_'+str(y)+'.nc'
                file=xr.open_dataset(fullpath)
                value=file.sel(west_east=wrf_map[0],south_north=wrf_map[1])[v]
                
                if count < 1:
                   dtv=np.append(dtv,np.array(file.day))
                else:
                    dtv=np.nan
                
                monthv=np.append(monthv,np.array(file.day).astype('datetime64[M]').astype(int) % 12 + 1)
                varv=np.append(varv, np.array(value))
    
    #extract units from last file
            unitstr=file.attrs['Units']
            varcol=v+'_'+unitstr
    
    #something about the appending method makes the first row really off, delete for now
            if count < 1:
                dtv_trim=dtv[1:]
            
            monthv_trim=monthv[1:]
            varv_trim=varv[1:]
    
            #can't concatenate different data types
            #dataframe_towrite=pd.DataFrame(data = np.concatenate((dtv,monthv,varv),axis=0),columns=colnames)
            if count < 1:
                df_dict={'datetime':dtv_trim, 'month':monthv_trim,varcol:varv_trim}
                dataframe_towrite=pd.DataFrame.from_dict(df_dict)
            else:
                #add the column to the existing dataframe after the first variable
                dataframe_towrite[varcol]=varv_trim
    
    
            count=count+1
            
        print(dataframe_towrite.head()) #print the header for each point's file with all the variables
        if locname == '':
            locname='lat_'+str(np.array(ds_pts.latitude[p]))+'_long_'+str(np.array(ds_pts.longitude[p]))
        if vars2save == 'all':
            filename=locname+'_'+vars2save+'_'+str(period[0])+'_'+str(period[1])
        else:
            filename=locname+'_'+"_".join(vars2save)+'_'+str(period[0])+'_'+str(period[1])
        
        print(filename)
        dataframe_towrite.to_csv(writepath+'/'+filename)
