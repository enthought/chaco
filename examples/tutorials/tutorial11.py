"""Tutorial 11: Demonstration of index and value.

We are going to change the orientation of the right_plot, but all of our
dataspace linking will still work. This is why it's good to work with index and
value instead of hardcoding to X and Y. We'll also add another LineInspector to
each plot to form a full crosshair.
"""

from enthought.chaco.tools.api import LineInspector

from tutorial10b import PlotExample3


class PlotExample4(PlotExample3):
    def _container_default(self):
        container = super(PlotExample4, self)._container_default()

        rplot, lplot = self.right_plot, self.left_plot
        rplot.orientation = "v"
        rplot.hgrid.mapper = rplot.index_mapper
        rplot.vgrid.mapper = rplot.value_mapper
        rplot.y_axis.mapper = rplot.index_mapper
        rplot.x_axis.mapper = rplot.value_mapper


        lplot.overlays.append(LineInspector(component=lplot,
             axis="value", write_metadata=True, is_listener=True, color="blue"))
        lplot.overlays.append(LineInspector(component=lplot,
             axis="value", write_metadata=True, is_listener=True, color="blue"))

        rplot.overlays.append(LineInspector(component=rplot,
             axis="value", write_metadata=True, is_listener=True, color="blue"))
        rplot.overlays.append(LineInspector(component=rplot,
             axis="value", write_metadata=True, is_listener=True, color="blue"))

        return container


demo = PlotExample4()

if __name__ == "__main__":
    demo.configure_traits()
