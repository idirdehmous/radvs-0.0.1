import argparse
import numpy as np
from  math import pi ,sqrt , sin , cos ,asin , acos , atan ,atan2
import sys , os
import warnings as _warnings
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap 
from matplotlib import ticker
import h5py
# Import  non-standard modules  
sys.path.append('../mod')
import decodehdf5




re=6371.0*1000.0
ke=4.0/3.0
RE= 6371.0*1000.0*4.0/3.0

def Plot_data(lon , lat , data ,rlat, rlon  ,*imagename):

    fig = plt.figure(figsize=(8,8))
    # Set the radar location on the center of the plot  
    ll_lat=rlat-3.
    ur_lat=rlat+3.
    ll_lon=rlon-3.
    ur_lon=rlon+3

#    m = Basemap(projection='cyl',lon_0=rlat,lat_0=rlon,llcrnrlat=ll_lat,
#               urcrnrlat=ur_lat,llcrnrlon=ll_lon,urcrnrlon=ur_lon,resolution='l')
    m = Basemap(width=1100000,height=800000,projection='lcc',
            resolution='c',lat_1=45.,lat_2=55,lat_0=rlat,lon_0=rlon)
    m.drawcoastlines()
    m.drawcountries()
#    m.drawmapboundary(fill_color='aqua')
    data1     = np.ma.array(data)
    mask_data = np.ma.masked_where(data1 == 99999.0  ,data1)
    plt.rcParams.update({'figure.max_open_warning': 0})
    x,y= m(lon,lat)
#    plt.scatter(lon, lat, c=mask_data, cmap='jet')
    m.pcolormesh(x, y  , mask_data, cmap='jet')
    plt.colorbar()
    plt.show()
    #plt.savefig(str(imagename[0])+'.png')





def Vrad_coordinates(fid , dataset):

    # Get the Radar location and height  
    rlat   =decodehdf5.Radar_info(fid)[0]
    rlon   =decodehdf5.Radar_info(fid)[1]
    rheight=decodehdf5.Radar_info(fid)[2]

    a1gate      = decodehdf5.Get_data_attrib(fid,dataset)[0][0]
    elangle     = decodehdf5.Get_data_attrib(fid,dataset)[1][0]
    nbins       = decodehdf5.Get_data_attrib(fid,dataset)[2][0]
    nrays       = decodehdf5.Get_data_attrib(fid,dataset)[3][0]
    rscale      = decodehdf5.Get_data_attrib(fid,dataset)[4][0]
    rstart      = decodehdf5.Get_data_attrib(fid,dataset)[5][0]
    vals     = decodehdf5.Get_data_attrib(fid,dataset)[6][0]
    gain     = decodehdf5.Get_data_attrib(fid,dataset)[7][0]
    nodata   = decodehdf5.Get_data_attrib(fid,dataset)[8][0]
    offset   = decodehdf5.Get_data_attrib(fid,dataset)[9][0]
    nodetect = decodehdf5.Get_data_attrib(fid,dataset)[10][0]

    # Array initalization
    elev =elangle *pi/180.0                            # Radar beam elevation in radians 
    rdist1=np.empty([nbins])
    lat  =np.empty([nrays,nbins])
    lon  =np.empty([nrays,nbins])
    vralt=np.empty([nrays,nbins])
    dopp_vel = np.empty([nrays,nbins])


    for iray in range(nrays):
        for jbin in range(nbins):
            rdist = jbin*rscale                        # Radar-bins distance 
            azimt = (iray *360./nrays)*pi/180.         # Azimuth of a ray 
            vralt[iray,jbin]   = sqrt (rdist**2 + RE**2+  2.0*rdist* RE* sin(elev))-RE  # Altitude of each bin 
            rgdist  = RE *atan(rdist*cos(vralt[iray,jbin] * pi/180.)/(RE + rdist * sin(vralt[iray,jbin] * pi/180.)))  # Radar-bins distance on ground
            lat[iray,jbin]  = asin(sin(rlat*pi/180.)*cos(rgdist/RE)+cos(rlat*pi/180.)*sin(rgdist/RE)*cos(azimt))*180./pi
            lon[iray,jbin]  = rlon + atan2(sin(azimt)*sin(rgdist/RE)*cos(rlat*pi/180.) ,
                               cos(rgdist/RE)-sin(rlat*pi/180.)*sin(lat[iray,jbin]*pi/180.))*180./pi

    # Compute the real radial velocity wind speed and  
    # set a  99999.0 flag for no-data (255) 
    for iray in range(nrays):
        for jbin in range(nbins):
            if vals[iray,jbin] < 255:
               dopp_vel[iray,jbin] = vals[iray,jbin]*gain + offset
            else:
               dopp_vel[iray,jbin] = 99999.0
    return elangle , nodetect,  lon, lat, vralt, dopp_vel



