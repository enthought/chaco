#!/usr/bin/env python
"""
Loads and saves RGB images from disk
 - Left-drag pans the plot.
 - Mousewheel up and down zooms the plot in and out.
 - Pressing "z" brings up the Zoom Box, and you can click-drag a rectangular
   region to zoom.  If you use a sequence of zoom boxes, pressing alt-left-arrow
   and alt-right-arrow moves you forwards and backwards through the "zoom
   history".
"""

# Standard library imports
import os, sys

# Major library imports

# Enthought library imports
from traits.util.resource import find_resource
from traits.api import File, HasTraits, Instance
from traitsui.api import Handler, Item, View
from traitsui.menu \
    import Action, CloseAction, Menu, MenuBar, OKCancelButtons, Separator

# Chaco imports
from chaco.api \
    import ArrayPlotData, ImageData, Plot, PlotGraphicsContext
from enable.component_editor import ComponentEditor
from chaco.tools.api import PanTool, ZoomTool


#-------------------------------------------------------------------------------
# Class 'DemoView'
#-------------------------------------------------------------------------------

class DemoView(HasTraits):

    ### Public Traits ##########################################################

    # A Plot Data object to hold our image data
    pd = Instance(ArrayPlotData, ())

    # A Plot object to plot our image data
    plot = Instance(Plot)


    ### Private Traits #########################################################

    # File name to load image from
    resource_path = os.path.join('examples','basic','capitol.jpg')
    alt_path = 'capitol.jpg'
    image_path = find_resource('Chaco', resource_path, alt_path=alt_path,
        return_path=True)
    _load_file = File(image_path)

    # File name to save image to
    _save_file = File


    ### Traits Views ###########################################################

    # This view is for a file dialog to select the 'load' filename
    load_file_view = View(
        Item('_load_file'),
        buttons=OKCancelButtons,
        kind='livemodal',  # NB must use livemodal, plot objects don't copy well
        width=400,
        resizable=True,
    )

    # This view is for a file dialog to select the 'save' filename
    save_file_view = View(
        Item('_save_file'),
        buttons=OKCancelButtons,
        kind='livemodal',  # NB must use livemodal, plot objects don't copy well
        width=400,
        resizable=True,
    )

    #---------------------------------------------------------------------------
    # Public 'DemoView' interface
    #---------------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super(DemoView, self).__init__(*args, **kwargs)

        # Create the plot object, set some options, and add some tools
        plot = self.plot = Plot(self.pd, default_origin="top left")
        plot.x_axis.orientation = "top"
        plot.padding = 50
        plot.padding_top = 75
        plot.tools.append(PanTool(plot))
        zoom = ZoomTool(component=plot, tool_mode="box", always_on=False)
        plot.overlays.append(zoom)

        # Load the default image
        self._load()

        # Plot the image plot with this image
        self.plot.img_plot("imagedata")

    def default_traits_view(self):
        """ Returns the default view to use for this class.
        """
        # NOTE: I moved the view to this method so we can declare a handler
        # for the view. Alternatively, we could move the DemoController class
        # to the top and declare view=Instance(HasTraits) instead.
        traits_view = View(
            Item('plot',
                 editor=ComponentEditor(),
                 show_label=False,
            ),
            menubar=MenuBar(
                Menu(Action(name="Save Plot", action="save"), # see Controller for
                     Action(name="Load Plot", action="load"), # these callbacks
                     Separator(),
                     CloseAction,
                     name="File",
                ),
            ),
            width=600,
            height=600,
            resizable=True,
            handler=DemoController
        )
        return traits_view

    #---------------------------------------------------------------------------
    # Private 'DemoView' interface
    #---------------------------------------------------------------------------

    def _save(self):
        # Create a graphics context of the right size
        win_size = self.plot.outer_bounds
        plot_gc = PlotGraphicsContext(win_size)

        # Have the plot component into it
        plot_gc.render_component(self.plot)

        # Save out to the user supplied filename
        plot_gc.save(self._save_file)

    def _load(self):
        # Load the image with the user supplied filename
        image = ImageData.fromfile(self._load_file)

        # Update the plot data. NB we must extract _data from the image
        # for the time being, until ImageData is made more friendly
        self.pd.set_data("imagedata", image._data)

        # Set the title and redraw
        self.plot.title = os.path.basename(self._load_file)
        self.plot.request_redraw()



#-------------------------------------------------------------------------------
# Class 'DemoController'
#-------------------------------------------------------------------------------

class DemoController(Handler):

    # The HasTraits object we are a controller for
    view = Instance(DemoView)

    #---------------------------------------------------------------------------
    # Public 'DemoController' interface
    #---------------------------------------------------------------------------

    def init(self, info):
        """ Initializes the controls of a user interface.
        Overridden here to assign the 'view' trait.
        """
        self.view = info.object

    def save(self, ui_info):
        """
        Callback for the 'Save Image' menu option.
        """
        ui = self.view.edit_traits(view='save_file_view')
        if ui.result == True:
            self.view._save()

    def load(self, ui_info):
        """
        Callback for the 'Load Image' menu option.
        """
        ui = self.view.edit_traits(view='load_file_view')
        if ui.result == True:
            self.view._load()


#===============================================================================
# # popup object that is used by the demo.py application.
#===============================================================================
# Note: we declare a 'popup' rather than a 'demo' since the menubar doesn't seem
# to show up in a 'panel' mode.
popup = DemoView()

#-------------------------------------------------------------------------------
# Function 'main'
#-------------------------------------------------------------------------------

def main(argv=None):
    view = DemoView()
    view.configure_traits()


#-------------------------------------------------------------------------------

if __name__ == "__main__":
    sys.exit(main())
