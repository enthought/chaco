## ex_chaco_colorbar_01.py

# standard imports
import os, inspect

# numpy imports
from numpy import sin, exp, linspace, meshgrid, pi

# Enthought imports
from enable.api import Component, ComponentEditor
from traits.api import HasTraits
from traitsui.api import Item, Group, View
from chaco.api import ArrayPlotData, jet, Plot

# defines
windowSize = (800,600)

# window title is file name
windowTitle = os.path.split(__file__)[1]

class TraitedPlot( HasTraits ):

  # create an interesting scalar field for the image plot
  twoPi = 2.0 * pi
  xA = linspace(-twoPi, twoPi, 600)
  yA = linspace(-twoPi, twoPi, 600)
  ( xMG,yMG ) = meshgrid( xA,yA )
  z1MG = exp(-(xMG**2 + yMG**2)) / 100.0
  zxMG = sin( xMG ) / xMG
  zyMG = sin( yMG ) / yMG
  zMG = zxMG + zyMG

  # Create an ArrayPlotData object and give it this data
  myAPD = ArrayPlotData()
  myAPD.set_data( "Z", zMG )
  myAPD.set_data( "X",xA )
  myAPD.set_data( "Y",yA )

  # Create the plot
  myTP = Plot( myAPD )

  # add the image plot to this plot object
  myTP.img_plot(
      "Z",
      xbounds = (xA[0],xA[-1]),
      ybounds = (yA[0],yA[-1]),
      colormap = jet,
  )

  # add the title and padding around the plot
  myTP.title = "2D sin(x)/x"
  myTP.padding = 50

  # grids, fonts, etc
  myTP.x_axis.title = "X Phase (rad)"
  myTP.y_axis.title = "Y Phase (rad)"

  # set up the view for both the graphics and control
  traits_view = View(
      Item(
          'myTP',
          editor = ComponentEditor(size = windowSize),
          show_label = False,
      ),
      resizable = True,
      title = windowTitle,
  )

if __name__ == "__main__":

  tp = TraitedPlot()
  tp.configure_traits()

