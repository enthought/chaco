## ex_chaco_colormapper_03.py

# standard imports
import os, inspect

# numpy imports
from numpy import sin, sqrt,abs, exp, linspace, meshgrid, pi

# Enthought imports
from enable.api import Component, ComponentEditor
from traits.api import HasTraits, Instance
from traitsui.api import Item, Group, View
from chaco.api import ArrayPlotData, Plot, ColorBar
from chaco.api import LinearMapper, HPlotContainer
from chaco.api import ImageData, DataRange1D

from chaco import default_colormaps

# defines
windowSize = (800,600)

# window title is file name
windowTitle = os.path.split(__file__)[1]

class TraitedPlot( HasTraits ):

  # the plot container
  myTIC = Instance( HPlotContainer )

  # set up the view for both the graphics and control
  traits_view = View(
      Item(
          'myTIC',
          editor = ComponentEditor(size = windowSize),
          show_label = False,
      ),
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
    myTP = Plot( myAPD )

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
    myDR1D = DataRange1D( myID )

    # pick a colormap
    myColorMapperFn = default_colormaps.color_map_name_dict['copper']

    # choose one or more modifications to the colormap function
    #myColorMapperFn = default_colormaps.reverse( myColorMapperFn )
    #myColorMapperFn = default_colormaps.center( myColorMapperFn,500 )
    #myColorMapperFn = default_colormaps.fix( myColorMapperFn,(-500,500) )

    # finally, build the colormapper function
    myColorMapper = myColorMapperFn( myDR1D )

    # add the image plot to this plot object
    # specify the colormap explicitly
    myTP.img_plot(
        "Z",
        xbounds = (xA[0],xA[-1]),
        ybounds = (yA[0],yA[-1]),
        colormap = myColorMapper,
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

    # range of the colormapper. Changes the min/max values that are mapped
    # to the ends of the color range. Try +/-2000 for poor contrast and +/-200 for
    # saturated. Asymmetrical values work as well.
    #myTP.color_mapper.range.low_setting = 0
    #myTP.color_mapper.range.high_setting = 1000

    # build up a single container for the colorbar and the image
    myHPC = HPlotContainer( use_backbuffer = True )
    myHPC.add( myTP )
    myHPC.add( myTCB )

    return( myHPC )

if __name__ == "__main__":

  tp = TraitedPlot()
  tp.configure_traits( )
