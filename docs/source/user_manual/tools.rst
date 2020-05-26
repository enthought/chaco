******************
Tools and Overlays
******************

================================================================
Overview
================================================================


Chaco, Enable, and Event Dispatch
=================================


A Basic Tool
============


A Basic Overlay
===============


================================================================
Interaction Tools
================================================================

PanTool
=======

ZoomTool
========

RectZoom
========

DragZoom
========

LegendTool
==========

DataLabelTool
=============

MoveTool
========


================================================================
Inspector-type Tools
================================================================

DataPrinter
===========

LineInspector
=============

ScatterInspector
================

CursorTool
==========

HighlightTool
=============

ImageInspectorTool
==================
The :class:`chaco.tools.api.ImageInspectorTool` is designed to work with an
:class:`chaco.api.ImagePlot` renderer to display the data space coordinates and
data value of the displayed 2D array. The tool is designed to be used in
conjunction with the :class:`chaco.overlays.api.ImageInspectorOverlay`: the
tool collects mouse position and data values and triggers `Event` emissions,
and the overlay catches these events and displays the data as an overlay.

To use it, as for other tools, you need to:

    1. create a tool object and append it to the **renderer**'s list of tools,
    2. create an overlay object and append it to the **renderer**'s list of
       overlays.

For example, a method to build a :class:`chaco.api.Plot` object with that tool
could look like::

    def build_plot(self, img):
        plot = Plot(data=ArrayPlotData(img=img))
        # Capture the renderer object to pass it to the tool
        img_plot = plot.img_plot("img")[0]
        # Tool code to be added here...
        return plot

Note that unlike other `ImagePlot` examples, the renderer returned by the
:meth:`chaco.api.Plot.img_plot` call is captured since the tool
will need it. The tool code to be inserted would look something like this::

    imgtool = ImageInspectorTool(component=img_plot)
    img_plot.tools.append(imgtool)
    overlay = ImageInspectorOverlay(component=img_plot, image_inspector=imgtool,
                                    bgcolor="white", border_visible=True)

    img_plot.overlays.append(overlay)

Note the two important connections that are made for the tool/overlay to work
correctly. The first one is that the component that is passed is the Chaco
renderer rather than the `Plot` object, since it has access to the data being
displayed. The second connection is that, for the overlay to update when the
tool catches a mouse event, it needs to be provided the tool instance as its
:attr:`image_inspector` attribute.

In addition to the background color and :attr:`border_visible`, other
interesting overlay attributes to consider overriding include
:attr:`tooltip_mode` to control the location of the text box and all of the
:class:`chaco.overlays.api.TextBoxOverlay` attributes (see below).

Finally, the overlay's :meth:`_build_text_from_event` method can be overwritten
to customize the actual text content. The method should receive a single
argument, the event data (dictionary), and return the desired text to display.
The event data contains 3 keys: `indices` with the 2D coordinates of the mouse
in data space, `color_value` containing the color of the tile where the mouse
is, and `data_value` with the scalar value being displayed in that tile.

For a complete example, see :download:`examples/demo/basic/image_inspector.py
<../../../examples/demo/basic/image_inspector.py>`.

TraitsTool
==========



================================================================
Selection Tools
================================================================

RangeSelection
==============

LassoSelection
==============

SelectTool
==========



================================================================
Drawing Tools
================================================================

DrawPointsTool
==============

LineSegmentTool
===============


================================================================
Core Overlays
================================================================

Axis
====

Grid
====

Legend
======


================================================================
Annotation Overlays
================================================================

PointMarker
===========

DataBox
=======


.. _tools/text_box_overlay:

TextBoxOverlay
==============
The :class:`chaco.overlays.api.TextBoxOverlay` is the base class of
the overlay component of several inspector type tools (see above). It is
designed to draw a text box over the plots to display custom information.

The rendering of the text can be customized with the following attributes:

    * :attr:`bgcolor` and :attr:`border_visible` to control the styling of the
      box,
    * :attr:`alpha` to control the transparency of the text box,
    * :attr:`text_color` and :attr:`font` to control how the text looks like,
    * :attr:`align` to control what corner of the plot the text box should
      appear,
    * ...

.. note:: The overlay can also be used directly by any custom tool that needs
          to display information upon an event. It should be done by
          subclassing the overlay and defining a listener on the inspector's
          state which will modify the overlay's :attr:`text` (and optionally
          visibility) attribute(s). After a `text` update, the component's
          :meth:`request_redraw` should be called. Good examples include
          :class:`chaco.overlays.api.ImageInspectorOverlay`.


ToolTip
=======

PlotLabel
=========




