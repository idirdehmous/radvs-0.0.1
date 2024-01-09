# -*- coding: utf-8 -*- 


import argparse
import numpy as np 
from  math import pi ,sqrt , sin , cos ,asin , acos , atan ,atan2
import sys , os 
import warnings as _warnings
import matplotlib 
matplotlib.use("Agg")              # Interactive mode off 
import matplotlib.pyplot as plt
from matplotlib import ticker
from mpl_toolkits.basemap import Basemap 
import pyproj 
import h5py
# Import  non-standard modules  
sys.path.append('../mod')
import decodehdf5
import pixe2coord
import locate_bin
import vis 

_warnings.filterwarnings('always', category=DeprecationWarning,
                         module='matplotlib')





re=6371.0*1000.0
ke=4.0/3.0
RE= 6371.0*1000.0*4.0/3.0     # Effective earth radius in middle altitude in meter RE=R*4/3



def Ppi(data ,elangle , site ,filename  , var):
    """
    Function to plot PPI 
    the module vis.py  is copied from  wradlib 
    by adding some custom modifications 
    The data are presented on polar (curvilinear r/azimuth ) grid !
    """
    # Masking the data with no value (255 in pixel space  -->  99999 in velocity space)
    fig=plt.figure(figsize=(8,8))
    data1     = np.ma.array(data)
    mask_data = np.ma.masked_where(data1 == 99999.0  ,data1)
    ax, pm    = vis.plot_ppi(mask_data,elangle,site )
    ylabel    = ax.set_ylabel('[km]')
    cb        = plt.colorbar(pm, ax=ax , pad=0.1)
    tick_locator = ticker.MaxNLocator(nbins=8)
    cb.locator   = tick_locator
    cb.update_ticks()
    cb.set_label('Radial velocity  [m/s]')
   
    fname= os.path.basename(filename)
    plt.title(fname + '\n'+'  Parameter: '+var_name+'    ,Elevation : '+str(elangle)+' deg', fontsize=10)
    elangle= '%.2f' % elangle
    plt.savefig(var_name+'_'+str(elangle)+'.png')

 


def Plot_data(lon , lat , data ,rlat, rlon ,*imagename):
    """
    Small function for plotting ,whether we want to 
    have graphical plot of the data in lat/lon grid 

    'Under implementation ...! '
    """ 

    fig = plt.figure(figsize=(13,8))
    # Set the radar location on the center of the plot  
    ll_lat=rlat-6.
    ur_lat=rlat+5.
    ll_lon=rlon-5.
    ur_lon=rlon+10.
#    wgs84=pyproj.Proj("+init=EPSG:4326")
#    isn2004=pyproj.Proj("+proj=lcc +lat_1=45.0 +lat_2=65.0 +lat_0=46.0 +lon_0=15 x_0=21978.16865951358, y_0=7556.316217664036 +no_defs +a=6378137 +rf=298.257222101 +to_meter=1")
#    x0 ,y0 =pyproj.transform(wgs84, isn2004, rlon, rlat)
#    xx, yy = pyproj.transform(wgs84, isn2004, lon, lat) 

#    print(x0, y0)
#    m = Basemap(
#               llcrnrlon=ll_lon, llcrnrlat=ll_lat,
#               urcrnrlon=ur_lon, urcrnrlat=ur_lat,
#               lat_0=rlat, lon_0=rlon, projection='lcc', resolution='h')

    m = Basemap(width=12000000,height=9000000,
            resolution='l',projection='lcc',\
            lat_1=45.,lat_2=55,lat_0=rlat,lon_0=rlon)

    m.drawcoastlines()
    m.drawcountries()
#    m.drawmapboundary(fill_color='aqua')
    data1     = np.ma.array(data)
    mask_data = np.ma.masked_where(data1 == 99999.0  ,data1)
#    plt.rcParams.update({'figure.max_open_warning': 0})
    cs = plt.pcolormesh(lon,lat,mask_data ,cmap=plt.get_cmap('jet'), vmin =data.min(), vmax = data.max())
#    plt.scatter(lon , lat , mask_data )
    plt.savefig(str(imagename[0])+'.png')
 




if __name__=='__main__':

 
   parser = argparse.ArgumentParser(argparse.RawTextHelpFormatter) 
   parser.add_argument('-f'  ,"--file"      , help='input filename in hdf5 format'   , required=False)
   parser.add_argument('-n','--dataset', metavar='N', type=int, nargs='+', help='index of the dataset to be decoded sparated by spaces example: 1 2 3 4 5 6 .... ')
 
   args   = parser.parse_args()
   if args.file == None and args.dataset==None:
      print '      '
      print 'hdf5_plot.py is used for plotting data on polar grid. \n Requieres input arguments  !'
      print '      '



   filename=args.file
   if args.file == None:
      print (parser.print_help())
      sys.exit(1)
   
   fid = h5py.File(filename, 'r')
   

   # Get the informations about the Radar
   rlat     =decodehdf5.Radar_info(fid)[0]
   rlon     =decodehdf5.Radar_info(fid)[1]
   rheight  =decodehdf5.Radar_info(fid)[2]
   wmoid    =decodehdf5.Radar_info(fid)[3]
   node     =decodehdf5.Radar_info(fid)[4]
   nscans   =decodehdf5.Scan_nr(fid)
   site=(rlat,rlon,rheight)


   dset=[]
   if args.dataset == None:
      print (parser.print_help())
      sys.exit(2)
   else:
      dset=args.dataset


   print '-'*50
   print ' '*50
   print 'RADAR FILE GLOBAL INFORMATIONS  '
   print '-'*50
   print 'Decoding hdf5 file ...   ' ,filename
   print 'Radar name              :' ,wmoid , '   ' , node
   print 'Radar position  , Lat   :' ,rlat ,'Lon  :' ,rlon
   print 'Number of scans in file :' ,nscans
   print 'Radar station height    :' ,rheight ,' m'
   print ' '*50



   for i in dset:
       if i == 0:
          print 'Dataset index must be greater than  0 \ndataset0 doesn\' t exist . Check your dataset index sequence!'
          sys.exit(3)
       else:
          dataset  = '/dataset%d' %  i
          elangle  =  decodehdf5.Get_data_attrib(fid,dataset)[1][0]
          var_name =  decodehdf5.Get_data_attrib(fid,dataset)[11]
          elev     =  elangle *pi/180.0
          print 'Dataset %s ' %i , 'Elevation angle :' ,elangle , ' deg'

     
          elangle ,nazimt ,ndist,  nodetect,  lon, lat, vralt, data =pixe2coord.Vrad_coordinates(fid , dataset)

         # Calling the Ppi function to plot the Polar Plane Indicator
          Ppi (data , elangle , site ,filename, var_name )


