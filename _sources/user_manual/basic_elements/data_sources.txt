Data sources
============

A data source is a wrapper object for the actual data that the plot will be
handling. For the most part, a data source looks like an array of values,
with an optional mask and metadata.

The :ref:`data source interface <data_source_interface>`
provides methods for retrieving data,
estimating a size of the dataset,
indications about the dimensionality of the data, a place for metadata
(such as selections and annotations), and events that fire when the data gets
changed.

There are two primary reasons for a data source class:

* It provides a way for different plotting objects to reference the same data.

* It defines the interface to expose data from existing applications to Chaco.

In most cases, the standard :class:`~chaco.array_data_source.ArrayDataSource`
will suffice.

.. _data_source_interface:

Interface
---------

The basic interface for data sources is defined in
:class:`~chaco.abstract_data_source.AbstractDataSource`.
Here is a summary of the most important attributes and methods
(see the docstrings of this class for more details):

    :attr:`~chaco.abstract_data_source.AbstractDataSource.value_dimension`

      The dimensionality of the data value at each point. It is defined
      as a :class:`DimensionTrait`, i.e., one of
      "scalar", "point", "image", or "cube". For example,
      a :class:`GridDataSource` represents data in a 2D array and thus its
      :attr:`value_dimension` is "scalar".

    :attr:`~chaco.abstract_data_source.AbstractDataSource.index_dimension`

      The dimensionality of the data value at each point. It is defined
      as a :class:`DimensionTrait`, i.e., one of
      "scalar", "point", "image", or "cube". For example,
      a :class:`GridDataSource` represents data in a 2D array and thus its
      :attr:`index_dimension` is "image".

    :attr:`~chaco.abstract_data_source.AbstractDataSource.metadata`

      A dictionary that maps strings to arbitrary data. Usually, the mapped
      data is a set of indices, as in the case of selections and annotations.
      By default, :attr:`metadata` contains the keys *"selections"* (representing
      indices that are currently selected by some tool)
      and *"annotations"*, both initialized to an empty list.

    :attr:`~chaco.abstract_data_source.AbstractDataSource.persist_data`

      If True (default), the data that this data source refers to is serialized
      when the data source is.

    :meth:`~chaco.abstract_data_source.AbstractDataSource.get_data()`

      Returns a data array containing the data referred to by the data source.
      Treat the returned array as read-only.

    :meth:`~chaco.abstract_data_source.AbstractDataSource.is_masked()`

      Returns True if this data source's data uses a mask. In this case,
      to retrieve the data, call ``get_data_mask()`` instead of ``get_data()``.

    :meth:`~chaco.abstract_data_source.AbstractDataSource.get_data_mask()`

      Returns the full, raw, source data array and a corresponding binary
      mask array.  Treat both arrays as read-only.

    :meth:`~chaco.abstract_data_source.AbstractDataSource.get_size()`

      Returns the size of the data.

    :meth:`~chaco.abstract_data_source.AbstractDataSource.get_bounds()`

      Returns a tuple (min, max) of the bounding values for the data source.
      In the case of 2-D data, min and max are 2-D points that represent the
      bounding corners of a rectangle enclosing the data set.
      If data is the empty set, then the min and max vals are 0.0.

Events
------

:class:`~chaco.abstract_data_source.AbstractDataSource` defines three events
that can be used in Traits applications to react to changes in the data source:

    :attr:`~chaco.abstract_data_source.AbstractDataSource.data_changed`

      Fired when the data values change.

      .. note::

         This majority of concrete data sources do not fire this event when
         the data values change. Rather, the event is usually fired when new
         data or a new mask is assigned through setter methods (see
         notes below).

    :attr:`~chaco.abstract_data_source.AbstractDataSource.bounds_changed`

      Fired when the data bounds change.

    :attr:`~chaco.abstract_data_source.AbstractDataSource.metadata_changed`
      Fired when the content of :attr:`metadata` changes (both the
      :attr:`metadata` dictionary object or any of its items).


List of Chaco data sources
--------------------------

This is a list of all concrete implementations of data sources in Chaco:


:class:`~chaco.array_data_source.ArrayDataSource`

  A data source representing a single, continuous array of numerical data.
  This is the most common data source for Chaco plots.

  This subclass adds the following attributes and methods to the basic
  interface:

  :attr:`~chaco.abstract_data_source.ArrayDataSource.sort_order`

    The sort order of the data, one of 'ascending', 'descending', or 'none'.
    If the underlying data is sorted, and this attribute is set appropriately,
    Chaco is able to use shortcuts and optimizations in many places.

  :attr:`~chaco.abstract_data_source.ArrayDataSource.reverse_map(pt)`

    Returns the index of *pt* in the data source (optimized if
    :attr:`sort_order` is set).

  .. note::

     This class does not listen to the array for changes in the data values.
     The
     :attr:`data_changed` event is fired only when the data or the mask
     are set with the methods :meth:`set_data`, :meth:`set_mask`,
     or :meth:`remove_mask`.


:class:`~chaco.image_data.ImageData`

  Represents a 2D grid of image data.

  The underlying data array is 3D, where the third dimension is either
  1 (one scalar value at each point of the grid), 3 (one RGB vector at each
  point), or 4 (one RGBa vector at each point). The depth of the
  array is defined in the attribute
  :attr:`~chaco.image_data.ImageData.value_depth`.

  Access to the image data is controlled by three properties:
  The boolean attribute :attr:`~chaco.image_data.ImageData.transposed`
  defines whether the data array stored by this class is to be interpreted
  as transposed; :attr:`~chaco.image_data.ImageData.raw_value` returns the
  underlying data array as-is, ignoring :attr:`transposed`;
  :attr:`~chaco.image_data.ImageData.value` returns the data array or its
  transposed depending on the value of :attr:`transposed`.

  The correct usage pattern of these attributes is to give to the class
  contiguous image data, and assign :attr:`transposed` if the
  two axis should be swapped. Functions that would benefit from working on
  contiguous data can then use :attr:`raw_value` directly. (See the
  class docstrings for more details, and some caveats.)

  Noteworthy methods of this class are:

  :attr:`~chaco.image_data.ImageData.fromfile(filename)`

    Factory method that creates an :class:`ImageData` instance from an image
    file. *filename* can be either a file path or a file object.

  :meth:`~chaco.image_data.ImageData.get_width`,
  :meth:`~chaco.image_data.ImageData.get_height`

    Return the width or the height of the image (takes the value
    of :attr:`transposed` into account).

  :meth:`~chaco.image_data.ImageData.get_array_bounds`

    Return ((0, width), (0, height)).

  .. note::

     This class does not implement the methods
     related to masking, and it does not fire :attr:`bounds_changed` events.

  .. note::

     This class does not listen to the array for changes in the data values.
     The :attr:`data_changed` event is fired only when the data
     are set with the method :meth:`set_data`.


:class:`~chaco.grid_data_source.GridDataSource`

  Data source representing the coordinates of a 2D grid.
  It is used, for example, as a source for the index data in an
  :class:`ImagePlot`.

  It defines these attributes:

  :attr:`~chaco.abstract_data_source.GridDataSource.sort_order`

    Similar to the :attr:`sort_order` attribute for the
    :class:`ArrayDataSource` class above, but this is a tuple
    with two elements, one per dimension.

  .. note::

     This class does not implement the methods
     related to masking, and it does not fire :attr:`bounds_changed` events.

  .. note::

     This class does not listen to the array for changes in the data values.
     The :attr:`data_changed` event is fired only when the data
     is set with the method :meth:`set_data`.


:class:`~chaco.multi_array_data_source.MultiArrayDataSource`

  A data source representing a single, continuous array of
  multidimensional numerical data.

  It is useful, for example, to define 2D vector data at each point of
  a scatter plot (as in :class:`~chaco.quiverplot.QuiverPlot`),
  or to represent multiple values
  for each index (as in :class:`~chaco.multi_line_plot.MultiLinePlot`).

  As :class:`ArrayDataSource`, this data source defines a
  :attr:`~chaco.abstract_data_source.MultiArrayDataSource.sort_order`
  attribute for its index dimension.

  .. warning::

     In :class:`MultiArrayDataSource`,
     the :attr:`index_dimension` and :attr:`value_dimension` attributes
     are integers that define which dimension of the data array
     correspond to indices and which
     to values (default is 0 and 1, respectively). This is different from
     the same attributes in the interface, which are strings describing the
     *dimensionality* of index and value.

  .. note::

     This class does not listen to the array for changes in the data values.
     The :attr:`data_changed` event is fired only when the data or the mask
     are set with the method :meth:`set_data`.


:class:`~chaco.point_data_source.PointDataSource`

  A data source representing a set of (X,Y) points.

  This is a subclass of :class:`ArrayDataSource`, and inherits its methods
  and attributes. The attribute
  :attr:`~chaco.point_data_source.PointDataSource.sort_index` defines
  whether the data is sorted along the X's or the Y's (as specified
  in :attr:`sort_order`).

  .. note::

     This class does not listen to the array for changes in the data values.
     The :attr:`data_changed` event is fired only when the data or the mask
     are set with the method :meth:`set_data`.


:class:`~chaco.function_data_source.FunctionDataSource`

  A subclass of :class:`~chaco.array_data_source.ArrayDataSource` that
  sets the values of the underlying data array based on a function
  (defined in the callable attribute
  :attr:`~chaco.function_data_source.FunctionDataSource.func`)
  evaluated on a 1D data range (defined in
  :attr:`~chaco.function_data_source.FunctionDataSource.data_range`).


:class:`~chaco.function_data_source.FunctionImageData`

  A subclass of :class:`~chaco.array_data_source.ImageData` that
  sets the values of the underlying data array based on a 2D function
  (defined in the callable attribute
  :attr:`~chaco.function_data_source.FunctionDataSource.func`)
  evaluated on a 2D data range (defined in
  :attr:`~chaco.function_data_source.FunctionDataSource.data_range`).
