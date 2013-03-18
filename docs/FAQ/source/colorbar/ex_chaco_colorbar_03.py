#!/usr/bin/env python

## ex_chaco_colorbar_03.py

## -- Notes -----------------------------------------------------------------

## -- Imports ---------------------------------------------------------------
# standard imports
import os
from math import atan2, sqrt

# numpy imports
from numpy import sin, cos, exp, linspace, meshgrid, pi

# Enthought imports
from enable.api import Component, ComponentEditor
from traits.api import HasTraits, Instance, Range, Str, on_trait_change
from traitsui.api import Item, Group, View

# Chaco imports
from chaco.api import ArrayPlotData, jet, Plot, ColorBar
from chaco.api import LinearMapper, HPlotContainer

## -- Defines ---------------------------------------------------------------
graphicWindowSize = (800,600)
colorbarWindowSize = (100,600)

# window title is file name
windowTitle = os.path.split(__file__)[1]

## -- Let's Begin -----------------------------------------------------------

## -- Functions -------------------------------------------------------------

## -- Classes ---------------------------------------------------------------

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

  # add the colorbar
  #myTCB = ColorBar(
  #    plot = myTP,
  #    index_mapper = LinearMapper( range = myTP.color_mapper.range ),
  #)

  myTCB = ColorBar(
        plot = myTP,
        index_mapper = LinearMapper( range = myTP.color_mapper.range ),
        color_mapper = myTP.color_mapper,
        orientation = 'v',
        resizable = 'v',
        width = 40,
        padding = 30,
  )
  #myTCB.plot = myTP
  myTCB.padding_top = myTP.padding_top
  myTCB.padding_bottom = myTP.padding_bottom

  # build up a single container for the colorbar and the image
  myHPC = HPlotContainer( use_backbuffer = True )
  myHPC.add( myTP )
  myHPC.add( myTCB )
  myHPC.bgcolor = "lightgray"

  # set up the view for both the graphics and control

  traits_view = View(
        Group(
            Item( 'myHPC',
                   editor = ComponentEditor( size = graphicWindowSize ),
                   show_label = False
            ),
            orientation = "vertical"
        ),
        resizable = True,
        title = windowTitle,
  )
  #                       padding=20)

  ## The border is visible (overrides enable.Component).
  #border_visible = True
  ## The orientation of the index axis.
  #orientation = Enum('v', 'h')
  ## Should the bar go left-to-right or bottom-to-top (normal) or the reverse?
  #direction = Enum('normal', 'flipped')
  ## Overrides the default background color trait in PlotComponent.
  #bgcolor = 'transparent'
  ## Draw layers in "draw order"
  #use_draw_order = True
  ## Default width is 40 pixels (overrides enable.CoordinateBox)
  #width = 40

  # Faux origin for the axis to look at
  #origin = Enum('bottom left', 'top left', 'bottom right', 'top right')

  ## The border is visible (overrides enable.Component).
  #border_visible = True
  ## The orientation of the index axis.
  #orientation = Enum('v', 'h')
  ## Should the bar go left-to-right or bottom-to-top (normal) or the reverse?
  #direction = Enum('normal', 'flipped')
  ## Overrides the default background color trait in PlotComponent.
  #bgcolor = 'transparent'
  ## Draw layers in "draw order"
  #use_draw_order = True
  ## Default width is 40 pixels (overrides enable.CoordinateBox)
  #width = 40
  #
  ## Faux origin for the axis to look at
  #origin = Enum('bottom left', 'top left', 'bottom right', 'top right')




  # Dimensions that this component is resizable in.  For resizable
  # components,  get_preferred_size() is called before their actual
  # bounds are set.
  #
  # * 'v': resizable vertically
  # * 'h': resizable horizontally
  # * 'hv': resizable horizontally and vertically
  # * '': not resizable
  #
  # Note that this setting means only that the *parent* can and should resize
  # this component; it does *not* mean that the component automatically
  # resizes itself.
  #resizable = Enum("hv", "h", "v", "")


  ##------------------------------------------------------------------------
  ## Border and background traits
  ##------------------------------------------------------------------------
  #
  ## The width of the border around this component.  This is taken into account
  ## during layout, but only if the border is visible.
  #border_width = Int(1)
  #
  ## Is the border visible?  If this is false, then all the other border
  ## properties are not used.
  #border_visible = Bool(False)
  #
  ## The line style (i.e. dash pattern) of the border.
  #border_dash = LineStyle
  #
  ## The color of the border.  Only used if border_visible is True.
  #border_color = black_color_trait
  #
  ## The background color of this component.  By default all components have
  ## a white background.  This can be set to "transparent" or "none" if the
  ## component should be see-through.
  #bgcolor = white_color_trait


## -- Main ------------------------------------------------------------------

if __name__ == "__main__":

  # build the object, and show the window
  tP = TraitedPlot()
  tP.configure_traits()

## -- EOF -------------------------------------------------------------------
