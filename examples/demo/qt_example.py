"""
Example of how to directly embed Chaco into Qt widgets.

The actual plot being created is drawn from the basic/line_plot1.py code.
"""
from traits.etsconfig.etsconfig import ETSConfig
ETSConfig.toolkit = "qt4"

from numpy import linspace
from scipy.special import jn
from pyface.qt import QtGui
from pyface.util.guisupport import get_app_qt4, start_event_loop_qt4

from enable.api import Window

from chaco.api import ArrayPlotData, Plot
from chaco.tools.api import PanTool, ZoomTool


def create_chaco_plot(parent):
    x = linspace(-2.0, 10.0, 100)
    pd = ArrayPlotData(index = x)
    for i in range(5):
        pd.set_data("y" + str(i), jn(i,x))

    # Create some line plots of some of the data
    plot = Plot(pd, title="Line Plot", padding=50, border_visible=True)
    plot.legend.visible = True
    plot.plot(("index", "y0", "y1", "y2"), name="j_n, n<3", color="red")
    plot.plot(("index", "y3"), name="j_3", color="blue")

    # Attach some tools to the plot
    plot.tools.append(PanTool(plot))
    zoom = ZoomTool(component=plot, tool_mode="box", always_on=False)
    plot.overlays.append(zoom)

    # This Window object bridges the Enable and Qt4 worlds, and handles events
    # and drawing.  We can create whatever hierarchy of nested containers we
    # want, as long as the top-level item gets set as the .component attribute
    # of a Window.
    return Window(parent, -1, component=plot)


def main():
    app = get_app_qt4()
    main_window = QtGui.QMainWindow()
    main_window.resize(500,500)

    enable_window = create_chaco_plot(main_window)

    # The .control attribute references a QWidget that gives Chaco events
    # and that Chaco paints into.
    main_window.setCentralWidget(enable_window.control)

    main_window.show()
    start_event_loop_qt4(app)
    return main_window


if __name__ == "__main__":
    # Save window so that it doesn't get garbage collected when run within
    # existing event loop (i.e. from ipython).
    window = main()
