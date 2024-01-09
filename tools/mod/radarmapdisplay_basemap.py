"""
pyart.graph.radarmapdisplay_basemap
===================================

Class for creating plots on a geographic map using a Radar object and Basemap.

.. autosummary::
    :toctree: generated/
    :template: dev_template.rst

    RadarMapDisplayBasemap

"""

import sys 
sys.path.append('../../mod')
import decodehdf5
import pixe2coord
import warnings
import numpy as np
import matplotlib.pyplot as plt 
import pyproj 
try:
    from mpl_toolkits.basemap import Basemap
    _BASEMAP_AVAILABLE = True
except ImportError:
    _BASEMAP_AVAILABLE = False


#from radardisplay import RadarDisplay
from common import parse_ax_fig, parse_vmin_vmax, parse_cmap
#from exceptions import MissingOptionalDependency
import h5py 




def _check_basemap():
    """ Check that basemap is not None, raise ValueError if it is. """
    if basemap is None:
       raise ValueError('no basemap plotted')





def plot_ppi_map(field,lat , lon , site,  sweep=0, mask_tuple=None,
            vmin=None, vmax=None, cmap=None, norm=None, mask_outside=False,ax=None, fig=None,
            lat_lines=None, lon_lines=None,
            projection='lcc', area_thresh=10000,
            min_lon=None, max_lon=None, min_lat=None, max_lat=None,
            width=None, height=None, lon_0=None, lat_0=None,
            resolution='h', shapefile=None, edges=True, gatefilter=None,
            basemap=None, filter_transitions=True, embelish=True,using_corners=True) :
    """
        Plot a PPI volume sweep onto a geographic map.

        Additional arguments are passed to Basemap.

        Parameters
        ----------
        field : str
            Field to plot.
        sweep : int, optional
            Sweep number to plot.
    """


    # parse parameters
    ax, fig = parse_ax_fig(ax, fig)
#    cmap = parse_cmap(cmap, field)

    if lat_lines is None:
       lat_lines = np.arange(30, 46, 1)
    if lon_lines is None:
       lon_lines = np.arange(-110, -75, 1)
    if lat_0 is None:
       lat_0 = site[0]
    if lon_0 is None:
       lon_0 = site[1]

    # get data for the plot
    
    data = field 
   
    #x, y =  get_x_y(sweep, edges, filter_transitions)
    wgs84=pyproj.Proj("+init=EPSG:4326")
    isn2004=pyproj.Proj("+proj=lcc +lat_1=64.25 +lat_2=65.75 +lat_0=65 +lon_0=-19 +x_0=1700000 +y_0=300000 +no_defs +a=6378137 +rf=298.257222101 +to_meter=1")
    x, y = pyproj.transform(wgs84, isn2004, lon, lat)
    x_0 , y_0 =pyproj.transform (wgs84, isn2004 ,site[1], site[0])
    # mask the data where outside the limits
    if mask_outside:
       data = np.ma.masked_outside(data, vmax)


    # create the basemap if not provided
   
    if using_corners:
      basemap = Basemap(
               llcrnrlon=min_lon, llcrnrlat=min_lat,
               urcrnrlon=max_lon, urcrnrlat=max_lat,
               lat_0=lat_0, lon_0=lon_0, projection=projection,
               area_thresh=area_thresh, resolution=resolution, ax=ax)
     
   
        # add embelishments
      if embelish is True:
            basemap.drawcoastlines(linewidth=1.25)
            basemap.drawstates()
            basemap.drawparallels(
                lat_lines, labels=[True, False, False, False])
            basemap.drawmeridians(
                lon_lines, labels=[False, False, False, True])
      basemap = basemap
      
      x0, y0 = basemap(x_0, y_0)
      
        # plot the data and optionally the shape file
        # we need to convert the radar gate locations (x and y) which are in
        # km to meters as well as add the map coordiate radar location
        # which is given by self._x0, self._y0.
      pm = basemap.pcolormesh(
           x0 + x * 1000., y0 + y * 1000., data,
           vmin=vmin, vmax=vmax, cmap=cmap, norm=norm)

       

      if shapefile is not None:
         basemap.readshapefile(shapefile, 'shapefile', ax=ax)

        # add plot and field to lists
      plt.savefig('test.png')
     # plots.append(pm)
     # plot_vars.append(field)
 



filename='PALI01_LJLM_201811260100_new2.hdf'
fid = h5py.File(filename, 'r')

dataset = '/dataset%d' %  1
elangle , nodetect,  lon, lat, vralt, dopp_vel=pixe2coord.Vrad_coordinates(fid ,dataset)

rlat   =decodehdf5.Radar_info(fid)[0]
rlon   =decodehdf5.Radar_info(fid)[1]
site   =(rlat , rlon)

plot_ppi_map(dopp_vel,lat , lon , site, 
               sweep=0 , 
               mask_tuple=None,
               vmin=None,
               vmax=None,
               cmap=None,
               norm=None, 
               mask_outside=False,
               ax=None, 
               fig=None,
              lat_lines=None, 
              lon_lines=None,
              projection='lcc',
              area_thresh=10000,
              min_lon=0.,
              max_lon=20.,
              min_lat=40.,
              max_lat=60.,
              width=None,
              height=None,
              lon_0=rlon, 
              lat_0=rlat,
              resolution='h',
              shapefile=None,
              edges=True, 
              gatefilter=None,
              basemap=None, 
              filter_transitions=True, 
              embelish=True,
              using_corners=True)





