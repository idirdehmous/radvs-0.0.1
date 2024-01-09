import pyart 
import matplotlib 
matplotlib.use('Agg')
import matplotlib.pyplot as plt 
import numpy as np 
import warnings

warnings.filterwarnings('always', category=DeprecationWarning,
                         module='numpy')

filename='PALI01_LJLM_201811260500_new2.hdf'

radar=pyart.aux_io.read_odim_h5(filename)
display =pyart.graph.RadarMapDisplay(radar)

# plot the second tilt
rlat=46.0678
rlat=46.0678
rlon=15.2849
ll_lat=rlat-3
ll_lon=rlon-4
ur_lat=rlat+3
ur_lon=rlon+4
latlines=np.arange(40.0, 50.0, 2.0)
lonlines=np.arange(10.0, 20.0, 2.0)

display.plot_ppi_map('velocity', 1,
                     vmin=-30, 
                     vmax=30,
                     min_lon=ll_lon,  
                     max_lon=ur_lon,  
                     min_lat=ll_lat,  
                     max_lat=ur_lat,
                     lat_lines=latlines,
                     lon_lines=lonlines,
                     projection='lcc',
                     resolution='h',
                     lat_0=46.0678,
                     lon_0=15.2849,
                     colorbar_label='Radial velocity  [ m/s ]',
                     title=filename,
                     cmap='jet',
                     shapefile='/home/vhmod/mproj/epyg/tools/shp/limites/ne_10m_admin_0_boundary_lines_land',
                     embelish=True)




# plot range rings at 10 , 80 , 150 and 220 km 
display.plot_range_ring(10., line_style='k-')
display.plot_range_ring(80., line_style='k--')
display.plot_range_ring(150., line_style='k-')
display.plot_range_ring(220., line_style='k--')


plt.savefig('test_pyart.png')




quit()
# plots cross hairs
display.plot_line_xy(np.array([-40000.0, 40000.0]), np.array([0.0, 0.0]),
                     line_style='k-')
display.plot_line_xy(np.array([0.0, 0.0]), np.array([-20000.0, 200000.0]),
                     line_style='k-')

# Indicate the radar location with a point
display.plot_point(radar.longitude['data'][0], radar.latitude['data'][0])

plt.show()
