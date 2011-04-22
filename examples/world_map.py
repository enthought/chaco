#!/usr/bin/env python
"""
Displays a world map with locations plotted on top. Locations are expected to
be tuples of latitude, longitude where West and South are expressed as
negative values.
 - Mousewheel up and down zooms the plot in and out.
 - Pressing "z" brings up the Zoom Box, and you can click-drag a rectangular
   region to zoom.  If you use a sequence of zoom boxes, pressing alt-left-arrow
   and alt-right-arrow moves you forwards and backwards through the "zoom
   history".
"""

# Standard library imports
import os.path
import urllib

# Major library imports
import numpy

# ETS imports
from enthought.chaco.api import Plot, ArrayPlotData, ImageData
from enthought.chaco.tools.api import ZoomTool
from enable.component_editor import ComponentEditor
from traits.api import HasTraits, Instance, Str
from traitsui.api import Item, View

class WorldMapPlot(HasTraits):

    ### Public Traits ##########################################################

    # The plot which will be displayed
    plot = Instance(Plot)

    # The URL which points to the world map image to be downloaded
    image_url = Str("http://veimages.gsfc.nasa.gov/2433/land_shallow_topo_2048.jpg")


    ### Private Traits #########################################################

    # The path to where the image exists on the filesystem
    image_path = Str()

    # The view
    traits_view = View(Item('plot', editor=ComponentEditor(),
                            width=800, height=400, show_label=False),
                       resizable=True)

    #---------------------------------------------------------------------------
    # Public interface
    #---------------------------------------------------------------------------

    def __init__(self, **kw):
        super(WorldMapPlot, self).__init__(**kw)

        self._download_map_image()
        image = ImageData.fromfile(self.image_path)

        # For now, the locations are hardcoded, though this can be changed
        # eassily to take command line args, read from a file, or by other
        # means
        austin_loc = (30.16, -97.44)

        locations_x = numpy.array([austin_loc[1]])
        locations_y = numpy.array([austin_loc[0]])

        # transform each of the locations to the image data space, including
        # moving the origin from bottom left to top left
        locations_x = (locations_x + 180) * image.data.shape[1]/360
        locations_y = (locations_y*-1 + 90) * image.data.shape[0]/180

        # Create the plott data, adding the image and the locations
        plot_data = ArrayPlotData()
        plot_data.set_data("imagedata", image._data)
        plot_data.set_data("locations_x", locations_x)
        plot_data.set_data("locations_y", locations_y)

        # Create the plot with the origin as top left, which matches
        # how the image data is aligned
        self.plot = Plot(plot_data, default_origin="top left")
        self.plot.img_plot('imagedata')

        # Plot the locations as a scatter plot to be overlayed on top
        # of the map
        loc_plot = self.plot.plot(('locations_x',  'locations_y'),
                                    type='scatter', size=3, color='yellow',
                                    marker='dot')[0]

        loc_plot.x_mapper.range.high = image.data.shape[1]
        loc_plot.x_mapper.range.low = 0
        loc_plot.y_mapper.range.high = image.data.shape[0]
        loc_plot.y_mapper.range.low = -0

        # set up any tools, in this case just the zoom tool
        zoom = ZoomTool(component=self.plot, tool_mode="box", always_on=False)
        self.plot.overlays.append(zoom)

    #---------------------------------------------------------------------------
    # Protected interface
    #---------------------------------------------------------------------------

    def _download_map_image(self):
        """ Downloads a map from the image_url attribute. This is done
            primarily to keep the redistributable Chaco package as small
            as possible
        """
        example_dir = os.path.dirname(__file__)
        self.image_path = os.path.join(example_dir, 'data',
                                        os.path.split(self.image_url)[1])

        if not os.path.exists(self.image_path):
            print "Downloading map image"
            urllib.urlretrieve(self.image_url, self.image_path)

#===============================================================================
# demo object that is used by the demo.py application.
#===============================================================================
demo = WorldMapPlot()

if __name__ == "__main__":
    demo.configure_traits()
