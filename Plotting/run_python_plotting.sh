#!/bin/sh
#BATCH --job-name=plot_schism
#SBATCH --partition=savio4_htc # savio3 # savio_bigmem #savio3 savio4_htc?? 
##.  // /SBATCH --qos=aiolos_savio3_normal 
#SBATCH --account=fc_esdl #co_aiolos #fc_esdl # 
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=56 #40 #56
## SBATCH --cpus-per-task=1
#SBATCH --time=2:00:00
#SBATCH --export=ALL

echo "Running python on savio4 with 1 nodes 56 tasks"


#import anaconda and python
#module purge
#module load anaconda3/2024.02-1-11.4
#module load python

#source /global/home/groups/fc_esdl/scripts/schism_scripts/set_paths_jenna.sh

#which environment
#env=schimpy

#file to run
#conda run -n geoplot python -u test_plot_lib.py
#conda run -n geoplot python -u aggregate_netcdf.py
#conda run -n $env python -u aggregate_netcdf.py
#conda run -n schimpy python -u schism_plotting_JI.py
#~/.conda/envs/geoplot/bin/python -u schism_plotting_JI.py
#~/.conda/envs/geoplot/bin/python -u aggregate_netcdf.py
~/.conda/envs/geoplot/bin/python -u prospectus_plots.py

echo "\n Done!"

