
from numpy import linspace
from scipy.special import jn

from enthought.tvtk.api import tvtk
from enthought.mayavi import mlab
from enthought.enable.vtk_backend.vtk_window import EnableVTKWindow
from enthought.chaco.api import ArrayPlotData, Plot
from enthought.chaco.tools.api import PanTool, ZoomTool

def main():
    # Create some x-y data series to plot
    x = linspace(-2.0, 10.0, 100)
    pd = ArrayPlotData(index = x)
    for i in range(5):
        pd.set_data("y" + str(i), jn(i,x))

    # Create some line plots of some of the data
    plot = Plot(pd, padding=30, border_visible=True, 
                 overlay_border=True, use_backbuffer=False)
    plot.legend.visible = True
    plot.plot(("index", "y0", "y1", "y2"), name="j_n, n<3", color="auto")
    plot.plot(("index", "y3"), name="j_3", color="auto")
    plot.tools.append(PanTool(plot))
    zoom = ZoomTool(component=plot, tool_mode="box", always_on=False)
    plot.overlays.append(zoom)

    # Create the mlab test mesh and get references to various parts of the
    # VTK pipeline
    m = mlab.test_mesh()
    scene = mlab.gcf().scene
    render_window = scene.render_window
    renderer = scene.renderer
    rwi = scene.interactor

    # Create the Enable Window
    window = EnableVTKWindow(rwi, renderer, 
            component=plot,
            #istyle_class = tvtk.InteractorStyleSwitch,
            istyle_class = tvtk.InteractorStyle,
            resizable = "",
            bounds = [200, 200],
            padding_top = 20,
            padding_bottom = 20,
            padding_left = 20,
            )

    #rwi.render()
    #rwi.start()
    mlab.show()
    return window, render_window

if __name__=="__main__":
    main()

