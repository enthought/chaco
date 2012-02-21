""" An example of how to use Chaco to render a visual Traits UI editor.
This particular editor allows the user to set two endpoints of an
interval.
"""

# FIXME: WX-only, and broken even there.

from __future__ import with_statement

# Force WX
from traits.etsconfig.api import ETSConfig
ETSConfig.toolkit = 'wx'

from traitsui.editor_factory import EditorFactory
from traitsui.wx.editor import Editor

from enable.window import Window
from enable.api import ColorTrait

from chaco.api import OverlayPlotContainer, create_line_plot, \
     LinePlot
from chaco.tools.api import RangeSelection, RangeSelectionOverlay

from traits.api import Int, TraitType, Instance, Float

from math import pi


class Interval(TraitType):
    """Trait that represents an interval.

    """
    info_text = "an interval (x,y) where x < y"

    def __init__(self, low=0, high=1, **metadata):
        value = (low, high)
        TraitType.__init__(self, value, **metadata)
        self.value = (low, high)

    def validate(self, object, name, value):
        low, high = value

        if low <= high:
            return value

        self.error(object, name, value)

    def create_editor(self):
        return IntervalEditor()


class IntervalEditorFactory(EditorFactory):
    width = Int(300)
    height = Int(40)

    def simple_editor(self, ui, object, name, description, parent):
        trait = object.trait(name).trait_type
        low, high = trait.value
        return IntervalEditorImpl(parent, factory=self, ui=ui,
                                  object=object, name=name,
                                  description=description,
                                  low=low,
                                  high=high)

class RangeKnobsOverlay(RangeSelectionOverlay):
    radius = Float(3)
    low_color = ColorTrait("red")
    high_color = ColorTrait("red")

    # Override the default alpha and border color, inherited from
    # RangeSelectionOverlay; these are more appropriate for our application.
    alpha = Float(0.8)
    border_color = ColorTrait("black")

    def overlay(self, component, gc, view_bounds=None, mode="normal"):
        mid_y = component.position[1] + component.bounds[1]/2
        # Draw each of a possibly disjoint set of selections
        coords = self._get_selection_screencoords()
        for coord in coords:
            start, end = coord
            with gc:
                gc.set_alpha(self.alpha)
                gc.set_stroke_color(self.border_color_)
                gc.set_line_width(self.border_width)

                gc.rect(start + self.radius, mid_y - 1,
                        (end - start - 2*self.radius), 2)
                gc.draw_path()

                gc.set_fill_color(self.low_color_)
                self._circle(gc, start, mid_y, self.radius)
                # Have to stroke/fill the path before we change out the
                # fill color
                gc.draw_path()

                gc.set_fill_color(self.high_color_)
                self._circle(gc, end, mid_y, self.radius)
                gc.draw_path()

    def _circle(self, gc, x, y, radius):
        with gc:
            gc.translate_ctm(x, y)
            gc.arc(0, 0, 2*radius, 0, 2*pi)


class IntervalEditorImpl(Editor):
    low = Int
    high = Int
    plot = Instance(LinePlot)

    def init(self, parent):
        factory = self.factory
        container = OverlayPlotContainer(bgcolor='transparent',
                                         padding=0, spacing=0)

        window = Window(parent, component=container)

        interval = self.high - self.low
        data = ([self.low, self.high], [0.5]*2)
        plot = create_line_plot(data, color='black', bgcolor="sys_window")
        plot.x_mapper.range.low = self.low - interval*0.1
        plot.x_mapper.range.high = self.high + interval*0.1
        plot.y_mapper.range.high = 1.0
        plot.y_mapper.range.low = 0.0

        range_selection = RangeSelection(plot, left_button_selects=True)
        # Do not allow the user to reset the range
        range_selection.event_state = "selected"
        range_selection.deselect = lambda x: None
        range_selection.on_trait_change(self.update_interval, 'selection')

        plot.tools.append(range_selection)
        plot.overlays.append(RangeKnobsOverlay(plot))
        self.plot = plot
        container.add(self.plot)

        # To set the low and high, we're actually going to set the
        # 'selection' metadata on the line plot to the tuple (low,high).
        plot.index.metadata["selections"] = (0, 1.0)

        # Tell the editor what to display
        self.control = window.control
        self.control.SetSize((factory.width, factory.height))

    def update_interval(self, value):
        low, high = value

        low = max(low, 0)
        high = min(high, 1)

        self.plot.index.metadata['selections'] = (low, high)
        self.value = (low, high)

    def update_editor(self):
        pass

# The user normally uses the factory as if it were an editor, e.g.:
#
#   View(Item('interval', editor=IntervalEditor()))
#
IntervalEditor = IntervalEditorFactory



# --- Demonstration ---

if __name__ == "__main__":
    from traits.api import HasTraits
    from traitsui.api import View, Item
    class IntervalTest(HasTraits):
        interval = Interval(low=0, high=1)

        traits_view = View(Item('interval',
                                editor=IntervalEditor()
                                ),
                           resizable=True)

    it = IntervalTest()
    it.configure_traits()
