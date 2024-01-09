#--------------------------------------------------------------------
# ZAMG (Zentralantstahlt fuer meteorologie und geodynamik) (Austria)
# ONM  (Office national de la meteorologie)  (Algeria)          
#
# __AUTHOR      : IDIR DEHMOUS   
#     
# __E-MAIL      : idirdehmous@gmail.com

# Last update  : Vienna , 20-12-2018 

#-------------------------------------------------------------------


This folder contains a first version of RadVS 
(Radar Doppler Velocity Simulator)
a model to simulate radar radial velocity from a NWP model 

The model is organized as following :

  - 'RadVS.py'  :  Main script to read Model forecast file (in fa format)
                open and read the HDF5 observation file 
                paralelizes th processes 
                and finally write the obtained 
                radial velocity values in the same 
                used hdf5 file by overwritting 
                VRAD parameter values

 - 'mod'        :     Contains the necessary modules 
                      called by the main script RadVS.py 
                      -decodhdf5.py : reading hdf5 file attributes and values
                      -pixe2cord.py : geographical transformation from polar 
                                      to lat/lon grid 
                      -doppsim.so   : fortran module to perfome
                                      the interpolation from model 
                                      grid points into observation locations
                      -vis.py       : module used by hdf5_plot.py in order to create
                                      PPI plots on polar grid 
 
 - 'tools'          : Contains the tools 
                      hdf5_plot.py : plot PPI(Polar Plan Indicator)
                                     for a given dataset 
                      scan_odim.py : Scan opera odim file and prints all 
                                     attributes values found under each dataset
                                     and station global informations
 
Python dependencies  :
    -h5py   
    -EpyGrAM utility 
    -numpy 
    -matplolib 


                                  
This software is   still    missing   some   technical 
adaptation to handle   all   the files provided by the 
europeen opera hub  community  ,    and the algorithme 
used to simulate the  radial wind could be improved by 
other sophisticated techniques.So be free to share and 
give any suggestions !!!



# Dieses model war im december entwickelt , es war 
# bald weinachtsfest , so 
# Frohes weinachtenfest fuer alle !!!  
# ;-) 
         
--------------------------------------------------------------
