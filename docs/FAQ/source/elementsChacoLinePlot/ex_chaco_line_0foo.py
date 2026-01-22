## ex_chaco_line_01.py

# standard imports
import inspect
import numpy as np

# Enthought imports
from enable.api import Component, ComponentEditor
from traits.api import HasTraits
from traitsui.api import Item, Group, View
from chaco.api import Plot, ArrayPlotData

class TraitedPlot( HasTraits ):
  '''simple line plot'''

  # generate interesting data
  numPoints = 100
  extent = 2.0 * np.pi
  phaseA = np.linspace( -extent,extent,numPoints )
  amplitudeA = np.sin( phaseA ) * np.exp(-abs( phaseA ))

  # map names to data. TADP postfix => Traits ArrayPlotData
  myTADP = ArrayPlotData()
  myTADP.set_data( 'X',phaseA )
  myTADP.set_data( 'Y',amplitudeA )

  # generate the plot. TP postfix => Traits Plot
  myTP = Plot( myTADP )
  myTP.plot(
      ("X", "Y"),
      type = 'line',
  )

  # generate the view
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

if __name__ == "__main__":

  # generate and display the plot
  tp = TraitedPlot()
  tp.configure_traits()

  # after we close the plot, all the attributes of the plot have been guarenteed
  # to be set (see Lazy Initialization). Introspect into the tp object

  # generate a list of the public attributes in the Traits Plot objext
  myPublics = [thisItem for thisItem in inspect.getmembers(tp.myTP) if thisItem[0][0] != '_']
  print( myPublics )

  # use the print_traits() method to show a subset of the plot attributes
  tp.myTP.print_traits()

  # the data
  tp.myTP.data.print_traits()
  tp.myTP.datasources['X'].print_traits()
  tp.myTP.datasources['Y'].print_traits()

  # padding
  tp.myTP.padding
  tp.myTP.padding_left
  tp.myTP.padding_right
  tp.myTP.padding_bottom
  tp.myTP.padding_top

  # grids
  tp.myTP.x_grid.print_traits()

  # axes
  tp.myTP.x_axis.print_traits()

  # plotting ranges
  tp.myTP.range2d.print_traits()
  tp.myTP.range2d.x_range.print_traits()
