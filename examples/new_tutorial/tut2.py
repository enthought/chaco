#!/usr/bin/env python
#
# This example extends the plot from example 1 to show how to put two
# plots side-by-side.  We will also add tools to make the plots interactive.

from numpy import *
from enthought.chaco.api import *
from enthought.chaco.tools.api import *
from scipy.special import jn

from tut1 import PlotFrame

class Tut2Frame(PlotFrame):
    def make_plot(self):
        x = linspace(-2*pi, 2*pi, 200)
        y1 = jn(0, x)
        y2 = jn(1, x)
        y3 = jn(2, x)
        pd = ArrayPlotData(x=x, y1=y1, y2=y2, y3=y3)

        plot1 = Plot(pd)
        plot1.plot(("x", "y1"), type="line", color="red")
        plot1.plot(("x", "y2"), type="scatter", color="blue")
        plot1.tools.append(PanTool(plot1))
        plot1.overlays.append(ZoomTool(plot1))

        plot2 = Plot(pd)
        plot2.plot(("x", "y3"), type="scatter", color="purple")
        plot2.tools.append(PanTool(plot2))
        plot2.overlays.append(ZoomTool(plot2))

        c = HPlotContainer()
        c.add(plot1, plot2)
        return c

if __name__ == "__main__":
    import wx
    app = wx.PySimpleApp()
    frame = Tut2Frame(None, size=(1000,500))
    app.MainLoop()

