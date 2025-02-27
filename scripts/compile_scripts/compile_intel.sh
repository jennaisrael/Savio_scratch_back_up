#!/bin/sh
#BATCH --job-name=compile_SCHISM
#SBATCH --partition=savio3 
#SBATCH --account=fc_esdl
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=10
#SBATCH --time=00:05:00
#SBATCH --export=ALL


module purge
module load intel/oneapi-2022.2.0
module load openmpi/4.1.3
module load jasper/2.0.14
module load ncl/6.4.0-intel
module load libpng/1.6.34
module load cmake/3.22.0
module load lapack/3.8.0
# module load hdf5/1.8.18-intel-s
module unload openmpi/2.0.2-intel
module list


export MPI_HOME=/global/software/sl-7.x86_64/modules/intel/oneapi-2022.2.0/openmpi/4.1.3/
export  NETCDF=/global/software/sl-7.x86_64/modules/intel/2016.4.072/netcdf/4.4.1.1-intel-s/lib

# Replace this with your filepath
cd /global/scratch/users/jennaisrael/schism
# Delete old build directory
rm -r build/
mkdir build/
cd build

module show openmpi

cmake -DBUILD_TYPE=Debug -C  ../cmake/SCHISM.local.build -C ../cmake/SCHISM.local.savio ../src/ -DPREC_EVAP=ON -DTVD_LIM=VL # -DUSE_GOTM=ON

echo -e "\n\n\n\n now running make..."

make -j16 pschism
