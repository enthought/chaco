## ex_chaco_myTP.grid_02.py

"""
Simple plot, with grid options
"""

## -- Notes -----------------------------------------------------------------

## -- Imports ---------------------------------------------------------------
# standard imports
import inspect
import numpy as np

# Enthought imports
from enable.api import Component, ComponentEditor
from traits.api import HasTraits
from traitsui.api import Item, Group, View
from chaco.api import Plot, ArrayPlotData

## -- Let's Begin -----------------------------------------------------------

## -- Classes ---------------------------------------------------------------

class MyPlot( HasTraits ):
  '''simple line plot'''

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

  # grid line color. See colorspec. can be e.g. "black" or e.g. (0.827, 0.827,
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

  # the thinknexx of the grid lines, in pixels. Attribute line_weight is
  # aliased here.
  myTP.x_grid.line_width

  # the grid_mapper method that drives this PlotGrid. Defaults to
  # <chaco.linear_mapper.LinearMapper object at 0x0BB35720>
  myTP.x_grid.mapper

  # the tick_generator method (implimenting AbstractTickGenerator) that drives
  # this plot. Defaults to <chaco.ticks.DefaultTickGenerator object at
  # 0x05FED180>),
  myTP.x_grid.tick_generator


  mySize = (800,600)
  myTitle = 'myPlot'
  traits_view = View(
      Group(
          Item(
              'myTP',
              editor = ComponentEditor(size = mySize),
              show_label = False,
          ),
          orientation = "vertical",
      ),
      resizable = True,
      title = myTitle,
      width = mySize[0], height = mySize[1],
  )

## -- Functions -------------------------------------------------------------

## -- Main ------------------------------------------------------------------

if __name__ == "__main__":

  myPlot = MyPlot()
  myPlot.configure_traits()

## -- EOF -------------------------------------------------------------------
