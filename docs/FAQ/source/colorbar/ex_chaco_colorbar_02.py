## ex_chaco_colorbar_02.py

# standard imports
import os, inspect

# numpy imports
from numpy import sin, exp, linspace, meshgrid, pi

# Enthought imports
from enable.api import Component, ComponentEditor
from traits.api import HasTraits
from traitsui.api import Item, Group, View
from chaco.api import ArrayPlotData, jet, Plot, ColorBar
from chaco.api import LinearMapper, HPlotContainer, PlotLabel

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

  # generate a ColorBar instance
  myTCB = ColorBar(
    plot = myTP,
    index_mapper = LinearMapper( range = myTP.color_mapper.range ),
    color_mapper = myTP.color_mapper,
    orientation = 'v',
    resizable = 'v',
    width = 40,
    padding = 30,
  )

  # set the padding of the ColorBar to match the padding of the plot
  myTCB.padding_top = myTP.padding_top
  myTCB.padding_bottom = myTP.padding_bottom

  # set up the ColorBar grid and axes
  myTCB.grid_visible = True

  myTCB._axis.axis_line_color = 'black'
  myTCB._axis.axis_line_style = 'solid'
  myTCB._axis.axis_line_visible = True
  myTCB._axis.axis_line_weight = 1.0

  myTCB._axis.bgcolor = 'transparent'
  myTCB._axis.border_color ='black'
  myTCB._axis.border_dash = 'solid'
  myTCB._axis.border_visible = False
  myTCB._axis.border_width = 1

  myTCB._axis.orientation = 'left'        # 'left' or 'right'

  myTCB._axis.resizable = 'hv'
  myTCB._axis.small_haxis_style = False
  myTCB._axis.tick_color = 'black'
  myTCB._axis.tick_in = 5
  myTCB._axis.tick_interval = 'auto'
  myTCB._axis.tick_label_alignment = 'edge'
  myTCB._axis.tick_label_color = 'black'
  myTCB._axis.tick_label_font = 'Arial 12'
  myTCB._axis.tick_label_margin = 2
  myTCB._axis.tick_label_offset = 8.0
  myTCB._axis.tick_label_position = 'outside'
  myTCB._axis.tick_label_rotate_angle = 0
  myTCB._axis.tick_out = 5
  myTCB._axis.tick_visible = True
  myTCB._axis.tick_weight = 1.0
  myTCB._axis.title = 'Value of Z'
  myTCB._axis.title_angle = 90.0
  myTCB._axis.title_color = 'black'
  myTCB._axis.title_font = 'Arial 14'
  myTCB._axis.title_spacing = 'auto'

  # build a plot title for the ColorBar out of a PlotLabel instance
  myTPL = PlotLabel()

  # tell the PlotLabel that its parent component is the ColorBar and tell the
  # ColorBar that one of its overlays is the PlotLabel
  myTPL.component = myTCB
  myTCB.overlays.append( myTPL )

  # Text, fonts, etc.
  myTPL.text = "Z Value"
  myTPL.font = "Arial 16 bold"

  # build up a single container for the colorbar and the image
  myHPC = HPlotContainer( use_backbuffer = True )
  myHPC.add( myTP )
  myHPC.add( myTCB )
  myHPC.bgcolor = "lightgray"

  # set up the view for the graphic and colorbar
  traits_view = View(
      Group(
          Item( 'myHPC',
                editor = ComponentEditor( size = windowSize ),
                show_label = False
          ),
          orientation = "vertical"
      ),
      resizable = True,
      title = windowTitle,
  )

if __name__ == "__main__":

  # build the object, and show the window
  tp = TraitedPlot()
  tp.configure_traits()

  # examine the ColorBar object
  print( type(tp.myTCB) )

  membersList = inspect.getmembers( tp.myTCB )
  publicList = [thisItem for thisItem in membersList if thisItem[0][0] != '_']
  print( publicList )
  
  tp.myTCB.print_traits()

  # look at the _axis trait of the ColorBar
  print( type(tp.myTCB._axis) )

  membersList = inspect.getmembers( tp.myTCB._axis )
  publicList = [thisItem for thisItem in membersList if thisItem[0][0] != '_']
  print( publicList )

  tp.myTCB._axis.print_traits()
