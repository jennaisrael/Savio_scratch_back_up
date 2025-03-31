#!/bin/sh
#BATCH --job-name=compile_SCHISM
#SBATCH --partition=compute #savio3 # savio_bigmem #savio3
##SBATCH --qos=#fc_esdl #aiolos_savio3_normal 
#SBATCH --account=ddp473 #fc_esdl #co_aiolos 
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=10
#SBATCH --time=00:05:00
#SBATCH --export=ALL

#EXPANSE
module purge
module load cpu/0.15.4
module load intel/19.1.1.217
module load intel-mpi/2019.8.254
#module load jasper/2.0.16
#module load ncl/6.6.2-openblas
module load zlib/1.2.11
module load libpng/1.6.37
module load cmake/3.18.2
#module load netlib-lapack/3.9.1/d4fs2fg
module load netcdf-c/4.7.4
module load netcdf-fortran/4.5.3
#module load anaconda3/2021.05/kfluefz
module load python/3.8.5
module list
#/global/software/sl-7.x86_64/modules/intel/2018.1.163/openmpi/2.0.2-intel 
# /global/software/sl-7.x86_64/modules/intel/oneapi-2022.2.0/openmpi/4.1.3/
##SBATCH --time=00:05:00
##SBATCH --export=ALL
#//// SBATCH --cpus-per-task=10

# netcdf in intel is compatible with fortran 

# # old modules before Savio rocky update 
# module purge
# module load intel/oneapi-2022.2.0
# module load openmpi/4.1.3
# module load jasper/2.0.14
# module load ncl/6.4.0-intel
# module load libpng/1.6.34
# module load cmake/3.22.0 #3.22.0  #3.15.1
# module load lapack/3.8.0
# module load hdf5/1.8.18-intel-s 
# module unload openmpi/2.0.2-intel
# module list 

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

##### STILL DEBUGGING 
##updated list as of July 2024
#module purge
#module load intel-oneapi-compilers/2023.1.0
#module load intel-oneapi-mpi/2021.10.0 
##module load gcc/10.5.0 #module spider openmpi/4.1.3 said I needed this module loaded first
##module load openmpi/4.1.3
#export JASPERLIB=/global/home/groups/consultsw/sl-7.x86_64/modules/jasper/2.0.14/lib64
#export JASPERINC=/global/home/groups/consultsw/sl-7.x86_64/modules/jasper/2.0.14/include

#export NCLLIB=/global/home/groups/consultsw/sl-7.x86_64/modules/intel/ncl/6.4.0-intel/lib
#export NCLINC=/global/home/groups/consultsw/sl-7.x86_64/modules/intel/ncl/6.4.0-intel/include
##export libifport.so.5
#export ZLIBLIB=/global/home/groups/consultsw/sl-7.x86_64/modules/zlib/1.2.11/lib
#export ZLIINC=/global/home/groups/consultsw/sl-7.x86_64/modules/zlib/1.2.11/include

#export LIBPNGLIB=/global/home/groups/consultsw/sl-7.x86_64/modules/libpng/1.6.34/lib
#export LIBPNGINC=/global/home/groups/consultsw/sl-7.x86_64/modules/libpng/1.6.34/include

#module load cmake/3.27.7
##module load netlib-lapack/3.11.0
## export CMAKELIB=/global/home/groups/consultsw/sl-7.x86_64/modules/cmake/3.15.1 #this does not have lib and include directories, just bin, doc and share

#export LAPACK=/global/home/groups/consultsw/sl-7.x86_64/modules/lapack/3.8.0 #this does not have lib and include directories, libblas.so  libblas.so.3  liblapack.a  liblapack.so  liblapack.so.3  libtmglib.a  libtmglib.so

##module unload openmpi/4.1.6
#module load netcdf-c/4.9.2
#module load netcdf-fortran/4.6.1
#module load anaconda3/2024.02-1-11.4
#module load python
#module list


# # /global/software/sl-7.x86_64/modules/intel/2016.4.072/netcdf/4.4.1.1-intel-s/include
# export MPI_HOME=/global/software/sl-7.x86_64/modules/intel/oneapi-2022.2.0/openmpi/4.1.3/

# # export NETCDF=/global/software/sl-7.x86_64/modules/intel/2016.4.072/netcdf/4.4.1.1-intel-p/include
# export NETCDF=/global/software/sl-7.x86_64/modules/intel/oneapi-2022.2.0/netcdf/4.9.0-gcc-p/include/


#   1) gcc/6.3.0              3) hdf5/1.8.18-gcc-p      5) cmake/3.22.0           7) lapack/3.8.0
#   2) openmpi/3.0.1-gcc      4) netcdf/4.4.1.1-gcc-p   6) python/3.10.10

# export MPI_HOME=/global/software/sl-7.x86_64/modules/intel/oneapi-2022.2.0/openmpi/4.1.3/ 
# #export MPI_HOME=/global/software/sl-7.x86_64/modfiles/gcc/11.3.0/openmpi/5.0.0-ucx
# # export NetCDF_ROOT=/global/software/sl-7.x86_64/modfiles/gcc/11.3.0/netcdf/4.9.0-gcc-p 


# # export NETCDF_HOME=/global/software/sl-7.x86_64/modfiles/gcc/11.3.0/netcdf/4.9.0-gcc-p 
# # export LD_PATH=$LD_PATH:$NETCDF
# # export MPI_HOME=/global/software/sl-7.x86_64/modfiles/intel/oneapi-2022.2/scg/openmpi/4.1.3 


#cd /global/home/groups/fc_esdl/compiling/schism5.10/schism
#go to directory where SCHISM drive is
cd /expanse/lustre/scratch/jisrael/temp_project/schism
# Delete old build director.y 
rm -r build/
mkdir build/
cd build

module show openmpi

cmake -DBUILD_TYPE=Debug -C  ../cmake/SCHISM.local.build -C ../cmake/SCHISM.local.expanse.intel ../src/ -DPREC_EVAP=ON -DTVD_LIM=VL # -DUSE_GOTM=ON #-DGOTM_BASE=/global/scratch/users/siennaw/software/gotm/code/
echo -e "\n\n\n\n now running make..."

make -j16 pschism

cd Utilities 
make -j16 
# make VERBOSE=1 pschism
