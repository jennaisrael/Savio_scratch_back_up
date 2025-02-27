#!/bin/sh
#BATCH --job-name=preprocess_SCHISM
#SBATCH --partition=savio3 
#SBATCH --account=fc_esdl
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=10
#SBATCH --export=ALL
#SBATCH --time=00:40:00


module load python
module list 

# Go to folder 
cd /global/scratch/users/jennaisrael/BayDeltaSCHISM/templates/bay_delta_test

# takes about 20-30 min 
# conda activate schism
# prepare_schism main_bay_delta_w_grid.yaml


# Run the prepare_schism.py script 
conda run -n schism python $prepare main_bay_delta_w_grid.yaml

#fn=/global/home/users/jennaisrael/.conda/envs/schism/lib/python3.10/site-packages/schimpy/prepare_schism.py/create_vgrid_lsc2.py #update the env name here "schism"

# # Run create_vgrid_lsc2.py script. This won’t work if the previous ^ one crashed.
# conda run -n schism python $fn --hgrid hgrid.gr3  --minmaxregion minmaxlayer_slr_0_mod105.shp   --vgrid vgrid.in.d --vgrid_version 5.10 #update the env name here "schism"