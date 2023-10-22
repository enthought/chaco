Chaco Plot - Grid Options
=========================

.. highlight:: python
  :linenothreshold: 5

.. index::
  pair: Axes; Grid
  single: Grid

Generate a Chaco plot, and output attributes associated with the
grid::

  ## ex_chaco_myTP.grid_01.py

  # standard imports
  import inspect, os
  import numpy as np

  # Enthought imports
  from enable.api import Component, ComponentEditor
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

    # The dataspace interval between minor grid lines. options are Trait('auto',
    # 'auto', Float). If negative, it's a suggestion of how many minor lines to
    # use but still uses an algorithm to make a "nice" number of grid lines minor
    # grid lines.
    myTP.x_grid.grid_interval = 'auto'

    # grid line color. See colorspec. can be e.g. "black" or (0.827, 0.827,
    # 0.827, 1.0). line_color_ is useful as a read_only tuple containing the
    # numerical color
    myTP.x_grid.line_color = 'blue'
    myTP.x_grid.line_color_

    # The style (i.e., the dash pattern) of the grid lines. See the linestyle spec.
    # default = LineStyle('solid'). Options are 'dash','dot','solid','dot
    # dash','long dash'
    # The line_style_ attribute is an array that describes the line style
    # in terms of [pixels on, pixels off, ...]. For example, 'dot' corresponds
    # to array([ 2., 2.])). Attribute line_style_ overrides the line_style
    # attribute. Should have an even number of elements. Odd lengths will work but
    # result is non-intuitive.
    myTP.x_grid.line_style  = 'dot'
    myTP.x_grid.line_style_

    # the thickness of the grid lines, in pixels. Attribute line_weight is
    # aliased here.
    myTP.x_grid.line_width

    # the grid_mapper method that drives this PlotGrid. Defaults to a
    # <chaco.linear_mapper.LinearMapper object>
    myTP.x_grid.mapper

    # the tick_generator method (implimenting AbstractTickGenerator) that drives
    # this plot. Defaults to a <chaco.ticks.DefaultTickGenerator object>,
    myTP.x_grid.tick_generator

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

    print( tp.myTP.x_grid )

    myMethods = inspect.getmembers(tp.myTP.x_grid)
    myPublics = [thisItem for thisItem in myMethods if thisItem[0][0] != '_']
    print( myPublics )

    tp.myTP.x_grid.print_traits()

The outputs of the ``print( myPlot.myTP.x_grid )``, ``print( myPublics )`` and the
``tp.myTP.x_grid.print_traits()`` provide useful insight into the grid
characteristics of the plot.

Excruciating Detail
-------------------

.. index:
  pair: PlotGrid; print_traits()

Here's the output of the ``print( myPlot.myTP.x_grid )`` call::

  <chaco.grid.PlotGrid object at 0x05E89D20>

Here's the output from the ``print( myPublics )`` call::

  [
  ('add_class_trait', <bound method MetaHasTraits.add_class_trait of <class 'chaco.grid.PlotGrid'>>),
  ('add_trait', <bound method PlotGrid.add_trait of <chaco.grid.PlotGrid object at 0x05E89D20>>),
  ('add_trait_category', <bound method MetaHasTraits.add_trait_category of <class 'chaco.grid.PlotGrid'>>),
  ('add_trait_listener', <bound method PlotGrid.add_trait_listener of <chaco.grid.PlotGrid object at 0x05E89D20>>),
  ('all_trait_names', <bound method PlotGrid.all_trait_names of <chaco.grid.PlotGrid object at 0x05E89D20>>),
  ('as_coordinates', <bound method PlotGrid.as_coordinates of <chaco.grid.PlotGrid object at 0x05E89D20>>),
  ('aspect_ratio', None),
  ('base_trait', <bound method PlotGrid.base_trait of <chaco.grid.PlotGrid object at 0x05E89D20>>),
  ('bgcolor', 'none'),
  ('bgcolor_', (0.0, 0.0, 0.0, 0.0)),
  ('bounds', [700, 500]),
  ('class_default_traits_view', <bound method MetaHasTraits.class_default_traits_view of <class 'chaco.grid.PlotGrid'>>),
  ('class_editable_traits', <bound method MetaHasTraits.class_editable_traits of <class 'chaco.grid.PlotGrid'>>),
  ('class_trait_names', <bound method MetaHasTraits.class_trait_names of <class 'chaco.grid.PlotGrid'>>),
  ('class_trait_view', <bound method MetaHasTraits.class_trait_view of <class 'chaco.grid.PlotGrid'>>),
  ('class_trait_view_elements', <bound method MetaHasTraits.class_trait_view_elements of <class 'chaco.grid.PlotGrid'>>),
  ('class_traits', <bound method MetaHasTraits.class_traits of <class 'chaco.grid.PlotGrid'>>),
  ('cleanup', <bound method PlotGrid.cleanup of <chaco.grid.PlotGrid object at 0x05E89D20>>),
  ('clone_traits', <bound method PlotGrid.clone_traits of <chaco.grid.PlotGrid object at 0x05E89D20>>),
  ('component', <chaco.plot.Plot object at 0x05E22120>),
  ('configure_traits', <bound method PlotGrid.configure_traits of <chaco.grid.PlotGrid object at 0x05E89D20>>),
  ('container', None),
  ('copy_traits', <bound method PlotGrid.copy_traits of <chaco.grid.PlotGrid object at 0x05E89D20>>),
  ('copyable_trait_names', <bound method PlotGrid.copyable_trait_names of <chaco.grid.PlotGrid object at 0x05E89D20>>),
  ('data_max', None),
  ('data_min', None),
  ('default_traits_view', <bound method PlotGrid.default_traits_view of <chaco.grid.PlotGrid object at 0x05E89D20>>),
  ('dispatch', <bound method PlotGrid.dispatch of <chaco.grid.PlotGrid object at 0x05E89D20>>),
  ('do_layout', <bound method PlotGrid.do_layout of <chaco.grid.PlotGrid object at 0x05E89D20>>),
  ('draw', <bound method PlotGrid.draw of <chaco.grid.PlotGrid object at 0x05E89D20>>),
  ('draw_select_box', <bound method PlotGrid.draw_select_box of <chaco.grid.PlotGrid object at 0x05E89D20>>),
  ('edit_traits', <bound method PlotGrid.edit_traits of <chaco.grid.PlotGrid object at 0x05E89D20>>),
  ('editable_traits', <bound method PlotGrid.editable_traits of <chaco.grid.PlotGrid object at 0x05E89D20>>),
  ('flip_axis', False),
  ('get', <bound method PlotGrid.trait_get of <chaco.grid.PlotGrid object at 0x05E89D20>>),
  ('get_absolute_coords', <bound method PlotGrid.get_absolute_coords of <chaco.grid.PlotGrid object at 0x05E89D20>>),
  ('get_event_transform', <bound method PlotGrid.get_event_transform of <chaco.grid.PlotGrid object at 0x05E89D20>>),
  ('get_preferred_size', <bound method PlotGrid.get_preferred_size of <chaco.grid.PlotGrid object at 0x05E89D20>>),
  ('grid_interval', 'auto'),
  ('has_traits_interface', <bound method PlotGrid.has_traits_interface of <chaco.grid.PlotGrid object at 0x05E89D20>>),
  ('invalidate', <bound method PlotGrid.invalidate of <chaco.grid.PlotGrid object at 0x05E89D20>>),
  ('invalidate_and_redraw', <bound method PlotGrid.invalidate_and_redraw of <chaco.grid.PlotGrid object at 0x05E89D20>>),
  ('invalidate_draw', <bound method PlotGrid.invalidate_draw of <chaco.grid.PlotGrid object at 0x05E89D20>>),
  ('is_in', <bound method PlotGrid.is_in of <chaco.grid.PlotGrid object at 0x05E89D20>>),
  ('line_color', 'blue'),
  ('line_color_', (0.0, 0.0, 1.0, 1.0)),
  ('line_style', 'dot'),
  ('line_style_', array([ 2.,  2.])),
  ('line_width', 1),
  ('mapper', <chaco.linear_mapper.LinearMapper object at 0x05E89AE0>),
  ('mapper_updated', <bound method PlotGrid.mapper_updated of <chaco.grid.PlotGrid object at 0x05E89D20>>),
  ('on_trait_change', <bound method PlotGrid.on_trait_change of <chaco.grid.PlotGrid object at 0x05E89D20>>),
  ('on_trait_event', <bound method PlotGrid.on_trait_change of <chaco.grid.PlotGrid object at 0x05E89D20>>),
  ('orientation', 'vertical'),
  ('overlay', <bound method PlotGrid.overlay of <chaco.grid.PlotGrid object at 0x05E89D20>>),
  ('position', [50, 50]),
  ('print_traits', <bound method PlotGrid.print_traits of <chaco.grid.PlotGrid object at 0x05E89D20>>),
  ('remove_trait', <bound method PlotGrid.remove_trait of <chaco.grid.PlotGrid object at 0x05E89D20>>),
  ('remove_trait_listener', <bound method PlotGrid.remove_trait_listener of <chaco.grid.PlotGrid object at 0x05E89D20>>),
  ('request_redraw', <bound method PlotGrid.request_redraw of <chaco.grid.PlotGrid object at 0x05E89D20>>),
  ('reset_traits', <bound method PlotGrid.reset_traits of <chaco.grid.PlotGrid object at 0x05E89D20>>),
  ('set', <bound method PlotGrid.trait_set of <chaco.grid.PlotGrid object at 0x05E89D20>>),
  ('set_outer_bounds', <bound method PlotGrid.set_outer_bounds of <chaco.grid.PlotGrid object at 0x05E89D20>>),
  ('set_outer_position', <bound method PlotGrid.set_outer_position of <chaco.grid.PlotGrid object at 0x05E89D20>>),
  ('set_trait_dispatch_handler', <bound method MetaHasTraits.set_trait_dispatch_handler of <class 'chaco.grid.PlotGrid'>>),
  ('sync_trait', <bound method PlotGrid.sync_trait of <chaco.grid.PlotGrid object at 0x05E89D20>>),
  ('tick_generator', <chaco.ticks.DefaultTickGenerator object at 0x05E89D50>),
  ('trait', <bound method PlotGrid.trait of <chaco.grid.PlotGrid object at 0x05E89D20>>),
  ('trait_context', <bound method PlotGrid.trait_context of <chaco.grid.PlotGrid object at 0x05E89D20>>),
  ('trait_get', <bound method PlotGrid.trait_get of <chaco.grid.PlotGrid object at 0x05E89D20>>),
  ('trait_items_event', <built-in method trait_items_event of PlotGrid object at 0x05E89D20>),
  ('trait_monitor', <bound method MetaHasTraits.trait_monitor of <class 'chaco.grid.PlotGrid'>>),
  ('trait_names', <bound method PlotGrid.trait_names of <chaco.grid.PlotGrid object at 0x05E89D20>>),
  ('trait_property_changed', <built-in method trait_property_changed of PlotGrid object at 0x05E89D20>),
  ('trait_set', <bound method PlotGrid.trait_set of <chaco.grid.PlotGrid object at 0x05E89D20>>),
  ('trait_setq', <bound method PlotGrid.trait_setq of <chaco.grid.PlotGrid object at 0x05E89D20>>),
  ('trait_subclasses', <bound method MetaHasTraits.trait_subclasses of <class 'chaco.grid.PlotGrid'>>),
  ('trait_view', <bound method PlotGrid.trait_view of <chaco.grid.PlotGrid object at 0x05E89D20>>),
  ('trait_view_elements', <bound method PlotGrid.trait_view_elements of <chaco.grid.PlotGrid object at 0x05E89D20>>),
  ('trait_views', <bound method PlotGrid.trait_views of <chaco.grid.PlotGrid object at 0x05E89D20>>),
  ('traits', <bound method PlotGrid.traits of <chaco.grid.PlotGrid object at 0x05E89D20>>),
  ('traits_init', <built-in method traits_init of PlotGrid object at 0x05E89D20>),
  ('traits_inited', <built-in method traits_inited of PlotGrid object at 0x05E89D20>),
  ('transverse_bounds', None),
  ('use_draw_order', True),
  ('validate_trait', <bound method PlotGrid.validate_trait of <chaco.grid.PlotGrid object at 0x05E89D20>>),
  ('visible', True),
  ('visual_attr_changed', <bound method PlotGrid.visual_attr_changed of <chaco.grid.PlotGrid object at 0x05E89D20>>),
  ('wrappers',
    { 'new': <class traits.trait_notifiers.NewTraitChangeNotifyWrapper at 0x03D643B0>,
      'ui': <class traits.trait_notifiers.FastUITraitChangeNotifyWrapper at 0x03D64340>,
      'extended': <class traits.trait_notifiers.ExtendedTraitChangeNotifyWrapper at 0x03D64308>,
      'fast_ui': <class traits.trait_notifiers.FastUITraitChangeNotifyWrapper at 0x03D64340>,
      'same': <class traits.trait_notifiers.TraitChangeNotifyWrapper at 0x03D642D0>})
  ]

Here's the output from the ``tp.myTP.x_grid.print_traits()`` call::

  _active_tool:          None
  _backbuffer:           None
  _cache_valid:          False
  _layout_needed:        True
  _tick_extents:         array([[  50.,  550.],\n   ...,\n       [  50.,  550.]])
  _tick_list:            None
  _tick_positions:       array([[ 121.,   50.],\n   ...,\n       [ 678.,   50.]])
  _window:               None
  accepts_focus:         True
  active_tool:           None
  aspect_ratio:          None
  auto_center:           True
  auto_handle_event:     False
  backbuffer_padding:    True
  bgcolor:               'none'
  bgcolor_:              (0.0, 0.0, 0.0, 0.0)
  border_color:          'black'
  border_dash:           'solid'
  border_visible:        False
  border_width:          1
  bounds:                [700, 500]
  classes:               []
  component:             <chaco.plot.Plot object at 0x05E22120>
  container:             None
  controller:            None
  cursor_color:          'black'
  cursor_style:          'default'
  data_max:              None
  data_min:              None
  draw_layer:            'overlay'
  draw_order:            ['background', 'image', 'un..., 'annotation', 'overlay']
  draw_valid:            False
  drawn_outer_bounds:    [0.0, 0.0]
  drawn_outer_position:  [0.0, 0.0]
  event_state:           'normal'
  fill_padding:          False
  fixed_preferred_size:  None
  flip_axis:             False
  grid_interval:         'auto'
  height:                500
  hpadding:              0
  id:                    ''
  inset_border:          True
  invisible_layout:      False
  layout_needed:         True
  line_color:            'blue'
  line_color_:           (0.0, 0.0, 1.0, 1.0)
  line_style:            'dot'
  line_style_:           array([ 2.,  2.])
  line_weight:           1
  line_width:            1
  mapper:                <chaco.linear_mapper.LinearMapper object at 0x05E89AE0>
  orientation:           'vertical'
  outer_bounds:          (700, 500)
  outer_height:          500
  outer_position:        (50, 50)
  outer_width:           700
  outer_x:               50
  outer_x2:              749
  outer_y:               50
  outer_y2:              549
  overlay_border:        True
  overlays:              []
  padding:               [0, 0, 0, 0]
  padding_accepts_focus: True
  padding_bottom:        0
  padding_left:          0
  padding_right:         0
  padding_top:           0
  pointer:               'arrow'
  position:              [50, 50]
  resizable:             'hv'
  tick_generator:        <chaco.ticks.DefaultTickGenerator object at 0x05E89D50>
  tools:                 []
  tooltip:               None
  transverse_bounds:     None
  transverse_mapper:     None
  underlays:             []
  unified_draw:          False
  use_backbuffer:        False
  use_draw_order:        True
  use_selection:         False
  viewports:             []
  visible:               True
  vpadding:              0
  width:                 700
  window:                None
  x:                     50
  x2:                    749
  y:                     50
  y2:                    549
