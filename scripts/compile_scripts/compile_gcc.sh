#!/bin/sh
#BATCH --job-name=compile_SCHISM
#SBATCH --partition=savio3 # savio_bigmem #savio3
#SBATCH --account=fc_esdl
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=10
#SBATCH --time=00:05:00
#SBATCH --export=ALL






module purge
# Try new GCC 6.3.0 Version
module load gcc/6.3.0
module load openmpi/3.0.1-gcc
module load netcdf/4.4.1.1-gcc-s
module load hdf5/1.8.18-gcc-p
module load cmake/3.22.0
module load lapack
module unload openmpi/2.0.2-gcc


export MPI_HOME=/global/software/sl-7.x86_64/modfiles/gcc/6.3.0/openmpi/3.0.1-gcc
export NETCDF_ROOT=/global/software/sl-7.x86_64/modfiles/gcc/6.3.0/netcdf/4.4.1.1-gcc-s
export NETCDF=$NETCDF_ROOT


cd /global/scratch/users/jennaisrael/schism

# Delete old build director.y
rm -r build/
mkdir build/
cd build


module show openmpi


cmake -DBUILD_TYPE=Debug -C  ../cmake/SCHISM.local.build -C ../cmake/SCHISM.local.savio ../src/ -DPREC_EVAP=ON -DTVD_LIM=VL 


echo -e "\n\n\n\n now running make..."


make -j16 pschism