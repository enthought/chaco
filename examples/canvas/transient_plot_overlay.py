

from enthought.traits.api import Enum, Float, Instance, Trait, Tuple

from enthought.chaco2.api import AbstractOverlay, PlotComponent, BasePlotContainer

class TransientPlotOverlay(BasePlotContainer, AbstractOverlay):
    """ Allows an arbitrary plot component to be overlaid on top of another one.
    """
    
    # The PlotComponent to draw as an overlay
    overlay_component = Instance(PlotComponent)

    # Where this overlay should draw relative to our .component
    align = Enum("right", "left", "top", "bottom")

    # The amount of space between the overlaying component and the underlying
    # one.  This is either horizontal or vertical (depending on the value of
    # self.align), but is not both.
    margin = Float(10)

    # An offset to apply in X and Y
    offset = Trait(None, None, Tuple)

    # Override default values of some inherited traits
    unified_draw = True

    def _bounds_default(self):
        return [350, 150]

    def overlay(self, component, gc, view_bounds=None, mode="normal"):
        self._do_layout()
        gc.save_state()
        gc.clear_clip_path()
        self.overlay_component._draw(gc, view_bounds, mode)
        gc.restore_state()

    def _do_layout(self):
        component = self.component
        bounds = self.outer_bounds

        if self.align in ("right", "left"):
            y = component.outer_y -(bounds[1] - component.outer_height) / 2
            if self.align == "right":
                x = component.outer_x2 + self.margin
            else:
                x = component.outer_x - bounds[0] - self.margin

        else:   # "top", "bottom"
            x = component.outer_x -(bounds[0] - component.outer_width) / 2
            if self.align == "top":
                y = component.outer_y2 + self.margin
            else:
                y = component.outer_y - bounds[1] - self.margin
        
        if self.offset is not None:
            x += self.offset[0]
            y += self.offset[1]

        overlay_component = self.overlay_component
        overlay_component.outer_bounds = self.outer_bounds
        overlay_component.outer_position = [x, y]
        overlay_component._layout_needed = True
        overlay_component.do_layout()

    def dispatch(self, event, suffix):
        if self.visible and self.overlay_component.is_in(event.x, event.y):
            return self.overlay_component.dispatch(event, suffix)


