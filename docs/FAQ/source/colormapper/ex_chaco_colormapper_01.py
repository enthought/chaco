## ex_chaco_colormapper_01.py

# standard imports
import os, inspect

# numpy imports
from numpy import sin, sqrt,abs, exp, linspace, meshgrid, pi

# Enthought imports
from enable.api import Component, ComponentEditor
from traits.api import HasTraits
from traitsui.api import Item, Group, View
from chaco.api import ArrayPlotData, Plot, ColorBar
from chaco.api import LinearMapper, HPlotContainer

# defines
windowSize = (800,600)

# window title is file name
windowTitle = os.path.split(__file__)[1]

class TraitedPlot( HasTraits ):

  # create an interesting scalar field for the image plot
  # Eggholder function
  limitF = 500.0
  xA = linspace(-limitF, limitF, 600)
  yA = linspace(-limitF, limitF, 600)
  ( xMG,yMG ) = meshgrid( xA,yA )
  zMG = -(yMG + 47) * sin( sqrt(abs(yMG + xMG/2 + 47 )))
  zMG = zMG - xMG * sin( sqrt(abs(xMG - (yMG + 47))))

  # Create an ArrayPlotData object and give it this data
  myAPD = ArrayPlotData()
  myAPD.set_data( "Z", zMG )
  myAPD.set_data( "X",xA )
  myAPD.set_data( "Y",yA )

  # Create the plot.
  myTP = Plot( myAPD )

  # add the image plot to this plot object. If we don't specify the colormapper,
  # it defaults to default_colormaps.Spectral
  myTP.img_plot(
      "Z",
      xbounds = (xA[0],xA[-1]),
      ybounds = (yA[0],yA[-1]),
  )

  # add the title and padding around the plot
  myTP.title = "Eggholder Function"
  myTP.padding = 50

  # grids, fonts, etc
  myTP.x_axis.title = "X"
  myTP.y_axis.title = "Y"

  # generate a ColorBar. pulls its colormapper from the myTP Plot object
  myTCB = ColorBar(
    plot = myTP,
    index_mapper = LinearMapper( range = myTP.color_mapper.range ),
    orientation = 'v',
    resizable = 'v',
    width = 40,
    padding = 30,
  )

  # set the padding of the ColorBar to match the padding of the plot
  myTCB.padding_top = myTP.padding_top
  myTCB.padding_bottom = myTP.padding_bottom

  # build up a single container for the colorbar and the image
  myHPC = HPlotContainer( use_backbuffer = True )
  myHPC.add( myTP )
  myHPC.add( myTCB )

  # set up the view for both the graphics and control
  traits_view = View(
      Item(
          'myHPC',
          editor = ComponentEditor(size = windowSize),
          show_label = False,
      ),
      resizable = True,
      title = windowTitle,
  )

if __name__ == "__main__":

  tp = TraitedPlot()
  tp.configure_traits()

  tp.myTP.color_mapper.print_traits()
  tp.myTP.color_mapper.range.print_traits()
