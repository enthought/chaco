
from numpy import linspace
from scipy.special import jn

from enthought.tvtk.api import tvtk
from enthought.mayavi import mlab
from enthought.enable.vtk_backend.vtk_window import EnableVTKWindow
from enthought.chaco.api import ArrayPlotData, Plot, OverlayPlotContainer
from enthought.chaco.tools.api import PanTool, ZoomTool, MoveTool

def main():
    # Create some x-y data series to plot
    x = linspace(-2.0, 10.0, 100)
    pd = ArrayPlotData(index = x)
    for i in range(5):
        pd.set_data("y" + str(i), jn(i,x))

    # Create some line plots of some of the data
    plot = Plot(pd, bgcolor="none", padding=30, border_visible=True, 
                 overlay_border=True, use_backbuffer=False)
    plot.legend.visible = True
    plot.plot(("index", "y0", "y1", "y2"), name="j_n, n<3", color="auto")
    plot.plot(("index", "y3"), name="j_3", color="auto")
    plot.tools.append(PanTool(plot))
    zoom = ZoomTool(component=plot, tool_mode="box", always_on=False)
    plot.overlays.append(zoom)

    # Create the mlab test mesh and get references to various parts of the
    # VTK pipeline
    f = mlab.figure(size=(600,500))
    m = mlab.test_mesh()
    scene = mlab.gcf().scene
    render_window = scene.render_window
    renderer = scene.renderer
    rwi = scene.interactor

    plot.resizable = ""
    plot.bounds = [200,200]
    plot.padding = 25
    plot.outer_position = [30,30]
    plot.tools.append(MoveTool(component=plot,drag_button="right"))

    container = OverlayPlotContainer(bgcolor = "transparent",
                    fit_window = True)
    container.add(plot)

    # Create the Enable Window
    window = EnableVTKWindow(rwi, renderer, 
            component=container,
            #istyle_class = tvtk.InteractorStyleSwitch,
            #istyle_class = tvtk.InteractorStyle,
            istyle_class = tvtk.InteractorStyleTrackballCamera, 
            bgcolor = "transparent",
            event_passthrough = True,
            )

    mlab.show()
    return window, render_window

if __name__=="__main__":
    main()

