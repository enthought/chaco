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
