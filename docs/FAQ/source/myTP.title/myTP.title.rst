Chaco Plot - Title Options
==========================

.. highlight:: python
  :linenothreshold: 5

.. index::
  pair: Title; Plot

Plot titles are Delegates to a PlotLabel object, which is stored in the Plot
object in the ``_title`` attribute. This ocde generates a Chaco plot, with
explicit plot title options and introspection into the attributes involving
the plot's title::

  ## ex_chaco_myTP.title_01.py

  # standard imports
  import os, inspect
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

    myTP.padding = 50               # pixels twixt plot and window edge.

    # most title attributes delegate to the underlying _title attribute, which
    # is a PlotLabel object.
    myTP.title = 'My Plot Title'    # title appearing on plot
    myTP.title_angle = 0            # angle of the title in degrees
    myTP.title_color = 'blue'       # title color. see colorspec
    myTP.title_font = "swiss 16"    # title font. see fontspec
    myTP.title_position = 'top'     # top, bottom, left, right
    myTP.title_spacing = 'auto'     # spacing between the axis line and the title

    myTP._title.hjustify = 'center' # left, right or cener
    myTP._title.vjustify = 'center' # top, bottom or center

    mySize = (800,600)
    myTitle = 'myPlot'
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

    print( type(tp.myTP._title) )

    # print only the public members of the list
    membersList = inspect.getmembers( tp.myTP._title )
    publicList = [thisItem for thisItem in membersList if thisItem[0][0] != '_']
    print( publicList )

    tp.myTP._title.print_traits()


The output of the ``print( type(tp.myTP._title) )`` line is::

  <class 'chaco.plot_label.PlotLabel'>

The output of the ``print( publiList )`` line is::

  [
  ('add_class_trait', <bound method MetaHasTraits.add_class_trait of <class 'chaco.plot_label.PlotLabel'>>),
  ('add_trait', <bound method PlotLabel.add_trait of <chaco.plot_label.PlotLabel object at 0x05E7E300>>),
  ('add_trait_category', <bound method MetaHasTraits.add_trait_category of <class 'chaco.plot_label.PlotLabel'>>),
  ('add_trait_listener', <bound method PlotLabel.add_trait_listener of <chaco.plot_label.PlotLabel object at 0x05E7E300>>),
  ('all_trait_names', <bound method PlotLabel.all_trait_names of <chaco.plot_label.PlotLabel object at 0x05E7E300>>),
  ('as_coordinates', <bound method PlotLabel.as_coordinates of <chaco.plot_label.PlotLabel object at 0x05E7E300>>),
  ('aspect_ratio', None),
  ('base_trait', <bound method PlotLabel.base_trait of <chaco.plot_label.PlotLabel object at 0x05E7E300>>),
  ('bounds', [700, 50]),
  ('class_default_traits_view', <bound method MetaHasTraits.class_default_traits_view of <class 'chaco.plot_label.PlotLabel'>>),
  ('class_editable_traits', <bound method MetaHasTraits.class_editable_traits of <class 'chaco.plot_label.PlotLabel'>>),
  ('class_trait_names', <bound method MetaHasTraits.class_trait_names of <class 'chaco.plot_label.PlotLabel'>>),
  ('class_trait_view', <bound method MetaHasTraits.class_trait_view of <class 'chaco.plot_label.PlotLabel'>>),
  ('class_trait_view_elements', <bound method MetaHasTraits.class_trait_view_elements of <class 'chaco.plot_label.PlotLabel'>>),
  ('class_traits', <bound method MetaHasTraits.class_traits of <class 'chaco.plot_label.PlotLabel'>>),
  ('cleanup', <bound method PlotLabel.cleanup of <chaco.plot_label.PlotLabel object at 0x05E7E300>>),
  ('clone_traits', <bound method PlotLabel.clone_traits of <chaco.plot_label.PlotLabel object at 0x05E7E300>>),
  ('component', <chaco.plot.Plot object at 0x05E1BAE0>),
  ('configure_traits', <bound method PlotLabel.configure_traits of <chaco.plot_label.PlotLabel object at 0x05E7E300>>),
  ('container', None),
  ('controller', None),
  ('copy_traits', <bound method PlotLabel.copy_traits of <chaco.plot_label.PlotLabel object at 0x05E7E300>>),
  ('copyable_trait_names', <bound method PlotLabel.copyable_trait_names of <chaco.plot_label.PlotLabel object at 0x05E7E300>>),
  ('default_traits_view', <bound method PlotLabel.default_traits_view of <chaco.plot_label.PlotLabel object at 0x05E7E300>>),
  ('dispatch', <bound method PlotLabel.dispatch of <chaco.plot_label.PlotLabel object at 0x05E7E300>>),
  ('do_layout', <bound method PlotLabel.do_layout of <chaco.plot_label.PlotLabel object at 0x05E7E300>>),
  ('draw', <bound method PlotLabel.draw of <chaco.plot_label.PlotLabel object at 0x05E7E300>>),
  ('draw_layer', 'overlay'),
  ('draw_select_box', <bound method PlotLabel.draw_select_box of <chaco.plot_label.PlotLabel object at 0x05E7E300>>),
  ('edit_traits', <bound method PlotLabel.edit_traits of <chaco.plot_label.PlotLabel object at 0x05E7E300>>),
  ('editable_traits', <bound method PlotLabel.editable_traits of <chaco.plot_label.PlotLabel object at 0x05E7E300>>),
  ('event_state', 'normal'),
  ('get', <bound method PlotLabel.trait_get of <chaco.plot_label.PlotLabel object at 0x05E7E300>>),
  ('get_absolute_coords', <bound method PlotLabel.get_absolute_coords of <chaco.plot_label.PlotLabel object at 0x05E7E300>>),
  ('get_event_transform', <bound method PlotLabel.get_event_transform of <chaco.plot_label.PlotLabel object at 0x05E7E300>>),
  ('get_preferred_size', <bound method PlotLabel.get_preferred_size of <chaco.plot_label.PlotLabel object at 0x05E7E300>>),
  ('has_traits_interface', <bound method PlotLabel.has_traits_interface of <chaco.plot_label.PlotLabel object at 0x05E7E300>>),
  ('hjustify', 'center'),
  ('invalidate_and_redraw', <bound method PlotLabel.invalidate_and_redraw of <chaco.plot_label.PlotLabel object at 0x05E7E300>>),
  ('invalidate_draw', <bound method PlotLabel.invalidate_draw of <chaco.plot_label.PlotLabel object at 0x05E7E300>>),
  ('is_in', <bound method PlotLabel.is_in of <chaco.plot_label.PlotLabel object at 0x05E7E300>>),
  ('on_trait_change', <bound method PlotLabel.on_trait_change of <chaco.plot_label.PlotLabel object at 0x05E7E300>>),
  ('on_trait_event', <bound method PlotLabel.on_trait_change of <chaco.plot_label.PlotLabel object at 0x05E7E300>>),
  ('overlay', <bound method PlotLabel.overlay of <chaco.plot_label.PlotLabel object at 0x05E7E300>>),
  ('overlay_position', 'top'),
  ('overlays', []),
  ('position', [50, 550]),
  ('print_traits', <bound method PlotLabel.print_traits of <chaco.plot_label.PlotLabel object at 0x05E7E300>>),
  ('remove_trait', <bound method PlotLabel.remove_trait of <chaco.plot_label.PlotLabel object at 0x05E7E300>>),
  ('remove_trait_listener', <bound method PlotLabel.remove_trait_listener of <chaco.plot_label.PlotLabel object at 0x05E7E300>>),
  ('request_redraw', <bound method PlotLabel.request_redraw of <chaco.plot_label.PlotLabel object at 0x05E7E300>>),
  ('reset_traits', <bound method PlotLabel.reset_traits of <chaco.plot_label.PlotLabel object at 0x05E7E300>>),
  ('set', <bound method PlotLabel.trait_set of <chaco.plot_label.PlotLabel object at 0x05E7E300>>),
  ('set_outer_bounds', <bound method PlotLabel.set_outer_bounds of <chaco.plot_label.PlotLabel object at 0x05E7E300>>),
  ('set_outer_position', <bound method PlotLabel.set_outer_position of <chaco.plot_label.PlotLabel object at 0x05E7E300>>),
  ('set_trait_dispatch_handler', <bound method MetaHasTraits.set_trait_dispatch_handler of <class 'chaco.plot_label.PlotLabel'>>),
  ('sync_trait', <bound method PlotLabel.sync_trait of <chaco.plot_label.PlotLabel object at 0x05E7E300>>),
  ('tools', []),
  ('trait', <bound method PlotLabel.trait of <chaco.plot_label.PlotLabel object at 0x05E7E300>>),
  ('trait_context', <bound method PlotLabel.trait_context of <chaco.plot_label.PlotLabel object at 0x05E7E300>>),
  ('trait_get', <bound method PlotLabel.trait_get of <chaco.plot_label.PlotLabel object at 0x05E7E300>>),
  ('trait_items_event', <built-in method trait_items_event of PlotLabel object at 0x05E7E300>),
  ('trait_monitor', <bound method MetaHasTraits.trait_monitor of <class 'chaco.plot_label.PlotLabel'>>),
  ('trait_names', <bound method PlotLabel.trait_names of <chaco.plot_label.PlotLabel object at 0x05E7E300>>),
  ('trait_property_changed', <built-in method trait_property_changed of PlotLabel object at 0x05E7E300>),
  ('trait_set', <bound method PlotLabel.trait_set of <chaco.plot_label.PlotLabel object at 0x05E7E300>>),
  ('trait_setq', <bound method PlotLabel.trait_setq of <chaco.plot_label.PlotLabel object at 0x05E7E300>>),
  ('trait_subclasses', <bound method MetaHasTraits.trait_subclasses of <class 'chaco.plot_label.PlotLabel'>>),
  ('trait_view', <bound method PlotLabel.trait_view of <chaco.plot_label.PlotLabel object at 0x05E7E300>>),
  ('trait_view_elements', <bound method PlotLabel.trait_view_elements of <chaco.plot_label.PlotLabel object at 0x05E7E300>>),
  ('trait_views', <bound method PlotLabel.trait_views of <chaco.plot_label.PlotLabel object at 0x05E7E300>>),
  ('traits', <bound method PlotLabel.traits of <chaco.plot_label.PlotLabel object at 0x05E7E300>>),
  ('traits_init', <built-in method traits_init of PlotLabel object at 0x05E7E300>),
  ('traits_inited', <built-in method traits_inited of PlotLabel object at 0x05E7E300>),
  ('underlays', []),
  ('use_draw_order', True),
  ('validate_trait', <bound method PlotLabel.validate_trait of <chaco.plot_label.PlotLabel object at 0x05E7E300>>),
  ('visible', True),
  ('vjustify', 'center'),
  ('wrappers',
    { 'new': <class traits.trait_notifiers.NewTraitChangeNotifyWrapper at 0x03D09F80>,
      'ui': <class traits.trait_notifiers.FastUITraitChangeNotifyWrapper at 0x03D09F10>,
      'extended': <class traits.trait_notifiers.ExtendedTraitChangeNotifyWrapper at 0x03D09ED8>,
      'fast_ui': <class traits.trait_notifiers.FastUITraitChangeNotifyWrapper at 0x03D09F10>,
      'same': <class traits.trait_notifiers.TraitChangeNotifyWrapper at 0x03D09EA0>})]

The output of the ``tp.myTP._title.print_traits()`` line is::

  _active_tool:          None
  _backbuffer:           None
  _label:                <chaco.label.Label object at 0x05E8C150>
  _layout_needed:        True
  _window:               None
  accepts_focus:         True
  active_tool:           None
  angle:                 0.0
  aspect_ratio:          None
  auto_center:           True
  auto_handle_event:     False
  backbuffer_padding:    True
  bgcolor:               'transparent'
  border_color:          'black'
  border_dash:           'solid'
  border_visible:        True
  border_width:          0
  bounds:                [700, 50]
  classes:               []
  color:                 'blue'
  component:             <chaco.plot.Plot object at 0x05E0B750>
  container:             None
  controller:            None
  cursor_color:          'black'
  cursor_style:          'default'
  draw_layer:            'overlay'
  draw_order:            ['background', 'image', 'un..., 'annotation', 'overlay']
  draw_valid:            False
  drawn_outer_bounds:    [0.0, 0.0]
  drawn_outer_position:  [0.0, 0.0]
  event_state:           'normal'
  fill_padding:          False
  fixed_preferred_size:  None
  font:                  Font(size=16,family=1,weigh... face_name='',encoding=0 )
  height:                50
  hjustify:              'center'
  hpadding:              0
  id:                    ''
  inset_border:          True
  invisible_layout:      False
  layout_needed:         True
  line_spacing:          5
  margin:                2
  outer_bounds:          (700, 50)
  outer_height:          50
  outer_position:        (50, 550)
  outer_width:           700
  outer_x:               50
  outer_x2:              749
  outer_y:               550
  outer_y2:              599
  overlay_border:        True
  overlay_position:      'top'
  overlays:              []
  padding:               [0, 0, 0, 0]
  padding_accepts_focus: True
  padding_bottom:        0
  padding_left:          0
  padding_right:         0
  padding_top:           0
  pointer:               'arrow'
  position:              [50, 550]
  resizable:             'h'
  text:                  'My Plot Title'
  tools:                 []
  tooltip:               None
  underlays:             []
  unified_draw:          False
  use_backbuffer:        False
  use_draw_order:        True
  use_selection:         False
  viewports:             []
  visible:               True
  vjustify:              'center'
  vpadding:              0
  width:                 700
  window:                None
  x:                     50
  x2:                    749
  y:                     550
  y2:                    599

.. index::
  pair: Snippet; Title

Snippet
-------
::

  myTP.padding = 50               # pixels twixt plot and window edge.

  # most title attributes delegate to the underlying _title attribute, which
  # is a PlotLabel object.
  myTP.title = 'My Plot Title'    # title appearing on screen
  myTP.title_angle = 0            # angle of the title in degrees
  myTP.title_color = 'blue'       # title color. see colorspec
  myTP.title_font = "swiss 16"    # title font. see fontspec
  myTP.title_position = 'top'     # top, bottom, left, right
  myTP.title_spacing = 'auto'     # spacing between the axis line and the title

  myTP._title.hjustify = 'center' # left, right or cener
  myTP._title.vjustify = 'center' # top, bottom or center
