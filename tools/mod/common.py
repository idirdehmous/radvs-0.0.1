"""
pyart.graph.common
==================

Common graphing routines.

.. autosummary::
    :toctree: generated/

    parse_ax
    parse_ax_fig
    parse_vmin_vmax
    parse_lon_lat
    set_limits

"""

import matplotlib.pyplot as plt


########################
# Common radar methods #
########################


def get_field_limits(field, container=None, selection=0):
    """
    Return the data limits from the configuration file for a given field,
    radar and sweep

    Parameters
    ----------
    field: str
        Field name.
    container: Radar, Grid or None
        This is an optional parameter that will be use to get informations
        related to the field, like for instace nyquist velocity.
    selection: int
        selection of the data in the container, case container is a Radar this
        is the sweep to be considered

    Returns
    -------
    vmin, vmax: 2-tuplet of float
        Minimun and Maximun teorical value for field, if field is not
        in the configuration file returns (None, None).
    """
    if field in _DEFAULT_FIELD_LIMITS:
        limits = _DEFAULT_FIELD_LIMITS[field]
        if callable(limits):
            limits = limits(container, selection)
        return limits
    else:
        return None, None





def parse_ax(ax):
    """ Parse and return ax parameter. """
    if ax is None:
        ax = plt.gca()
    return ax


def parse_ax_fig(ax, fig):
    """ Parse and return ax and fig parameters. """
    if ax is None:
        ax = plt.gca()
    if fig is None:
        fig = plt.gcf()
    return ax, fig



def parse_cmap(cmap, field=None):
    """ Parse and return the cmap parameter. """
    if cmap is None:
        cmap = get_field_colormap(field)
    return cmap




def parse_vmin_vmax(field, vmin, vmax):
    """ Parse and return vmin and vmax parameters. """
    field_default_vmin, field_default_vmax = get_field_limits(field)
    if vmin is None:
        if 'valid_min' in field_dict:
            vmin = field_dict['valid_min']
        else:
            vmin = field_default_vmin
    if vmax is None:
        if 'valid_max' in field_dict:
            vmax = field_dict['valid_max']
        else:
            vmax = field_default_vmax
    return vmin, vmax


def parse_lon_lat(grid, lon, lat):
    """ Parse lat and lon parameters """
    if lat is None:
        lat = grid.origin_latitude['data'][0]
    if lon is None:
        lon = grid.origin_longitude['data'][0]
    return lon, lat









def set_limits(xlim=None, ylim=None, ax=None):
    """
    Set the display limits.

    Parameters
    ----------
    xlim : tuple, optional
        2-Tuple containing y-axis limits in km. None uses default limits.
    ylim : tuple, optional
        2-Tuple containing x-axis limits in km. None uses default limits.
    ax : Axis
        Axis to adjust.  None will adjust the current axis.

    """
    if ax is None:
        ax = plt.gca()
    if ylim is not None:
        ax.set_ylim(ylim)
    if xlim is not None:
        ax.set_xlim(xlim)
