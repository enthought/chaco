**********
Plot Types
**********

The code to generate the examples in this section can be found in
the directory ``tutorials/user_guide/plot_types/`` in the examples
directory.

================================================================
X-Y Plot Types
================================================================

grids

hittest

selected

Line Plot
=========

Standard line plot implementation. The aspect of the line is controlled by the
parameters

:attr:`~chaco.lineplot.LinePlot.line_width`
  The width of the line (default is 1.0)

:attr:`~chaco.lineplot.LinePlot.line_style`
  The style of the line, one of 'solid' (default), 'dot dash', 'dash', 'dot',
  or 'long dash'.

:attr:`~chaco.lineplot.LinePlot.render_style`
  The rendering style of the line plot, one of
  'connectedpoints' (default), 'hold', or 'connectedhold'

These images illustrate the differences in rendering style:

* ``renderstyle='connectedpoints'``

    .. image:: images/user_guide/line_plot.png
      :width: 350px

* ``renderstyle='hold'``

    .. image:: images/user_guide/line_hold_plot.png
      :width: 350px

* ``renderstyle='connectedhold'``

    .. image:: images/user_guide/line_connectedhold_plot.png
      :width: 350px

Scatter Plot
============

Standard scatter plot implementation. The aspect of the markers is controlled
by the parameters

:attr:`~chaco.scatterplot.ScatterPlot.marker`
  The marker type, one of 'square'(default), 'circle', 'triangle',
  'inverted_triangle', 'plus', 'cross', 'diamond', 'dot', or 'pixel'.
  One can also define a new marker shape by setting this parameter to 'custom',
  and set the :attr:`~chaco.scatterplot.custom_symbol` parameter to
  a :class:`CompiledPath` instance (see the file
  ``demo/basic/scatter_custom_marker.py`` in the Chaco examples directory).

:attr:`~chaco.scatterplot.ScatterPlot.marker_size`
  Size of the marker in pixels, not including the outline (default is 4.0).

:attr:`~chaco.scatterplot.ScatterPlot.line_width`
  Width of the outline around the markers (default is 1.0). If this is 0.0,
  no outline is drawn.

:attr:`~chaco.scatterplot.ScatterPlot.color`
    The fill color of the marker (default is black).

:attr:`~chaco.scatterplot.ScatterPlot.outline_color`
    The color of the outline to draw around the marker (default is black).

.. image:: images/user_guide/scatter_plot.png
  :width: 500px


Pseudocolor Scatter Plot
========================


.. image:: images/user_guide/cmap_scatter_plot.png
  :width: 500px


Candle Plot
===========

A candle plot represents summary statistics of distribution of values
for a set of discrete items. Each distribution is characterized by
a central line (usually representing the mean), a bar (usually representing
one standard deviation around the mean or the 10th and 90th percentile),
and two stems (usually indicating the maximum and minimum values).

The positions of the centers, and of the extrema of the bar and stems are
set with the following data sources

:attr:`~chaco.candle_plot.CandlePlot.center_values`
  Value of the centers. It can be set to ``None``, in which case the center is
  not plotted.

:attr:`~chaco.candle_plot.CandlePlot.bar_min` and :attr:`~chaco.candle_plot.CandlePlot.bar_max`
  Lower and upper values of the bar.

:attr:`~chaco.candle_plot.CandlePlot.min_values` and :attr:`~chaco.candle_plot.CandlePlot.max_values`
  Lower and upper values of the stem. They can be set to ``None``, in
  which case the stems are not plotted.

It is possible to customize the appearance of the candle plot with
these parameters

:attr:`~chaco.candle_plot.CandlePlot.bar_color` (alias of :attr:`~chaco.candle_plot.CandlePlot.color`)
  Fill color of the bar (default is black).

:attr:`~chaco.candle_plot.CandlePlot.bar_line_color` (alias of :attr:`~chaco.candle_plot.CandlePlot.outline_color`)
  Color of the box forming the bar (default is black).

:attr:`~chaco.candle_plot.CandlePlot.center_color`
  Color of the line indicating the center. If ``None``, it defaults to
  :attr:`~chaco.candle_plot.CandlePlot.bar_line_color`.

:attr:`~chaco.candle_plot.CandlePlot.stem_color`
  Color of the stems and endcaps. If ``None``, it defaults to
  :attr:`~chaco.candle_plot.CandlePlot.bar_line_color`.

:attr:`~chaco.candle_plot.CandlePlot.line_width`, :attr:`~chaco.candle_plot.CandlePlot.center_width`, and :attr:`~chaco.candle_plot.CandlePlot.stem_width`
  Thickness in pixels of the lines drawing the corresponding elements.
  If ``None``, they default to :attr:`~chaco.candle_plot.CandlePlot.line_width`.

:attr:`~chaco.candle_plot.CandlePlot.end_cap`
  If ``False``, the end caps are not plotted (default is ``True``).


At the moment, it is not possible to control the width of the central bar
and end caps.

.. image:: images/user_guide/candle_plot.png
  :width: 500px


Errorbar Plot
=============


Filled Line Plot
================



================================================================
Image and 2D Plots
================================================================



Image Plots (from file)
=======================


Pseudocolor Scalar Plot
=======================


Contour Plot
============


Polygon Plot
============



================================================================
Other Plot Types
================================================================

Bar Plot
========


Quiver Plot
===========


Polar Plot
==========

Jitter Plot
===========

A plot showing 1D data by adding a random jitter around the main axis.
It can be useful for visualize dense collections of points.
This plot has got a single mapper,
called :class:`~chaco.jitterplot.JitterPlot.mapper`.

Useful parameters are:

:attr:`~chaco.jitterplot.JitterPlot.jitter_width`
  The size, in pixels, of the random jitter around the axis.

:attr:`~chaco.jitterplot.JitterPlot.marker`
  The marker type, one of 'square'(default), 'circle', 'triangle',
  'inverted_triangle', 'plus', 'cross', 'diamond', 'dot', or 'pixel'.
  One can also define a new marker shape by setting this parameter to 'custom',
  and set the :attr:`~chaco.scatterplot.custom_symbol` parameter to
  a :class:`CompiledPath` instance (see the file
  ``demo/basic/scatter_custom_marker.py`` in the Chaco examples directory).

:attr:`~chaco.jitterplot.JitterPlot.marker_size`
  Size of the marker in pixels, not including the outline (default is 4.0).

:attr:`~chaco.jitterplot.JitterPlot.line_width`
  Width of the outline around the markers (default is 1.0). If this is 0.0,
  no outline is drawn.

:attr:`~chaco.jitterplot.JitterPlot.color`
    The fill color of the marker (default is black).

:attr:`~chaco.jitterplot.JitterPlot.outline_color`
    The color of the outline to draw around the marker (default is black).

.. image:: images/user_guide/jitter_plot.png
  :width: 500px
