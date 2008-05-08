"""
A Demonstration of the CursorTool functionality
"""

from enthought.chaco2.api import create_line_plot, OverlayPlotContainer,\
             PlotComponent, HPlotContainer, Plot, ArrayPlotData, jet
from enthought.chaco2.chaco2_plot_container_editor import PlotContainerEditor
from enthought.chaco2.tools.api import PanTool, SimpleZoom
from enthought.chaco2.tools.cursor_tool import CursorTool, BaseCursorTool
from enthought.traits.api import HasTraits, Instance, DelegatesTo, Delegate
from enthought.traits.ui.api import View, Item, HGroup
import numpy

class CursorTest(HasTraits):
    plot = Instance(PlotComponent)
    cursor1 = Instance(BaseCursorTool)
    cursor2 = Instance(BaseCursorTool)
    
    #these don't update in the View. Why not?
    cursoridx1 = DelegatesTo('cursor1', prefix='current_index')
    cursoridx2 = DelegatesTo('cursor2', prefix='current_index')
    
    def __init__(self):
        container = HPlotContainer(padding=0, spacing=20)
        self.plot = container
        #a subcontainer for the first plot. I'm not sure why this is required
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
        
        def onchange():
            print csr.current_index, self.cursoridx1
        csr.on_trait_change(onchange, name='current_position')
        
        #this is a rendered component so it goes in the overlays list
        line.overlays.append(csr)
        
        #some other standard tools
        line.tools.append(PanTool(line, drag_button="right"))
        line.overlays.append(SimpleZoom(line))
        
        #make some 2D data for a colourmap plot
        x = numpy.linspace(-5,5,100)
        y = numpy.linspace(-5,5,100)
        X,Y = numpy.meshgrid(x, y)
        Z = numpy.sin(X)*numpy.arctan2(Y,X)
        
        #easiest way to get a CMapImagePlot is to use the Plot class
        ds = ArrayPlotData()
        ds.set_data('img', Z)
        
        img = Plot(ds, padding=40)
        cmapImgPlot = img.img_plot("img",
                     xbounds = x,
                     ybounds = y,
                     colormap = jet)[0]
        
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
        cmapImgPlot.overlays.append(SimpleZoom(cmapImgPlot))

        
    traits_view = View(Item('plot',
                            editor=PlotContainerEditor()),
                        HGroup(Item('cursoridx1', width=300),
                               Item('cursoridx2', width=300)),
                        resizable=True,
                        width=800,
                        height=400)
    
test = CursorTest()
test.configure_traits()

