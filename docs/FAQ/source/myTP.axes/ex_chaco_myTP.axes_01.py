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
