"""
Contains the logic behind creating and configuring new plots
from a set of user-supplied arguments.
"""

# Standard library imports
import re

# Major library imports
from numpy import all, array, arange, asarray, reshape, shape, transpose

# Chaco imports
from chaco.api import (create_line_plot, create_scatter_plot,
    ArrayDataSource, ImageData)

from chaco.tools.api import HighlightTool



# Local relative imports
from chaco_shell_error import ChacoShellError


# Normally I don't define an __all__, but this lets us distinguish
# the top level plot-producing functions from the various helper
# functions.
__all__ = ["do_plot", "do_imshow", "do_pcolor", "do_contour", "do_plotv",
           "SizeMismatch", ]


#-----------------------------------------------------------------------------
# Exceptions
#-----------------------------------------------------------------------------

class SizeMismatch(ChacoShellError):
    pass


#-----------------------------------------------------------------------------
# Utility functions
#-----------------------------------------------------------------------------

def is1D (a):
    s = shape(a)
    return ((len(s) == 1) or (s[0] == 1) or (s[1] == 1))

def is2D (a):
    return (len(shape(a)) == 2)

def row ( a ):
        return reshape( asarray( a ), [1,-1] )

def col ( a ):
        return reshape( asarray( a ), [-1,1] )


#-----------------------------------------------------------------------------
# Plot commands for chaco-style plotv()
#-----------------------------------------------------------------------------

def do_plotv(session, *args, **kw):
    """ Creates a list of plots from the data in ``*args`` and options in
    ``**kw``, according to the docstring on commands.plot().
    """

    sort = kw.get("sort", "none")
    sources_list = make_data_sources(session, sort, *args)

    plot_type = kw.get("type", "line")
    if plot_type == "scatter":
        plots = [create_scatter_plot(sources) for sources in sources_list]
    elif plot_type == "line":
        plots = [create_line_plot(sources) for sources in sources_list]
    else:
        raise ChacoShellError, "Unknown plot type '%s'." % plot_type

    for plot in plots:
        plot.orientation = kw.get("orientation", "h")


    return plots

def make_data_sources(session, index_sort="none", *args):
    """ Given a list of arguments, returns a list of (index, value) datasources
    to create plots from.
    """
    # Make sure everything is a numpy array
    data = []
    for arg in args:
        if isinstance(arg, list) or isinstance(arg, tuple):
            data.append(array(arg))
        else:
            data.append(arg)

    if len(data) == 0:
        raise ChacoShellError, "Insufficient data for plot."

    # 1D array(s)
    if len(data[0].shape) == 1:
        if len(data) == 1:
            # Only a single array was provided
            index_ds = ArrayDataSource(arange(len(data[0])), sort_order="ascending")
            value_ds = ArrayDataSource(data[0], sort_order="none")
            return [(index_ds, value_ds)]

        else:
            # multiple arrays were provided
            index_ds = ArrayDataSource(data[0], sort_order=index_sort)
            return [(index_ds, ArrayDataSource(v, sort_order="none")) for v in data[1:]]

    # 2D arrays
    elif len(data[0].shape) == 2:
        sources = []
        # Loop over all the 2D arrays
        for ary in data:
            if ary.shape[0] > ary.shape[1]:
                index_ary = ary[:, 0]
                value_arrays = ary[:, 1:]
            else:
                index_ary = ary[0]
                value_arrays = transpose(ary[1:])
            index_ds = ArrayDataSource(index_ary, sort_order=index_sort)
            sources.extend([(index_ds, ArrayDataSource(v, sort_order="none")) for v in value_arrays])
        return sources

    # Not a two-dimensional array, error.
    else:
        raise ChacoShellError, "Unable to create plot data sources from array of" \
                               "shape " + str(data[1].shape) + "."


#-----------------------------------------------------------------------------
# Plot commands for matlab-compatible plot() function
#-----------------------------------------------------------------------------

# Regular expressions for parsing the format string

color_re = re.compile('[ymcrgbwk]')
color_trans = {
    'y': 'yellow',
    'm': 'magenta',
    'c': 'cyan',
    'r': 'red',
    'g': 'green',
    'b': 'blue',
    'w': 'white',
    'k': 'black'
}

# This one isn't quite right:

marker_re = re.compile('[ox+s^v]|(?:[^-])[.]')
marker_trans = {
    '.': 'dot',
    'o': 'circle',
    'x': 'cross',
    '+': 'plus',
    's': 'square',
    '^': 'triangle',
    'v': 'down triangle'
}

line_re = re.compile('--|-\.|[-:]')
line_trans = {
    '-':  'solid',
    ':':  'dot',
    '-.': 'dot dash',
    '--': 'dash'
}

def _process_format(format):
    """
    Converts a format string into a (color, line, marker, marker_color) tuple.
    """
    if format == '':
        return ('black', 'solid', None, None)
    color, line, marker, marker_color = 'black', None, None, None
    m = color_re.findall(format)
    if len(m) > 0:
        color = marker_color = color_trans[m[0]]
        if len(m) > 1:
            marker_color = color_trans[m[1]]
    m = marker_re.findall(format)
    # The -1 takes care of 'r.', etc:
    if len(m) > 0:
        marker = marker_trans[m[0][-1]]
    m = line_re.findall(format)
    if len(m):
        line = line_trans[m[0]]
    return (color, line, marker, marker_color)

def _process_group(group, plot_data=None):
    """ Returns a (x_1D, y_1D, format_str) tuple from an input tuple
    of 1 to 3 elements: (x,y,format_str).

    A PlotData object can be optionally provided to disambiguate the cases
    when exactly two strings are passed in.  The two strings could be the
    names of the x and y datasources, or they could be the name of the y
    datasource and a format string.  By checking the second string against
    the plot_data's list of datasources, the method can determine what it is meant
    to be.
    """
    # Interpret and split the 'group' tuple into x, y, and plotinfo
    plotinfo = ''
    if len(group) == 1:
        y = group[0]
        y_data = plot_data.get_data(y)
        x = plot_data.set_data("", arange(len(y_data)), generate_name=True)
    elif len(group) == 2:
        # There are two possibilities here; a single y was provided along
        # with a format string, or an x and y were provided.  If PlotData
        # was provided, use that to disambiguate; otherwise, assume that the
        # second string is a format string.
        if isinstance(group[1], basestring):
            if plot_data and group[1] in plot_data.list_data():
                x = group[0]
                y = group[1]
            else:
                plotinfo = group[1]
                y = group[0]
                y_data = plot_data.get_data(y)
                x = plot_data.set_data("", arange(len(y_data)), generate_name=True)
        else:
            x, y = group
    elif len(group) == 3:
        x, y, plotinfo = group
    else:
        raise ChacoShellError("Found too many elements in group while" \
                              " constructing plot.")
    return x, y, plotinfo


def _check_sort_order(data):
    diffs = data[1:] - data[:-1]
    if all(diffs >= 0):
        return "ascending"
    elif all(diffs <= 0):
        return "descending"
    else:
        return "none"


def do_plot(plotdata, active_plot, *data_and_formats, **kwtraits):
    """ Takes a list of data (arrays or names) and format string arguments
    and creates new plots on the active_plot.  Returns a list of plot names
    on the active plot.
    """
    # The list of data and formats is broken up by format strings,
    # so we break it up by arguments that are strings.
    cur_group = []
    groups = []
    valid_names = plotdata.list_data()
    for arg in data_and_formats:
        if not isinstance(arg, basestring):
            # an array was passed in
            cur_group.append(plotdata.set_data("", arg, generate_name=True))
        elif arg in valid_names:
            # the name of an existing plotdata item was passed in
            cur_group.append(arg)
        else:
            # String that is not in plotdata is interpreted as a format
            # string, thereby terminating this group
            cur_group.append(arg)
            groups.append(cur_group)
            cur_group = []

    if len(cur_group) > 0:
        groups.append(cur_group)

    # Process the list of groups and create a list of plots;
    # broadcast the keyword traits to all of them.
    plots = []

    for group in groups:
        x, y, format_str = _process_group(group, plot_data = plotdata)
        linecolor, line, marker, markercolor = _process_format(format_str)
        plot_type = []
        format = kwtraits.copy()
        if line is not None:
            plot_type.append("line")
            format["line_style"] = line
            format["color"] = linecolor
        if marker is not None:
            plot_type.append("scatter")
            format["marker"] = marker
            format["color"] = markercolor

        # Check the data sort order, but only if it will create a new datasource
        if x not in active_plot.datasources:
            x_sort_order = _check_sort_order(plotdata.get_data(x))
        plots.extend(active_plot.plot((x,y), type=",".join(plot_type), **format))

        # Set the sort order
        x_ds = active_plot.datasources[x]
        if isinstance(x_ds, ArrayDataSource):
            x_ds.sort_order = x_sort_order

        # Check to see if the active_plot has a highlighter tool already; if not,
        # then add it.
        for tool in active_plot.tools:
            if isinstance(tool, HighlightTool):
                break
        else:
            active_plot.tools.append(HighlightTool(active_plot))

    return plots

def do_imread(*data, **kwargs):
    """ Returns image file as array. """

    # Check to see if the data given is either a file path or a file object
    if isinstance(data[0], basestring) or isinstance(data[0], file):
        return ImageData.fromfile(data[0])
    else:
        raise ValueError("do_imread takes a string filename")



def do_imshow(plotdata, active_plot, *data, **kwargs):
    """ Creates an image plot on the active plot, given either
    a filename or data.
    """

    if len(data) != 1:
        raise ValueError("do_imshow takes one data source")

    valid_names = plotdata.list_data()

    x = None
    y = None
    if not isinstance(data[0], basestring):
        #an array was passed in
        z = plotdata.set_data("", data[0], generate_name=True)
    elif data[0] in valid_names:
        #the name of an existing plotdata item was passed in
        z = data[0]
    else:
        #the name of the file was passed in
        #create plot data
        image = do_imread(data[0], *data, **kwargs)
        z = plotdata.set_data("", image, generate_name=True)

    plot_list = [active_plot.img_plot(z, xbounds=x, ybounds=y, **kwargs)]

    return plot_list


def do_pcolor(plotdata, colormap, active_plot, *data, **kwargs ):
    """ Creates a pseudocolor image plot on the active plot, given a 2-D
    scalar data and a colormap.
    """

    valid_names = plotdata.list_data()

    # if we get just one data source, it is assumed to be the scalar field
    if len(data) == 1:
        x = None
        y = None
        if not isinstance(data[0], basestring):
            # an array was passed in
            z = plotdata.set_data("", data[0], generate_name=True)
        elif data[0] in valid_names:
            # the name of an existing plotdata item was passed in
            z = data[0]

    # three data sources means we got x-y grid data of some sort, too
    elif len(data) == 3:
        if not isinstance(data[0], basestring):
            x = plotdata.set_data("", data[0], generate_name=True)
        elif data[0] in valid_names:
            x = data[0]
        if not isinstance(data[0], basestring):
            y = plotdata.set_data("", data[1], generate_name=True)
        elif data[0] in valid_names:
            y = data[1]
        if not isinstance(data[0], basestring):
            z = plotdata.set_data("", data[2], generate_name=True)
        elif data[0] in valid_names:
            z = data[2]
    else:
        raise ValueError("do_pcolor takes one or three data sources")

    plot_list = [active_plot.img_plot(z, xbounds=x, ybounds=y,
                                colormap=colormap, **kwargs)]
    return plot_list



def do_contour(plotdata, colormap, active_plot, type, *data, **kwargs ):
    """ Creates a contour plot on the active plot, given a 2-D
    scalar data and a colormap.
    """

    valid_names = plotdata.list_data()

    # if we get just one data source, it is assumed to be the scalar field
    if len(data) == 1:
        x = None
        y = None
        if not isinstance(data[0], basestring):
            # an array was passed in
            z = plotdata.set_data("", data[0], generate_name=True)
        elif data[0] in valid_names:
            # the name of an existing plotdata item was passed in
            z = data[0]

    # three data sources means we got x-y grid data of some sort, too
    elif len(data) == 3:
        if not isinstance(data[0], basestring):
            x = plotdata.set_data("", data[0], generate_name=True)
        elif data[0] in valid_names:
            x = data[0]
        if not isinstance(data[0], basestring):
            y = plotdata.set_data("", data[1], generate_name=True)
        elif data[0] in valid_names:
            y = data[1]
        if not isinstance(data[0], basestring):
            z = plotdata.set_data("", data[2], generate_name=True)
        elif data[0] in valid_names:
            z = data[2]
    else:
        raise ValueError("do_contour takes one or three data sources")

    # we have to do slightly different calls here because of the different
    # handling of colourmaps
    if type is 'poly':
        plot_list = [active_plot.contour_plot(z, type, xbounds=x, ybounds=y,
                                    poly_cmap=colormap,
                                    **kwargs)]
    else:
        plot_list = [active_plot.contour_plot(z, type, xbounds=x, ybounds=y,
                                    colors=colormap,
                                    **kwargs)]

    return plot_list



# EOF
