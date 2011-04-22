#!/usr/bin/env python
#
#
# Tutorial 11.  Demonstration of why it's good to work with .index and
#               .value instead of hardcoding to X and Y.
#
# We are going to change the orientation of the right_plot,
# but all of our dataspace linking will still work.  We'll also
# add another LineInspector to each plot to form a full crosshair.


from tutorial10b import PlotFrame3
from chaco.tools.api import LineInspector

class PlotFrame4(PlotFrame3):
    def _create_plot(self):
        container = super(PlotFrame4, self)._create_plot()

        plot = self.right_plot
        plot.orientation = "v"
        plot.hgrid.mapper = plot.index_mapper
        plot.vgrid.mapper = plot.value_mapper
        plot.y_axis.mapper = plot.index_mapper
        plot.x_axis.mapper = plot.value_mapper

        self.left_plot.overlays.append(LineInspector(component=self.left_plot,
                axis="value", write_metadata=True, is_listener=True, color="blue"))

        self.right_plot.overlays.append(LineInspector(component=self.right_plot,
                axis="value", write_metadata=True, is_listener=True, color="blue"))
        return container

if __name__ == "__main__":
    import wx
    app = wx.PySimpleApp()
    frame = PlotFrame4(None)
    app.MainLoop()
