
import wx
from enthought.chaco2.api import Plot, color_map_name_dict
from enthought.chaco2.tools.api import PanTool, RectZoomTool

import plot_maker
from session import PlotSession

session = PlotSession()


#------------------------------------------------------------------------
# General help commands
#------------------------------------------------------------------------

def chaco_commands():
    """
    Prints out the current list of all shell commands.  Information
    on each command is available in that command's docstring (__doc__).

    Window/Plot Management
    ------------------
    figure -- create a new figure window
    activate -- activates an existing window or plot
    close -- closes a window
    curplot -- returns a reference to the active window's Plot object
    show -- starts the GUI and displays windows (should only be used
            in scripts)

    Plotting
    --------
    plot -- plots some data
    scatter -- plots some data as a scatterplot (unordered X/Y data)
    line -- plots some data as an ordered set of of X,Y points
    imread -- creates an array from an image file on disk
    imshow -- creates an image plot from a file on disk
    pcolor -- plots some scalar data as a pseudocolor image
    contour -- creates a contour line plot of some scalar data
    contourf -- creates a contour poly plot of some scalar data
    loglog -- plots an x-y line or scatter plot on log-log scale
    semilogx -- plots an x-y line or scatter plot with a log x-scale
    semilogy -- plots an x-y line or scatter plot with a log y-scale
    hold -- turns "hold" on or off
    show -- shows plot on screen; used when running from script
    

    Axes, Annotations, Legends
    --------------------------
    legend -- creates a legend and adds it to the plot
    xaxis -- toggles the horizontal axis, sets the interval
    yaxis -- toggles the vertical axis, sets the interval
    xgrid -- toggles the grid running along the X axis
    ygrid -- toggles the grid running along the Y axis
    xtitle -- sets the title of a horizontal axis
    ytitle -- sets the title of a vertical axis
    title -- sets the title of the plot


    Tools
    -----
    colormap -- sets the current colormap    
    """
    print chaco_commands.__doc__

    # The following are not implemented yet
    """
    tool -- toggles certain tools on or off
    save -- saves the current plot to a file
    load -- loads a saved plot from file into the active plot area

    Layout
    ------
    names -- temporarily overlays plot areas with their names
    hidenames -- force remove the name overlays from show_names
    happend -- create a new plot area horizontally after the active plot
    vappend -- create a new plot area vertically after the active plot
    hsplit -- splits the current plot into two horizontal subplots
    vsplit -- splits the current plot into two vertical subplots
    save_layout -- saves the current layout of plots and plots areas
    load_layout -- loads a saved layout of plot areas and applies it to the
                   current set of plots

    Sessions
    --------
    save_session -- saves the current "workspace", defined as the set of
                    active windows and plots
    load_session -- restores a previously-saved session
    save_prefs -- saves the current session's preferences, either in a
                  separate file or as the chaco2.shell defaults
    load_prefs -- loads a previously-saved set of preferences
    """

#------------------------------------------------------------------------
# Window management commands
#------------------------------------------------------------------------

def figure(name=None, title=None):
    """ Creates a new figure window and returns its index
    
    figure(name=None, title=None)

    name: an optional string indicating the name to use for this window.
          If this is provided, then this name can be used instead of
          the window's integer index in other window-related functions.
    
    title: if this is provided, then sets the title of the plot window.
           If this is blank but 'name' is provided, then that is used.
           If neither are name nor title are provided, then uses the
           value of default_window_name in the Preferences.
    """
    win = session.new_window(name, title)
    activate(win)
    return win


def activate(ident=None):
    """ Activates and raises a figure window
    
    activate(ident=None)

    ident: integer index or name of the window.  If neither is specified,
           then raises the currently active window.
    """
    if ident is not None:
        win = session.get_window(ident)
    else:
        win = session.active_window
    
    if win is not None:
        session.active_window = win
        win.raise_window()
    return

def show():
    """ Shows all the figure windows that have been created thus far, and
    creates a GUI main loop.  This is useful in scripts to show plots and
    keep their windows open, and has no effect when used from the interpreter
    prompt.
    """

    app = wx.GetApp()
    if not(app.IsMainLoopRunning()):
        frame = session.active_window
        app.SetTopWindow(frame)
        app.MainLoop()
    return


def close(ident=None):
    """ Closes a figure window
    
    close(ident=None):

    ident: integer index or name of the window to close, or "all".  If nothing
           is specified, then closes the active window.
    """
    win_list = []
    if ident is None:
        win_list.append(session.active_window)
    elif ident == 'all':
        win_list = session.windows
    else:
        win_list.append(session.get_window(ident))
    
    for win in win_list:
        win.close()
    return

def colormap(map):
    """Sets the active colormap
    
    colormap(hsv)

    map: a string naming a default colormap, or a callable returning an
         AbstractColorMap
    """
    if isinstance(map, basestring):
        session.colormap = color_map_name_dict[map]
    else:
        session.colormap = map
    

def hold(state=None):
    """ Turns "hold" on or off, or toggles the current state if none
    is given.

    Usage: hold([True|False])
    """
    if state is None:
        session.hold = not session.hold
    else:
        session.hold = state
    return

def curplot():
    if session.active_window:
        return session.active_window.get_container()
    else:
        return None

#------------------------------------------------------------------------
# Plotting functions
#------------------------------------------------------------------------

def _do_plot_boilerplate(kwargs):
    """ Used by various plotting functions.  Checks/handles hold state,
    returns a Plot object for the plotting function to use.
    """
    
    if kwargs.has_key("hold"):
        hold(kwargs["hold"])
        del kwargs["hold"]

    # Check for an active window; if none, open one.
    if len(session.windows) == 0:
        figure()
        
    cont = session.active_window.get_container()

    if not cont:
        cont = Plot(session.data)
        session.active_window.set_container(cont)

    existing_tools = [type(t) for t in (cont.tools + cont.overlays)]
    if not PanTool in existing_tools:
        cont.tools.append(PanTool(cont))
#    if not RectZoomTool in existing_tools:
#        cont.overlays.append(RectZoomTool(cont, drag_button="right"))

    if not session.hold:
        cont.delplot(*cont.plots.keys())

    return cont


def plot(*data, **kwargs):
    """ Plots data in a matlab-compatible way.  Data is assumed to be
    X vs Y.  Any additional kwargs passed in are broadcast to all plots.

    Example:
        x = arange(-pi, pi, pi/100.)
        plot(x, sin(x), "b-")

    To use previous data, names can be provided instead of actual data arrays.
    """

    cont = _do_plot_boilerplate(kwargs)
    
    plots = plot_maker.do_plot(session.data, cont,
                               *data, **kwargs)

    cont.request_redraw()
    return


def semilogx(*data, **kwargs):
    """ Plots data on a semilog scale in a matlab-compatible way.  Data is 
    assumed to be X vs Y.  Any additional kwargs passed in are broadcast 
    to all plots.

    Example:
        x = linspace(0, 10.0 100)
        semilogx(x, sqrt(x), "b-")

    To use previous data, names can be provided instead of actual data arrays.

    Adding a semilog plot to an active plot with a currently different scale 
    will rescale the plot. 
    """
    kwargs["index_scale"] = "log"
    plot(*data, **kwargs)


def semilogy(*data, **kwargs):
    """ Plots data on a semilog scale in a matlab-compatible way.  Data is 
    assumed to be X vs Y.  Any additional kwargs passed in are broadcast 
    to all plots.

    Example:
        x = linspace(0, 10.0, 100)
        semilogy(x, exp(x), "b-")

    To use previous data, names can be provided instead of actual data arrays.

    Adding a semilog plot to an active plot with a currently different scale 
    will rescale the plot. 
    """
    kwargs["value_scale"] = "log"
    plot(*data, **kwargs)


def loglog(*data, **kwargs):
    """ Plots data on a log-log scale in a matlab-compatible way.  Data is 
    assumed to be X vs Y.  Any additional kwargs passed in are broadcast 
    to all plots.

    Example:
        x = linspace(0, 10.0, 100)
        loglog(x, x**2, "b-")

    To use previous data, names can be provided instead of actual data arrays.

    Adding a loglog plot to an active plot with a currently different scale 
    will rescale the plot. 
    """
    kwargs["index_scale"] = "log"
    kwargs["value_scale"] = "log"
    plot(*data, **kwargs)


def imread(*data, **kwargs):
    """ Returns image file as an array """

    return plot_maker.do_imread(*data, **kwargs)


def imshow(*data, **kwargs):
    """ Creates an image plot from a file on disk.  Will take either
    filename or image data.  Any additional kwargs passed in are broadcast
    to all plots.

    Example:
        imshow("example.jpg")

    Example2:
        image = ImageData.fromfile("example.jpg")
        imshow(image)

    To use previous data, names can be provided instead of filename or
    data arrays.

    """
    
    cont = _do_plot_boilerplate(kwargs)

    plots = plot_maker.do_imshow(session.data, cont,
                                 *data, **kwargs)

    cont.request_redraw()
    return


def pcolor(*data, **kwargs):
    """ Colormaps scalar data in a roughly matlab-compatible way. Data are 
    assumed to be a scalar image.  Any additional kwargs passed in are 
    broadcast to all plots.

    Example:
        xs = linspace(0,10,100)
        ys = linspace(0,20,200)
        x,y=meshgrid(xs,ys)
        z = sin(x)*y
        pcolor(x, y, z)

    To use previous data, names can be provided instead of actual data arrays.
    """

    cont = _do_plot_boilerplate(kwargs)

    plots = plot_maker.do_pcolor(session.data, session.colormap, cont, 
                                 *data, **kwargs)
    cont.request_redraw()
    return



def contour(*data, **kwargs):
    """ Contour line plots scalar data in a roughly matlab-compatible way.  
    Data are assumed to be a scalar image.  Any additional kwargs passed in 
    are broadcast to all plots.

    Example:
        xs = linspace(0,10,100)
        ys = linspace(0,20,200)
        x,y=meshgrid(xs,ys)
        z = sin(x)*y
        contour(z)

    To use previous data, names can be provided instead of actual data arrays.
    """

    cont = _do_plot_boilerplate(kwargs)

    plots = plot_maker.do_contour(session.data, session.colormap, cont, 
                                  "line", *data, **kwargs)
    cont.request_redraw()
    return



def contourf(*data, **kwargs):
    """ Contour polygon plots scalar data in a roughly matlab-compatible way.  
    Data are assumed to be a scalar image.  Any additional kwargs passed in 
    are broadcast to all plots.

    Example:
        xs = linspace(0,10,100)
        ys = linspace(0,20,200)
        x,y=meshgrid(xs,ys)
        z = sin(x)*y
        contourf(z)

    To use previous data, names can be provided instead of actual data arrays.
    """

    cont = _do_plot_boilerplate(kwargs)

    plots = plot_maker.do_contour(session.data, session.colormap, cont, 
                                  "poly", *data, **kwargs)
    cont.request_redraw()
    return



def plotv(*args, **kwargs):
    """ Creates a plot of a particular type, or using a "best guess"
    approach based on the data, using chaco semantics.
    
    plotv(data1, data2, ..., **keywords)
    
    The number and shape of data arrays determine how the data is
    interpreted, and how many plots are created.
    
    Single-dimensional arrays (shape = (N,))
    -------------------------
    1. Single array: the data is treated as the value array, and an index
       array is generated automatically using arange(len(value))
    2. Multiple arrays: the first array is treated as the index array, and
       each subsequent array is used as the value for a new plot.  All of
       the plots share a common index (first array).
    
    Multi-dimensional arrays (shape = (N,2) or (2,N))
    ------------------------
    1. Single array (NxM or MxN, N > M): interpreted as M-1 plots of
       N data points each, just like in the multiple 1D array case above.
    2. Multiple arrays: each array is treated as a separate set of inter-
       related plots, with its own index and value data sources
    
    Keyword arguments
    -----------------
    type: comma-separated combination of "line", "scatter", "polar"
    sort: "ascending", "descending", or "none", indicating the sorting order
          of the array that will be used as the index
    color: the color of the plot line and/or marker
    bgcolor: the background color of the plot
    grid: boolean specifying whether or not to draw a grid on the plot
    axis: boolean specifying whether or not to draw an axis on the plot
    orientation: "h" for index on the X axis, "v" for index on the Y axis
    
    Scatter plot keywords
    ---------------------
    marker: the type of marker to use (square, diamond, circle, cross,
            crossed circle, triangle, inverted triangle, plus, dot, pixel
    marker_size: the size (in pixels) of the marker
    outline_color: the color of the marker outline
    
    Line plot keywords
    ------------------
    width: the thickness of the line
    dash: the dash style to use (solid, dot dash, dash, dot, long dash)
    """
    
    cont = session.active_window.get_container()
    plots = plot_maker.do_plotv(session, *args, **kwargs)
    cont.add(*plots)
    return


#-----------------------------------------------------------------------------
# Annotations
#-----------------------------------------------------------------------------

def xtitle(text):
    """ Sets the horizontal axis label to the given text """
    p = curplot()
    if p:
        p.x_axis.title = text
        p.request_redraw()


def ytitle(text):
    """ Sets the vertical axis label to the given text """
    p = curplot()
    if p:
        p.y_axis.title = text
        p.request_redraw()

def title(text):
    """ Sets the plot title given text """
    p = curplot()
    if p:
        p.title = text
        p.request_redraw()

def xaxis(interval=None):
    """ Configures the xaxis.
    Usage:
        xaxis(): toggles the horizontal axis on or off
        xaxis(val): changes the xaxis interval between ticks to val
    """
    p = curplot()
    if p:
        if interval is not None:
            p.x_axis.tick_interval = interval
        else:
            p.x_axis.visible ^= True
        p.request_redraw()
        
def yaxis(interval=None):
    """ Configures the xaxis.
    Usage:
        yaxis(): toggles the vertical axis on or off
        yaxis(val): changes the yaxis interval between ticks to val
    """
    p = curplot()
    if p:
        if interval is not None:
            p.y_axis.tick_interval = interval
        else:
            p.y_axis.visible ^= True
        p.request_redraw()

def xgrid():
    """ Toggles the grid perpendicular to the X axis on and off """
    p = curplot()
    if p:
        p.x_grid.visible ^= True
        p.request_redraw()

def ygrid():
    """ Toggles the grid perpendicular to the Y axis on and off """
    p = curplot()
    if p:
        p.y_grid.visible ^= True
        p.request_redraw()
    
#-----------------------------------------------------------------------------
# Tools
#-----------------------------------------------------------------------------

def tool():
    """ Toggles tools on and off """
    p = curplot()
    if p:
        pass
    

# EOF
