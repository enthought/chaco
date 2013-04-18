Chaco Plot - Axes Range Options
===============================

.. highlight:: python
  :linenothreshold: 5

.. index::
  pair: Axes; Range

The range of a 2D Chaco plot is controled by the ``range2d`` object. Let's generate
a Chaco plot, and output attributes associated with the range of the axes::

  ## ex_chaco_myTP.range_01.py

  # standard imports
  import inspect, os
  import numpy as np

  # Enthought imports
  from enable.api import ComponentEditor
  from traits.api import HasTraits
  from traitsui.api import Item, Group, View
  from chaco.api import Plot, ArrayPlotData

  # defines
  windowSize = (800,600)

  # window title is file name
  windowTitle = os.path.split(__file__)[1]

  class TraitedPlot( HasTraits ):

    numPoints = 100
    extent = 2.0 * np.pi
    phaseA = np.linspace( -extent,extent,numPoints )
    amplitudeA = np.sin( phaseA ) * np.exp(-abs( phaseA ))

    myTADP = ArrayPlotData()
    myTADP.set_data( 'X',phaseA )
    myTADP.set_data( 'Y',amplitudeA )

    myTP = Plot( myTADP )
    myTP.plot(
        ("X", "Y"),
        type = 'line',
    )

    # The actual value of the lower left/upper right bounds of this range as (x,y)
    # points. To set them, use low_setting/high_setting.
    myTP.range2d.low
    myTP.range2d.high

    # a 2-tuple of lower left/upper right (x,y) bounds. Either can be set to
    # 'auto', causing the range to autocalculate
    myTP.range2d.low_setting
    myTP.range2d.high_setting

    # Sets all the bounds of the range simultaneously. Lower left/upper right
    # corners of the data range.
    # Ex. myTP.range2d.set_bounds( (1,2), (3,4) ) sets the lower left to (1,2) and
    # the upper right to (3,4)
    myTP.range2d.set_bounds

    # ranges in the x- and y- dimensions. These are DataRange1D objects, one for
    # the x- axis and one for the y- axis
    myTP.range2d.x_range
    myTP.range2d.y_range

    # the low/high values for the x-/y- axes. can be set to
    #   'auto': The lower bound is automatically set at or below the minimum
    #     of the data.
    #   'track': The lower bound tracks the upper bound by tracking_amount.
    #   CFloat: An explicit value for the lower bound
    # set with the appropriate _setting method
    myTP.range2d.x_range.low
    myTP.range2d.x_range.high
    myTP.range2d.y_range.low
    myTP.range2d.y_range.high

    myTP.range2d.x_range.low_setting
    myTP.range2d.x_range.high_setting
    myTP.range2d.y_range.low_setting
    myTP.range2d.y_range.high_setting

    # Do 'auto' bounds imply an exact fit to the data? (One Boolean per dimension)
    # If False, the bounds pad a little bit of margin on either side. Setting
    # the range2d.tight_bounds does not work (i.e. myTP.range2d.tight_bounds =
    # (False,False)) does nothing. Defaults to (True,True) which causes the axes
    # bounds to exactly correspond to the data
    myTP.range2d.x_range.tight_bounds = False
    myTP.range2d.y_range.tight_bounds = False

    # The minimum percentage difference between low and high for each dimension.
    # That is, (high-low) >= epsilon * low.
    myTP.range2d.epsilon

    # If any of the bounds is 'auto', this method refreshes the actual low and
    # high values from the set of the view filters' data sources.
    myTP.range2d.refresh()

    # Resets the bounds of this range.
    myTP.range2d.reset()

    traits_view = View(
        Group(
            Item(
                'myTP',
                editor = ComponentEditor(size = windowSize),
                show_label = False,
            ),
            orientation = "vertical",
        ),
        resizable = True,
        title = windowTitle,
    )

  if __name__ == "__main__":

    tp = TraitedPlot()
    tp.configure_traits()

    print( tp.myTP.range2d )

    myMethods = inspect.getmembers(tp.myTP.range2d)
    myPublics = [thisItem for thisItem in myMethods if thisItem[0][0] != '_']
    print( myPublics )

    tp.myTP.range2d.print_traits()

The reader is encouraged to examine the outputs of the ``print( myPlot.myTP.range2d )``,
the ``print( myPublics )`` and the the ``tp.myTP.range2d.print_traits()`` calls.
The outputs are reproduced under Excruciating Detail below.

Excruciating Detail
-------------------

.. index
  pair: DataRange2D; print_traits()

The result of the ``print( myPlot.myTP.range2d )`` call is::

  <chaco.data_range_2d.DataRange2D object at 0x05BD1FC0>

The output from the ``print( myPublics )`` call is::

  [
  ('add', <bound method DataRange2D.add of <chaco.data_range_2d.DataRange2D object at 0x05BE7210>>),
  ('add_class_trait', <bound method MetaHasTraits.add_class_trait of <class 'chaco.data_range_2d.DataRange2D'>>),
  ('add_trait', <bound method DataRange2D.add_trait of <chaco.data_range_2d.DataRange2D object at 0x05BE7210>>),
  ('add_trait_category', <bound method MetaHasTraits.add_trait_category of <class 'chaco.data_range_2d.DataRange2D'>>),
  ('add_trait_listener', <bound method DataRange2D.add_trait_listener of <chaco.data_range_2d.DataRange2D object at 0x05BE7210>>),
  ('all_trait_names', <bound method DataRange2D.all_trait_names of <chaco.data_range_2d.DataRange2D object at 0x05BE7210>>),
  ('base_trait', <bound method DataRange2D.base_trait of <chaco.data_range_2d.DataRange2D object at 0x05BE7210>>),
  ('bound_data', <bound method DataRange2D.bound_data of <chaco.data_range_2d.DataRange2D object at 0x05BE7210>>),
  ('class_default_traits_view', <bound method MetaHasTraits.class_default_traits_view of <class 'chaco.data_range_2d.DataRange2D'>>),
  ('class_editable_traits', <bound method MetaHasTraits.class_editable_traits of <class 'chaco.data_range_2d.DataRange2D'>>),
  ('class_trait_names', <bound method MetaHasTraits.class_trait_names of <class 'chaco.data_range_2d.DataRange2D'>>),
  ('class_trait_view', <bound method MetaHasTraits.class_trait_view of <class 'chaco.data_range_2d.DataRange2D'>>),
  ('class_trait_view_elements', <bound method MetaHasTraits.class_trait_view_elements of <class 'chaco.data_range_2d.DataRange2D'>>),
  ('class_traits', <bound method MetaHasTraits.class_traits of <class 'chaco.data_range_2d.DataRange2D'>>),
  ('clip_data', <bound method DataRange2D.clip_data of <chaco.data_range_2d.DataRange2D object at 0x05BE7210>>),
  ('clone_traits', <bound method DataRange2D.clone_traits of <chaco.data_range_2d.DataRange2D object at 0x05BE7210>>),
  ('configure_traits', <bound method DataRange2D.configure_traits of <chaco.data_range_2d.DataRange2D object at 0x05BE7210>>),
  ('copy_traits', <bound method DataRange2D.copy_traits of <chaco.data_range_2d.DataRange2D object at 0x05BE7210>>),
  ('copyable_trait_names', <bound method DataRange2D.copyable_trait_names of <chaco.data_range_2d.DataRange2D object at 0x05BE7210>>),
  ('default_traits_view', <bound method DataRange2D.default_traits_view of <chaco.data_range_2d.DataRange2D object at 0x05BE7210>>),
  ('edit_traits', <bound method DataRange2D.edit_traits of <chaco.data_range_2d.DataRange2D object at 0x05BE7210>>),
  ('editable_traits', <bound method DataRange2D.editable_traits of <chaco.data_range_2d.DataRange2D object at 0x05BE7210>>),
  ('epsilon', (0.0001, 0.0001)),
  ('get', <bound method DataRange2D.trait_get of <chaco.data_range_2d.DataRange2D object at 0x05BE7210>>),
  ('has_traits_interface', <bound method DataRange2D.has_traits_interface of <chaco.data_range_2d.DataRange2D object at 0x05BE7210>>),
  ('mask_data', <bound method DataRange2D.mask_data of <chaco.data_range_2d.DataRange2D object at 0x05BE7210>>),
  ('on_trait_change', <bound method DataRange2D.on_trait_change of <chaco.data_range_2d.DataRange2D object at 0x05BE7210>>),
  ('on_trait_event', <bound method DataRange2D.on_trait_change of <chaco.data_range_2d.DataRange2D object at 0x05BE7210>>),
  ('print_traits', <bound method DataRange2D.print_traits of <chaco.data_range_2d.DataRange2D object at 0x05BE7210>>),
  ('refresh', <bound method DataRange2D.refresh of <chaco.data_range_2d.DataRange2D object at 0x05BE7210>>),
  ('remove', <bound method DataRange2D.remove of <chaco.data_range_2d.DataRange2D object at 0x05BE7210>>),
  ('remove_trait', <bound method DataRange2D.remove_trait of <chaco.data_range_2d.DataRange2D object at 0x05BE7210>>),
  ('remove_trait_listener', <bound method DataRange2D.remove_trait_listener of <chaco.data_range_2d.DataRange2D object at 0x05BE7210>>),
  ('reset', <bound method DataRange2D.reset of <chaco.data_range_2d.DataRange2D object at 0x05BE7210>>),
  ('reset_traits', <bound method DataRange2D.reset_traits of <chaco.data_range_2d.DataRange2D object at 0x05BE7210>>),
  ('set', <bound method DataRange2D.trait_set of <chaco.data_range_2d.DataRange2D object at 0x05BE7210>>),
  ('set_bounds', <bound method DataRange2D.set_bounds of <chaco.data_range_2d.DataRange2D object at 0x05BE7210>>),
  ('set_trait_dispatch_handler', <bound method MetaHasTraits.set_trait_dispatch_handler of <class 'chaco.data_range_2d.DataRange2D'>>),
  ('sync_trait', <bound method DataRange2D.sync_trait of <chaco.data_range_2d.DataRange2D object at 0x05BE7210>>),
  ('trait', <bound method DataRange2D.trait of <chaco.data_range_2d.DataRange2D object at 0x05BE7210>>),
  ('trait_context', <bound method DataRange2D.trait_context of <chaco.data_range_2d.DataRange2D object at 0x05BE7210>>),
  ('trait_get', <bound method DataRange2D.trait_get of <chaco.data_range_2d.DataRange2D object at 0x05BE7210>>),
  ('trait_items_event', <built-in method trait_items_event of DataRange2D object at 0x05BE7210>),
  ('trait_monitor', <bound method MetaHasTraits.trait_monitor of <class 'chaco.data_range_2d.DataRange2D'>>),
  ('trait_names', <bound method DataRange2D.trait_names of <chaco.data_range_2d.DataRange2D object at 0x05BE7210>>),
  ('trait_property_changed', <built-in method trait_property_changed of DataRange2D object at 0x05BE7210>),
  ('trait_set', <bound method DataRange2D.trait_set of <chaco.data_range_2d.DataRange2D object at 0x05BE7210>>),
  ('trait_setq', <bound method DataRange2D.trait_setq of <chaco.data_range_2d.DataRange2D object at 0x05BE7210>>),
  ('trait_subclasses', <bound method MetaHasTraits.trait_subclasses of <class 'chaco.data_range_2d.DataRange2D'>>),
  ('trait_view', <bound method DataRange2D.trait_view of <chaco.data_range_2d.DataRange2D object at 0x05BE7210>>),
  ('trait_view_elements', <bound method DataRange2D.trait_view_elements of <chaco.data_range_2d.DataRange2D object at 0x05BE7210>>),
  ('trait_views', <bound method DataRange2D.trait_views of <chaco.data_range_2d.DataRange2D object at 0x05BE7210>>),
  ('traits', <bound method DataRange2D.traits of <chaco.data_range_2d.DataRange2D object at 0x05BE7210>>),
  ('traits_init', <built-in method traits_init of DataRange2D object at 0x05BE7210>),
  ('traits_inited', <built-in method traits_inited of DataRange2D object at 0x05BE7210>),
  ('validate_trait', <bound method DataRange2D.validate_trait of <chaco.data_range_2d.DataRange2D object at 0x05BE7210>>),
  ('wrappers',
    { 'new': <class traits.trait_notifiers.NewTraitChangeNotifyWrapper at 0x03D36110>,
      'ui': <class traits.trait_notifiers.FastUITraitChangeNotifyWrapper at 0x03D360A0>,
      'extended': <class traits.trait_notifiers.ExtendedTraitChangeNotifyWrapper at 0x03D36068>,
      'fast_ui': <class traits.trait_notifiers.FastUITraitChangeNotifyWrapper at 0x03D360A0>,
      'same': <class traits.trait_notifiers.TraitChangeNotifyWrapper at 0x03D36030>})
  ]

Here's the output from the ``tp.myTP.range2d.print_traits()`` call::

  _high_setting: ('auto', 'auto')
  _high_value:   (inf, inf)
  _low_setting:  ('auto', 'auto')
  _low_value:    (-inf, -inf)
  _xrange:       <chaco.data_range_1d.DataRange1D object at 0x05BE75D0>
  _yrange:       <chaco.data_range_1d.DataRange1D object at 0x05BE7750>
  epsilon:       (0.0001, 0.0001)
  high:          (8.0, 0.4)
  high_setting:  ('auto', 'auto')
  low:           (-8.0, -0.4)
  low_setting:   ('auto', 'auto')
  sources:       []
  tight_bounds:  (True, True)
  x_range:       <chaco.data_range_1d.DataRange1D object at 0x05BE75D0>
  y_range:       <chaco.data_range_1d.DataRange1D object at 0x05BE7750>
