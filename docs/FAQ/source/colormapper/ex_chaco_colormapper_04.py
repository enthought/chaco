## ex_chaco_colormapper_04.py

# standard imports
import os, inspect

# numpy imports
from numpy import sin, sqrt,abs, exp, linspace, meshgrid, pi

# Enthought imports
from enable.api import Component, ComponentEditor
from traits.api import HasTraits, Instance, Enum, Range, Bool
from traitsui.api import Item, Group, VGroup, View, RangeEditor
from chaco.api import ArrayPlotData, Plot, ColorBar
from chaco.api import LinearMapper, HPlotContainer
from chaco.api import ImageData, DataRange1D

from chaco import default_colormaps

# defines
windowSize = (800,600)

# window title is file name
windowTitle = os.path.split(__file__)[1]

class TraitedPlot( HasTraits ):

  # the Traits Plot Container
  myTP = Instance( Plot )
  myTCB = Instance( ColorBar )
  myTIC = Instance( HPlotContainer )

  # contains a list of default colormap names
  colormapNameTE = Enum(
      default_colormaps.color_map_name_dict.keys(),
      label = 'Color Map Name',
      desc = 'the color map name',
  )

  # the low saturation value for the colormap
  colormapLowTR = Range(
      value = -1000,
      low = -1000,
      high = 1000,
      label = 'Color Map Low',
      desc = 'the color map low saturation value',
  )

  colormapHighTR = Range(
      value = 1000,
      low = -1000,
      high = 1000,
      label = 'Color Map High',
      desc = 'the color map high saturation value',
  )

  reversedColormapTB = Bool(
      value = False,
      label = 'Reverse the Color Map',
      desc = 'the color map reversal state',
  )

  # set up the view for both the graphics and control
  traits_view = View(
    Item(
        name = 'myTIC',
        editor = ComponentEditor(size = windowSize),
        show_label = False,
    ),
    Item( name = "colormapNameTE" ),
    Item(
        name = "colormapLowTR",
        editor = RangeEditor(
            auto_set = False,
            enter_set = True,
            mode = 'slider',
            low = -1000,
            high = 1000,
        ),
    ),
    Item(
        name = "colormapHighTR",
        editor = RangeEditor(
            auto_set = False,
            enter_set = True,
            mode = 'slider',
            low = -1000,
            high = 1000,
        ),
    ),
    Item( name = "reversedColormapTB" ),
    resizable = True,
    title = windowTitle,
  )

  def _myTIC_default( self ):

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

    # Create the plot
    self.myTP = Plot( myAPD )

    # contains a dict of default colormaps and their functions. We have to
    # pass the colormapper the data range of interest to set up the private
    # attributes
    default_colormaps.color_map_name_dict

    # the colormap method needs the range of the image data that we want to
    # plot. We first put the image data (zMG) into an ImageData object. We
    # then use DataRange1D on the ImageData instance to produce a DataRange1D
    # instance describing the ImageData data. Finally, we feed the DataRange1D
    # instance into the colormapper to produce a working colormapper.
    myID = ImageData( )
    myID.set_data( zMG )
    self.myDR1D = DataRange1D( myID )

    # pick an unmodified (i.e. unreversed, no ranges) colormap and build
    # the colormap functions
    myColorMapperFn = default_colormaps.color_map_name_dict[self.colormapNameTE]
    myColorMapper = myColorMapperFn( self.myDR1D )

    # add the image plot to this plot object
    # specify the colormap explicitly
    self.myTP.img_plot(
        "Z",
        xbounds = (xA[0],xA[-1]),
        ybounds = (yA[0],yA[-1]),
        colormap = myColorMapper,
    )

    # add the title and padding around the plot
    self.myTP.title = "Eggholder Function"
    self.myTP.padding = 50

    # grids, fonts, etc
    self.myTP.x_axis.title = "X"
    self.myTP.y_axis.title = "Y"

    # generate a ColorBar. pulls its colormapper from the myTP Plot object
    self.myTCB = ColorBar(
      plot = self.myTP,
      index_mapper = LinearMapper( range = self.myTP.color_mapper.range ),
      orientation = 'v',
      resizable = 'v',
      width = 40,
      padding = 30,
    )

    # set the padding of the ColorBar to match the padding of the plot
    self.myTCB.padding_top = self.myTP.padding_top
    self.myTCB.padding_bottom = self.myTP.padding_bottom

    # build up a single container for the colorbar and the image
    myHPC = HPlotContainer( use_backbuffer = True )
    myHPC.add( self.myTP )
    myHPC.add( self.myTCB )

    return( myHPC )

  def _modify_colormap(self):

    #myTP.color_mapper.range.low_setting = 0
    #myTP.color_mapper.range.high_setting = 1000

    # pick out the color map function
    myColorMapperFn = default_colormaps.color_map_name_dict[self.colormapNameTE]

    # reverse the colormap, if req'd
    if self.reversedColormapTB:
      myColorMapperFn = default_colormaps.reverse( myColorMapperFn )

    ## TODO adjust for too low, too high, end cases

    myColorMapperFn = default_colormaps.fix(
        myColorMapperFn,
        (self.colormapLowTR, self.colormapHighTR)
    )
    myColorMapper = myColorMapperFn( self.myDR1D )
    self.myTP.color_mapper = myColorMapper
    self.myTP.request_redraw()

  def _reversedColormapTB_changed( self,old,new ):
    S = '_reversedColormapTB_changed() - old: %s, new: %s' % (old,new)
    print( S )
    self._modify_colormap()

  def _colormapNameTE_changed( self,old,new ):
    S = '_colormapNameTE_changed() - old: %s, new: %s' % (old,new)
    print( S )
    self._modify_colormap()

  def _colormapLowTR_changed( self,old,new ):
    S = '_colormapLowTR_changed() - old: %s, new: %s' % (old,new)
    print( S )

    # check for boundary conditions
    if self.colormapLowTR >= self.colormapHighTR:
      self.colormapLowTR = old
      print( 'colormapLowTR restored to old value: %s' % old )
    self._modify_colormap()

  def _colormapHighTR_changed( self,old,new ):
    S = '_colormapHighTR_changed() - old: %s, new: %s' % (old,new)
    print( S )
    if self.colormapHighTR <= self.colormapLowTR:
      self.colormapHighTR = old
      print( 'colormapHighTR restored to old value: %s' % old )
    self._modify_colormap()

if __name__ == "__main__":

  tp = TraitedPlot()
  tp.configure_traits( )
