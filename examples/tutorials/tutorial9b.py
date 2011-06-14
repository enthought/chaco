"""Tutorial 9b. Synchronize the Y data space as well,and add some tools."""


from chaco.tools.api import ZoomTool

from tutorial8 import PlotExample


class PlotExample2(PlotExample):
    def _container_default(self):
        container = super(PlotExample2, self)._container_default()

        rplot, lplot = self.right_plot, self.left_plot
        rplot.index_mapper.range = lplot.index_mapper.range
        rplot.value_mapper.range = lplot.value_mapper.range

        lplot.overlays.append(ZoomTool(lplot, tool_mode="box",always_on=False))
        rplot.overlays.append(ZoomTool(rplot, tool_mode="box",always_on=False))

        return container

demo = PlotExample2()

if __name__ == "__main__":
    demo.configure_traits()
