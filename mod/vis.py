#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2011-2018, wradlib developers.
# Distributed under the MIT License. See LICENSE.txt for more info.

"""
Visualisation
   plot_ppi
   create_cg

"""

# standard libraries
import os.path as path
import warnings

# site packages
import numpy as np
import matplotlib 
matplotlib.use('Agg')
import matplotlib.pyplot as pl
from matplotlib import patches, axes, lines
from matplotlib.projections import PolarAxes
from matplotlib.transforms import Affine2D
from mpl_toolkits.axisartist import (SubplotHost, ParasiteAxesAuxTrans,
                                     GridHelperCurveLinear)
from mpl_toolkits.axisartist.grid_finder import FixedLocator, DictFormatter
import mpl_toolkits.axisartist.angle_helper as ah
from matplotlib.ticker import NullFormatter, FuncFormatter
from matplotlib.collections import LineCollection, PolyCollection
import bins_loc




def plot_ppi(data, elangle,site ,r=None, az=None,fig=None,cg=True ,refrac=True):


    """Plots a Plan Position Indicator (PPI).

    """

    # kwargs handling
    re=6370040.
    ke=4./3.
    ax=111
    func='pcolormesh'
    # providing 'reasonable defaults', based on the data's shape
    if r is None:
        d1 = np.arange(data.shape[1], dtype=np.float)
    else:
        d1 = np.asanyarray(r.copy())

    if az is None:
        d2 = np.arange(data.shape[0], dtype=np.float)
    else:
        d2 = np.asanyarray(az.copy())

    x = np.append(d1, d1[-1] + (d1[-1] - d1[-2]))
        # the angular dimension is supposed to be cyclic, so we just add the
        # first element
    y = np.append(d2, d2[0])
#    else:
        # no autoext basically is only useful, if the user supplied the correct
        # dimensions himself.
#        x = d1
#        y = d2
      

    if refrac:
        # with refraction correction, significant at higher elevations
        # calculate new range values
        x = bins_loc.bin_distance(x, elangle, site[2], re, ke=ke)

    # axes object is given
    if isinstance(ax, axes.Axes):
        if cg:
            try:
                caax = ax.parasites[0]
                paax = ax.parasites[1]
            except AttributeError:
                raise TypeError("If `cg=True` `ax` need to be of type"
                                " `mpl_toolkits.axisartist.SubplotHost`")


    else:
        if fig is None:
            if ax is 111:
                # create new figure if there is only one subplot
                fig = pl.figure()
            else:
                # assume current figure
                fig = pl.gcf()
        if cg:
            # create curvelinear axes
            ax, caax, paax = create_cg( fig, ax)
            # this is in fact the outermost thick "ring"
            ax.axis["lon"] = ax.new_floating_axis(1, np.max(x) )
            ax.axis["lon"].major_ticklabels.set_visible(False)
            # and also set tickmarklength to zero for better presentation
            ax.axis["lon"].major_ticks.set_ticksize(0)
        else:
            ax = fig.add_subplot(ax)


    if cg:
        xx, yy = np.meshgrid(y, x)
        # set bounds to min/max
        xa = yy * np.sin(np.radians(xx)) 
        ya = yy * np.cos(np.radians(xx)) 
        plax = paax
        data = data.transpose()
    


    # plot the stuff
    plotfunc = getattr(plax, func)
    pm = plotfunc(xx, yy, data ,cmap=pl.get_cmap('jet'))
   

    if cg:
        # show curvelinear and cartesian grids
        ax.set_ylim(np.min(ya), np.max(ya))
        ax.set_xlim(np.min(xa), np.max(xa))
        ax.grid(True)
        caax.grid(True)
    else:
        ax.set_aspect('equal')

    return ax, pm





def create_cg( fig=None, subplot=111):
    """ Helper function to create curvelinear grid

    The function makes use of the Matplotlib AXISARTIST namespace
    `mpl_toolkits.axisartist \
    <https://matplotlib.org/mpl_toolkits/axes_grid/users/axisartist.html>`_.

    Returns
    -------
    cgax : matplotlib toolkit axisartist Axes object
        curvelinear Axes (r-theta-grid)
    caax : matplotlib Axes object (twin to cgax)
        Cartesian Axes (x-y-grid) for plotting cartesian data
    paax : matplotlib Axes object (parasite to cgax)
        The parasite axes object for plotting polar data
    """


    # Set theta start to north
    tr_rotate = Affine2D().translate(-90, 0)

    # set theta running clockwise
    tr_scale = Affine2D().scale(-np.pi / 180, 1)

    # create transformation
    tr = tr_rotate + tr_scale + PolarAxes.PolarTransform()

    #  build up curvelinear grid
    extreme_finder = ah.ExtremeFinderCycle(20, 20,
                                               lon_cycle=360,
                                               lat_cycle=None,
                                               lon_minmax=(360, 0),
                                               lat_minmax=(0, np.inf),)

    # locator and formatter for angle annotation
    locs = [i for i in np.arange(0., 359., 10.)]
    grid_locator1 = FixedLocator(locs)
    tick_formatter1 = DictFormatter(dict([(i, r"${0:.0f}^\circ$".format(i)) for i in locs]))

    # grid_helper for curvelinear grid
    grid_helper = GridHelperCurveLinear(tr,
                                    extreme_finder=extreme_finder,
                                    grid_locator1=grid_locator1,
                                    grid_locator2=None,
                                    tick_formatter1=tick_formatter1,
                                    tick_formatter2=None,
                                     )

    # try to set nice locations for range gridlines
    grid_helper.grid_finder.grid_locator2._nbins = 15.0
    grid_helper.grid_finder.grid_locator2._steps = [0, 1, 1.5, 2,2.5,5,10]

    # if there is no figure object given
    if fig is None:
    # create new figure if there is only one subplot
      if subplot is 111:
         fig = pl.figure()
        # otherwise get current figure or create new figure
      else:
         fig = pl.gcf()

    # generate Axis
    cgax = SubplotHost(fig, subplot, grid_helper=grid_helper)

    fig.add_axes(cgax)

    # PPIs always plottetd with equal aspect
    cgax.set_aspect('equal', adjustable='box')

    # get twin axis for cartesian grid
    caax = cgax.twin()
    # move axis annotation from right to left and top to bottom for
    # cartesian axis
    caax.toggle_axisline()
    # make right and top axis visible and show ticklabels (curvelinear axis)
    cgax.axis["top", "right"].set_visible(True)
    cgax.axis["top", "right"].major_ticklabels.set_visible(False)


    # make ticklabels of left and bottom axis invisible (curvelinear axis)
    cgax.axis["left", "bottom"].major_ticklabels.set_visible(False)
    
 
    # and also set tickmarklength to zero for better presentation
    # (curvelinear axis)
    cgax.axis["top", "right", "left", "bottom"].major_ticks.set_ticksize(0)



    # show theta (angles) on top and right axis
    cgax.axis["top"].get_helper().nth_coord_ticks = 0
    cgax.axis["right"].get_helper().nth_coord_ticks = 0

    # generate and add parasite axes with given transform
    paax = ParasiteAxesAuxTrans(cgax, tr, "equal")
    # note that paax.transData == tr + cgax.transData
    # Anything you draw in paax will match the ticks and grids of cgax.
    cgax.parasites.append(paax)

    return cgax, caax, paax



