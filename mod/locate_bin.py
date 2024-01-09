#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (c) 2011-2018, wradlib developers.
# Distributed under the MIT License. See LICENSE.txt for more info.

"""
bins locations  :

 -   bin_altitude
 -   bin_distance
 -   site_distance
"""

import numpy as np


def bin_altitude(r, theta, sitealt, re, ke=4./3.):
    """Calculates the height of a radar bin taking the refractivity of the \
    atmosphere into account.
    Based on :cite:`Doviak1993` the bin altitude is calculated as
        h = \\sqrt{r^2 + (k_e r_e)^2 + 2 r k_e r_e \\sin\\theta} - k_e r_e


    Parameters
        Array of heights of the radar bins in [m]

    """
    RE = ke * re
    sr = RE + sitealt
#    return np.sqrt(r ** 2 + sr ** 2 + 2 * r * sr * np.sin(np.radians(theta))) - RE
    return np.sqrt(r ** 2 + RE ** 2   +  2 * r * RE * np.sin(np.radians(theta))) - RE





def bin_distance(r, theta, sitealt, re, ke=4./3.):
    """Calculates great circle distance from radar site to radar bin over \
    spherical earth, taking the refractivity of the atmosphere into account.

        s = k_e r_e \\arctan\\left(
        \\frac{r \\cos\\theta}{r \\cos\\theta + k_e r_e + h}\\right)

    where :math:`h` would be the radar site altitude amsl.

    Parameters
    ----------
    Returns
    -------
    distance : :class:`numpy:numpy.ndarray`
        Array of great circle arc distances [m]
    """

    RE = ke * re
    sr = RE + sitealt
    theta = np.radians(theta)
    return RE * np.arctan(r * np.cos(theta) / (r * np.sin(theta) + sr))


def site_distance(r, theta, binalt, re=None, ke=4./3.):
    """Calculates great circle distance from bin at certain altitude to the \
    radar site over spherical earth, taking the refractivity of the \
    atmosphere into account.
    Based on :cite:`Doviak1993` the site distance may be calculated as
        s = k_e r_e \\arcsin\\left(
        \\frac{r \\cos\\theta}{k_e r_e + h_n(r, \\theta, r_e, k_e)}\\right)

    where :math:`h_n` would be provided by
    :func  .misc.bin_altitude`.
    """
    RE = ke * re
    return reff * np.arcsin(r * np.cos(np.radians(theta)) / (RE + binalt))
