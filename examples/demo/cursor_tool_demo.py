"""
Cursor tool

A cursor tool lets you drag vertical and horizontal lines whose intersection
defines one point on the plot.

Left-button drag to move the cursors round.

Right-drag to pan the plots. 'z'-key to Zoom

"""
# Major library imports
import numpy

# Enthought library imports
from chaco.api import create_line_plot, OverlayPlotContainer, \
             HPlotContainer, Plot, ArrayPlotData, viridis
from chaco.tools.api import PanTool, ZoomTool
from chaco.tools.cursor_tool import CursorTool, BaseCursorTool
from enable.component_editor import ComponentEditor
from traits.api import HasTraits, Instance, DelegatesTo
from traitsui.api import View, Item, HGroup, VGroup


class CursorTest(HasTraits):
    plot = Instance(HPlotContainer)
    cursor1 = Instance(BaseCursorTool)
    cursor2 = Instance(BaseCursorTool)

    cursor1pos = DelegatesTo('cursor1', prefix='current_position')
    cursor2pos = DelegatesTo('cursor2', prefix='current_position')

    def __init__(self):
        #The delegates views don't work unless we caller the superclass __init__
        super(CursorTest, self).__init__()

        container = HPlotContainer(padding=0, spacing=20)
        self.plot = container
        #a subcontainer for the first plot.
        #I'm not sure why this is required. Without it, the layout doesn't work right.
        subcontainer = OverlayPlotContainer(padding=40)
        container.add(subcontainer)

        #make some data
        index = numpy.linspace(-10,10,512)
        value = numpy.sin(index)

        #create a LinePlot instance and add it to the subcontainer
        line = create_line_plot([index, value], add_grid=True,
                                add_axis=True, index_sort='ascending',
                                orientation = 'h')
        subcontainer.add(line)

        #here's our first cursor.
        csr = CursorTool(line,
                        drag_button="left",
                        color='blue')
        self.cursor1 = csr
        #and set it's initial position (in data-space units)
        csr.current_position = 0.0, 0.0

        #this is a rendered component so it goes in the overlays list
        line.overlays.append(csr)

        #some other standard tools
        line.tools.append(PanTool(line, drag_button="right"))
        line.overlays.append(ZoomTool(line))

        #make some 2D data for a colourmap plot
        xy_range = (-5, 5)
        x = numpy.linspace(xy_range[0], xy_range[1] ,100)
        y = numpy.linspace(xy_range[0], xy_range[1] ,100)
        X,Y = numpy.meshgrid(x, y)
        Z = numpy.sin(X)*numpy.arctan2(Y,X)

        #easiest way to get a CMapImagePlot is to use the Plot class
        ds = ArrayPlotData()
        ds.set_data('img', Z)

        img = Plot(ds, padding=40)
        cmapImgPlot = img.img_plot("img",
                     xbounds = xy_range,
                     ybounds = xy_range,
                     colormap = viridis)[0]

        container.add(img)

        #now make another cursor
        csr2 = CursorTool(cmapImgPlot,
                           drag_button='left',
                           color='white',
                           line_width=2.0
                           )
        self.cursor2 = csr2

        csr2.current_position = 1.0, 1.5

        cmapImgPlot.overlays.append(csr2)

        #add some standard tools. Note, I'm assigning the PanTool to the
        #right mouse-button to avoid conflicting with the cursors
        cmapImgPlot.tools.append(PanTool(cmapImgPlot, drag_button="right"))
        cmapImgPlot.overlays.append(ZoomTool(cmapImgPlot))


    traits_view = View(VGroup(
                            HGroup(Item('plot',
                                        editor=ComponentEditor(),
                                        resizable=True, springy=True,
                                        show_label=False),
                                        springy=True),
                            HGroup(Item('cursor1pos', width=300),
                                   Item('cursor2pos', width=300))),
                        title="Cursor Tool Demo",
                        resizable=True,
                        width=800,
                        height=420)

#===============================================================================
# # demo object that is used by the demo.py application.
#===============================================================================
demo = CursorTest()

if __name__=='__main__':
    demo.configure_traits()

