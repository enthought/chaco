.. _fundamentals:

==================
Chaco Fundamentals
==================

While you can go a long way using the high-level APIs provided by the
:py:class:`~chaco.plot.Plot` class, to use Chaco to its full potential
it helps to have a deeper understanding of the building blocks of the
library.

Foundations
===========

Chaco relies on a number of underlying libraries for core capabilities.
Understanding these libraries is important for writing heavily interactive
visualizations, as well as new tools, overlays and plot renderers.

Traits
------

Chaco is written using `Traits <https://docs.enthought.com/traits/>`_ which not
only provides basic type-checking of data, but also attribute change
notification which is key to the interactive updating of Chaco.

You should be comfortable with Traits when writing any significant
Chaco-based application or when extending Chaco's capabilities.

TraitsUI
--------

`TraitsUI <https://docs.enthought.com/traitsui/>`_ is a rapid GUI application
development library built on top of Traits.  While it is not required for
the development of applications that use Chaco, it is the most natural way
of providing other UI elements for your users to interact with your
visualizations; or alternatively the most natural environment for writing
applications which embed Chaco plots.  Chaco also provides TraitsUI
views for configuring some Chaco objects.

You will need at least a basic familiarity with TraitsUI for most Chaco
use cases.

Kiva
----

`Kiva <https://docs.enthought.com/enable/kiva>`_ provides an abstracted 2D drawing
API and a number of back-end implementations.  This permits writing of
drawing code that can be used almost un-modified when rendering to a screen,
to a vector document format (such as PDF or PostScript), or to a raster file
format (such as PNG).

The core object for Kiva code is the "graphics context" which represents a
2D drawing surface and the current state of the drawing environment.  When
Chaco classes need to do any drawing they will usually be supplied with an
appropriate graphics context to render into, but very occasionally (such as
when saving a plot out to a file) you may want to create your own context to
draw into.

If you want to write new Chaco overlays or plot renderers you should develop
an understanding of Kiva.

Enable
------

`Enable <https://docs.enthought.com/enable/>`_ provides interactivity and layout
on top of the Kiva drawing library.  Enable is the library that handles the
interface between Chaco plots and the OS/windowing system, as well as the
basic hierarchical layout and layering of visible components of a plot.

Enable provides two base classes that are at the root of much of the Chaco
code:

:py:class:`~enable.component.Component`
    An object that occupies a rectangular region of the window and knows how
    to
    draw itself and dispatch user interactions.  The
    :py:class:`~enable.container.Container` class is a subclass of
    :py:class:`~enable.component.Component` that handles hierarchical layout
    and event dispatch.

    The drawing of :py:class:`~enable.component.Component` objects is split
    across a number of layers, so that overlays, underlays, borders and
    background can be rendered in a coherent manner.

:py:class:`~enable.base_tool.BaseTool`
    An object that handles a particular type of user interaction (eg. mouse
    events or key presses).  Each tool is a state machine and so the
    interactions can vary depending on the state that the tool is in (eg.
    "normal" vs. "dragging" state for a tool that handles moving
    interactions).

An understanding of Enable is important for writing new interactive tools, as
well as for understanding and controlling how components are layered and layed
out.

Chaco Object Model
==================

The :py:class:`~.chaco.plot.Plot` class provides a fairly simple API for
creating a plot in an application, but beneath that lies a set of classes
that handle converting the numbers in the numpy arrays into pixels on the
screen.  Between the :py:class:`~.chaco.array_plot_data.ArrayPlotData` and the
:py:class:`~.chaco.plot.Plot` are a series of classes which hold state for
various operations and transformations.

Data Flow
---------

The data flow between these classes can generally be sumarised as follows:

.. graphviz::

    digraph dataflow {
        rankdir=LR;
        node [shape=plaintext];
        "Plot Data" -> "Data sources" -> "Ranges" -> "Mappers" -> "Renderers" -> "Plot";
        "Data sources" ->  "Renderers";
        "Mappers" -> "Axes and Grids";
        "Pan and Zoom" -> "Ranges";
    }

Data sources
    These hold individual data sets from the plot data (ie. something that
    looks like a single NumPy array) and update when the data changes.

    Examples: :py:class:`~chaco.array_data_source.ArrayDataSource`,
    :py:class:`~chaco.image_data.ImageData`,
    :py:class:`~chaco.grid_data_source.GridDataSource`.

Ranges
    These hold a range of displayed data values and can be updated either
    by changes to the data or changes in the state of pan or zoom tools.

    Examples: :py:class:`~chaco.data_range_1d.DataRange1D`,
    :py:class:`~chaco.data_range_2d.DataRange2D`.

Mappers
    These are responsible for mapping data values to screen (or color) values.

    Examples: :py:class:`~chaco.linear_mapper.LinearMapper`,
    :py:class:`~chaco.log_mapper.LogMapper`,
    :py:class:`~chaco.grid_mapper.GridMapper`.

Renderers
    These are the objects responsible for rendering plot data, such as line
    plots or scatter plots.  They need to be update either when the data they
    are displaying changes, or the mapping from data space to screen space
    changes.

    Examples: :py:class:`~chaco.plots.lineplot.LinePlot`,
    :py:class:`~chaco.plots.scatterplot.ScatterPlot`,
    :py:class:`~chaco.plots.cmap_image_plot.CMapImagePlot`,
    :py:class:`~chaco.plots.text_plot_1d.TextPlot1D`.

Axes and Grids
    These are the objects responsible for drawing axes ticks and grid lines,
    and need to know the mapping between data space and screen space.  Axes
    and Grids are examples of Overlays (although they are technically
    underlays).

    Examples: :py:class:`~chaco.axis.PlotAxis`,
    :py:class:`~chaco.label_axis.LabelAxis`,
    :py:class:`~chaco.grid.PlotGrid`.

Pan and Zoom
    These are pan and zoom commands that come from user interactions, such as
    via a pan or zoom operation, from resizing the plot window, or from other
    application-based setting of the range of values to display.  Pan and zoom
    are commonly initated via Tools.

    Examples: :py:class:`~chaco.tools.pan_tool.PanTool`,
    :py:class:`~chaco.tools.zoom_tool.ZoomTool`.

Data Flow Examples
~~~~~~~~~~~~~~~~~~

Consider the following example::

    def create_plot():
        t = np.linspace(0, 2*np.pi, 100)
        amplitude1 = 2*np.sin(t)
        amplitude2 = np.cos(2*t)
        plot_data = ArrayPlotData(
            t=t,
            amplitude1=amplitude1,
            amplitude2=amplitude2,
        )
        plot = Plot(plot_data)
        plot.plot(('t', 'amplitude1'), type='line')
        plot.plot(('t', 'amplitude2'), type='scatter')
        return plot

This sets up a number of objects and connects them together, so that data
flows roughly as follows:

.. graphviz::

    digraph dataflow {

        subgraph cluster_level {
            node [shape=plaintext];
            style=invis;
            "Data source" -> "Range" -> "Mapper" -> "Underlay" -> "Renderer" [style=invis];
        }
        node [shape=rectangle];

        subgraph index {
            color=white;
            "ArrayDataSource: time" -> "Range1D: index" -> "LinearMapper: index" -> "PlotAxis: index";
        }
        subgraph value {
            color=white;
            "ArrayDataSource: amplitude1" -> "Range1D: value";
            "ArrayDataSource: amplitude2" -> "Range1D: value";
            "Range1D: value" -> "LinearMapper: value" -> "PlotAxis: value";
        }

        {rank = same; "Data source"; "ArrayDataSource: time"; "ArrayDataSource: amplitude1"; "ArrayDataSource: amplitude2"}
        {rank = same; "Range"; "Range1D: index"; "Range1D: value"}
        {rank = same; "Mapper"; "LinearMapper: index"; "LinearMapper: value"}
        {rank = same; "Underlay"; "PlotAxis: index"; "PlotAxis: value"}
        {rank = same; "Renderer"; "LinePlot"; "ScatterPlot"}

        "ArrayPlotData" -> "ArrayDataSource: time";
        "ArrayPlotData" -> "ArrayDataSource: amplitude1";
        "ArrayPlotData" -> "ArrayDataSource: amplitude2";
        "ArrayDataSource: time" -> "LinePlot";
        "ArrayDataSource: time" -> "ScatterPlot";
        "ArrayDataSource: amplitude1" -> "LinePlot";
        "ArrayDataSource: amplitude2" -> "ScatterPlot";
        "LinearMapper: value" -> "LinePlot";
        "LinearMapper: value" -> "ScatterPlot";
        "LinearMapper: index" -> "LinePlot";
        "LinearMapper: index" -> "ScatterPlot";
        "PlotAxis: index" -> "Plot";
        "PlotAxis: value" -> "Plot";
        "LinePlot" -> "Plot";
        "ScatterPlot" -> "Plot";
    }

Updates to the data stored in the array plot data object trigger updates
through the pathways indicated, first updating the data sources for each
array, upon which the data ranges depend.  In turn the mappers update their
state when the data ranges update, and the underlays and plot renderers
update their state based on changes to the mappers and, for the renderers,
on the changes to the data sources.  Finally the changes to the state of the
components are flagged in the Enable drawing system, which will then schedule
the plot for re-drawing during the GUI event loop's next paint event.

Notice also how this diagram shows that mappers and ranges are shared between
renderers and underlays that share the same physical space.  Plots which don't
share the same screen space shouldn't share mappers, but can share data and/or
ranges.

For example, here are two plots which share the same array plot data::

    def create_plot():
        t = np.linspace(0, 2*np.pi, 100)
        amplitude1 = 2*np.sin(t)
        amplitude2 = np.cos(2*t)
        plot_data = ArrayPlotData(
            t=t,
            amplitude1=amplitude1,
            amplitude2=amplitude2,
        )
        plot_1 = Plot(plot_data)
        plot_1.plot(('t', 'amplitude1'), type='line')
        plot_2 = Plot(plot_data)
        plot_2.plot(('t', 'amplitude2'), type='scatter')
        container = HPlotContainer(plot_1, plot2)

Which gives rise to the following data flow diagram:

.. graphviz::

    digraph dataflow {

        subgraph cluster_level {
            node [shape=plaintext];
            style=invis;
            "Data source" -> "Range" -> "Mapper" -> "Underlay" -> "Renderer" [style=invis];
        }
        node [shape=rectangle];

        subgraph index_1 {
            color=white;
            "Range1D: index 1" -> "LinearMapper: index 1" -> "PlotAxis: index 1";
        }
        subgraph value_1 {
            color=white;
            "Range1D: value 1" -> "LinearMapper: value 1" -> "PlotAxis: value 1";
        }
        subgraph index_2 {
            color=white;
            "Range1D: index 2" -> "LinearMapper: index 2" -> "PlotAxis: index 2";
        }
        subgraph value_2 {
            color=white;
            "Range1D: value 2" -> "LinearMapper: value 2" -> "PlotAxis: value 2";
        }

        {rank = same; "Data source"; "ArrayDataSource: time"; "ArrayDataSource: amplitude1"; "ArrayDataSource: amplitude2"}
        {rank = same; "Range"; "Range1D: index 1"; "Range1D: value 1"; "Range1D: index 2"; "Range1D: value 2"}
        {rank = same; "Mapper"; "LinearMapper: index 1"; "LinearMapper: value 1"; "LinearMapper: index 2"; "LinearMapper: value 2"}
        {rank = same; "Underlay"; "PlotAxis: index 1"; "PlotAxis: value 1"; "PlotAxis: index 2"; "PlotAxis: value 2"}
        {rank = same; "Renderer"; "LinePlot"; "ScatterPlot"}

        "ArrayPlotData" -> "ArrayDataSource: time";
        "ArrayPlotData" -> "ArrayDataSource: amplitude1";
        "ArrayPlotData" -> "ArrayDataSource: amplitude2";
        "ArrayDataSource: time" -> "Range1D: index 1"
        "ArrayDataSource: time" -> "Range1D: index 2"
        "ArrayDataSource: time" -> "LinePlot";
        "ArrayDataSource: time" -> "ScatterPlot";
        "ArrayDataSource: amplitude1" -> "Range1D: value 1";
        "ArrayDataSource: amplitude1" -> "Range1D: value 2";
        "ArrayDataSource: amplitude1" -> "LinePlot";
        "ArrayDataSource: amplitude2" -> "Range1D: value 1";
        "ArrayDataSource: amplitude2" -> "Range1D: value 2"
        "ArrayDataSource: amplitude2" -> "ScatterPlot";
        "LinearMapper: value 1" -> "LinePlot";
        "LinearMapper: value 2" -> "ScatterPlot";
        "LinearMapper: index 1" -> "LinePlot";
        "LinearMapper: index 2" -> "ScatterPlot";
        "PlotAxis: index 1" -> "Plot 1";
        "PlotAxis: value 1" -> "Plot 1";
        "PlotAxis: index 2" -> "Plot 2";
        "PlotAxis: value 2" -> "Plot 2";
        "LinePlot" -> "Plot 1";
        "ScatterPlot" -> "Plot 2";
    }

In contrast to the previous example the ranges and mappers are not related
in any way between the two plots.  This means that changes to the visible
region in data space for one plot will not affect the other, and because
the values span a different range initially they will have different value
scales.

It is common to want to share one or both of the ranges between plots to
keep the axes synchronized in data space.

For example, here are two plots which share the same data ranges::

    def create_plot():
        t = np.linspace(0, 2*np.pi, 100)
        amplitude1 = 2*np.sin(t)
        amplitude2 = np.cos(2*t)
        plot_data = ArrayPlotData(
            t=t,
            amplitude1=amplitude1,
            amplitude2=amplitude2,
        )
        plot_1 = Plot(plot_data)
        plot_1.plot(('t', 'amplitude1'), type='line')
        plot_2 = Plot(plot_data)
        plot_2.plot(('t', 'amplitude2'), type='scatter')
        plot_2.index_range = plot_1.index_range
        plot_2.value_range = plot_1.value_range
        container = HPlotContainer(plot_1, plot2)

Which gives rise to the following data flow diagram:

.. graphviz::

    digraph dataflow {

        subgraph cluster_level {
            node [shape=plaintext];
            style=invis;
            "Data source" -> "Range" -> "Mapper" -> "Underlay" -> "Renderer" [style=invis];
        }
        node [shape=rectangle];

        subgraph index_1 {
            color=white;
            "Range1D: index" -> "LinearMapper: index 1" -> "PlotAxis: index 1";
        }
        subgraph value_1 {
            color=white;
            "Range1D: value" -> "LinearMapper: value 1" -> "PlotAxis: value 1";
        }
        subgraph index_2 {
            color=white;
            "Range1D: index" -> "LinearMapper: index 2" -> "PlotAxis: index 2";
        }
        subgraph value_2 {
            color=white;
            "Range1D: value" -> "LinearMapper: value 2" -> "PlotAxis: value 2";
        }

        {rank = same; "Data source"; "ArrayDataSource: time"; "ArrayDataSource: amplitude1"; "ArrayDataSource: amplitude2"}
        {rank = same; "Range"; "Range1D: index"; "Range1D: value"}
        {rank = same; "Mapper"; "LinearMapper: index 1"; "LinearMapper: value 1"; "LinearMapper: index 2"; "LinearMapper: value 2"}
        {rank = same; "Underlay"; "PlotAxis: index 1"; "PlotAxis: value 1"; "PlotAxis: index 2"; "PlotAxis: value 2"}
        {rank = same; "Renderer"; "LinePlot"; "ScatterPlot"}

        "ArrayPlotData" -> "ArrayDataSource: time";
        "ArrayPlotData" -> "ArrayDataSource: amplitude1";
        "ArrayPlotData" -> "ArrayDataSource: amplitude2";
        "ArrayDataSource: time" -> "Range1D: index";
        "ArrayDataSource: time" -> "LinePlot";
        "ArrayDataSource: time" -> "ScatterPlot";
        "ArrayDataSource: amplitude1" -> "Range1D: value";
        "ArrayDataSource: amplitude1" -> "LinePlot";
        "ArrayDataSource: amplitude2" -> "Range1D: value";
        "ArrayDataSource: amplitude2" -> "ScatterPlot";
        "LinearMapper: value 1" -> "LinePlot";
        "LinearMapper: value 2" -> "ScatterPlot";
        "LinearMapper: index 1" -> "LinePlot";
        "LinearMapper: index 2" -> "ScatterPlot";
        "PlotAxis: index 1" -> "Plot 1";
        "PlotAxis: value 1" -> "Plot 1";
        "PlotAxis: index 2" -> "Plot 2";
        "PlotAxis: value 2" -> "Plot 2";
        "LinePlot" -> "Plot 1";
        "ScatterPlot" -> "Plot 2";
    }

Here any change to the range will automatically update the mappers
of both, so the visible ranges will match.  However since the screen
space of the two plots is different, we don't want to share mappers
(mappers can only be shared when the plots are contained in an
:py:class:`~chaco.plot_containers.OverlayPlotContainer` or a
subclass such as :py:class:`~chaco.data_view.DataView` or
:py:class:`~chaco.plot.Plot`)

Data Sources
------------

At its core, Chaco is about visualizing interactive data.  As such, Chaco has
a standard API for representing data: all of these classes implement the
:py:class:`~chaco.abstract_data_source.AbstractDataSource` API.  This class
has methods for getting and setting the data that is provided by the data
source, as well as basic information about the data's size and (for numerical
data) the numerical bounds of the values.  A data source can also hold a
dictionary of arbitrary additional metadata.

The workhorse data source is the
:py:class:`~chaco.array_data_source.ArrayDataSource`
which holds a single NumPy of array of numerical data and which covers almost
all common use cases.  In most cases where you need to work with an
:py:class:`~chaco.array_data_source.ArrayDataSource` you call
:py:meth:`~chaco.array_data_source.ArrayDataSource.set_data` to change the
stored data, listen to the
:py:attr:`~chaco.abstract_data_source.AbstractDataSource.data_changed` event
trait for when the data changes and call
:py:meth:`~chaco.array_data_source.ArrayDataSource.get_data` to get the
current value of the data.

Some users of a data source only care about the range of values that are
contained in that data.  In this case the data source API provides a
:py:attr:`~chaco.abstract_data_source.AbstractDataSource.bounds_changed` trait
that indicates that the maximum or minimum value of the data has changed, and
those values can be efficiently retrieved via the
:py:meth:`~chaco.array_data_source.ArrayDataSource.get_bounds` trait.

Similarly there is a
:py:attr:`~chaco.abstract_data_source.AbstractDataSource.metadata_changed`
event trait that is fired when the metadata dictionary is replaced or
modified.

A common use case for alternative data sources is to render a computed
function (such as a curve that has been fit to the data) dynamically
rather than having to sample a fixed set of points.  This can be done
by supplying the plot data with an
:py:class:`~chaco.function_data_source.FunctionDataSource` and plotting
that::

    def create_plot():
        t = np.linspace(0, 2*np.pi, 100)
        amplitude = 2*np.sin(t) + numpy.random.normal(scale=0.1)
        plot_data = ArrayPlotData(t=t, amplitude=amplitude)
        plot = Plot(plot_data)
        plot.plot(('t', 'amplitude'), type='scatter')

        def f(low, high):
            return 2*np.sin(np.linspace(low, high, 100))

        data_source = FunctionDataSource(
            func=f, data_range=plot.index_range
        )
        plot_data.set_data('f', data_source)
        plot.plot(('t', 'f'), type='line')

        return plot

Mappers
-------

Data as provided by the
:py:class:`~chaco.abstract_data_source.AbstractDataSource` is not suitable
for display; it needs to be mapped to an appropriate value for rendering
into a graphics context.  The most obvious mapping transforms data values
into Enable's drawing coordinates (often simply referred to as "screen"
coordinates, whether or not they are actually rendered to a screen).
However similar transformations need to be performed to map numerical data
to color values for displaying on colormapped plots.  There are two
hierarchies of classes that perform these transformations.

The abstract base class for mapping data is the
:py:class:`~chaco.abstract_mapper.AbstractMapper` and this class
specifies methods
:py:meth:`~chaco.abstract_mapper.AbstractMapper.map_screen` for
mapping data values to screen values,
:py:meth:`~chaco.abstract_mapper.AbstractMapper.map_data` for
mapping screen values back to data values, and
:py:meth:`~chaco.abstract_mapper.AbstractMapper.map_data_array`
for mapping a collection of screen values to data values.  Perhaps
most importantly, the mapper fires the
:py:attr:`~chaco.abstract_mapper.AbstractMapper.updated` event.

Chaco provides a number of sub-classes of the base class for various
use-cases.  The most commonly used is the
:py:class:`~chaco.linear_mapper.LinearMapper` which provides a one
dimensional linear transformation between data space and screen space,
but there is also :py:class:`~chaco.log_mapper.LogMapper` which provides
one dimensional logarithmic transformation, and
:py:class:`~chaco.grid_mapper.GridMapper` which provides a mapping frrom
a two dimensional data source to a point in screen (x, y) coordinates
using a combination of two one dimensional mappers.

For mapping of values to colors, there is the
:py:class:`~chaco.abstract_colormap.AbstractColormap` class and
the two sub-classes :py:class:`~chaco.color_mapper.ColorMapper` and
:py:class:`~chaco.discrete_color_mapper.DiscreteColorMapper`.  These have
the same base API as
:py:class:`~chaco.abstract_mapper.AbstractMapper` but also provide
some specialized methods for converting to integer RGB values efficiently.
Chaco provides a large number of default color maps suitable for various
visualization types.

Ranges
------

A common problem to many data mappers is that the range of data values
may change dynamically, and when data changes it is desirable to have
the mapper automatically update itself to ensure that the full range of
data values is mapped to the screen.  This functionality is broken out
into subclasses of the
:py:class:`~chaco.abstract_data_range.AbstractDataRange` class.

These classes track a collection of
:py:class:`~chaco.abstract_data_source.AbstractDataSource` instances via
their :py:attr:`~chaco.abstract_data_range.AbstractDataRange.sources`
trait, and when the bounds of any of those data sources change then
the range adjusts its upper and lower bound appropriately.  Data mappers
then listen to the values of the upper and lower bounds of the range and
use that to adjust the transformation that they apply.  The actual
values of the upper and lower bounds in data space coordinates are
provided by the :py:attr:`~chaco.abstract_data_range.AbstractDataRange.low`
and :py:attr:`~chaco.abstract_data_range.AbstractDataRange.high` traits.

However there are situations where the behaviour of the range should
change, for example after a pan or zoom operation the value of the
bounds should remain fixed to whatever values the user panned or zoomed
to even if the underlying data changes.  For these purposes, code
interacting with a data range can set the
:py:attr:`~chaco.abstract_data_range.AbstractDataRange.low_setting` and
:py:attr:`~chaco.abstract_data_range.AbstractDataRange.high_setting` traits
either to an absolute numerical value in the data space, or to a number of
other values, such as ``auto`` or ``track`` that determine the behaviour
when data changes.

The most commonly used subclass is
:py:class:`~chaco.data_range_1d.DataRange1D` which has a number of
additional affordances to facilitate pleasant appearing plots, such as
the ability to add some padding above and below the data via the
:py:attr:`~chaco.data_range_1d.DataRange1D.margin` trait, or even
to supply a custom padding calculation function.

It is worthwhile noting that data ranges can be shared between mappers,
and this permits linking of axes bounds or color maps ranges across
different plots.

Axes and Grids
--------------

Axes and grids are auxilliary objects that draw plot decorations.
They are underlays (and so inherit from
:py:class:`~chaco.abstract_overlay.AbstractOverlay`) and are
usually drawn into the underlay layer of a :py:class:`~chaco.plot.Plot`
but they are also able to be used as stand-alone components if needed
(for example to create multi-axis plots).

These objects present numerous options for their styling, but perhaps
more importantly allow control over the algorithm to used for determining
where tick marks and grid lines should be drawn.  Both classes have a
:py:attr:`tick_generator` trait which takes an instance of an
:py:class:`~chaco.ticks.AbstractTickGenerator` which has a single
method :py:meth:`~chaco.ticks.AbstractTickGenerator.get_ticks` that
returns the tick positions for the current data and screen space bounds.

There are several standard tick generators available for use,
but in the absence of anything else the
:py:class:`~chaco.ticks.DefaultTickGenerator` is used, which tries to
generate genererally pleasing ticks at round numbers for both linear
and logarithmic mappings.  The
:py:class:`~chaco.ticks.MinorTickGenerator` is similar, but generates
generate denser ticks that are suitable for use as a minor scale.  The
:py:class:`~chaco.ticks.ShowAllTickGenerator` simply shows ticks at
a list of supplied data values, giving complete control at the expense
of not being able to dynamically adapt to changes from panning and
zooming.

For more complex tick generation, such as time axes where the "natural"
tick spacings, positions and even label formatting can change as you
zoom through different levels, the
:py:class:`~chaco.scales_tick_generator.ScalesTickGenerator` allows the
user to specify a multi-leveled
:py:class:`~chaco.scales.scales.ScaleSystem`.  In particular this system
provides the :py:class:`~chaco.scales.time_scale.CalendarScaleSystem`
which by default correct ticks axes with time values ranging from microseconds
through to years.

For example, you can create an hours, minutes, seconds time axis (ignoring
higher level calendar constructs) for a plot as follows::

    from chaco.scales.api import (
        CalendarScaleSystem, HMSScales, ScalesTickGenerator
    )

    def create_plot():
        t = np.linspace(0, 3600, 36001)
        a = np.sin(2*pi*60*t)
        plot_data = ArrayPlotData(t=t, a=a)
        plot = Plot(plot_data)
        plot.plot(('t', 'a'), type='line')
        plot.index_axis.tick_generator = ScalesTickGenerator(
            scale=CalendarScaleSystem(*HMSScales)
        )

        return plot

Plot Renderers
--------------

The core of the Chaco plotting library are the plot renderers which are
responsible for drawing the markings that represent the data, all of which
implement the :py:class:`~chaco.abstract_plot_renderer.AbstractPlotRenderer`
API.  This ABC is a subclass of
:py:class:`~chaco.plot_component.PlotComponent`, and so all plot renderers
are expected to implement the key parts of the Enable drawing API. Most
specialized plot renderers expect a :py:meth:`render` method that performs
actual drawing of the plot into a provided Kiva graphics context.

Most plot renders have the notion of "index" and "value" data that
they are plotting. Each item in the index has a corresponding value, so if
a function were being plotted the index are points in the domain and the
values are points in the range.  For plot renderers the index usually
provides a location at which the value should be rendered, and the value
provides a position offset or color value. Importantly, the index and value
are not directly linked to horizontal or vertical screen space.

Different subclasses of the abstract plot renderer implement common
conventions for handling index and value representation. For example:

:py:class:`~chaco.base_xy_plot.BaseXYPlot`
    This class handles plots like line plots and bar plots where the index
    gives offsets along one axis and the values are along the other axis.

:py:class:`~chaco.base_1d_plot.Base1DPlot`
    This class handles plots where the index gives the offset along one
    axis, and the values are displayed by markings at or near those points.

:py:class:`~chaco.base_2d_plot.Base2DPlot`
    This class handles plots like contour and image plots where the
    index lies on a regular 2D grid and values are displayed by markings
    at or near those points.

There are a number of other plot types that handle special cases like
candle plots.

Plot renderers have mappers for each of their data dimensions, but they
also express convenience APIs mapping data values to and from screen
(x, y) values using the methods
:py:meth:`~chaco.abstract_plot_renderer.AbstractPlotRenderer.map_data`
and
:py:meth:`~chaco.abstract_plot_renderer.AbstractPlotRenderer.map_screen`.
These are usually simple wrappers around the appropriate mapper calls of
the same name.

Plot renderers also have to provide information for tools that want to
interact with the values on the plot.  They are expected to provide a
:py:meth:`~chaco.abstract_plot_renderer.AbstractPlotRenderer.map_index`
method which handles mapping a screen point to an index item (ie. an
integer index into the index data source).

Tools
-----

Up to this point, all the classes discussed are dynamic in the sense
that if the underlying data changes then the visualization will update
appropriately.  However it is often the case that you want to add other
interactions to a visualization.  The most common of these is the
ability to pan or zoom the plot to focus on particular details, but
there number of ways that you might want a user to interact with the
visualization is potentially vast.  As a result one of the most common
ways to customize a visualization is by writing new tools.

Tools are technically a feature of Enable, rather than Chaco, and as
a result there are a number of tools and base classes there that can
be used as the foundation or inspiration for custom interactions.  For
example, the following Enable tools may be of use:

:py:class:`enable.tools.move_tool.MoveTool`
    A tool which changes the screen location of a component by dragging
    with the mouse.  This can be useful for allowing the user to move
    plot decorations such as legends around the plot.

:py:class:`enable.tools.resize_tool.ResizeTool`
    A tool which changes the screen size of a component by dragging
    edges or corners.

:py:class:`enable.tools.hover_tool.HoverTool`
    A tool which calls a callback when the mouse hs not moved
    significantly for a period of time.

:py:class:`enable.tools.button_tool.ButtonTool`
    A tool that makes a component act like a button, with a
    :py:class:`enable.tools.button_tool.ButtonTool.clicked`
    trait that you can react to via the usual Traits mechanisms.

:py:class:`enable.tools.pyface.context_menu_tool.ContextMenuTool`
    A tool which displays a context menu at the point where the
    use right-clicks, using Pyface's menu and action classes.

:py:class:`enable.tools.traits_tool.TraitsTool`
    A tool which opens a TraitsUI dialog when a component is
    double-clicked.

:py:class:`enable.tools.base_drop_tool.BaseDropTool`
    A base tool which responds to operating system drag and drop.
    Must be subclassed to implement methods that indicate whether
    a type of object can be dropped, and what to do if they are
    dropped.

:py:class:`enable.tools.value_drag_tool.ValueDragTool`
    A base tool which changes a numeric value as the user
    drags the mouse.  Must be subclassed to provide methods to
    get and set the value.  There is a subclass
    :py:class:`enable.tools.value_drag_tool.AttributeDragTool`
    which sets the values of attributes on an object as the
    mouse moves, which is a common use case.

Overlays and Underlays
----------------------

In some instances you want to render additional decorations that are
independent of the plot type.  In a similar fashion to the Tool classes
auxilliary renderers can be attached to plots as "overlays" (and using
the same mechanism, just rendering into a different layer, as
"underlays").  Common use cases for overlays include cursor lines,
selection regions, hover text, legends and other annotations.  Overlays
are frequently designed to work together with a particular Tool or class
of tools, but can frequently be used independently if desired.

Overlays and underlays which need to render relative to points in
data space will frequently want to make use of the plot mappers to know
where in screen space to perform their drawing operations..

