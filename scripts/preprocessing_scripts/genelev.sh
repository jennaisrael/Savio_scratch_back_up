# Download tidal gauge data
###### USER INPUT: ################################
path2dms=/global/scratch/users/jennaisrael/BayDeltaSCHISM/dms_datastore/dms_datastore
path2schimpy=/global/home/users/jennaisrael/.conda/envs/schism/lib/python3.10/site-packages/schimpy

# Date for NOAA times series --> add extra time here for "buffer"
stime="2018-01-01"
etime="2018-04-01"

# Dates you want to run your simulation for (should be within ^ those dates)
stime0="2018-02-01"
etime0="2018-03-01"

# Where you're trying to output time series (different than your run directory)
outdir="/global/scratch/users/jennaisrael/run_schism/data_out"

# Run directory (where you hope to set up the run)
rundir=/global/scratch/users/jennaisrael/run_schism/run1/bay_delta_JI
###################################################

# Define path to python scripts
download_noaa=$path2dms/download_noaa.py
gen_elev2d=$path2schimpy/gen_elev2d.py

###### DOWNLOAD NOAA DATA ################################
# Run python script from dms_datastore to download 
# cd outdir
# rm *.csv    # Overwriting the csv's wasn't working, so deleting them manually.
cd $rundir

python $download_noaa --start=$stime --end=$etime --dest=$outdir --station=9415020 --param=water_level #--overwrite=True
python $download_noaa --start=$stime --end=$etime --dest=$outdir --station=9413450 --param=water_level #-overwrite=True
##########################################################

# I set this manually after seeing what the output files were named. Can automate this later. 
out_monterey=$outdir/noaa_9413450_9413450_water_level_2018_2018.csv
out_ptreyes=$outdir/noaa_9415020_9415020_water_level_2018_2018.csv


# Gen_elev2d wants full timestamp as input, so add hours/minutes to the end of our sim time
stime1=$stime0"T00:00:00"
etime1=$etime0"T00:00:00"

python $gen_elev2d --outfile elev2D.th.nc --stime=$stime1 --etime=$etime1 $out_ptreyes $out_monterey