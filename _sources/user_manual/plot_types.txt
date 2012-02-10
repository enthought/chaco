**********
Plot Types
**********

This section gives an overview of individual plot classes in Chaco.

The code to generate the figures in this section can be found in
the directory ``tutorials/user_guide/plot_types/`` in the examples
directory.

For more complete examples, see also the :ref:`annotated examples <examples>`
page.

================================================================
X-Y Plot Types
================================================================

These plots display information in a two-axis coordinate system.
Unless otherwise stated, they are subclasses of
:class:`~chaco.base_xy_plot.BaseXYPlot`.


explain that you need to provide index, value, and mappers

grids

hittest

selected


.. _line_plot:

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
      :width: 500px

* ``renderstyle='hold'``

    .. image:: images/user_guide/line_hold_plot.png
      :width: 500px

* ``renderstyle='connectedhold'``

    .. image:: images/user_guide/line_connectedhold_plot.png
      :width: 500px


.. _scatter_plot:

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


Colormapped Scatter Plot
========================

Colormapped scatter plot. Additional information can be added to each point
by setting a different color.

The color information is controlled by the
:attr:`~chaco.colormapped_scatterplot.ColormappedScatterPlot.color_data`
data source, and the
:attr:`~chaco.colormapped_scatterplot.ColormappedScatterPlot.color_mapper`
mapper. A large number of ready-to-use color maps are defined in the
module :mod:`chaco.default_colormaps`.

In addition to the parameters supported by a
:ref:`scatter plot <scatter_plot>`, a colormapped scatter plot defines
these attributes:

:attr:`~chaco.colormapped_scatterplot.ColormappedScatterPlot.fill_alpha`
  Set the alpha value of the points.

:attr:`~chaco.colormapped_scatterplot.ColormappedScatterPlot.render_method`
  Set the sequence in which the points are drawn. It is one of

  'banded'
    draw points by color band; this is more efficient but some colors
    will appear more prominently if there are a lot of overlapping points

  'bruteforce'
    set the stroke color before drawing each marker

  'auto' (default)
    the approach is selected based on the number of points

  In practice, there is not much performance difference between the two
  methods.

In this example plot, color represents property-tax rate (red is low,
green is high):

.. image:: images/user_guide/cmap_scatter_plot.png
  :width: 500px

Variable Size Scatter Plot
==========================

Alternatively, one can display additional information in a scatter plot by
setting different sizes for the markers.

The size information is controlled by the
:attr:`~chaco.variable_size_scatterplot.VariableSizeScatterPlot.marker_size`
attribute, that accepts an array where each element represents the size
of the corresponding marker. Other attributes are inherited from
the :ref:`scatter plot <scatter_plot>` class.

This is the same plot as above, with the radius od the circles representing
property-tax rate:

.. image:: images/user_guide/vsize_scatter_plot.png
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

A plot with error bars. Note that :class:`~chacho.errorbar_plot.ErrorBarPlot`
only plots the error bars, and needs to be combined with a
:class:`~chacho.errorbar_plot.LinePlot` if one would like to have
a line connecting the central values.

The positions of the exterma of the bars are set by the data sources
:attr:`~chaco.errorbar_plot.value_low` and
:attr:`~chaco.errorbar_plot.value_high`.

In addition to the parameters supported by a
:ref:`line plot <line_plot>`, an errorbar plot defines
these attributes:

:attr:`~chaco.errorbar_plot.endcap_size`
  The width of the endcap bars in pixels.

:attr:`~chaco.errorbar_plot.endcap_style`
  Either 'bar' (default) or 'none', in which case no endcap bars are plotted.

.. image:: images/user_guide/errorbar_plot.png
  :width: 500px


Filled Line Plot
================

A line plot filled with color to the axis.

The following parameters are defined:

:attr:`~chaco.filled_line_plot.FilledLinePlot.fill_color`
  The color used to fill the plot.

:attr:`~chaco.filled_line_plot.FilledLinePlot.fill_direction`
  Fill the plot toward the origin ('down', default) ot towards the axis
  maximum ('up').

:attr:`~chaco.lineplot.LinePlot.render_style`
  The rendering style of the line plot, one of
  'connectedpoints' (default), 'hold', or 'connectedhold' (see
  :ref:`line plot <line_plot>` for a description of the different
  rendering styles).

:attr:`~chaco.filled_line_plot.FilledLinePlot` is a subclass of
:attr:`~chaco.filled_line_plot.PolygonPlot`, so to set the thickness of the
plot line one should use the parameter
:attr:`~chaco.filled_line_plot.PolygonPlot.edge_width` instead of
:attr:`line_width`.

.. image:: images/user_guide/filled_line_plot.png
  :width: 500px


================================================================
Image and 2D Plots
================================================================


These plots display information as a two-dimensional image.
Unless otherwise stated, they are subclasses of
:class:`~chaco.base_2d_plot.Base2DPlot`.

explain index, value, mappers


.. _image_plot:

Image Plots
=======================

Plot image data, provided as RGB or RGBA color information. If you need to
plot a 2D array as an image, use a :ref:`colormapped scalar plot
<colormapped_scalar_plot>`

In an :class:`~chaco.base_2d_plot.ImagePlot`, the :attr:`index` attribute
corresponds to the the data coordinates of the pixels (often a
:class:`~chaco.grid_data_source.GridDataSource`). The
:attr:`index_mapper` maps the data coordinates to
screen coordinates (typically using
a :class:`~chaco.grid_mapper.GridMapper`). The `value` is the image itself,
wrapped into the data source class :class:`~chaco.image_data.ImageData`.

.. image:: images/user_guide/image_plot.png
  :width: 500px

A typical use case is to display an image loaded from a file.
The preferred way to do this is using the factory method
:meth:`~chaco.image_data.ImageData.from_file` of the class
:class:`~chaco.image_data.ImageData`. For example: ::

    image_source = ImageData.fromfile('capitol.jpg')

    w, h = image_source.get_width(), image_source.get_height()
    index = GridDataSource(np.arange(w), np.arange(h))
    index_mapper = GridMapper(range=DataRange2D(low=(0, 0),
                                                high=(w-1, h-1)))

    image_plot = ImagePlot(
        index=index,
        value=image_source,
        index_mapper=index_mapper,
        origin='top left',
        **PLOT_DEFAULTS
    )


The code above displays this plot:

.. image:: images/user_guide/image_from_file_plot.png
  :width: 500px

.. _colormapped_scalar_plot:

Colormapped Scalar Plot
=======================

Plot a scalar field as an image. The image information is given as a 2D
array; the scalar values in the 2D array are mapped to colors using a color
map.

The basic class for colormapped scalar plots is
:class:`~chaco.cmap_image_plot.CMapImagePlot`.
As in :ref:`image plots <image_plot>`, the :attr:`index` attribute
corresponds to the the data coordinates of the pixels (a
:class:`~chaco.grid_data_source.GridDataSource`), and the
:attr:`index_mapper` maps the data coordinates to
screen coordinates (a :class:`~chaco.grid_mapper.GridMapper`). The scalar
data is passed through the :attr:`value` attribute as an
:class:`~chaco.image_data.ImageData` source. Finally,
a color mapper maps the scalar data to colors. The module
:mod:`chaco.default_colormaps` defines many ready-to-use colormaps.

For example: ::

    NPOINTS = 200

    xs = np.linspace(-2 * np.pi, +2 * np.pi, NPOINTS)
    ys = np.linspace(-1.5*np.pi, +1.5*np.pi, NPOINTS)
    x, y = np.meshgrid(xs, ys)
    z = scipy.special.jn(2, x)*y*x

    index = GridDataSource(xdata=xs, ydata=ys)
    index_mapper = GridMapper(range=DataRange2D(index))

    color_source = ImageData(data=z, value_depth=1)
    color_mapper = dc.Spectral(DataRange1D(color_source))

    cmap_plot = CMapImagePlot(
        index=index,
        index_mapper=index_mapper,
        value=color_source,
        value_mapper=color_mapper,
        **PLOT_DEFAULTS
    )


This creates the plot:

.. image:: images/user_guide/cmap_image_plot.png
  :width: 500px


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
