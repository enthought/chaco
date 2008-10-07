
.. _modules_and_classes:

Commonly Used Modules and Classes
=================================

Base Classes
------------

.. rubric:: Plot Component

All visual components in Chaco subclass from :class:`PlotComponent`. It defines
all of the common visual attributes like background color, border styles and
color, and whether the component is visible. (Actually, most of these visual
attributes are inherited from the Enable drawing framework.) More importantly,
it provides the base behaviors for participating in layout, handling event
dispatch to tools and overlays, and drawing various layers in the correct order.
Subclasses almost never need to override or customize these base behaviors, but
if they do, there are several easy extension points.

:class:`PlotComponent` is a subclass of Enable :class:`Component`. It has its
own default drawing order. It redefines the inherited traits :attr:`draw_order`
and :attr:`draw_layer`, but it doesn't define any new traits. Therefore, you
may need to refer to the API documentation for Enable :class:`Component`,
even when you have subclassed Chaco :class:`PlotComponent`.

If you subclass :class:`PlotComponent`, you need to implement :meth:`do_layout`,
if you want to size the component correctly.
 

Data Objects
------------

Data Source
~~~~~~~~~~~

A data source is a wrapper object for the actual data that it will be
handling. It provides methods for retrieving data, estimating a size of the
dataset, indications about the dimensionality of the data, a place for metadata
(such as selections and annotations), and events that fire when the data gets
changed. There are two primary reasons for a data source class: 

* It provides a way for different plotting objects to reference the same data.
* It defines the interface for embedding Chaco into an existing application.  
  In most cases, the standard ArrayDataSource will suffice. 

    *Interface:* :class:`AbstractDataSource`

    *Subclasses:* :class:`ArrayDataSource`, :class:`MultiArrayDataSource`, 
    :class:`PointDataSource`, :class:`GridDataSource`, :class:`ImageData`

Data Range
~~~~~~~~~~

A data range expresses bounds on data space of some dimensionality. The simplest
data range is just a set of two scalars representing (low, high) bounds in 1-D.
One of the important aspects of DataRanges is that their bounds can be set to
``auto``, which means that they automatically scale to fit their associated
datasources. (Each data source can be associated with multiple ranges,
and each data range can be associated with multiple data sources.)

    *Interface*: :class:`AbstractDataRange`

    *Subclasses*: :class:`BaseDataRange`, :class:`DataRange1D`, 
    :class:`DataRange2D`
    
Data Source
~~~~~~~~~~~

A data source is an object that supplies data to Chaco. For the most part, a
data source looks like an array of values, with an optional mask and metadata.

    *Interface*: :class:AbstractDataSource`
    
    *Subclasses*: :class:`ArrayDataSource`, :class:`DataContextDataSource`,
    :class:`GridDataSource`, :class:`ImageData`, :class:`MultiArrayDataSource`,
    :class:`PointDataSource`

The :attr:`metadata` trait attribute is a dictionary where you can stick 
stuff for other tools to find, without inserting it in the actual data.

Events that are fired on data sources are:

 * :attr:`data_changed`
 * :attr:`bounds_changed`
 * :attr:`metadata_changed`
 
    
Mapper
~~~~~~

Mappers perform the job of mapping a data space region to screen space, and
vice versa. Bounds on mappers are set by data range objects. 

    *Interface*: :class:`AbstractMapper`

    *Subclasses*: :class:`Base1DMapper`, :class:`LinearMapper`, 
    :class:`LogMapper`, :class:`GridMapper`, :class:`PolarMapper`


Containers
----------

PlotContainer
~~~~~~~~~~~~~

:class:`PlotContainer` is Chaco's way of handling layout. Because it logically
partitions the screen space, it also serves as a way for efficient event
dispatch. It is very similar to sizers or layout grids in GUI toolkits like
WX. Containers are subclasses of :class:`PlotComponent`, thus allowing them to
be nested. :class:`BasePlotContainer` implements the logic to correctly render
and dispatch events to sub-components, while its subclasses implement the
different layout calculations. 

A container gets the preferred size from its components, and tries to allocate
space for them. Non-resizeable components get their required size; whatever is
left over is divided among the resizeable components.

Chaco currently has three types of containers, 
described in the following sections.

    *Interface*: :class:`BasePlotContainer`

    *Subclasses*: :class:`OverlayPlotContainer`, :class:`HPlotContainer`, 
    :class:`VPlotContainer`, :class:`GridPlotContainer`

The listed subclasses are defined in the module 
:mod:`enthought.chaco.plot_containers`.

Renderers
---------
Plot renderers are the classes that actually draw a type of plot. 

    *Interface*: :class:`AbstractPlotRenderer`
    *Subclasses*:
      * :class:`BarPlot`
      * :class:`Base2DPlot`
        * :class:`ContourLinePlot`
        * :class:`ContourPolyPlot`
        * :class:`ImagePlot`: displays an image file, or color-maps scalar
          data to make an image
          * :class:`CMapImagePlot`
      * :class:`BaseXYPlot`: This class is often emulated by writers of other
        plot renderers, but renderers don't *need* to be structured this way.
        By convention, many have a :meth:`hittest` method. They *do* need
        to implement :meth:`map_screen`, :meth:`map_data`, and :meth:`map_index`
        from :class:`AbstractPlotRenderer`.
        * :class:`LinePlot`
          * :class:`ErrorBarPlot`
        * :class:`PolygonPlot`
          * :class:`FilledLinePlot`
        * :class:`ScatterPlot`
          * :class:`ColormappedScatterPlot`
        * :class:`ColorBar`
        * :class:`PolarLineRenderer`: NOTE: doesn't play well with others
        
You can use these classes to compose more interesting plots.

The module :mod:`enthought.chaco.plot_factory` contains various convenience
functions for creating plots, which simplify the set-up.

The :class:`enthought.chaco.plot.Plot` class (called "capital P Plot" when
speaking) represents what the user usually thinks of as a "plot": a set of data,
renderers, and axes in a single screen region. It is a subclass of
:class:`DataView`.
      
Tools
-----
Tools attach to a component, which gives events to the tool.

:class:`BaseTool` is an Enable :class:`Interactor`.

Do not try to make tools that draw: use an overlay for that.

Some tool subclasses exist in both Enable and Chaco, because they were created
first in Chaco, and then moved into Enable. 

    *Interface*: :class:`BaseTool`
    *Subclasses*: 
        * :class:`BroadcasterTool`: Keeps a list of other tools, and broadcasts
          events it receives to all those tools.
        * :class:`DataPrinter`: Prints the data-space position of the point
          under the cursor.
        * :class:`enthought.enable.tools.api.DragTool`: Enable base class
          for tools that do dragging.
          * :class:`MoveTool`
          * :class:`ResizeTool`
          * :class:`ViewportPanTool`
        * :class:`enthought.chaco.tools.api.DragTool`: Chaco base class
          for tools that do dragging.
          * :class:`BaseCursorTool`
            * :class:`CursorTool1D`
            * :class:`CursorTool2D`
          * :class:`DataLabelTool`
          * :class:`DragZoom`
          * :class:`LegendTool`
          * :class:`MoveTool`
        * :class:`DrawPointsTool`
        * :class:`HighlightTool`
        * :class:`HoverTool`
        * :class:`ImageInspectorTool`
        * :class:`LineInspector`
        * :class:`PanTool`
          * :class:`TrackingPanTool`
        * :class:`PointMarker`
        * :class:`SaveTool`
        * :class:`SelectTool`
          * :class:`ScatterInspector`
          * :class:`SelectableLegend`
        * :class:`enthought.enable.tools.api.TraitsTool`
        * :class:`enthought.chaco.tools.api.TraitsTool`
            
          

DragTool is a base class for tools that do dragging.

Other tools do things like panning, moving, highlighting, line segments, range selection, drag zoom, move data labels, scatter inspection, Traits UI. 

Overlays
--------


Miscellaneous
-------------


