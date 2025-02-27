#!/bin/sh
#BATCH --job-name=compile_SCHISM
#SBATCH --partition=savio3 # savio_bigmem #savio3
##SBATCH --qos=aiolos_savio3_normal 
#SBATCH --account=fc_esdl 
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=10

#/global/software/sl-7.x86_64/modules/intel/2018.1.163/openmpi/2.0.2-intel 
# /global/software/sl-7.x86_64/modules/intel/oneapi-2022.2.0/openmpi/4.1.3/
#SBATCH --time=00:05:00
#SBATCH --export=ALL
#//// SBATCH --cpus-per-task=10

# netcdf in intel is compatible with fortran 

module purge
module load intel/oneapi-2022.2.0
module load openmpi/4.1.3
module load jasper/2.0.14
module load ncl/6.4.0-intel
module load libpng/1.6.34
module load cmake/3.22.0 #3.22.0  #3.15.1
module load lapack/3.8.0
module load hdf5/1.8.18-intel-s 
module unload openmpi/2.0.2-intel
module list 

# GCC COMPILER !!!! 
# module purge
# module load gcc/11.3.0
# module load openmpi # /5.0.0-ucx
# module load hdf5 # /1.12.2-gcc-p
# module load lapack/3.10.1-gcc
# module load python/3.8.8  
# module load cmake # /3.22.0  
# module load gnu-parallel/2019.03.22 
# module load netcdf/4.9.0-gcc-p 
# module list 


# /global/software/sl-7.x86_64/modules/intel/2016.4.072/netcdf/4.4.1.1-intel-s/include
export MPI_HOME=/global/software/sl-7.x86_64/modules/intel/oneapi-2022.2.0/openmpi/4.1.3/



 
export NETCDF=/global/software/sl-7.x86_64/modules/intel/2016.4.072/netcdf/4.4.1.1-intel-p/include

 







#   1) gcc/6.3.0              3) hdf5/1.8.18-gcc-p      5) cmake/3.22.0           7) lapack/3.8.0
#   2) openmpi/3.0.1-gcc      4) netcdf/4.4.1.1-gcc-p   6) python/3.10.10

export MPI_HOME=/global/software/sl-7.x86_64/modules/intel/oneapi-2022.2.0/openmpi/4.1.3/ 
#export MPI_HOME=/global/software/sl-7.x86_64/modfiles/gcc/11.3.0/openmpi/5.0.0-ucx
# export NetCDF_ROOT=/global/software/sl-7.x86_64/modfiles/gcc/11.3.0/netcdf/4.9.0-gcc-p 


# export NETCDF_HOME=/global/software/sl-7.x86_64/modfiles/gcc/11.3.0/netcdf/4.9.0-gcc-p 
# export LD_PATH=$LD_PATH:$NETCDF
# export MPI_HOME=/global/software/sl-7.x86_64/modfiles/intel/oneapi-2022.2/scg/openmpi/4.1.3 

cd /global/scratch/users/jennaisrael/schism

# Delete old build director.y 
rm -r build/
mkdir build/
cd build

module show openmpi


# cmake -DBUILD_TYPE=Debug -C  ../cmake/SCHISM.local.build -C ../cmake/SCHISM.local.savio.intel ../src/ -DPREC_EVAP=ON -DTVD_LIM=VL # -DUSE_GOTM=ON #-DGOTM_BASE=/global/scratch/users/siennaw/software/gotm/code/
# echo -e "\n\n\n\n now running make..."

# make -j16 pschism
module show openmpi

cmake -DBUILD_TYPE=Debug -C  ../cmake/SCHISM.local.build -C ../cmake/SCHISM.local.savio.intel ../src/ -DPREC_EVAP=ON -DTVD_LIM=VL # -DUSE_GOTM=ON #-DGOTM_BASE=/global/scratch/users/siennaw/software/gotm/code/
echo -e "\n\n\n\n now running make..."

make -j16 pschism

cd Utilities 
make -j16 

# make VERBOSE=1 pschism
