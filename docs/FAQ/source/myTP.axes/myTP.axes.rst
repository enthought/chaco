Chaco Plot - Axes Options
=========================

.. highlight:: python
  :linenothreshold: 5

.. index:: Axes

Let's generate a Chaco plot, and output attributes associated with the
axes labelling, tick marks, etc. We'll concentrate on the x-axis but, of course,
the material applies to the y-axis as well.
::

  ## ex_chaco_myTP.axes_01.py

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

    # Define the axis label. title is a string or unicode object that is rendered
    # using the given font and color. title_font is a string describing a font
    # (e.g. '12 pt bold italic', 'swiss family Arial' or 'default 12'; see
    # TraitKivaFont for details). Finally, title_spacing is the space between the
    # axis line and the title (either the number of pixels or 'auto', default).
    myTP.x_axis.title = 'My X-Axis Title'
    myTP.x_axis.title_font = 'modern 20'
    myTP.x_axis.title_color = 'red'
    myTP.x_axis.title_spacing = 'auto'

    # These attributes control the aspect of the ticks on the axis. If
    # tick_visible is True, ticks are represented as lines of color tick_color
    # (default is black) and thickness tick_weight (in pixels, default is 1). Each
    # line extends into the plot area by tick_in pixels and into the label area by
    # tick_out pixels (default is 5).
    myTP.x_axis.tick_weight
    myTP.x_axis.tick_color
    myTP.x_axis.tick_in
    myTP.x_axis.tick_out
    myTP.x_axis.tick_visible = True

    # The attributes allow the user to fine-tune the aspect of the tick labels:
    # first of all, the font (e.g. '12 pt bold italic') and color of the labels.
    # The position and orientation of the label can be also be closely controlled:
    # tick_label_rotate_angle give the rotation angle (only multiples of 90
    # degrees are supported); tick_label_alignment selects whether the corner
    # ('corner') or center ('edge', default) of the label are aligned to the
    # corresponding tick ('corner' is better for 45 degrees rotation);
    # tick_label_margin and tick_label_offset control the margin around the tick
    # labels, and their distance from the axis; finally, tick_label_position can
    # be set to either 'outside' (default) or 'inside' depending on whether the
    # labels should be displayed inside or outside the plot area.
    myTP.x_axis.tick_label_font = 'modern 16'
    myTP.x_axis.tick_label_color
    myTP.x_axis.tick_label_rotate_angle
    myTP.x_axis.tick_label_alignment
    myTP.x_axis.tick_label_margin
    myTP.x_axis.tick_label_offset
    myTP.x_axis.tick_label_position

    # By default, tick labels are assumed to be floating point numbers, and are
    # displayed as such after removing trailing zeros and the decimal dot if
    # necessary (e.g., '10.000' will be displayed as '10', and '21.10' as '21.1').
    # The default behavior can be changed by setting tick_label_formatter to a
    # callable that takes the value of the tick label and returns a formatted
    # string.
    myTP.x_axis.tick_label_formatter

    # Locations and distances of ticks are controlled by the attribute
    # tick_generator. Default is chaco.ticks.auto_ticks or
    # chaco.ticks.log_auto_ticks
    myTP.x_axis.tick_interval           # 'auto'
    myTP.x_axis.tick_generator

    # Orientation of the axis. Can put it on the top or bottom.
    # left or right available, but not useful
    myTP.x_axis.orientation = 'bottom'

    # axis line
    myTP.x_axis.axis_line_weight            # 2
    myTP.x_axis.axis_line_color             # 'black'
    myTP.x_axis.axis_line_color_            # (0.0, 0.0, 0.0, 1.0)
    myTP.x_axis.axis_line_style             # 'solid'
    myTP.x_axis.axis_line_style_            # None
    myTP.x_axis.axis_line_visible           # True or False

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

    print( tp.myTP.x_axis )

    myMethods = inspect.getmembers(tp.myTP.x_axis)
    myPublics = [thisItem for thisItem in myMethods if thisItem[0][0] != '_']
    print( myPublics )

    tp.myTP.x_axis.print_traits()

The reader is encouraged to examine the outputs of the ``print(
myPlot.myTP.x_axis )``, the ``print( myPublics )`` and the
``tp.myTP.x_axis.print_traits()`` line for insight into the behavior of the
plot title. The data is also available under the Excruciating Detail heading
below.

Excruciating Detail
-------------------

.. index:
  pair: PlotAxis; print_traits()

The output of the ``print( myPlot.myTP.x_axis )`` call is::

  <chaco.axis.PlotAxis object at 0x05E6F270>

The output from the ``print( myPublics )`` call is::

  [
  ('add_class_trait', <bound method MetaHasTraits.add_class_trait of <class 'chaco.axis.PlotAxis'>>),
  ('add_trait', <bound method PlotAxis.add_trait of <chaco.axis.PlotAxis object at 0x05E6F270>>),
  ('add_trait_category', <bound method MetaHasTraits.add_trait_category of <class 'chaco.axis.PlotAxis'>>),
  ('add_trait_listener', <bound method PlotAxis.add_trait_listener of <chaco.axis.PlotAxis object at 0x05E6F270>>),
  ('all_trait_names', <bound method PlotAxis.all_trait_names of <chaco.axis.PlotAxis object at 0x05E6F270>>),
  ('as_coordinates', <bound method PlotAxis.as_coordinates of <chaco.axis.PlotAxis object at 0x05E6F270>>),
  ('aspect_ratio', None),
  ('axis_line_color', 'black'),
  ('axis_line_color_', (0.0, 0.0, 0.0, 1.0)),
  ('axis_line_style', 'solid'),
  ('axis_line_style_', None),
  ('axis_line_visible', True),
  ('axis_line_weight', 1.0),
  ('base_trait', <bound method PlotAxis.base_trait of <chaco.axis.PlotAxis object at 0x05E6F270>>),
  ('border_visible', False),
  ('bounds', [700, 50]),
  ('class_default_traits_view', <bound method MetaHasTraits.class_default_traits_view of <class 'chaco.axis.PlotAxis'>>),
  ('class_editable_traits', <bound method MetaHasTraits.class_editable_traits of <class 'chaco.axis.PlotAxis'>>),
  ('class_trait_names', <bound method MetaHasTraits.class_trait_names of <class 'chaco.axis.PlotAxis'>>),
  ('class_trait_view', <bound method MetaHasTraits.class_trait_view of <class 'chaco.axis.PlotAxis'>>),
  ('class_trait_view_elements', <bound method MetaHasTraits.class_trait_view_elements of <class 'chaco.axis.PlotAxis'>>),
  ('class_traits', <bound method MetaHasTraits.class_traits of <class 'chaco.axis.PlotAxis'>>),
  ('cleanup', <bound method PlotAxis.cleanup of <chaco.axis.PlotAxis object at 0x05E6F270>>),
  ('clone_traits', <bound method PlotAxis.clone_traits of <chaco.axis.PlotAxis object at 0x05E6F270>>),
  ('component', <chaco.plot.Plot object at 0x05E270C0>),
  ('configure_traits', <bound method PlotAxis.configure_traits of <chaco.axis.PlotAxis object at 0x05E6F270>>),
  ('container', None),
  ('copy_traits', <bound method PlotAxis.copy_traits of <chaco.axis.PlotAxis object at 0x05E6F270>>),
  ('copyable_trait_names', <bound method PlotAxis.copyable_trait_names of <chaco.axis.PlotAxis object at 0x05E6F270>>),
  ('default_traits_view', <bound method PlotAxis.default_traits_view of <chaco.axis.PlotAxis object at 0x05E6F270>>),
  ('dispatch', <bound method PlotAxis.dispatch of <chaco.axis.PlotAxis object at 0x05E6F270>>),
  ('do_layout', <bound method PlotAxis.do_layout of <chaco.axis.PlotAxis object at 0x05E6F270>>),
  ('draw', <bound method PlotAxis.draw of <chaco.axis.PlotAxis object at 0x05E6F270>>),
  ('draw_select_box', <bound method PlotAxis.draw_select_box of <chaco.axis.PlotAxis object at 0x05E6F270>>),
  ('draw_valid', False),
  ('drawn_outer_bounds', [0.0, 0.0]),
  ('drawn_outer_position', [0.0, 0.0]),
  ('edit_traits', <bound method PlotAxis.edit_traits of <chaco.axis.PlotAxis object at 0x05E6F270>>),
  ('editable_traits', <bound method PlotAxis.editable_traits of <chaco.axis.PlotAxis object at 0x05E6F270>>),
  ('ensure_labels_bounded', False),
  ('ensure_ticks_bounded', False),
  ('get', <bound method PlotAxis.trait_get of <chaco.axis.PlotAxis object at 0x05E6F270>>),
  ('get_absolute_coords', <bound method PlotAxis.get_absolute_coords of <chaco.axis.PlotAxis object at 0x05E6F270>>),
  ('get_event_transform', <bound method PlotAxis.get_event_transform of <chaco.axis.PlotAxis object at 0x05E6F270>>),
  ('get_preferred_size', <bound method PlotAxis.get_preferred_size of <chaco.axis.PlotAxis object at 0x05E6F270>>),
  ('has_traits_interface', <bound method PlotAxis.has_traits_interface of <chaco.axis.PlotAxis object at 0x05E6F270>>),
  ('invalidate', <bound method PlotAxis.invalidate of <chaco.axis.PlotAxis object at 0x05E6F270>>),
  ('invalidate_and_redraw', <bound method PlotAxis.invalidate_and_redraw of <chaco.axis.PlotAxis object at 0x05E6F270>>),
  ('invalidate_draw', <bound method PlotAxis.invalidate_draw of <chaco.axis.PlotAxis object at 0x05E6F270>>),
  ('is_in', <bound method PlotAxis.is_in of <chaco.axis.PlotAxis object at 0x05E6F270>>),
  ('mapper', <chaco.linear_mapper.LinearMapper object at 0x07AF2E70>),
  ('mapper_updated', <bound method PlotAxis.mapper_updated of <chaco.axis.PlotAxis object at 0x05E6F270>>),
  ('on_trait_change', <bound method PlotAxis.on_trait_change of <chaco.axis.PlotAxis object at 0x05E6F270>>),
  ('on_trait_event', <bound method PlotAxis.on_trait_change of <chaco.axis.PlotAxis object at 0x05E6F270>>),
  ('orientation', 'bottom'),
  ('overlay', <bound method PlotAxis.overlay of <chaco.axis.PlotAxis object at 0x05E6F270>>),
  ('overlays', []),
  ('padding_bottom', 0),
  ('padding_left', 0),
  ('padding_right', 0),
  ('padding_top', 0),
  ('position', [50, 0]),
  ('print_traits', <bound method PlotAxis.print_traits of <chaco.axis.PlotAxis object at 0x05E6F270>>),
  ('remove_trait', <bound method PlotAxis.remove_trait of <chaco.axis.PlotAxis object at 0x05E6F270>>),
  ('remove_trait_listener', <bound method PlotAxis.remove_trait_listener of <chaco.axis.PlotAxis object at 0x05E6F270>>),
  ('request_redraw', <bound method PlotAxis.request_redraw of <chaco.axis.PlotAxis object at 0x05E6F270>>),
  ('reset_traits', <bound method PlotAxis.reset_traits of <chaco.axis.PlotAxis object at 0x05E6F270>>),
  ('set', <bound method PlotAxis.trait_set of <chaco.axis.PlotAxis object at 0x05E6F270>>),
  ('set_outer_bounds', <bound method PlotAxis.set_outer_bounds of <chaco.axis.PlotAxis object at 0x05E6F270>>),
  ('set_outer_position', <bound method PlotAxis.set_outer_position of <chaco.axis.PlotAxis object at 0x05E6F270>>),
  ('set_trait_dispatch_handler', <bound method MetaHasTraits.set_trait_dispatch_handler of <class 'chaco.axis.PlotAxis'>>),
  ('small_haxis_style', False),
  ('sync_trait', <bound method PlotAxis.sync_trait of <chaco.axis.PlotAxis object at 0x05E6F270>>),
  ('tick_color', 'black'),
  ('tick_color_', (0.0, 0.0, 0.0, 1.0)),
  ('tick_generator', <chaco.ticks.DefaultTickGenerator object at 0x05E6F2A0>),
  ('tick_in', 5),
  ('tick_interval', 'auto'),
  ('tick_label_alignment', 'edge'),
  ('tick_label_color', 'black'),
  ('tick_label_font', Font(size=16,family=3,weight=0, style=0, face_name='',encoding=0 )),
  ('tick_label_formatter', <function DEFAULT_TICK_FORMATTER at 0x058EA930>),
  ('tick_label_margin', 2),
  ('tick_label_offset', 8.0),
  ('tick_label_position', 'outside'),
  ('tick_label_rotate_angle', 0),
  ('tick_out', 5),
  ('tick_visible', True),
  ('tick_weight', 1.0),
  ('ticklabel_cache',
    [ <chaco.label.Label object at 0x05F89300>,
      <chaco.label.Label object at 0x05F897E0>,
      <chaco.label.Label object at 0x05F89CC0>,
      <chaco.label.Label object at 0x05F861E0>,
      <chaco.label.Label object at 0x05F866C0>]),
  ('title', 'My X-Axis Title'),
  ('title_angle', 0.0),
  ('title_color', 'red'),
  ('title_color_', (1.0, 0.0, 0.0, 1.0)),
  ('title_font', Font(size=20,family=3,weight=0, style=0, face_name='',encoding=0 )),
  ('title_spacing', 'auto'),
  ('trait', <bound method PlotAxis.trait of <chaco.axis.PlotAxis object at 0x05E6F270>>),
  ('trait_context', <bound method PlotAxis.trait_context of <chaco.axis.PlotAxis object at 0x05E6F270>>),
  ('trait_get', <bound method PlotAxis.trait_get of <chaco.axis.PlotAxis object at 0x05E6F270>>),
  ('trait_items_event', <built-in method trait_items_event of PlotAxis object at 0x05E6F270>),
  ('trait_monitor', <bound method MetaHasTraits.trait_monitor of <class 'chaco.axis.PlotAxis'>>),
  ('trait_names', <bound method PlotAxis.trait_names of <chaco.axis.PlotAxis object at 0x05E6F270>>),
  ('trait_property_changed', <built-in method trait_property_changed of PlotAxis object at 0x05E6F270>),
  ('trait_set', <bound method PlotAxis.trait_set of <chaco.axis.PlotAxis object at 0x05E6F270>>),
  ('trait_setq', <bound method PlotAxis.trait_setq of <chaco.axis.PlotAxis object at 0x05E6F270>>),
  ('trait_subclasses', <bound method MetaHasTraits.trait_subclasses of <class 'chaco.axis.PlotAxis'>>),
  ('trait_view', <bound method PlotAxis.trait_view of <chaco.axis.PlotAxis object at 0x05E6F270>>),
  ('trait_view_elements', <bound method PlotAxis.trait_view_elements of <chaco.axis.PlotAxis object at 0x05E6F270>>),
  ('trait_views', <bound method PlotAxis.trait_views of <chaco.axis.PlotAxis object at 0x05E6F270>>),
  ('traits', <bound method PlotAxis.traits of <chaco.axis.PlotAxis object at 0x05E6F270>>),
  ('traits_init', <built-in method traits_init of PlotAxis object at 0x05E6F270>),
  ('traits_inited', <built-in method traits_inited of PlotAxis object at 0x05E6F270>),
  ('traits_view', <bound method PlotAxis.traits_view of <chaco.axis.PlotAxis object at 0x05E6F270>>),
  ('underlays', []),
  ('use_draw_order', True),
  ('validate_trait', <bound method PlotAxis.validate_trait of <chaco.axis.PlotAxis object at 0x05E6F270>>),
  ('viewports', []),
  ('visible', True),
  ('wrappers',
    { 'new': <class traits.trait_notifiers.NewTraitChangeNotifyWrapper at 0x03F8E500>,
      'ui': <class traits.trait_notifiers.FastUITraitChangeNotifyWrapper at 0x03F8E490>,
      'extended': <class traits.trait_notifiers.ExtendedTraitChangeNotifyWrapper at 0x03F8E458>,
      'fast_ui': <class traits.trait_notifiers.FastUITraitChangeNotifyWrapper at 0x03F8E490>,
      'same': <class traits.trait_notifiers.TraitChangeNotifyWrapper at 0x03F8E420>})
  ]

The output from the ``tp.myTP.x_axis.print_traits()`` call is::

  _active_tool:               None
  _axis_pixel_vector:         array([ 1.,  0.])
  _axis_vector:               array([ 699.,    0.])
  _backbuffer:                None
  _cache_valid:               True
  _end_axis_point:            array([ 749.,   50.])
  _inside_vector:             array([ 0.,  1.])
  _layout_needed:             False
  _major_axis:                array([ 1.,  0.])
  _major_axis_size:           700.0
  _minor_axis_size:           500.0
  _origin_point:              array([50, 50])
  _tick_label_bounding_boxes: [array([ 20.,  16.]), ar...]), array([ 14.,  16.])]
  _tick_label_list:           array([-5. , -2.5,  0. ,  2.5,  5. ])
  _tick_label_positions:      array([[ 121.,   50.],\n...n       [ 678.,   50.]])
  _tick_list:                 []
  _tick_positions:            array([[ 121.,   50.],\n...n       [ 678.,   50.]])
  _title_angle:               0.0
  _title_orientation:         array([ 0.,  1.])
  _window:                    None
  accepts_focus:              True
  active_tool:                None
  aspect_ratio:               None
  auto_center:                True
  auto_handle_event:          False
  axis_line_color:            'black'
  axis_line_color_:           (0.0, 0.0, 0.0, 1.0)
  axis_line_style:            'solid'
  axis_line_style_:           None
  axis_line_visible:          True
  axis_line_weight:           1.0
  backbuffer_padding:         True
  bgcolor:                    'transparent'
  border_color:               'black'
  border_dash:                'solid'
  border_visible:             False
  border_width:               1
  bounds:                     [700, 50]
  classes:                    []
  component:                  <chaco.plot.Plot object at 0x05E17C90>
  container:                  None
  controller:                 None
  cursor_color:               'black'
  cursor_style:               'default'
  draw_layer:                 'overlay'
  draw_order:                 ['background', 'image', ...'annotation', 'overlay']
  draw_valid:                 False
  drawn_outer_bounds:         [0.0, 0.0]
  drawn_outer_position:       [0.0, 0.0]
  ensure_labels_bounded:      False
  ensure_ticks_bounded:       False
  event_state:                'normal'
  fill_padding:               False
  fixed_preferred_size:       None
  height:                     50
  hpadding:                   0
  id:                         ''
  inset_border:               True
  invisible_layout:           False
  layout_needed:              False
  mapper:                     <chaco.linear_mapper.Lin...er object at 0x05E6C690>
  orientation:                'bottom'
  outer_bounds:               (700, 50)
  outer_height:               50
  outer_position:             (50, 0)
  outer_width:                700
  outer_x:                    50
  outer_x2:                   749
  outer_y:                    0
  outer_y2:                   49
  overlay_border:             True
  overlays:                   []
  padding:                    [0, 0, 0, 0]
  padding_accepts_focus:      True
  padding_bottom:             0
  padding_left:               0
  padding_right:              0
  padding_top:                0
  pointer:                    'arrow'
  position:                   [50, 0]
  resizable:                  'hv'
  small_haxis_style:          False
  tick_color:                 'black'
  tick_color_:                (0.0, 0.0, 0.0, 1.0)
  tick_generator:             <chaco.ticks.DefaultTick...or object at 0x05E73E70>
  tick_in:                    5
  tick_interval:              'auto'
  tick_label_alignment:       'edge'
  tick_label_color:           'black'
  tick_label_font:            Font(size=16,family=3,we...ace_name='',encoding=0 )
  tick_label_formatter:       <function DEFAULT_TICK_FORMATTER at 0x058CCAF0>
  tick_label_margin:          2
  tick_label_offset:          8.0
  tick_label_position:        'outside'
  tick_label_rotate_angle:    0
  tick_out:                   5
  tick_visible:               True
  tick_weight:                1.0
  ticklabel_cache:            [<chaco.label.Label obje...l object at 0x05F9A2D0>]
  title:                      'My X-Axis Title'
  title_angle:                0.0
  title_color:                'red'
  title_color_:               (1.0, 0.0, 0.0, 1.0)
  title_font:                 Font(size=20,family=3,we...ace_name='',encoding=0 )
  title_spacing:              'auto'
  tools:                      []
  tooltip:                    None
  underlays:                  []
  unified_draw:               False
  use_backbuffer:             False
  use_draw_order:             True
  use_selection:              False
  viewports:                  []
  visible:                    True
  vpadding:                   0
  width:                      700
  window:                     None
  x:                          50
  x2:                         749
  y:                          0
  y2:                         49
