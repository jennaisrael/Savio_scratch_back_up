#!/bin/sh
#BATCH --job-name=compile_SCHISM
#SBATCH --partition=savio3 # savio_bigmem #savio3
##SBATCH --qos=fc_esdl #aiolos_savio3_normal 
#SBATCH --account=fc_esdl #co_aiolos 
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --time=00:05:00
#SBATCH --export=ALL

module purge
module load gcc/13.2.0  
module load openmpi/4.1.6
module load netcdf-c/4.9.2
module load netcdf-fortran/4.6.1
module load cmake/3.27.7
module list


#cd /global/home/groups/fc_esdl/compiling/schism5.10/schism
cd /global/scratch/users/jennaisrael/schism/
# Delete old build director.y 
rm -r build/
mkdir build/
cd build

module show openmpi

cmake -DBUILD_TYPE=Debug -C  ../cmake/SCHISM.local.build -C ../cmake/SCHISM.local.savio.intel ../src/ -DPREC_EVAP=ON -DTVD_LIM=VL # -DUSE_GOTM=ON #-DGOTM_BASE=/global/scratch/users/siennaw/software/gotm/code/
echo -e "\n\n\n\n now running make..."

make -j16 pschism

cd Utilities 
make -j16 
# make VERBOSE=1 pschism
