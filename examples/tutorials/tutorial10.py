"""Tutorial 10. Demonstration that the views are linked, but the data is not."""


from chaco.tools.api import LineInspector

from tutorial9b import PlotExample2


class PlotExample3(PlotExample2):
    def _container_default(self):
        container = super(PlotExample3, self)._container_default()

        rplot, lplot = self.right_plot, self.left_plot
        lplot.overlays.append(LineInspector(component=lplot,
                write_metadata=True, is_listener=True))
        rplot.overlays.append(LineInspector(component=rplot,
                write_metadata=True, is_listener=True))

        return container

demo = PlotExample3()

if __name__ == "__main__":
    demo.configure_traits()
