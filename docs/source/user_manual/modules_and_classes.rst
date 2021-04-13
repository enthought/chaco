
.. _modules_and_classes:

Commonly Used Modules and Classes
=================================

Base Classes
-----------------------------------------------------------------------------

.. rubric:: Plot Component

All visual components in Chaco subclass from
:class:`~chaco.plot_component.PlotComponent`. It defines all of the common
visual attributes like background color, border styles and color, and whether
the component is visible. (Actually, most of these visual attributes are
inherited from the Enable drawing framework.) More importantly, it provides the
base behaviors for participating in layout, handling event dispatch to tools
and overlays, and drawing various layers in the correct order. Subclasses
almost never need to override or customize these base behaviors, but if they
do, there are several easy extension points.

PlotComponent is a subclass of Enable :class:`~enable.component.Component`. It
has its own default drawing order. It redefines the inherited traits
:attr:`draw_order` and :attr:`draw_layer`, but it doesn't define any new
traits. Therefore, you may need to refer to the API documentation for Enable
Component, even when you have subclassed Chaco PlotComponent.

If you subclass PlotComponent, you need to implement :meth:`do_layout`,
if you want to size the component correctly.


Data Objects
-----------------------------------------------------------------------------

.. rubric:: Data Source

A data source is a wrapper object for the actual data that it will be
handling. It provides methods for retrieving data, estimating a size of the
dataset, indications about the dimensionality of the data, a place for metadata
(such as selections and annotations), and events that fire when the data gets
changed. There are two primary reasons for a data source class:

* It provides a way for different plotting objects to reference the same data.
* It defines the interface for embedding Chaco into an existing application.
  In most cases, the standard ArrayDataSource will suffice.

*Interface:* :class:`~chaco.abstract_data_source.AbstractDataSource`

*Subclasses:* :class:`~chaco.array_data_source.ArrayDataSource`,
:class:`~chaco.multi_array_data_source.MultiArrayDataSource`,
:class:`~chaco.point_data_source.PointDataSource`,
:class:`~chaco.grid_data_source.GridDataSource`,
:class:`~chaco.image_data.ImageData`

.. rubric:: Data Range

A data range expresses bounds on data space of some dimensionality. The simplest
data range is just a set of two scalars representing (low, high) bounds in 1-D.
One of the important aspects of data ranges is that their bounds can be set to
``auto``, which means that they automatically scale to fit their associated
datasources. (Each data source can be associated with multiple ranges,
and each data range can be associated with multiple data sources.)

*Interface*: :class:`~chaco.abstract_data_range.AbstractDataRange`

*Subclasses*: :class:`~chaco.base_data_range.BaseDataRange`, 
:class:`~chaco.data_range_1d.DataRange1D`, 
:class:`~chaco.data_range_2d.DataRange2D`

.. rubric:: Data Source

A data source is an object that supplies data to Chaco. For the most part, a
data source looks like an array of values, with an optional mask and metadata.

*Interface*: :class:`~chaco.abstract_data_source.AbstractDataSource`

*Subclasses*: :class:`~chaco.array_data_source.ArrayDataSource`,
:class:`~chaco.grid_data_source.GridDataSource`,
:class:`~chaco.image_data.ImageData`,
:class:`~chaco.multi_array_data_source.MultiArrayDataSource`,
:class:`~chaco.point_data_source.PointDataSource`

The :attr:`metadata` trait attribute is a dictionary where you can stick
stuff for other tools to find, without inserting it in the actual data.

Events that are fired on data sources are:

* :attr:`data_changed`
* :attr:`bounds_changed`
* :attr:`metadata_changed`


.. rubric:: Mapper

Mappers perform the job of mapping a data space region to screen space, and
vice versa. Bounds on mappers are set by data range objects.

*Interface*: :class:`~chaco.abstract_mapper.AbstractMapper`

*Subclasses*: :class:`~chaco.base_1d_mapper.Base1DMapper`,
:class:`~chaco.linear_mapper.LinearMapper`,
:class:`~chaco.log_mapper.LogMapper`, :class:`~chaco.grid_mapper.GridMapper`,
:class:`~chaco.polar_mapper.PolarMapper`


Containers
-----------------------------------------------------------------------------

.. rubric:: PlotContainer

:class:`~.PlotContainer` is Chaco's way of handling layout. Because it logically
partitions the screen space, it also serves as a way for efficient event
dispatch. It is very similar to sizers or layout grids in GUI toolkits like
WX. Containers are subclasses of PlotComponent, thus allowing them to
be nested. :class:`~.BasePlotContainer` implements the logic to correctly render
and dispatch events to sub-components, while its subclasses implement the
different layout calculations.

A container gets the preferred size from its components, and tries to allocate
space for them. Non-resizeable components get their required size; whatever is
left over is divided among the resizeable components.

Chaco currently has three types of containers,
described in the following sections.

*Interface*: :class:`~.BasePlotContainer`

*Subclasses*: :class:`~.OverlayPlotContainer`, :class:`~.HPlotContainer`,
:class:`~.VPlotContainer`, :class:`~.GridPlotContainer`

The listed subclasses are defined in the module
:mod:`chaco.plot_containers`.


Renderers
-----------------------------------------------------------------------------

Plot renderers are the classes that actually draw a type of plot.

*Interface*: :class:`~.AbstractPlotRenderer`

*Subclasses*:

* :class:`~.BarPlot`
* :class:`~.Base2DPlot`

  * :class:`~.ContourLinePlot`
  * :class:`~.ContourPolyPlot`
  * :class:`~.ImagePlot`: displays an image file, or color-maps scalar
    data to make an image
  * :class:`~.CMapImagePlot`

* :class:`~.BaseXYPlot`: This class is often emulated by writers of other
  plot renderers, but renderers don't *need* to be structured this way.
  By convention, many have a :meth:`hittest` method. They *do* need
  to implement :meth:`map_screen`, :meth:`map_data`, and :meth:`map_index`
  from :class:`~.AbstractPlotRenderer`.

  * :class:`~.LinePlot`

    * :class:`~.ErrorBarPlot`

  * :class:`~.PolygonPlot`

    * :class:`~.FilledLinePlot`

  * :class:`~.ScatterPlot`

    * :class:`~.ColormappedScatterPlot`

  * :class:`~.ColorBar`
  * :class:`~.PolarLineRenderer`: NOTE: doesn't play well with others

You can use these classes to compose more interesting plots.

The module :mod:`chaco.plot_factory` contains various convenience
functions for creating plots, which simplify the set-up.

The :class:`~chaco.plot.Plot` class (called "capital P Plot" when
speaking) represents what the user usually thinks of as a "plot": a set of data,
renderers, and axes in a single screen region. It is a subclass of
:class:`~.DataView`.

Tools
-----------------------------------------------------------------------------

Tools attach to a component, which gives events to the tool.

All tools subclass from Enable's :py:class:`~enable.base_tool.BaseTool`, which
is in turn an Enable :py:class:`~enable.interactor.Interactor`.  Do not try to
make tools that draw: use an overlay for that.

Some tool subclasses exist in both Enable and Chaco, because they were created
first in Chaco, and then moved into Enable.

*Interface*: :py:class:`~enable.base_tool.BaseTool`

*Subclasses*:

* :class:`~.BroadcasterTool`: Keeps a list of other tools, and broadcasts
  events it receives to all those tools.
* :class:`~.DataPrinter`: Prints the data-space position of the point
  under the cursor.
* :class:`enable.tools.drag_tool.DragTool`: Enable base class
  for tools that do dragging.

  * :class:`~chaco.tools.move_tool.MoveTool`
  * :class:`enable.tools.resize_tool.ResizeTool`
  * :class:`enable.tools.viewport_pan_tool.ViewportPanTool`

* :class:`~.chaco.tools.drag_tool.DragTool`: Chaco base class
  for tools that do dragging.

  * :class:`~chaco.tools.cursor_tool.BaseCursorTool`

    * :class:`~chaco.tools.cursor_tool.CursorTool1D`
    * :class:`~chaco.tools.cursor_tool.CursorTool2D`

  * :class:`~.DataLabelTool`
  * :class:`~.DragZoom`
  * :class:`~.LegendTool`
  * :class:`~.MoveTool`

* :class:`~.DrawPointsTool`
* :class:`~.HighlightTool`
* :class:`enable.tools.hover_tool.HoverTool`
* :class:`~.ImageInspectorTool`
* :class:`~.LineInspector`
* :class:`~.PanTool`

  * :class:`~.TrackingPanTool`

* :class:`~.PointMarker`
* :class:`~.SaveTool`
* :class:`~.SelectTool`

  * :class:`~.ScatterInspector`
  * :class:`~.SelectableLegend`

* :class:`enable.tools.traits_tool.TraitsTool`

  * :class:`~chaco.tools.traits_tool.TraitsTool`

DragTool is a base class for tools that do dragging.

Other tools do things like panning, moving, highlighting, line segments, range selection, drag zoom, move data labels, scatter inspection, Traits UI.

Overlays
-----------------------------------------------------------------------------


Miscellaneous
-----------------------------------------------------------------------------


