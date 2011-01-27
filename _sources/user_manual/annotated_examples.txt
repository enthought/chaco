
.. _examples:

##################
Annotated Examples
##################

This section describes each of the examples provided with Chaco.  Each example
is designed to be a stand-alone demonstration of some of Chaco's features.
Though they are simple, many of the examples have capabilities that are
difficult to find in other plotting packages.

Extensibility is a core design goal of Chaco, and many people have used the
examples as starting points for their own applications.

``bar_plot.py``
---------------
An example showing Chaco's BarPlot class.

source: `bar_plot.py <https://svn.enthought.com/enthought/browser/Chaco/trunk/examples/bar_plot.py>`_

.. image:: example_images/bar_plot.png

``bigdata.py``
--------------
Demonstrates chaco performance with large datasets.

There are 10 plots with 100,000 points each.  Right-click and drag to
create a range selection region.  The region can be moved around and
resized (drag the edges).  These interactions are very fast because
of the backbuffering built into chaco.

Zooming with the mousewheel and the zoombox (as described in simple_line.py)
is also available, but panning is not.

source: `bigdata.py <https://svn.enthought.com/enthought/browser/Chaco/trunk/examples/bigdata.py>`_

.. image:: example_images/bigdata.png

``cursor_tool_demo.py``
-----------------------
A Demonstration of the CursorTool functionality

Left-button drag to move the cursors round.
Right-drag to pan the plots. 'z'-key to Zoom

source: `cursor_tool_demo.py <https://svn.enthought.com/enthought/browser/Chaco/trunk/examples/cursor_tool_demo.py>`_

.. image:: example_images/cursor_tool_demo.png

``data_labels.py``
------------------
Draws a line plot with several points labelled.  Demonstrates how to annotate
plots.

source: `data_labels.py <https://svn.enthought.com/enthought/browser/Chaco/trunk/examples/data_labels.py>`_

.. image:: example_images/data_labels.png

``data_view.py``
----------------
Example of how to use a DataView and bare renderers to create plots.

source: `data_view.py <https://svn.enthought.com/enthought/browser/Chaco/trunk/examples/data_view.py>`_

.. image:: example_images/data_view.png

``edit_line.py``
----------------
Allows editing of a line plot.

source: `edit_line.py <https://svn.enthought.com/enthought/browser/Chaco/trunk/examples/edit_line.py>`_

.. image:: example_images/edit_line.png

``financial_plot.py``
---------------------
Implementation of a standard financial plot visualization using Chaco renderers
and scales. Right-clicking and selecting an area in the top window zooms in
the corresponding area in the lower window.

source: `financial_plot.py <https://svn.enthought.com/enthought/browser/Chaco/trunk/examples/financial_plot.py>`_

.. image:: example_images/financial_plot.png

``financial_plot_dates.py``
---------------------------
Implementation of a standard financial plot visualization using Chaco renderers
and scales. Right-clicking and selecting an area in the top window zooms in
the corresopnding area in the lower window.
This differs from the financial_plot.py example in that it uses a date-oriented
axis.

source: `financial_plot_dates.py <https://svn.enthought.com/enthought/browser/Chaco/trunk/examples/financial_plot_dates.py>`_

.. image:: example_images/financial_plot_dates.png

``multiaxis.py``
----------------
Draws several overlapping line plots like simple_line.py, but uses a separate
Y range for each plot.  Also has a second Y-axis on the right hand side.
Demonstrates use of the BroadcasterTool.

source: `multiaxis.py <https://svn.enthought.com/enthought/browser/Chaco/trunk/examples/multiaxis.py>`_

.. image:: example_images/multiaxis.png

``multiaxis_using_Plot.py``
---------------------------
Draws some x-y line and scatter plots. On the left hand plot:
 - Left-drag pans the plot.
 - Mousewheel up and down zooms the plot in and out.
 - Pressing "z" opens the Zoom Box, and you can click-drag a rectangular 
   region to zoom. If you use a sequence of zoom boxes, pressing alt-left-arrow
   and alt-right-arrow moves you forwards and backwards through the "zoom 
   history".

source: `multiaxis_using_Plot.py <https://svn.enthought.com/enthought/browser/Chaco/trunk/examples/multiaxis_using_Plot.py>`_

.. image:: example_images/multiaxis_using_Plot.png

``noninteractive.py``
---------------------
This demonstrates how to create a plot offscreen and save it to an image file
on disk. The image is what is saved.

source: `noninteractive.py <https://svn.enthought.com/enthought/browser/Chaco/trunk/examples/noninteractive.py>`_

.. image:: example_images/noninteractive.png

``range_selection_demo.py``
---------------------------
Demo of the RangeSelection on a line plot.  Left-click and drag creates a
horizontal range selection; this selection can then be dragged around, or
resized by dragging its edges.

source: `range_selection_demo.py <https://svn.enthought.com/enthought/browser/Chaco/trunk/examples/range_selection_demo.py>`_

.. image:: example_images/range_selection_demo.png

``scales_test.py``
------------------
Draws several overlapping line plots.

Double-clicking on line or scatter plots opens a Traits editor for the plot.

source: `scales_test.py <https://svn.enthought.com/enthought/browser/Chaco/trunk/examples/scales_test.py>`_

.. image:: example_images/scales_test.png

``simple_line.py``
------------------
Draws several overlapping line plots.

Double-clicking on line or scatter plots opens a Traits editor for the plot.

source: `simple_line.py <https://svn.enthought.com/enthought/browser/Chaco/trunk/examples/simple_line.py>`_

.. image:: example_images/simple_line.png

.. [COMMENT]::

    ``simple_polar.py``
    -------------------
    Draws a static polar plot.

    source: `simple_polar.py <https://svn.enthought.com/enthought/browser/Chaco/trunk/examples/simple_polar.py>`_

    .. image:: example_images/simple_polar.png

``tornado.py``
--------------
Tornado plot example from Brennan Williams.

source: `tornado.py <https://svn.enthought.com/enthought/browser/Chaco/trunk/examples/tornado.py>`_

.. image:: example_images/tornado.png

``two_plots.py``
----------------
Demonstrates plots sharing datasources, ranges, etc...

source: `two_plots.py <https://svn.enthought.com/enthought/browser/Chaco/trunk/examples/two_plots.py>`_

.. image:: example_images/two_plots.png

``vertical_plot.py``
--------------------
Draws a static plot of bessel functions, oriented vertically, side-by-side.

You can experiment with using different containers (uncomment lines 32-33)
or different orientations on the plots (comment out line 43 and uncomment 44).

source: `vertical_plot.py <https://svn.enthought.com/enthought/browser/Chaco/trunk/examples/vertical_plot.py>`_

.. image:: example_images/vertical_plot.png

``data_cube.py``
----------------
Allows isometric viewing of a 3-D data cube (downloads the necessary data, about 7.8 MB)

source: `data_cube.py <https://svn.enthought.com/enthought/browser/Chaco/trunk/examples/advanced/data_cube.py>`_

.. image:: example_images/data_cube.png

``data_stream.py``
------------------
This demo shows how Chaco and Traits can be used to easily build a data
acquisition and visualization system.

Two frames are opened: one has the plot and allows configuration of
various plot properties, and one which simulates controls for the hardware
device from which the data is being acquired; in this case, it is a mockup
random number generator whose mean and standard deviation can be controlled
by the user.

source: `data_stream.py <https://svn.enthought.com/enthought/browser/Chaco/trunk/examples/advanced/data_stream.py>`_

.. image:: example_images/data_stream.png

``scalar_image_function_inspector.py``
--------------------------------------
Renders a colormapped image of a scalar value field, and a cross section
chosen by a line interactor.

source: `scalar_image_function_inspector.py <https://svn.enthought.com/enthought/browser/Chaco/trunk/examples/advanced/scalar_image_function_inspector.py>`_

.. image:: example_images/scalar_image_function_inspector.png

``spectrum.py``
--------------------------------------
This plot displays the audio spectrum from the microphone.

source: `spectrum.py <https://svn.enthought.com/enthought/browser/Chaco/trunk/examples/advanced/spectrum.py>`_

.. image:: example_images/spectrum.png

``cmap_image_plot.py``
----------------------
Draws a colormapped image plot.

source: `cmap_image_plot.py <https://svn.enthought.com/enthought/browser/Chaco/trunk/examples/basic/cmap_image_plot.py>`_

.. image:: example_images/cmap_image_plot.png

``cmap_image_select.py``
-------------------------
Draws a colormapped image plot. Selecting colors in the spectrum on the right
highlights the corresponding colors in the color map.

source: `cmap_image_select.py <https://svn.enthought.com/enthought/browser/Chaco/trunk/examples/basic/cmap_image_select.py>`_

.. image:: example_images/cmap_image_select.png

``cmap_scatter.py``
-------------------
Draws a colormapped scatterplot of some random data. Selection works the same as in cmap_image_select.py.

source: `cmap_scatter.py <https://svn.enthought.com/enthought/browser/Chaco/trunk/examples/basic/cmap_scatter.py>`_

.. image:: example_images/cmap_scatter.png

``contour_cmap_plot.py``
--------------------------
Renders some contoured and colormapped images of a scalar value field.

source: `countour_cmap_plot.py <https://svn.enthought.com/enthought/browser/Chaco/trunk/examples/basic/contour_cmap_plot.py>`_

.. image:: example_images/contour_cmap_plot.png

``contour_plot.py``
-------------------
Draws an contour polygon plot with a contour line plot on top.

source: `countour_plot.py <https://svn.enthought.com/enthought/browser/Chaco/trunk/examples/basic/contour_plot.py>`_

.. image:: example_images/contour_plot.png

``grid_container.py``
---------------------
Draws several overlapping line plots.

source: `grid_container.py <https://svn.enthought.com/enthought/browser/Chaco/trunk/examples/basic/grid_container.py>`_

.. image:: example_images/grid_container.png

``grid_container_aspect_ratio``
-------------------------------
Similar to grid_container.py, but demonstrates Chaco's capability to used a
fixed screen space aspect ratio for plot components.

source: `grid_container_aspect_ratio.py <https://svn.enthought.com/enthought/browser/Chaco/trunk/examples/basic/grid_container_aspect_ratio.py>`_

.. image:: example_images/grid_container_aspect_ratio.png

``image_from_file.py``
----------------------
Loads and saves RGB images from disk.

source: `image_from_file.py <https://svn.enthought.com/enthought/browser/Chaco/trunk/examples/basic/image_from_file.py>`_

.. image:: example_images/image_from_file.png

``image_inspector.py``
----------------------
Demonstrates the ImageInspectorTool and overlay on a colormapped image plot.
The underlying plot is similar to the one in cmap_image_plot.py.

source: `image_inspector.py <https://svn.enthought.com/enthought/browser/Chaco/trunk/examples/basic/image_inspector.py>`_

.. image:: example_images/image_inspector.png

``image_plot.py``
-----------------
Draws a simple RGB image

source: `image_plot.py <https://svn.enthought.com/enthought/browser/Chaco/trunk/examples/basic/image_plot.py>`_

.. image:: example_images/image_plot.png

``inset_plot.py``
-----------------
A modification of line_plot1.py that shows the second plot as a subwindow of
the first.  You can pan and zoom the second plot just like the first, and you
can move it around my right-click and dragging in the smaller plot.

source: `inset_plot.py <https://svn.enthought.com/enthought/browser/Chaco/trunk/examples/basic/inset_plot.py>`_

.. image:: example_images/inset_plot.png

``line_drawing.py``
--------------------
Demonstrates using a line segment drawing tool on top of the scatter plot from
simple_scatter.py.

source: `line_drawing.py <https://svn.enthought.com/enthought/browser/Chaco/trunk/examples/basic/line_drawing.py>`_

.. image:: example_images/line_drawing.png

``line_plot1.py``
-----------------
Draws some x-y line and scatter plots.

source: `line_plot1.py <https://svn.enthought.com/enthought/browser/Chaco/trunk/examples/basic/line_plot1.py>`_

.. image:: example_images/line_plot1.png

``line_plot_hold.py``
---------------------
Demonstrates the different 'hold' styles of LinePlot.

source: `line_plot_hold.py <https://svn.enthought.com/enthought/browser/Chaco/trunk/examples/basic/line_plot_hold.py>`_

.. image:: example_images/line_plot_hold.png

``log_plot.py``
-----------------
Draws some x-y log plots. (No Tools).

source: `log_plot.py <https://svn.enthought.com/enthought/browser/Chaco/trunk/examples/basic/log_plot.py>`_

.. image:: example_images/log_plot.png

``nans_plot.py``
----------------
This plot displays chaco's ability to handle data interlaced with NaNs.

source: `nans_plot.py <https://svn.enthought.com/enthought/browser/Chaco/trunk/examples/basic/nans_plot.py>`_

.. image:: example_images/nans_plot.png

``polygon_plot.py``
-------------------
Draws some different polygons.

source: `polygon_plot.py <https://svn.enthought.com/enthought/browser/Chaco/trunk/examples/basic/polygon_plot.py>`_

.. image:: example_images/polygon_plot.png

``polygon_move.py``
-------------------
Shares same basic interactions as polygon_plot.py, but adds a new one: 
right-click and drag to move a polygon around.

source: `polygon_move.py <https://svn.enthought.com/enthought/browser/Chaco/trunk/examples/basic/polygon_move.py>`_

.. image:: example_images/polygon_move.png

``regression.py``
-------------------
Demonstrates the Regression Selection tool.

Hold down the left mouse button to use the mouse to draw a selection region
around some points, and a line fit is drawn through the center of the points.
The parameters of the line are displayed at the bottom of the plot region.  You
can do this repeatedly to draw different regions.

source: `regression.py <https://svn.enthought.com/enthought/browser/Chaco/trunk/examples/basic/regression.py>`_

.. image:: example_images/regression.png

``scatter.py``
-------------------
Draws a simple scatterplot of a set of random points.

source: `scatter.py <https://svn.enthought.com/enthought/browser/Chaco/trunk/examples/basic/scatter.py>`_

.. image:: example_images/scatter.png

``scatter_inspector.py``
------------------------
Example of using tooltips on Chaco plots.

source: `scatter_inspector.py <https://svn.enthought.com/enthought/browser/Chaco/trunk/examples/basic/scatter_inspector.py>`_

.. image:: example_images/scatter_inspector.png

``scatter_select.py``
------------------------
Draws a simple scatterplot of random data.  The only interaction available is
the lasso selector, which allows you to circle a set of points.  Upon
completion of the lasso operation, the indices of the selected points are
printed to the console.

source: `scatter_select.py <https://svn.enthought.com/enthought/browser/Chaco/trunk/examples/basic/scatter_select.py>`_

.. image:: example_images/scatter_select.png

console output::

    New selection: 
        [789  799  819  830  835  836  851  867  892  901  902  909  913  924  929
         931  933  938  956  971  972  975  976  996  999 1011 1014 1016 1021 1030
         1045 1049 1058 1061 1073 1086 1087 1088]

``scrollbar.py``
-------------------
Draws some x-y line and scatter plots.

source: `scrollbar.py <https://svn.enthought.com/enthought/browser/Chaco/trunk/examples/basic/scrollbar.py>`_

.. image:: example_images/scrollbar.png

``tabbed_plots.py``
-------------------
Draws some x-y line and scatter plots.

source: `tabbed_plots.py <https://svn.enthought.com/enthought/browser/Chaco/trunk/examples/basic/tabbed_plots.py>`_

.. image:: example_images/tabbed_plots1.png
.. image:: example_images/tabbed_plots2.png

``traits_editor.py``
--------------------
This example creates a simple 1-D function examiner, illustrating the use of
ChacoPlotEditors for displaying simple plot relations, as well as Traits UI
integration. Any 1-D numpy/scipy.special function works in the function
text box.

source: `traits_editor.py <https://svn.enthought.com/enthought/browser/Chaco/trunk/examples/basic/traits_editor.py>`_

.. image:: example_images/traits_editor.png

``zoomable_colorbar.py``
------------------------
Draws a colormapped scatterplot of some random data.

Interactions on the plot are the same as for simple_line.py, and additionally, 
pan and zoom are available on the colorbar. 

Left-click pans the colorbar's data region.  Right-click-drag 
selects a zoom range.  Mousewheel up and down zoom in and out on
the data bounds of the color bar.

source: `zoomable_colorbar.py <https://svn.enthought.com/enthought/browser/Chaco/trunk/examples/basic/zoomable_colorbar.py>`_

.. image:: example_images/zoomable_colorbar.png

``zoomed_plot``
------------------------
The main executable file for the zoom_plot demo.
 
Right-click and drag on the upper plot to select a region to view in detail
in the lower plot.  The selected region can be moved around by dragging,
or resized by clicking on one of its edges and dragging.

source: `zoomed_plot <https://svn.enthought.com/enthought/browser/Chaco/trunk/examples/zoomed_plot/>`_

.. image:: example_images/zoomed_plot.png
