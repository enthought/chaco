## ex_chaco_plotlabel_01.py

# standard imports
import os, inspect

# numpy imports
from numpy import sin, cos, sqrt, abs, linspace, meshgrid

# Enthought imports
from enable.api import Component, ComponentEditor
from traits.api import HasTraits
from traitsui.api import Item, Group, View
from chaco.api import ArrayPlotData, Plot, ColorBar, PlotLabel
from chaco.api import LinearMapper, HPlotContainer, DataLabel

# defines
windowSize = (800,600)

# window title is file name
windowTitle = os.path.split(__file__)[1]

class TraitedPlot( HasTraits ):

  # create an interesting scalar field for the image plot
  # the valentine's plot
  # 5 + (-sqrt(1-x^2-(y-abs(x))^2))*cos(30*((1-x^2-(y-abs(x))^2))),
  # x is from -1 to 1, y is from -1 to 1.5, z is from 1 to 6
  xA = linspace(-1.0, 1.0, 600)
  yA = linspace(-1.0, 1.5, 600)
  ( xMG,yMG ) = meshgrid( xA,yA )
  zMG = (-sqrt( abs( 1 - xMG**2 - (yMG - abs(xMG))**2 )))
  zMG = zMG * cos( 30.0 * ( (1.0 - xMG**2 - (yMG - abs(xMG))**2)))
  zMG = zMG + 5.0

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
  myTP.title = "Valentine's Day Function"
  myTP.padding = 50

  # grids, fonts, etc
  myTP.x_axis.title = "X"
  myTP.y_axis.title = "Y"

  # PlotLabel stuff
  myTPL = PlotLabel( text = "Howdy" )

  # Can set the text this way as well. Also, can use newlines
  myTPL.text = "True\nLove\nAlways"

  # The color of the label text.
  myTPL.color = 'blue'

  # The font for the label text.
  myTPL.font = 'swiss 18 bold'

  # The angle of rotation of the label.
  myTPL.angle = 0       # try 45

  # misc
  myTPL.bgcolor = 'cornflowerblue'    # see ``cclor_table`` in enable/colors.py
  myTPL.border_width = 3              # defaults to 0 pixels
  myTPL.border_color = 'blue'         # defaults to black
  myTPL.border_visible = True         # defaults to True
  myTPL.margin = 5                    # number of pixels of margin between the
                                      # text and the plotlabel border, in both
                                      # X and Y dims
  myTPL.line_spacing = 20             # number of pixels of spacing between lines of text

  # layout related
  # Horizontal/vertical justification used if the label has more space
  # than it needs.
  myTPL.hjustify = 'center'     # Enum("center", "left", "right")
  myTPL.vjustify = 'center'     # Enum("center", "bottom", "top")

  # The position of this label relative to the object it is overlaying.
  # Can be "top", "left", "right", "bottom", and optionally can be preceeded
  # by the words "inside" or "outside", separated by a space.  If "inside"
  # and "outside" are not provided, then defaults to "outside".
  # Examples: 'inside top', 'outside right'
  myTPL.overlay_position = 'inside right'  # Trait("outside top", Str, None)

  myTPL.padding_left = 10     # extra padding added to the PlotLabel layout, in pixels
  myTPL.padding_right
  myTPL.padding_top
  myTPL.padding_bottom

  # By default, this acts like a component and will render on the main plot
  # layer unless its component attribute gets set.
  #myTPL.draw_layer

  # The label has a fixed height and can be resized horizontally. (Overrides
  # PlotComponent.)
  myTPL.resizable = 'h'       # defaults to 'h'

  # methods
  #myTPL.do_layout()                # Tells this component to do layout.
  myTPL.get_preferred_size()        # Returns the label?s preferred size, in pixels.

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

  # inform the Traits plot that it has a Traits PlotLabel overlay, and inform
  # the Traits PlotLabel instance that it is being overlayed onto the Traits
  # Plot
  myTP.overlays.append( myTPL )
  myTPL.component = myTP

  # Note that we could also have overlayed the PlotLabel on the Traits
  # Horizontal Plot container, myHPC. Then the positions would refer to
  # the plot container and not just to the plot
  #myHPC.overlays.append( myTPL )
  #myTPL.component = myHPC

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

  # traits of the Traits Plot
  tp.myTP.print_traits()

  # traits of the Traits Horizontal Plot Container
  tp.myHPC.print_traits()

  # traits of the Traits Plot Label
  tp.myTPL.print_traits()
