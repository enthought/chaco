""" Defines the ColormappedSelectionOverlay class.
"""
import six.moves as sm

from numpy import logical_and

# Enthought library imports
from traits.api import Any, Bool, Float, Instance, Property, Enum

# Local imports
from .abstract_overlay import AbstractOverlay
from .colormapped_scatterplot import ColormappedScatterPlot

class ColormappedSelectionOverlay(AbstractOverlay):
    """
    Overlays and changes a ColormappedScatterPlot to fade its non-selected
    points to a very low alpha.
    """

    # The ColormappedScatterPlot that this overlay is listening to.
    # By default, it looks at self.component
    plot = Property

    # The amount to fade the unselected points.
    fade_alpha = Float(0.15)

    # The minimum difference, in float percent, between the starting and ending
    # selection values, if range selection mode is enabled
    minimum_delta = Float(0.01)

    # Outline width for selected points.
    selected_outline_width = Float(1.0)
    # Outline width for unselected points.
    unselected_outline_width = Float(0.0)

    # The type of selection used by the data source.
    selection_type = Enum('range', 'mask')

    _plot = Instance(ColormappedScatterPlot)

    _visible = Bool(False)

    _old_alpha = Float
    _old_outline_color = Any
    _old_line_width = Float(0.0)

    def __init__(self, component=None, **kw):
        super(ColormappedSelectionOverlay, self).__init__(**kw)
        self.component = component
        return

    def overlay(self, component, gc, view_bounds=None, mode="normal"):
        """ Draws this component overlaid on another component.

        Implements AbstractOverlay.
        """
        if not self._visible:
            return

        plot = self.plot
        datasource = plot.color_data

        if self.selection_type == 'range':
            selections = datasource.metadata["selections"]

            if selections is not None and len(selections) == 0:
                return

            low, high = selections
            if abs(high - low) / abs(high + low) < self.minimum_delta:
                return

            # Mask the data with just the points falling within the data
            # range selected on the colorbar
            data_pts = datasource.get_data()
            mask = (data_pts >= low) & (data_pts <= high)

        elif self.selection_type == 'mask':
            mask = sm.reduce(logical_and, datasource.metadata["selection_masks"])
            if sum(mask)<2:
                return

        datasource.set_mask(mask)

        # Store the current plot color settings before overwriting them
        fade_outline_color = plot.outline_color_

        # Overwrite marker outline color and fill alpha settings of
        # the plot, then manually invoke the plot to draw onto the GC.
        plot.outline_color = list(self._old_outline_color[:3]) + [1.0]
        plot.fill_alpha = 1.0
        plot.line_width = self.selected_outline_width
        plot._draw_plot(gc, view_bounds, mode)


        # Restore the plot's previous color settings and data mask.
        plot.fill_alpha = self.fade_alpha
        plot.outline_color = fade_outline_color
        plot.line_width = self.unselected_outline_width
        datasource.remove_mask()
        return

    def _component_changed(self, old, new):
        if old:
            old.on_trait_change(self.datasource_change_handler, "color_data", remove=True)
        if new:
            new.on_trait_change(self.datasource_change_handler, "color_data")
            self._old_alpha = new.fill_alpha
            self._old_outline_color = new.outline_color
            self._old_line_width = new.line_width
            self.datasource_change_handler(new, "color_data", None, new.color_data)
        return

    def datasource_change_handler(self, obj, name, old, new):
        if old:
            old.on_trait_change(self.selection_change_handler, "metadata_changed", remove=True)
        if new:
            new.on_trait_change(self.selection_change_handler, "metadata_changed")
            self.selection_change_handler(new, "metadata_changed", None, new.metadata)
        return

    def selection_change_handler(self, obj, name, old, new):
        if self.selection_type == 'range':
            selection_key = 'selections'
        elif self.selection_type == 'mask':
            selection_key = 'selection_masks'

        if type(new) == dict and new.get(selection_key, None) is not None \
                             and len(new[selection_key]) > 0:
            if not self._visible:
                # We have a new selection, so replace the colors on the plot with the
                # faded alpha and colors
                plot = self.plot

                # Save the line width and set it to zero for the unselected points
                self._old_line_width = plot.line_width
                plot.line_width = self.unselected_outline_width
                # Save the outline color and set it to the faded version
                self._old_outline_color = plot.outline_color_
                outline_color = list(plot.outline_color_)
                if len(outline_color) == 3:
                    outline_color += [self.fade_alpha]
                else:
                    outline_color[3] = self.fade_alpha
                plot.outline_color = outline_color

                # Save the alpha value and set it to a faded version
                self._old_alpha = plot.fill_alpha
                plot.fill_alpha = self.fade_alpha

            self.plot.invalidate_draw()
            self._visible = True
        else:
            self.plot.fill_alpha = self._old_alpha
            self.plot.outline_color = self._old_outline_color
            self.plot.line_width = self._old_line_width
            self.plot.invalidate_draw()
            self._visible = False

        self.plot.request_redraw()
        return

    def _get_plot(self):
        if self._plot is not None:
            return self._plot
        else:
            return self.component

    def _set_plot(self, val):
        self._plot = val


# EOF
