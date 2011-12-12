import math

from chaco.api import Plot
from chaco.text_box_overlay import TextBoxOverlay
from enable.api import ComponentEditor
from traits.api import HasTraits, DelegatesTo, Instance, on_trait_change
from traitsui.api import View, Item, HGroup, RangeEditor

class TextBoxOverlayExample(HasTraits):

    text_label = DelegatesTo('_overlay', 'text')
    rotate_angle = DelegatesTo('_overlay', 'rotate_angle')

    _plot = Instance(Plot)
    _overlay = Instance(TextBoxOverlay)

    def __overlay_default(self):

        overlay = TextBoxOverlay(text='Hello World!')

        return overlay

    def __plot_default(self):

        plot = Plot()

        plot.overlays.append(self._overlay)

        return plot

    traits_view = View(
        Item('_plot', editor=ComponentEditor(), show_label=False),
        HGroup(
            Item('text_label'),
            Item('rotate_angle', editor=RangeEditor(low=0, high=360))
        ),
        title = 'Example of TextBoxOverlay'
    )

    @on_trait_change('text_label,rotate_angle')
    def _refresh_overlay(self):
        print ' Updates'
        self._overlay.request_redraw()
        self._plot.request_redraw()

if __name__ == '__main__':
    
    example = TextBoxOverlayExample(rotate_angle=0.)
    example.configure_traits()

