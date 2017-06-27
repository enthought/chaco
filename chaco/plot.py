""" Defines the Plot class.
"""
# Major library imports
import itertools
import warnings
from numpy import arange, array, ndarray, linspace
from types import FunctionType

# Enthought library imports
from traits.api import Delegate, Dict, Instance, Int, List, Property, Str

# Local, relative imports
from abstract_colormap import AbstractColormap
from abstract_data_source import AbstractDataSource
from abstract_plot_data import AbstractPlotData
from array_data_source import ArrayDataSource
from array_plot_data import ArrayPlotData
from base_xy_plot import BaseXYPlot
from barplot import BarPlot
from candle_plot import CandlePlot
from colormapped_scatterplot import ColormappedScatterPlot
from contour_line_plot import ContourLinePlot
from contour_poly_plot import ContourPolyPlot
from cmap_image_plot import CMapImagePlot
from data_range_1d import DataRange1D
from data_view import DataView
from default_colormaps import Spectral
from grid_data_source import GridDataSource
from grid_mapper import GridMapper
from image_data import ImageData
from image_plot import ImagePlot
from legend import Legend
from lineplot import LinePlot
from line_scatterplot_1d import LineScatterPlot1D
from linear_mapper import LinearMapper
from log_mapper import LogMapper
from plot_label import PlotLabel
from polygon_plot import PolygonPlot
from scatterplot import ScatterPlot
from scatterplot_1d import ScatterPlot1D
from text_plot_1d import TextPlot1D
from filled_line_plot import FilledLinePlot
from quiverplot import QuiverPlot
from jitterplot import JitterPlot




#-----------------------------------------------------------------------------
# The Plot class
#-----------------------------------------------------------------------------

class Plot(DataView):
    """ Represents a correlated set of data, renderers, and axes in a single
    screen region.

    A Plot can reference an arbitrary amount of data and can have an
    unlimited number of renderers on it, but it has a single X-axis and a
    single Y-axis for all of its associated data. Therefore, there is a single
    range in X and Y, although there can be many different data series. A Plot
    also has a single set of grids and a single background layer for all of its
    renderers.  It cannot be split horizontally or vertically; to do so,
    create a VPlotContainer or HPlotContainer and put the Plots inside those.
    Plots can be overlaid as well; be sure to set the **bgcolor** of the
    overlaying plots to "none" or "transparent".

    A Plot consists of composable sub-plots.  Each of these is created
    or destroyed using the plot() or delplot() methods.  Every time that
    new data is used to drive these sub-plots, it is added to the Plot's
    list of data and data sources.  Data sources are reused whenever
    possible; in order to have the same actual array drive two de-coupled
    data sources, create those data sources before handing them to the Plot.
    """

    #------------------------------------------------------------------------
    # Data-related traits
    #------------------------------------------------------------------------

    # The PlotData instance that drives this plot.
    data = Instance(AbstractPlotData)

    # Mapping of data names from self.data to their respective datasources.
    datasources = Dict(Str, Instance(AbstractDataSource))

    #------------------------------------------------------------------------
    # General plotting traits
    #------------------------------------------------------------------------

    # Mapping of plot names to *lists* of plot renderers.
    plots = Dict(Str, List)

    # The default index to use when adding new subplots.
    default_index = Instance(AbstractDataSource)

    # Optional mapper for the color axis.  Not instantiated until first use;
    # destroyed if no color plots are on the plot.
    color_mapper = Instance(AbstractColormap)

    # List of colors to cycle through when auto-coloring is requested. Picked
    # and ordered to be red-green color-blind friendly, though should not
    # be an issue for blue-yellow.
    auto_colors = List(["green", "lightgreen", "blue", "lightblue", "red",
                        "pink", "darkgray", "silver"])

    # index into auto_colors list
    _auto_color_idx = Int(-1)
    _auto_edge_color_idx = Int(-1)
    _auto_face_color_idx = Int(-1)

    # Mapping of renderer type string to renderer class
    # This can be overriden to customize what renderer type the Plot
    # will instantiate for its various plotting methods.
    renderer_map = Dict(dict(line = LinePlot,
                             bar = BarPlot,
                             scatter = ScatterPlot,
                             polygon = PolygonPlot,
                             filled_line = FilledLinePlot,
                             cmap_scatter = ColormappedScatterPlot,
                             img_plot = ImagePlot,
                             cmap_img_plot = CMapImagePlot,
                             contour_line_plot = ContourLinePlot,
                             contour_poly_plot = ContourPolyPlot,
                             candle = CandlePlot,
                             quiver = QuiverPlot,
                             scatter_1d = ScatterPlot1D,
                             textplot_1d = TextPlot1D,
                             line_scatter_1d = LineScatterPlot1D,
                             jitterplot = JitterPlot))

    #------------------------------------------------------------------------
    # Annotations and decorations
    #------------------------------------------------------------------------

    # The title of the plot.
    title = Property()

    # The font to use for the title.
    title_font = Property()

    # Convenience attribute for title.overlay_position; can be "top",
    # "bottom", "left", or "right".
    title_position = Property()

    # Use delegates to expose the other PlotLabel attributes of the plot title
    title_text = Delegate("_title", prefix="text", modify=True)
    title_color = Delegate("_title", prefix="color", modify=True)
    title_angle = Delegate("_title", prefix="angle", modify=True)

    # The PlotLabel object that contains the title.
    _title = Instance(PlotLabel)

    # The legend on the plot.
    legend = Instance(Legend)

    # Convenience attribute for legend.align; can be "ur", "ul", "ll", "lr".
    legend_alignment = Property

    #------------------------------------------------------------------------
    # Public methods
    #------------------------------------------------------------------------

    def __init__(self, data=None, **kwtraits):
        if 'origin' in kwtraits:
            self.default_origin = kwtraits.pop('origin')
        if "title" in kwtraits:
            title = kwtraits.pop("title")
        else:
            title = None
        super(Plot, self).__init__(**kwtraits)
        if data is not None:
            if isinstance(data, AbstractPlotData):
                self.data = data
            elif type(data) in (ndarray, tuple, list):
                self.data = ArrayPlotData(data)
            else:
                raise ValueError("Don't know how to create PlotData for data"
                                 "of type {}".format(type(data)))

        if not self._title:
            self._title = PlotLabel(font="swiss 16", visible=False,
                                   overlay_position="top", component=self)
        if title is not None:
            self.title = title

        if not self.legend:
            self.legend = Legend(visible=False, align="ur", error_icon="blank",
                                 padding=10, component=self)

        # ensure that we only get displayed once by new_window()
        self._plot_ui_info = None

        return

    def add_xy_plot(self, index_name, value_name, renderer_factory, name=None,
        origin=None, **kwds):
        """ Add a BaseXYPlot renderer subclass to this Plot.

        Parameters
        ----------
        index_name : str
            The name of the index datasource.
        value_name : str
            The name of the value datasource.
        renderer_factory : callable
            The callable that creates the renderer.
        name : string (optional)
            The name of the plot.  If None, then a default one is created
            (usually "plotNNN").
        origin : string (optional)
            Which corner the origin of this plot should occupy:
                "bottom left", "top left", "bottom right", "top right"
        **kwds :
            Additional keywords to pass to the factory.
        """
        if name is None:
            name = self._make_new_plot_name()
        if origin is None:
            origin = self.default_origin
        index = self._get_or_create_datasource(index_name)
        self.index_range.add(index)
        value = self._get_or_create_datasource(value_name)
        self.value_range.add(value)

        if self.index_scale == "linear":
            imap = LinearMapper(range=self.index_range)
        else:
            imap = LogMapper(range=self.index_range)
        if self.value_scale == "linear":
            vmap = LinearMapper(range=self.value_range)
        else:
            vmap = LogMapper(range=self.value_range)

        renderer = renderer_factory(
            index = index,
            value = value,
            index_mapper = imap,
            value_mapper = vmap,
            orientation = self.orientation,
            origin = origin,
            **kwds
        )
        self.add(renderer)
        self.plots[name] = [renderer]
        self.invalidate_and_redraw()
        return self.plots[name]

    def plot(self, data, type="line", name=None, index_scale="linear",
             value_scale="linear", origin=None, **styles):
        """ Adds a new sub-plot using the given data and plot style.

        Parameters
        ----------
        data : string, tuple(string), list(string)
            The data to be plotted. The type of plot and the number of
            arguments determines how the arguments are interpreted:

            one item: (line/scatter)
                The data is treated as the value and self.default_index is
                used as the index.  If **default_index** does not exist, one is
                created from arange(len(*data*))
            two or more items: (line/scatter)
                Interpreted as (index, value1, value2, ...).  Each index,value
                pair forms a new plot of the type specified.
            two items: (cmap_scatter)
                Interpreted as (value, color_values).  Uses **default_index**.
            three or more items: (cmap_scatter)
                Interpreted as (index, val1, color_val1, val2, color_val2, ...)

        type : comma-delimited string of "line", "scatter", "cmap_scatter"
            The types of plots to add.
        name : string
            The name of the plot.  If None, then a default one is created
            (usually "plotNNN").
        index_scale : string
            The type of scale to use for the index axis. If not "linear", then
            a log scale is used.
        value_scale : string
            The type of scale to use for the value axis. If not "linear", then
            a log scale is used.
        origin : string
            Which corner the origin of this plot should occupy:
                "bottom left", "top left", "bottom right", "top right"
        styles : series of keyword arguments
            attributes and values that apply to one or more of the
            plot types requested, e.g.,'line_color' or 'line_width'.

        Examples
        --------
        ::

            plot("my_data", type="line", name="myplot", color=lightblue)

            plot(("x-data", "y-data"), type="scatter")

            plot(("x", "y1", "y2", "y3"))

        Returns
        -------
        [renderers] -> list of renderers created in response to this call to plot()
        """
        if len(data) == 0:
            return

        if isinstance(data, basestring):
            data = (data,)

        self.index_scale = index_scale
        self.value_scale = value_scale

        # TODO: support lists of plot types
        plot_type = type
        if name is None:
            name = self._make_new_plot_name()
        if origin is None:
            origin = self.default_origin

        if plot_type in ("line", "scatter", "polygon", "bar", "filled_line"):
            # Tie data to the index range
            if len(data) == 1:
                if self.default_index is None:
                    # Create the default index based on the length of the first
                    # data series
                    value = self._get_or_create_datasource(data[0])
                    self.default_index = ArrayDataSource(arange(len(value.get_data())),
                                                         sort_order="none")
                    self.index_range.add(self.default_index)
                index = self.default_index
            else:
                index = self._get_or_create_datasource(data[0])
                if self.default_index is None:
                    self.default_index = index
                self.index_range.add(index)
                data = data[1:]

            # Tie data to the value_range and create the renderer for each data
            new_plots = []
            simple_plot_types = ("line", "scatter")
            for value_name in data:
                value = self._get_or_create_datasource(value_name)
                self.value_range.add(value)
                if plot_type in simple_plot_types:
                    cls = self.renderer_map[plot_type]
                    # handle auto-coloring request
                    if styles.get("color") == "auto":
                        self._auto_color_idx = \
                            (self._auto_color_idx + 1) % len(self.auto_colors)
                        styles["color"] = self.auto_colors[self._auto_color_idx]
                elif plot_type in ("polygon", "filled_line"):
                    cls = self.renderer_map[plot_type]
                    # handle auto-coloring request
                    if styles.get("edge_color") == "auto":
                        self._auto_edge_color_idx = \
                            (self._auto_edge_color_idx + 1) % len(self.auto_colors)
                        styles["edge_color"] = self.auto_colors[self._auto_edge_color_idx]
                    if styles.get("face_color") == "auto":
                        self._auto_face_color_idx = \
                            (self._auto_face_color_idx + 1) % len(self.auto_colors)
                        styles["face_color"] = self.auto_colors[self._auto_face_color_idx]
                elif plot_type == 'bar':
                    cls = self.renderer_map[plot_type]
                    # handle auto-coloring request
                    if styles.get("color") == "auto":
                        self._auto_color_idx = \
                            (self._auto_color_idx + 1) % len(self.auto_colors)
                        styles["fill_color"] = self.auto_colors[self._auto_color_idx]
                else:
                    raise ValueError("Unhandled plot type: " + plot_type)

                if self.index_scale == "linear":
                    imap = LinearMapper(range=self.index_range,
                                stretch_data=self.index_mapper.stretch_data)
                else:
                    imap = LogMapper(range=self.index_range,
                                stretch_data=self.index_mapper.stretch_data)
                if self.value_scale == "linear":
                    vmap = LinearMapper(range=self.value_range,
                                stretch_data=self.value_mapper.stretch_data)
                else:
                    vmap = LogMapper(range=self.value_range,
                                stretch_data=self.value_mapper.stretch_data)

                plot = cls(index=index,
                           value=value,
                           index_mapper=imap,
                           value_mapper=vmap,
                           orientation=self.orientation,
                           origin = origin,
                           **styles)

                self.add(plot)
                new_plots.append(plot)

            if plot_type == 'bar':
                # For bar plots, compute the ranges from the data to make the
                # plot look clean.

                def custom_index_func(data_low, data_high, margin, tight_bounds):
                    """ Compute custom bounds of the plot along index (in
                    data space).
                    """
                    bar_width = styles.get('bar_width', cls().bar_width)
                    plot_low = data_low - bar_width
                    plot_high = data_high + bar_width
                    return plot_low, plot_high

                if self.index_range.bounds_func is None:
                    self.index_range.bounds_func = custom_index_func

                def custom_value_func(data_low, data_high, margin, tight_bounds):
                    """ Compute custom bounds of the plot along value (in
                    data space).
                    """
                    plot_low = data_low - (data_high-data_low)*0.1
                    plot_high = data_high + (data_high-data_low)*0.1
                    return plot_low, plot_high

                if self.value_range.bounds_func is None:
                    self.value_range.bounds_func = custom_value_func

                self.index_range.tight_bounds = False
                self.value_range.tight_bounds = False
                self.index_range.refresh()
                self.value_range.refresh()

            self.plots[name] = new_plots

        elif plot_type == "cmap_scatter":
            if len(data) != 3:
                raise ValueError("Colormapped scatter plots require (index, value, color) data")
            else:
                index = self._get_or_create_datasource(data[0])
                if self.default_index is None:
                    self.default_index = index
                self.index_range.add(index)
                value = self._get_or_create_datasource(data[1])
                self.value_range.add(value)
                color = self._get_or_create_datasource(data[2])
                if not styles.has_key("color_mapper"):
                    raise ValueError("Scalar 2D data requires a color_mapper.")

                colormap = styles.pop("color_mapper", None)

                if self.color_mapper is not None and self.color_mapper.range is not None:
                    color_range = self.color_mapper.range
                else:
                    color_range = DataRange1D()

                if isinstance(colormap, AbstractColormap):
                    self.color_mapper = colormap
                    if colormap.range is None:
                        color_range.add(color)
                        colormap.range = color_range

                elif callable(colormap):
                    color_range.add(color)
                    self.color_mapper = colormap(color_range)
                else:
                    raise ValueError("Unexpected colormap %r in plot()." % colormap)

                if self.index_scale == "linear":
                    imap = LinearMapper(range=self.index_range,
                                stretch_data=self.index_mapper.stretch_data)
                else:
                    imap = LogMapper(range=self.index_range,
                                stretch_data=self.index_mapper.stretch_data)
                if self.value_scale == "linear":
                    vmap = LinearMapper(range=self.value_range,
                                stretch_data=self.value_mapper.stretch_data)
                else:
                    vmap = LogMapper(range=self.value_range,
                                stretch_data=self.value_mapper.stretch_data)

                cls = self.renderer_map["cmap_scatter"]
                plot = cls(index=index,
                           index_mapper=imap,
                           value=value,
                           value_mapper=vmap,
                           color_data=color,
                           color_mapper=self.color_mapper,
                           orientation=self.orientation,
                           origin=origin,
                           **styles)
                self.add(plot)

            self.plots[name] = [plot]
        else:
            raise ValueError("Unknown plot type: " + plot_type)

        return self.plots[name]


    def img_plot(self, data, name=None, colormap=None,
                 xbounds=None, ybounds=None, origin=None, hide_grids=True,
                 **styles):
        """ Adds image plots to this Plot object.

        If *data* has shape (N, M, 3) or (N, M, 4), then it is treated as RGB or
        RGBA (respectively) and *colormap* is ignored.

        If *data* is an array of floating-point data, then a colormap can
        be provided via the *colormap* argument, or the default of 'Spectral'
        will be used.

        *Data* should be in row-major order, so that xbounds corresponds to
        *data*'s second axis, and ybounds corresponds to the first axis.

        Parameters
        ----------
        data : string
            The name of the data array in self.plot_data
        name : string
            The name of the plot; if omitted, then a name is generated.
        xbounds, ybounds : string, tuple, or ndarray
            Bounds where this image resides. Bound may be: a) names of
            data in the plot data; b) tuples of (low, high) in data space,
            c) 1D arrays of values representing the pixel boundaries (must
            be 1 element larger than underlying data), or
            d) 2D arrays as obtained from a meshgrid operation
        origin : string
            Which corner the origin of this plot should occupy:
                "bottom left", "top left", "bottom right", "top right"
        hide_grids : bool, default True
            Whether or not to automatically hide the grid lines on the plot
        styles : series of keyword arguments
            Attributes and values that apply to one or more of the
            plot types requested, e.g.,'line_color' or 'line_width'.
        """
        if name is None:
            name = self._make_new_plot_name()
        if origin is None:
            origin = self.default_origin

        value = self._get_or_create_datasource(data)
        array_data = value.get_data()
        if len(array_data.shape) == 3:
            if array_data.shape[2] not in (3,4):
                raise ValueError("Image plots require color depth of 3 or 4.")
            cls = self.renderer_map["img_plot"]
            kwargs = dict(**styles)
        else:
            if colormap is None:
                if self.color_mapper is None:
                    colormap = Spectral(DataRange1D(value))
                else:
                    colormap = self.color_mapper
            elif isinstance(colormap, AbstractColormap):
                if colormap.range is None:
                    colormap.range = DataRange1D(value)
            else:
                colormap = colormap(DataRange1D(value))
            self.color_mapper = colormap
            cls = self.renderer_map["cmap_img_plot"]
            kwargs = dict(value_mapper=colormap, **styles)
        return self._create_2d_plot(cls, name, origin, xbounds, ybounds, value,
                                    hide_grids, cell_plot=True, **kwargs)


    def contour_plot(self, data, type="line", name=None, poly_cmap=None,
                     xbounds=None, ybounds=None, origin=None, hide_grids=True, **styles):
        """ Adds contour plots to this Plot object.

        Parameters
        ----------
        data : string
            The name of the data array in self.plot_data, which must be
            floating point data.
        type : comma-delimited string of "line", "poly"
            The type of contour plot to add. If the value is "poly"
            and no colormap is provided via the *poly_cmap* argument, then
            a default colormap of 'Spectral' is used.
        name : string
            The name of the plot; if omitted, then a name is generated.
        poly_cmap : string
            The name of the color-map function to call (in
            chaco.default_colormaps) or an AbstractColormap instance
            to use for contour poly plots (ignored for contour line plots)
        xbounds, ybounds : string, tuple, or ndarray
            Bounds where this image resides. Bound may be: a) names of
            data in the plot data; b) tuples of (low, high) in data space,
            c) 1D arrays of values representing the pixel boundaries (must
            be 1 element larger than underlying data), or
            d) 2D arrays as obtained from a meshgrid operation
        origin : string
            Which corner the origin of this plot should occupy:
                "bottom left", "top left", "bottom right", "top right"
        hide_grids : bool, default True
            Whether or not to automatically hide the grid lines on the plot
        styles : series of keyword arguments
            Attributes and values that apply to one or more of the
            plot types requested, e.g.,'line_color' or 'line_width'.
        """
        if name is None:
            name = self._make_new_plot_name()
        if origin is None:
            origin = self.default_origin

        value = self._get_or_create_datasource(data)
        if value.value_depth != 1:
            raise ValueError("Contour plots require 2D scalar field")
        if type == "line":
            cls = self.renderer_map["contour_line_plot"]
            kwargs = dict(**styles)
            # if colors is given as a factory func, use it to make a
            # concrete colormapper. Better way to do this?
            if "colors" in kwargs:
                cmap = kwargs["colors"]
                if isinstance(cmap, FunctionType):
                    kwargs["colors"] = cmap(DataRange1D(value))
                elif getattr(cmap, 'range', 'dummy') is None:
                    cmap.range = DataRange1D(value)
        elif type == "poly":
            if poly_cmap is None:
                poly_cmap = Spectral(DataRange1D(value))
            elif isinstance(poly_cmap, FunctionType):
                poly_cmap = poly_cmap(DataRange1D(value))
            elif getattr(poly_cmap, 'range', 'dummy') is None:
                poly_cmap.range = DataRange1D(value)
            cls = self.renderer_map["contour_poly_plot"]
            kwargs = dict(color_mapper=poly_cmap, **styles)
        else:
            raise ValueError("Unhandled contour plot type: " + type)

        return self._create_2d_plot(cls, name, origin, xbounds, ybounds, value,
                                    hide_grids, cell_plot=False, **kwargs)


    def _process_2d_bounds(self, bounds, array_data, axis, cell_plot):
        """Transform an arbitrary bounds definition into a linspace.

        Process all the ways the user could have defined the x- or y-bounds
        of a 2d plot and return a linspace between the lower and upper
        range of the bounds.

        Parameters
        ----------
        bounds : any
            User bounds definition

        array_data : 2D array
            The 2D plot data

        axis : int
            The axis along which the bounds are to be set

        cell_plot : bool
            Is the data plotted at the vertices or in the cells bounded by
            the grid (eg. contour plot vs. image plot)
        """

        if cell_plot:
            num_ticks = array_data.shape[axis] + 1
        else:
            num_ticks = array_data.shape[axis]

        if bounds is None:
            return arange(num_ticks)

        if isinstance(bounds, tuple):
            # create a linspace with the bounds limits
            return linspace(bounds[0], bounds[1], num_ticks)

        elif isinstance(bounds, ndarray) and bounds.ndim == 1:
            if len(bounds) != num_ticks:
                # bounds is 1D, but of the wrong size
                msg = ("1D bounds of an image plot needs to have 1 more "
                       "element than its corresponding data shape, because "
                       "they represent the locations of pixel boundaries.")
                raise ValueError(msg)
            else:
                return bounds

        elif isinstance(bounds, ndarray) and bounds.ndim == 2:
            # bounds is 2D, assumed to be a meshgrid
            # This is triggered when doing something like
            # >>> xbounds, ybounds = meshgrid(...)
            if bounds.shape[axis] != num_ticks:
                msg = ("2D bounds of an image plot needs to have the same "
                       "shape as the underlying data, because "
                       "they are assumed to be generated from meshgrids.")
                raise ValueError(msg)
            else:
                if axis == 0:
                    bounds = bounds[:,0]
                else:
                    bounds = bounds[0,:]
                return bounds

        raise ValueError("bounds must be None, a tuple, an array, "
                         "or a PlotData name")


    def _create_2d_plot(self, cls, name, origin, xbounds, ybounds, value_ds,
                        hide_grids, cell_plot=False, **kwargs):
        if name is None:
            name = self._make_new_plot_name()
        if origin is None:
            origin = self.default_origin

        array_data = value_ds.get_data()

        # process bounds to get linspaces
        if isinstance(xbounds, basestring):
            xbounds = self._get_or_create_datasource(xbounds).get_data()

        xs = self._process_2d_bounds(xbounds, array_data, 1, cell_plot)

        if isinstance(ybounds, basestring):
            ybounds = self._get_or_create_datasource(ybounds).get_data()

        ys = self._process_2d_bounds(ybounds, array_data, 0, cell_plot)

        # Create the index and add its datasources to the appropriate ranges
        index = GridDataSource(xs, ys, sort_order=('ascending', 'ascending'))
        self.range2d.add(index)
        mapper = GridMapper(range=self.range2d,
                            stretch_data_x=self.x_mapper.stretch_data,
                            stretch_data_y=self.y_mapper.stretch_data)

        plot = cls(index=index,
                   value=value_ds,
                   index_mapper=mapper,
                   orientation=self.orientation,
                   origin=origin,
                   **kwargs)

        if hide_grids:
            self.x_grid.visible = False
            self.y_grid.visible = False

        self.add(plot)
        self.plots[name] = [plot]
        return self.plots[name]


    def candle_plot(self, data, name=None, value_scale="linear", origin=None,
                    **styles):
        """ Adds a new sub-plot using the given data and plot style.

        Parameters
        ----------
        data : list(string), tuple(string)
            The names of the data to be plotted in the ArrayDataSource.  The
            number of arguments determines how they are interpreted:

            (index, bar_min, bar_max)
                filled or outline-only bar extending from **bar_min** to
                **bar_max**

            (index, bar_min, center, bar_max)
                above, plus a center line of a different color at **center**

            (index, min, bar_min, bar_max, max)
                bar extending from **bar_min** to **bar_max**, with thin
                bars at **min** and **max** connected to the bar by a long
                stem

            (index, min, bar_min, center, bar_max, max)
                like above, plus a center line of a different color and
                configurable thickness at **center**

        name : string
            The name of the plot.  If None, then a default one is created.

        value_scale : string
            The type of scale to use for the value axis.  If not "linear",
            then a log scale is used.

        Styles
        ------
        These are all optional keyword arguments.

        bar_color : string, 3- or 4-tuple
            The fill color of the bar; defaults to "auto".
        bar_line_color : string, 3- or 4-tuple
            The color of the rectangular box forming the bar.
        stem_color : string, 3- or 4-tuple (default = bar_line_color)
            The color of the stems reaching from the bar to the min and
            max values.
        center_color : string, 3- or 4-tuple (default = bar_line_color)
            The color of the line drawn across the bar at the center values.
        line_width : int (default = 1)
            The thickness, in pixels, of the outline around the bar.
        stem_width : int (default = line_width)
            The thickness, in pixels, of the stem lines
        center_width : int (default = line_width)
            The width, in pixels, of the line drawn across the bar at the
            center values.
        end_cap : bool (default = True)
            Whether or not to draw bars at the min and max extents of the
            error bar.

        Returns
        -------
        [renderers] -> list of renderers created in response to this call.
        """
        if len(data) == 0:
            return
        self.value_scale = value_scale

        if name is None:
            name = self._make_new_plot_name()
        if origin is None:
            origin = self.default_origin

        # Create the datasources
        if len(data) == 3:
            index, bar_min, bar_max = map(self._get_or_create_datasource, data)
            self.value_range.add(bar_min, bar_max)
            center = None
            min = None
            max = None
        elif len(data) == 4:
            index, bar_min, center, bar_max = map(self._get_or_create_datasource, data)
            self.value_range.add(bar_min, center, bar_max)
            min = None
            max = None
        elif len(data) == 5:
            index, min, bar_min, bar_max, max = \
                            map(self._get_or_create_datasource, data)
            self.value_range.add(min, bar_min, bar_max, max)
            center = None
        elif len(data) == 6:
            index, min, bar_min, center, bar_max, max = \
                            map(self._get_or_create_datasource, data)
            self.value_range.add(min, bar_min, center, bar_max, max)
        self.index_range.add(index)

        if styles.get("bar_color") == "auto" or styles.get("color") == "auto":
            self._auto_color_idx = \
                (self._auto_color_idx + 1) % len(self.auto_colors)
            styles["color"] = self.auto_colors[self._auto_color_idx]

        if self.index_scale == "linear":
            imap = LinearMapper(range=self.index_range,
                        stretch_data=self.index_mapper.stretch_data)
        else:
            imap = LogMapper(range=self.index_range,
                        stretch_data=self.index_mapper.stretch_data)
        if self.value_scale == "linear":
            vmap = LinearMapper(range=self.value_range,
                        stretch_data=self.value_mapper.stretch_data)
        else:
            vmap = LogMapper(range=self.value_range,
                        stretch_data=self.value_mapper.stretch_data)

        cls = self.renderer_map["candle"]
        plot = cls(index = index,
                          min_values = min,
                          bar_min = bar_min,
                          center_values = center,
                          bar_max = bar_max,
                          max_values = max,
                          index_mapper = imap,
                          value_mapper = vmap,
                          orientation = self.orientation,
                          origin = self.origin,
                          **styles)
        self.add(plot)
        self.plots[name] = [plot]
        return [plot]

    def quiverplot(self, data, name=None, origin=None,
                    **styles):
        """ Adds a new sub-plot using the given data and plot style.

        Parameters
        ----------
        data : list(string), tuple(string)
            The names of the data to be plotted in the ArrayDataSource.  There
            is only one combination accepted by this function:

            (index, value, vectors)
                index and value together determine the start coordinates of
                each vector.  The vectors are an Nx2

        name : string
            The name of the plot.  If None, then a default one is created.

        origin : string
            Which corner the origin of this plot should occupy:
                "bottom left", "top left", "bottom right", "top right"

        Styles
        ------
        These are all optional keyword arguments.

        line_color : string (default = "black")
            The color of the arrows
        line_width : float (default = 1.0)
            The thickness, in pixels, of the arrows.
        arrow_size : int (default = 5)
            The length, in pixels, of the arrowhead

        Returns
        -------
        [renderers] -> list of renderers created in response to this call.
        """
        if name is None:
            name = self._make_new_plot_name()
        if origin is None:
            origin = self.default_origin

        index, value, vectors = map(self._get_or_create_datasource, data)

        self.index_range.add(index)
        self.value_range.add(value)

        imap = LinearMapper(range=self.index_range,
                            stretch_data=self.index_mapper.stretch_data)
        vmap = LinearMapper(range=self.value_range,
                            stretch_data=self.value_mapper.stretch_data)

        cls = self.renderer_map["quiver"]
        plot = cls(index = index,
                   value = value,
                   vectors = vectors,
                   index_mapper = imap,
                   value_mapper = vmap,
                   name = name,
                   origin = origin,
                   **styles
                   )
        self.add(plot)
        self.plots[name] = [plot]
        return [plot]

    def plot_1d(self, data, type='scatter_1d', name=None, orientation=None,
                direction=None, scale="linear", **styles):
        """ Adds a new sub-plot using the given data and plot style.

        Parameters
        ----------
        data : string, tuple(string), list(string)
            The data to be plotted. The each item generates a separate renderer
            using the named data source
        type : string
            The type of plots to add.  One of  of "scatter_1d",
            "line_scatter_1d", "textplot_1d", "jitterplot"
        name : string
            The name of the plot.  If None, then a default one is created
            (usually "plotNNN").
        scale : string
            The type of scale to use for the index axis. If not "linear", then
            a log scale is used.
        orientation : string
            Whether the single dimension is horizontal ('h') or vertical ('v').
        direction : string
            Whether data is mapped in the usual direction (left to right or
            bottom to top) or reversed.
        styles : series of keyword arguments
            attributes and values that apply to one or more of the
            plot types requested, e.g.,'line_color' or 'line_width'.

        Returns
        -------
        [renderers] -> list of renderers created in response to this call to plot()
        """

        if len(data) == 0:
            return

        if isinstance(data, basestring):
            data = (data,)

        # TODO: support lists of plot types
        plot_type = type
        if name is None:
            name = self._make_new_plot_name()

        if orientation is None:
            orientation = self.orientation

        if direction is None:
            if orientation == 'v':
                if "bottom" in self.origin:
                    direction = 'normal'
                else:
                    direction = 'flipped'
            else:
                if "left" in self.origin:
                    direction = 'normal'
                else:
                    direction = 'flipped'

        plots = []
        if plot_type in ("scatter_1d", "textplot_1d", "line_scatter_1d",
                         "jitterplot"):
            # Tie data to the index range
            index = self._get_or_create_datasource(data[0])
            if self.default_index is None:
                self.default_index = index
            if orientation != self.orientation:
                index_range = self.value_range
                index_mapper = self.value_mapper
                self.value_scale = scale
            else:
                index_range = self.index_range
                index_mapper = self.index_mapper
                self.index_scale = scale
        else:
            raise ValueError("Unknown plot type: " + plot_type)

        if plot_type in ("scatter_1d", "line_scatter_1d", "jitterplot"):
            # simple 1d positional plots with no associated value
            for source in data:
                index = self._get_or_create_datasource(source)
                index_range.add(index)

                if scale == "linear":
                    imap = LinearMapper(range=index_range,
                                        stretch_data=index_mapper.stretch_data)
                else:
                    imap = LogMapper(range=index_range,
                                    stretch_data=index_mapper.stretch_data)

                cls = self.renderer_map[plot_type]
                plot = cls(index=index,
                            index_mapper=imap,
                            orientation=orientation,
                            direction=direction,
                            **styles)
                plots.append(plot)
                self.add(plot)
        elif plot_type in ("textplot_1d",):
            # simple positional plots with a single associated value
            for source in data[1:]:
                value = self._get_or_create_datasource(source)

                if scale == "linear":
                    imap = LinearMapper(range=index_range,
                                        stretch_data=index_mapper.stretch_data)
                else:
                    imap = LogMapper(range=index_range,
                                    stretch_data=index_mapper.stretch_data)
                cls = self.renderer_map[plot_type]
                plot = cls(index=index,
                           index_mapper=imap,
                           value=value,
                           orientation=orientation,
                           direction=direction,
                           **styles)
                plots.append(plot)
                self.add(plot)

        self.plots[name] = plots
        return plots


    def delplot(self, *names):
        """ Removes the named sub-plots. """

        # This process involves removing the plots, then checking the index range
        # and value range for leftover datasources, and removing those if necessary.

        # Remove all the renderers from us (container) and create a set of the
        # datasources that we might have to remove from the ranges
        deleted_sources = set()
        for renderer in itertools.chain(*[self.plots.pop(name) for name in names]):
            self.remove(renderer)
            deleted_sources.add(renderer.index)
            deleted_sources.add(renderer.value)

        # Cull the candidate list of sources to remove by checking the other plots
        sources_in_use = set()
        for p in itertools.chain(*self.plots.values()):
                sources_in_use.add(p.index)
                sources_in_use.add(p.value)

        unused_sources = deleted_sources - sources_in_use - set([None])

        # Remove the unused sources from all ranges
        for source in unused_sources:
            if source.index_dimension == "scalar":
                # Try both index and range, it doesn't hurt
                self.index_range.remove(source)
                self.value_range.remove(source)
            elif source.index_dimension == "image":
                self.range2d.remove(source)
            else:
                warnings.warn("Couldn't remove datasource from datarange.")

        return

    def hideplot(self, *names):
        """ Convenience function to sets the named plots to be invisible.  Their
        renderers are not removed, and they are still in the list of plots.
        """
        for renderer in itertools.chain(*[self.plots[name] for name in names]):
            renderer.visible = False
        return

    def showplot(self, *names):
        """ Convenience function to sets the named plots to be visible.
        """
        for renderer in itertools.chain(*[self.plots[name] for name in names]):
            renderer.visible = True
        return

    def new_window(self, configure=False):
        """Convenience function that creates a window containing the Plot

        Don't call this if the plot is already displayed in a window.
        """
        from chaco.ui.plot_window import PlotWindow
        if self._plot_ui_info is None:
            if configure:
                self._plot_ui_info = PlotWindow(plot=self).configure_traits()
            else:
                self._plot_ui_info = PlotWindow(plot=self).edit_traits()
        return self._plot_ui_info

    #------------------------------------------------------------------------
    # Private methods
    #------------------------------------------------------------------------



    def _make_new_plot_name(self):
        """ Returns a string that is not already used as a plot title.
        """
        n = len(self.plots)
        plot_template = "plot%d"
        while 1:
            name = plot_template % n
            if name not in self.plots:
                break
            else:
                n += 1
        return name

    def _get_or_create_datasource(self, name):
        """ Returns the data source associated with the given name, or creates
        it if it doesn't exist.
        """

        if name not in self.datasources:
            data = self.data.get_data(name)

            if type(data) in (list, tuple):
                data = array(data)

            if isinstance(data, ndarray):
                if len(data.shape) == 1:
                    ds = ArrayDataSource(data, sort_order="none")
                elif len(data.shape) == 2:
                    ds = ImageData(data=data, value_depth=1)
                elif len(data.shape) == 3 and data.shape[2] in (3,4):
                    ds = ImageData(data=data, value_depth=int(data.shape[2]))
                else:
                    raise ValueError("Unhandled array shape in creating new "
                                     "plot: %s" % str(data.shape))
            elif isinstance(data, AbstractDataSource):
                ds = data
            else:
                raise ValueError("Couldn't create datasource for data of "
                                 "type %s" % type(data))

            self.datasources[name] = ds

        return self.datasources[name]

    #------------------------------------------------------------------------
    # Event handlers
    #------------------------------------------------------------------------

    def _color_mapper_changed(self):
        for plist in self.plots.values():
            for plot in plist:
                plot.color_mapper = self.color_mapper
        self.invalidate_draw()

    def _data_changed(self, old, new):
        if old:
            old.on_trait_change(self._data_update_handler, "data_changed",
                                remove=True)
        if new:
            new.on_trait_change(self._data_update_handler, "data_changed")

    def _data_update_handler(self, name, event):
        # event should be a dict with keys "added", "removed", and "changed",
        # per the comments in AbstractPlotData.
        if "removed" in event:
            for name in event["removed"]:
                del self.datasources[name]

        if "added" in event:
            for name in event["added"]:
                self._get_or_create_datasource(name)

        if "changed" in event:
            for name in event["changed"]:
                if name in self.datasources:
                    source = self.datasources[name]
                    source.set_data(self.data.get_data(name))

    def _plots_items_changed(self, event):
        if self.legend:
            self.legend.plots = self.plots

    def _index_scale_changed(self, old, new):
        if old is None: return
        if new == old: return
        if not self.range2d: return
        if self.index_scale == "linear":
            imap = LinearMapper(range=self.index_range,
                                screen_bounds=self.index_mapper.screen_bounds,
                                stretch_data=self.index_mapper.stretch_data)
        else:
            imap = LogMapper(range=self.index_range,
                             screen_bounds=self.index_mapper.screen_bounds,
                             stretch_data=self.index_mapper.stretch_data)
        self.index_mapper = imap
        for key in self.plots:
            for plot in self.plots[key]:
                if not isinstance(plot, BaseXYPlot):
                    raise ValueError("log scale only supported on XY plots")
                if self.index_scale == "linear":
                    imap = LinearMapper(range=plot.index_range,
                                screen_bounds=plot.index_mapper.screen_bounds,
                                stretch_data=self.index_mapper.stretch_data)
                else:
                    imap = LogMapper(range=plot.index_range,
                                screen_bounds=plot.index_mapper.screen_bounds,
                                stretch_data=self.index_mapper.stretch_data)
                plot.index_mapper = imap

    def _value_scale_changed(self, old, new):
        if old is None: return
        if new == old: return
        if not self.range2d: return
        if self.value_scale == "linear":
            vmap = LinearMapper(range=self.value_range,
                                screen_bounds=self.value_mapper.screen_bounds,
                                stretch_data=self.value_mapper.stretch_data)
        else:
            vmap = LogMapper(range=self.value_range,
                             screen_bounds=self.value_mapper.screen_bounds,
                                stretch_data=self.value_mapper.stretch_data)
        self.value_mapper = vmap
        for key in self.plots:
            for plot in self.plots[key]:
                if not isinstance(plot, BaseXYPlot):
                    raise ValueError("log scale only supported on XY plots")
                if self.value_scale == "linear":
                    vmap = LinearMapper(range=plot.value_range,
                                screen_bounds=plot.value_mapper.screen_bounds,
                                stretch_data=self.value_mapper.stretch_data)
                else:
                    vmap = LogMapper(range=plot.value_range,
                                screen_bounds=plot.value_mapper.screen_bounds,
                                stretch_data=self.value_mapper.stretch_data)
                plot.value_mapper = vmap

    def __title_changed(self, old, new):
        self._overlay_change_helper(old, new)

    def _legend_changed(self, old, new):
        self._overlay_change_helper(old, new)
        if new:
            new.plots = self.plots

    def _handle_range_changed(self, name, old, new):
        """ Overrides the DataView default behavior.

        Primarily changes how the list of renderers is looked up.
        """
        mapper = getattr(self, name+"_mapper")
        if mapper.range == old:
            mapper.range = new
        if old is not None:
            for datasource in old.sources[:]:
                old.remove(datasource)
                if new is not None:
                    new.add(datasource)
        range_name = name + "_range"
        for renderer in itertools.chain(*self.plots.values()):
            if hasattr(renderer, range_name):
                setattr(renderer, range_name, new)

    #------------------------------------------------------------------------
    # Property getters and setters
    #------------------------------------------------------------------------

    def _set_legend_alignment(self, align):
        if self.legend:
            self.legend.align = align

    def _get_legend_alignment(self):
        if self.legend:
            return self.legend.align
        else:
            return None

    def _set_title(self, text):
        self._title.text = text
        if text.strip() != "":
            self._title.visible = True
        else:
            self._title.visible = False

    def _get_title(self):
        return self._title.text

    def _set_title_position(self, pos):
        if self._title is not None:
            self._title.overlay_position = pos

    def _get_title_position(self):
        if self._title is not None:
            return self._title.overlay_position
        else:
            return None

    def _set_title_font(self, font):
        old_font = self._title.font
        self._title.font = font
        self.trait_property_changed("title_font", old_font, font)

    def _get_title_font(self):
        return self._title.font
