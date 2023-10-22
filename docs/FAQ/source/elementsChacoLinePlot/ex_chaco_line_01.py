## ex_chaco_line_01.py

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

  # generate interesting data
  numPoints = 100
  extent = 2.0 * np.pi
  phaseA = np.linspace( -extent,extent,numPoints )
  amplitudeA = np.sin( phaseA ) * np.exp(-abs( phaseA ))

  # map arrays to plot names. TADP suffix => Traits ArrayPlotData
  myTADP = ArrayPlotData()
  myTADP.set_data( 'X',phaseA )
  myTADP.set_data( 'Y',amplitudeA )

  # generate the plot. TP suffix => Traits Plot
  myTP = Plot( myTADP )
  myTP.plot(
      ("X", "Y"),
      type = 'line',
  )

  # generate the view
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

  # generate and display the plot
  tp = TraitedPlot()
  tp.configure_traits()

  # after we close the plot, all the attributes of the plot will be set (see
  # Lazy Initialization). Introspect into the tp object

  # generate a list of the public attributes in the Traits Plot objext
  myPublics = [thisItem for thisItem in inspect.getmembers(tp.myTP) if thisItem[0][0] != '_']
  print( myPublics )

  # use the print_traits() method to show a subset of the plot attributes
  tp.myTP.print_traits()
