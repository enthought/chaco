from chaco.api import (ArrayPlotData, HPlotContainer, Plot)
from chaco.tools.api import RectangleSelection
from enable.api import ComponentEditor
from scipy.misc import face
from traits.api import (Any, Array, cached_property, HasTraits, Instance,
                        Property)
from traitsui.api import View, Item


class RectSelectionDemo(HasTraits):
    container = Instance(HPlotContainer)
    img = Array()
    img_plot = Instance(Plot)
    plot_data = Instance(ArrayPlotData())
    selection = Any()
    zoom_img = Property(Array, depends_on=['img', 'selection'])
    zoom_plot = Instance(Plot)

    def _container_default(self):
        img_plot = self.img_plot
        zoom_plot = self.zoom_plot
        container = HPlotContainer(img_plot, zoom_plot)
        return container

    @cached_property
    def _get_zoom_img(self):
        return self.img

    def _img_default(self):
        return face()

    def _img_plot_default(self):
        img_plot = Plot(self.plot_data)
        img_plot.img_plot("img",
                          origin="top left")
        rst = RectangleSelection(img_plot)
        img_plot.overlays.append(rst)
        self.selection = rst
        rst.on_trait_change(self.update_zoom, 'event_state')
        return img_plot

    def _plot_data_default(self):
        plot_data = ArrayPlotData(img=self.img,
                                  zoom_img=self.zoom_img)
        return plot_data

    def update_zoom(self):
        # selected box is in data space coordinates
        # by default data space is defined in number of array elements
        box = self.selection.selected_box
        height = self.img.shape[0]
        width = self.img.shape[1]
        if box is not ():
            # plot is displayed with the y-axis inverted, so we need to map
            # the 0-axis coordinates
            bottom = max(0, height - int(box[3]))
            top = min(height, height - int(box[2]))
            left = max(0, int(box[0]))
            right = min(width, int(box[1]))
            self.plot_data.set_data("zoom_img",
                                    self.img[bottom:top, left:right])
            self.zoom_plot.plot_components[0].index.set_data((left, right),
                                                             (bottom, top))

    def _zoom_plot_default(self):
        zoom_plot = Plot(self.plot_data)
        zoom_plot.img_plot("zoom_img",
                           origin="top left",)
        return zoom_plot

    default_traits_view = View(
        Item('container',
             editor=ComponentEditor(),
             show_label=False,
             width=800,),
        resizable=True,
        )


if __name__ == '__main__':
    rsd = RectSelectionDemo()
    rsd.configure_traits()
