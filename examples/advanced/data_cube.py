"""
Allows isometric viewing of a 3D data cube.
"""

# Standard library imports
from optparse import OptionParser
import sys

# Major library imports
from numpy import array, linspace, nanmin, nanmax, newaxis, pi, vectorize, zeros, sin, cos, tan

# Enthought library imports
from enthought.chaco2.api import ArrayDataSource, ArrayPlotData, ColorBar, ContourLinePlot, \
                                 ColormappedScatterPlot, CMapImagePlot, \
                                 ContourPolyPlot, DataRange1D, VPlotContainer, \
                                 DataRange2D, GridMapper, GridDataSource, \
                                 HPlotContainer, ImageData, LinearMapper, \
                                 LinePlot, OverlayPlotContainer, Plot, PlotAxis, GridPlotContainer, \
                                 BaseTool
from enthought.chaco2.default_colormaps import *
from enthought.chaco2.chaco2_plot_container_editor import PlotContainerEditor
from enthought.chaco2.tools.api import LineInspector, PanTool, RangeSelection, \
                                   RangeSelectionOverlay, SimpleZoom
from enthought.chaco2.example_support import DemoFrame, demo_main, COLOR_PALETTE
from enthought.enable2.api import Window
from enthought.traits.api import Any, Array, Callable, CFloat, CInt, Enum, Event, Float, HasTraits, \
                             Int, Instance, Str, Trait, on_trait_change
from enthought.traits.ui.api import Group, Handler, HGroup, Item, View
from enthought.traits.ui.menu import Action, CloseAction, Menu, \
                                     MenuBar, NoButtons, Separator


class Model(HasTraits):

    #Traits view definitions:
    #traits_view = View(
    #    Group(Item('function'), 
    #          HGroup(Item('npts_x', label="Number X Points"),
    #                 Item('npts_y', label="Number Y Points"),
    #                 Item('npts_z', label="Number Z Points")),
    #          HGroup(Item('min_x', label="Min X value"),
    #                 Item('max_x', label="Max X value")),
    #          HGroup(Item('min_y', label="Min Y value"),
    #                 Item('max_y', label="Max Y value")),
    #          HGroup(Item('min_z', label="Min Z value"),
    #                 Item('max_z', label="Max Z value"))),
    #                 buttons=["OK", "Cancel"])

    function = Str("sin(x) * cos(y) + sin(0.5*z)")
    #function = Str("tanh(x**2+y)*cos(y)*jn(0,x+y*2)")

    npts_x = CInt(256)
    npts_y = CInt(256)
    npts_z = CInt(113)

    min_x = CFloat(-2*pi)
    max_x = CFloat(2*pi)
    min_y = CFloat(-2*pi)
    max_y = CFloat(2*pi)
    min_z = CFloat(-pi)
    max_z = CFloat(pi)

    xs = Array
    ys = Array
    vals = Array

    minval = Float
    maxval = Float

    model_changed = Event

    def __init__(self, *args, **kwargs):
        super(Model, self).__init__(*args, **kwargs)
        self.compute_model()

    @on_trait_change("function", "npts_+", "min_+", "max_+")
    def compute_model(self):

        def vfunc(x, y, z):
            return sin(x) * cos(y) + sin(0.5*z)

        # Create the values
        self.xs = linspace(self.min_x, self.max_x, self.npts_x)
        self.ys = linspace(self.min_y, self.max_y, self.npts_y)
        self.zs = linspace(self.min_z, self.max_z, self.npts_z)

        #func = compile(self.function, "<string>", "eval")
        #vfunc = vectorize(lambda x,y,z: eval(func))
        self.vals = vfunc(self.xs[:, newaxis, newaxis], 
                          self.ys[newaxis, :, newaxis],
                          self.zs[newaxis, newaxis, :])

        self.minval = nanmin(self.vals)
        self.maxval = nanmax(self.vals)
        self.model_changed = True
        self._function = self.function


class ImageIndexTool(BaseTool):
    """ A tool to set the slice of a cube based on the user's clicks
    """

    # This callback will be called with the index into self.component's
    # index and value:
    #     callback(x_index, y_index)
    callback = Any()

    def normal_mouse_move(self, event):
        plot = self.component
        ndx = plot.map_index((event.x, event.y), 
                             threshold=5.0, index_only=True)
        if ndx:
            self.callback(*ndx)


class PlotFrame(DemoFrame):

    # These are the indices into the cube that each of the image plot views
    # will show
    slice_x = 10
    slice_y = 10
    slice_z = 0

    num_levels = Int(15)
    colormap = Any  #Enum(color_map_name_dict.keys())

    #---------------------------------------------------------------------------
    # Private Traits
    #---------------------------------------------------------------------------
        
    _cmap = Trait(jet, Callable)

    def _index_callback(self, plane, x_index, y_index):
        if plane == "xy":
            self.slice_x = x_index
            self.slice_y = y_index
        elif plane == "yz":
            self.slice_y = x_index
            self.slice_z = y_index
        elif plane == "xz":
            self.slice_x = x_index
            self.slice_z = y_index
        else:
            warnings.warn("Unrecognized plane for _index_callback: %s" % plane)
        self._update_images()
        self.center.invalidate_draw()
        #self.center.request_redraw()
        self.right.invalidate_draw()
        #self.right.request_redraw()
        self.bottom.invalidate_draw()
        #self.bottom.request_redraw()

        #self.centerplot.invalidate_and_redraw()
        #self.bottomplot.invalidate_and_redraw()
        #self.rightplot.invalidate_and_redraw()
        return
    
    def _create_window(self):
        # This approach creates a PlotData object with three ImageData arrays
        # that get plotted

        # Create the model
        self.model = model = Model()
        datacube = self.model.vals

        # Create the plot
        self.plotdata = ArrayPlotData()
        self._update_images()

        centerplot = Plot(self.plotdata, padding=0, use_backbuffer=False)
        imgplot = centerplot.img_plot("xy", xbounds=model.xs, ybounds=model.ys, 
                            colormap=jet)[0]
        imgplot.overlays.append(LineInspector(imgplot, axis="index_y",
            inspect_mode="space", write_metadata=True, is_listener=True))
        imgplot.overlays.append(LineInspector(imgplot, axis="index_x",
            inspect_mode="space", write_metadata=True, is_listener=True))
        imgplot.tools.append(ImageIndexTool(imgplot, callback=lambda i,j: self._index_callback("xy", i, j)))
        self.center = imgplot

        rightplot = Plot(self.plotdata, width=150, resizable="v",
                         padding=0, use_backbuffer=False)
        imgplot = rightplot.img_plot("yz", xbounds=model.zs, ybounds=model.ys,
                                     colormap=jet)[0]
        imgplot.tools.append(ImageIndexTool(imgplot, callback=lambda i,j: self._index_callback("yz", i, j)))
        self.right = imgplot

        bottomplot = Plot(self.plotdata, height=150, resizable="h", padding=0, use_backbuffer=False)
        imgplot = bottomplot.img_plot("xz", xbounds=model.xs, ybounds=model.zs,
                                      colormap=jet)[0]
        imgplot.tools.append(ImageIndexTool(imgplot, callback=lambda i,j: self._index_callback("xz", i, j)))
        self.bottom = imgplot

        container = GridPlotContainer(padding=20, fill_padding=True,
                                      bgcolor="white", use_backbuffer=False,
                                      shape=(2,2), spacing=(12,12))

        container.add(centerplot)
        container.add(rightplot)
        container.add(bottomplot)

        self.centerplot = centerplot
        self.rightplot = rightplot
        self.bottomplot = bottomplot
        self.container = container
        return Window(self, -1, component=container)

        
    def _update_images(self):
        """ Updates the image data in self.plotdata to correspond to the 
        slices given.
        """
        cube = self.model.vals
        pd = self.plotdata
        pd.set_data("xy", cube[:, :, self.slice_z].T)
        pd.set_data("xz", cube[:, self.slice_y, :].T)
        pd.set_data("yz", cube[self.slice_x, :, :])



if __name__ == "__main__":
    demo_main(PlotFrame, size=(800,700), title="Cube analyzer")

