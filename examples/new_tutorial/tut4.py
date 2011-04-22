#!/usr/bin/env python
#
# This tutorial shows how to use the ScatterInspector tool to interact with
# data in a plot.

from chaco.tools.api import *

from tut3 import Tut3Frame

class Tut4Frame(Tut3Frame):

    def make_plot(self):

        # We'll use the same pattern as in the previous examples: we just
        # extend the functionality of the make_plot() method in Tutorial 3
        # (tut3.py).
        container = Tut3Frame.make_plot(self)

        # Before we return the container, though, we'll modify some of its
        # contents.
        plot1, plot2 = container.components
        self.plot1 = plot1
        self.plot2 = plot2

        # Plots are automatically assigned names when they are created.  Since
        # plot2 only has one sub-plot on it, that subplot is named "plot0".  The
        # scatter renderer is the first (and only) renderer in the subplot, so
        # we get to it using [0].
        scatter = plot2.plots["plot0"][0]
        scatter.tools.append(ScatterInspector(scatter))

        # The ScatterInspector will modify the metadata of the underlying
        # datasource, which will cause a trait event to fire.  So, we'll hook
        # up a listener to that event.
        plot2.datasources["x"].on_trait_event(self.handler, "metadata_changed")

        return container

    def handler(self):
        # This handler method will get called every time the metadata of the
        # "x" datasource on self.plot2 gets updated.  We'll just dump out the
        # contents of that metadata to screen.  In this case, it is the index
        # of the point directly under the mouse, and the index of the last
        # point the mouse clicked on (indicated by "selection").
        metadata = self.plot2.datasources["x"].metadata
        print "Hover:", metadata["hover"]
        if "selection" in metadata:
            print "Selected:", metadata["selection"]


if __name__ == "__main__":
    import wx
    app = wx.PySimpleApp()
    frame = Tut4Frame(None, size=(1000,500))
    app.MainLoop()
