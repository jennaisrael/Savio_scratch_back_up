#!/bin/sh
#BATCH --job-name=pull_gauge_data
#SBATCH --partition=savio2 # savio_bigmem #savio3
#SBATCH --account=fc_esdl #co_aiolos #co_aiolos #fc_esdl #change this  
#SBATCH --nodes=1
#SBATCH --time=02:00:00
#SBATCH --export=ALL
#//SBATCH --ntasks-per-node=2
#//SBATCH --cpus-per-task=16



#EDIT 11/20 don't need to do this, just dont load python
#EDIT 10/18/2024 change the way we run python scripts per Sienna's fix: ~/.conda/envs/schimpy2/bin/python -u script.py
#do this in set_paths_user.sh call it $env

#updated list
module purge
module load intel-oneapi-compilers/2023.1.0
module load openmpi/4.1.3
export JASPERLIB=/global/home/groups/consultsw/sl-7.x86_64/modules/jasper/2.0.14/lib64
export JASPERINC=/global/home/groups/consultsw/sl-7.x86_64/modules/jasper/2.0.14/include
export NCLLIB=/global/home/groups/consultsw/sl-7.x86_64/modules/intel/ncl/6.4.0-intel
export ZLIBLIB=/global/home/groups/consultsw/sl-7.x86_64/modules/zlib/1.2.11
export LIBPNGLIB=/global/home/groups/consultsw/sl-7.x86_64/modules/libpng/1.6.34
module load cmake/3.27.7
export LAPACKIB=/global/home/groups/consultsw/sl-7.x86_64/modules/lapack/3.8.0
#module unload openmpi/4.1.6
module load anaconda3/2024.02-1-11.4
#module load python/3.10
module list 

#modified from /global/scratch/users/jennaisrael/schism_scripts_scratch/set_up_tidal_bc.sh to just call download_noaa.py from CADWR's DmS Datastore repository

#edit JI Nov 22, 2024 to have SLR variable in the environment

#start and end dates
# Date for NOAA times series --> add ~ month of extra time here for "buffer"
stime="1950-01-01"
etime="2021-10-01"

#Path where you want the data to be downloaded
path2tidal=/global/scratch/users/jennaisrael/time_varying_data/tide_gauge_data

# Define path to python scripts
#use this version which has commented out the troublesome logger line
download_noaa=/global/home/groups/fc_esdl/scripts/packages/dms_datastore/dms_datastore/download_noaa.py #/global/scratch/users/jennaisrael/dms_datastore/dms_datastore/download_noaa.py


echo "Download tidal gauge data..."
###### DOWNLOAD NOAA DATA ################################
# Run python script from dms_datastore to download 
cd $path2tidal

echo "Running download_noaa..."
#conda run -n schimpy python  $download_noaa --start=$stime --end=$etime --dest=$path2tidal --station=9415020 --param=water_level #--overwrite=True
echo "Pulling Point Reyes..."
~/.conda/envs/schimpy2/bin/python  $download_noaa --start=$stime --end=$etime --dest=$path2tidal --station=9415020 --param=water_level #--overwrite=True

echo "Pulling Monterey Bay..."
#conda run -n schimpy python  $download_noaa --start=$stime --end=$etime --dest=$path2tidal --station=9413450 --param=water_level #-overwrite=True
~/.conda/envs/schimpy2/bin/python $download_noaa --start=$stime --end=$etime --dest=$path2tidal --station=9413450 --param=water_level #-overwrite=True


# # Gen_elev2d wants full timestamp as input, so add hours/minutes to the end of our sim time
# stime1=$stime0"T00:00:00"
# etime1=$etime0"T00:00:00"


# echo "Running gen_elev2d..."
# #conda run -n schimpy python gen_elev2d.py --outfile elev2D.th.nc --stime=$stime1 --etime=$etime1 $out_ptreyes $out_monterey
# ~/.conda/envs/schimpy2/bin/python gen_elev2d.py --outfile elev2D.th.nc --stime=$stime1 --etime=$etime1 $out_ptreyes $out_monterey --slr=$slr
