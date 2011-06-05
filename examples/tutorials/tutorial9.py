"""Tutorial 9. Link the horizontal ranges of the two plots."""


from tutorial8 import PlotExample


class PlotExample2(PlotExample):
    def _container_default(self):
        container = super(PlotExample2, self)._container_default()

        rplot, lplot = self.right_plot, self.left_plot
        rplot.index_mapper.range = lplot.index_mapper.range
        lplot.value_mapper.range.low = min(rplot.value_mapper.range.low,
                                           lplot.value_mapper.range.low,)
        rplot.value_mapper.range = lplot.value_mapper.range

        return container

demo = PlotExample2()

if __name__ == "__main__":
    demo.configure_traits()
