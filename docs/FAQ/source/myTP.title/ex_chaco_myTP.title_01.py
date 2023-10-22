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
