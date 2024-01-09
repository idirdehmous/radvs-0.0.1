# -*- coding: utf-8 -*-
"""
MAIN PYTHON PROGRAM OF RaDVS MODEL  
LITTLE SOFTWARE TO SIMULATE THE RADAR DOPPLER RADIAL WIND 
FROM A MODEL FORCAST USING HDF5 FILE 

__AUTHOR      : IDIR DEHMOUS  
__INSTITUTION : ZAMG  (Zentralanstahlt fuer Meteorologie und Geodynamik),AUSTRIA
                ONM   (Office National de la Meteorologie ) ,ALGERIA 
__E-MAIL      : idirdehmous@gmail.com 

LAST UPDATE   : 18-12-2018   

"""
import argparse 
import  sys , os 
import multiprocessing as mp 
import collections
sys.path.append('./mod')
import decodehdf5
import pixe2coord
from math import acos , sin , cos , pi
import numpy as np
import h5py
from mpl_toolkits.basemap import Basemap
import matplotlib.pylab as plt
import datetime as dt
import doppsim

import epygram 
epygram.init_env()




parser = argparse.ArgumentParser(argparse.RawTextHelpFormatter)
parser.add_argument('-mf'  ,'--model_file'     , help='Input forecast file in FA format ' , required=False)
parser.add_argument('-rf'  ,'--radar_file'     , help='Input radar observation file , in HDF5 (PERA-ODIM) file format' , required=False)

args   = parser.parse_args()
fafile =args.model_file
rfile  =args.radar_file

if fafile  == None  or rfile == None:
   print (parser.print_help())
   sys.exit(1) 

#*************************************
#Reading FA file 
#*************************************
f = epygram.formats.resource(filename=fafile, openmode='r')



# Get the validity and basis forecast dates 
bdate  = f.validity.getbasis()
vdate  = f.validity.get()
byy=bdate.year
bmm=bdate.month
bdd=bdate.day
bhh=bdate.hour

vyy=int(vdate.year )
vmm=int(vdate.month)
vdd=int(vdate.day  )
vhh=int(vdate.hour ) 

# Get the dimensions grid and levels in the file 
geom  =f.geometry

# Dimensions
nlon = geom.dimensions['X']
nlat = geom.dimensions['Y']

# Lon, lat and levels
mlon, mlat = geom.get_lonlat_grid()
levels=geom.vcoordinate.levels
levels.reverse()
nlevel=len(levels)

# Initialization of listes with the first array of data as empty 
ugp=[np.empty([nlat,nlon])]  # Retrieving the u components values 
vgp=[np.empty([nlat,nlon])]  # Retrieving the v components values
hgp=[np.empty([nlat,nlon])]  # Retrieving the heights      values


for l in levels:
   ilevel="{:03}".format(l)                                              # Formatting the level number in 3 digits
   print 'Reading   U, V  and heights    from   level   -->' , ilevel  
   ufield='S'+str(ilevel)+'WIND.U.PHYS'                                  # (possiblity to increase the number of levels in model in other settings)
   vfield='S'+str(ilevel)+'WIND.V.PHYS'
   hfield='S'+str(ilevel)+'CLOUD_WATER'
   u=f.readfield(ufield)
   u.sp2gp()
   ugp.append(u.data)
   v=f.readfield(vfield)
   v.sp2gp()
   vgp.append(v.data)
   # Getting field's heights ---> 'CLOUD_WATER' fields
   h=f.readfield(hfield)
   hgp.append(h.data)

# Liste to np.array conversion
ugp=np.asarray(ugp)
vgp=np.asarray(vgp)
hgp=np.asarray(hgp)

# Remove the first array in each array , it corresponds to empty values 
ugp=np.delete(ugp, 0, 0)   
vgp=np.delete(vgp, 0, 0)
hgp=np.delete(hgp, 0, 0)




#**************************************************************************
# Reading radar data from HDF5 file 
# the modules used are :2
#     -decodehdf5.py  --> Opening and reading data from hdf5 file  
#     -pixe2coord.py  --> Convert pixel radar data to lat/lon and heights                
#**************************************************************************


# Open the HDF5 file 
fid = h5py.File(rfile, 'r')

# Get again the infos about the radar station
rlat     =decodehdf5.Radar_info(fid)[0]
rlon     =decodehdf5.Radar_info(fid)[1]
rheight  =decodehdf5.Radar_info(fid)[2]
wmoid    =decodehdf5.Radar_info(fid)[3]
node     =decodehdf5.Radar_info(fid)[4]
rdate    =decodehdf5.Radar_info(fid)[5]
rtime    =decodehdf5.Radar_info(fid)[6]
nscans   =decodehdf5.Scan_nr(fid)


# Check for model and observation files dates compatibility
ryy=int(rdate[0:4])
rmm=int(rdate[4:6])
rdd=int(rdate[6:8])
rhh=int(rtime[0:2])
rmn=int(rtime[2:4])
#if ryy != vyy  or rmm != vmm  or rdd != vdd:
#   print 'Incompatible dates between HDF5 file and model'
#   print 'Date model         : ',vyy,'-',vmm,'-',vdd
#   print 'Date HDF5 file     : ',ryy,'-',rmm,'-',rdd 
#   sys.exit(0)


def Dopp_Windsimulation(i):

    fid = h5py.File(rfile+'_'+str(i), 'r')
#    fid = h5py.File(rfile  , 'r')
   
    # Get the infos about the radar station
    rlat     =decodehdf5.Radar_info(fid)[0]
    rlon     =decodehdf5.Radar_info(fid)[1]
    rheight  =decodehdf5.Radar_info(fid)[2]
    wmoid    =decodehdf5.Radar_info(fid)[3]
    node     =decodehdf5.Radar_info(fid)[4]
    rdate    =decodehdf5.Radar_info(fid)[5]
    rtime    =decodehdf5.Radar_info(fid)[6]
    nscans   =decodehdf5.Scan_nr(fid)

    dataset='/dataset%d' %  i
    elangle ,nazimt ,ndist, nodetect,  lon, lat, vralt, dopp_vel=pixe2coord.Vrad_coordinates(fid , dataset)
    if len(dataset) < 10:    # Only for formatting the output text !!
       dataset=dataset+' '

   # Calling FORTRAN to do the hard work !!!
   # Importing fortran-python module  doppsim
    data= doppsim.interpolate(lon , lat ,vralt, mlon , mlat ,ugp[:,:,:] ,vgp[:,:,:], hgp[:,:,:] ,nazimt,ndist,elangle,rheight,nlevel) 
    vrad=[]
    for i in range(data[1].shape[0]):
       for j in range(data[1].shape[1]):

           if data[1][i,j] <= -999.:
              vrad.append(255)
           else:
              vrad.append(data[1][i,j])
    vrad=np.asarray(vrad)
    vrad=vrad.reshape(data[1].shape[0],data[1].shape[1])
    data=(data[0],vrad)   
    return data 


print 'NAME OF THE HDF5 FILE TO BE USED      :'  ,os.path.basename(rfile)
print 'NUMBER OF DATASETS IN THE   HDF5 FILE : ' ,nscans
print 'DATE AND HOUR IN FILE                 :'  ,str(ryy)+'-'+str(rmm)+'-'+str(rdd)+'  '+str(rhh)+':'+str("{:02}".format(rmn))
print '     '
print 'NAME OF FORECAST FILE TO BE USED      :'  ,os.path.basename(fafile)
print 'NUMBER OF LEVELS IN THE FORECAST FILE : ' ,nlevel
print 'DATE AND HOUR IN FORECAST FILE        :'  ,str(vyy)+'-'+str(vmm)+'-'+str(vdd)+'  '+str(vhh)+':00'
print '     '
print 'CALLING DOPPSIM MODULE FOR INTERPOLATION ... '




# Copy the file to be opened by each process 
for i in range(1,nscans+1):
    os.system('cp -f  '+rfile+'   '+rfile+'_'+str(i))

# Parallel execution with map function !
p = mp.Pool(nscans)
results=p.map(Dopp_Windsimulation  , range(1,nscans+1))

# Remove the files created by the processes
for i in range(1,nscans+1):
    os.system('rm   '+rfile+'_'+str(i))

angl_vrad={}  # Python dictionary which stores each elangle with its corresponding Radial valocity data   
for i in range(len(results)):
    elev=results[i][0]
    data=results[i][1]
    angl_vrad[elev]=data

data2write=collections.OrderedDict(sorted(angl_vrad.items(),reverse=True))



# Model validity date
vyy=str(vdate.year )
vmm=str(vdate.month)
vdd=str(vdate.day  )
vhh=str(vdate.hour )

# Create a copie of the file to be modified
fname=os.path.basename(rfile)    #  for example    PALI01_LJLM_201811260100_new2.hdf
hdf_prefix=fname[0:11]          
filedate  =vyy+str('{:02}'.format(int(vmm)))+str('{:02}'.format(int(vdd)))+str('{:02}'.format(int(vhh)))
newfilename=hdf_prefix+'_'+filedate+'00_sim.hdf'
cwd = os.getcwd()
os.system('cp  '+rfile+'  '+cwd+'/'+newfilename)
print 'len(data2write),nscans+1',len(data2write),nscans+1
for i in range(1,len(data2write)+1):
    fid = h5py.File(newfilename)
    path = "/dataset"+str(i)
# It s possible that the VRAD variable is read from another 
# subgroup than data3
# Checking for data3 object existance, 
# If it doesn't exist we create a new data3 and its what group
# Else if it s in the file, we overwrite the data under this group 
# So we are sure to find simulated velocity paramter ALWAYS !!under datasetN/data3/data 
    try:
       dim1=data2write.values()[i-1].shape[0]
       dim2=data2write.values()[i-1].shape[1]
       newgrp   = fid.create_group('dataset'+str(i)+'/data3')
       grp_what = fid.create_group('dataset'+str(i)+'/data3/what')
       grp_what.attrs['quantity'] = 'VRAD_SIM'
       grp_what.attrs['nrays']   = dim1
       grp_what.attrs['nbins']   = dim2
       grp_what.attrs['undetect']=254
       grp_what.attrs['offset']  =0.0
       grp_what.attrs['gain']    =1.0
       grp_what.attrs['nodata']  =255
       dset  = fid.create_dataset('/dataset'+str(i)+'/data3/data',data=data2write.values()[i-1], dtype=np.float32)
    except:
       Exception
       del fid['/dataset'+str(i)+'/data3/data']
       del fid['/dataset'+str(i)+'/data3/what']
       dim1=data2write.values()[i-1].shape[0]
       dim2=data2write.values()[i-1].shape[1]
       grp_what = fid.create_group ('dataset'+str(i)+'/data3/what')
       grp_what.attrs['quantity'] = 'VRAD_SIM'
       grp_what.attrs['nrays']   = dim1
       grp_what.attrs['nbins']   = dim2
       grp_what.attrs['undetect']=254
       grp_what.attrs['offset']  =0.0
       grp_what.attrs['gain']    =1.0
       grp_what.attrs['nodata']  =255  
       dset  = fid.create_dataset('/dataset'+str(i)+'/data3/data',data=data2write.values()[i-1], dtype=np.float32)
    print path,'finished'

print '     '
print 'DOPPLER RADIAL SIMULATED WINDS WRITTEN IN FILE :' , newfilename ,'\n'

quit()
