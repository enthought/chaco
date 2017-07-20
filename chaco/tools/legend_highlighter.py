import operator

import six
import six.moves as sm

# ETS imports
from chaco.tools.api import LegendTool
from traits.api import List, Float


def get_hit_plots(legend, event):
    if legend is None or not legend.is_in(event.x, event.y):
        return []

    try:
        # FIXME: The size of the legend is not being computed correctly, so
        # always look at the front of the label where we know we'll get a hit.
        label = legend.get_label_at(legend.x + 20, event.y)

    except:
        raise
        label = None

    if label is None:
        return []
    try:
        ndx = legend._cached_labels.index(label)
        label_name = legend._cached_label_names[ndx]
        renderers = legend.plots[label_name]
        return renderers
    except (ValueError, KeyError):
        return []


class LegendHighlighter(LegendTool):
    """ A tool for legends that allows clicking on the legend to show
    or hide certain plots.
    """

    #: Which mousebutton to use to move the legend
    drag_button = "right"

    #: What to divide the alpha value by when plot is not selected
    dim_factor = Float(3.0)

    #: How much to scale the line when it is selected or deselected
    line_scale = Float(2.0)

    # The currently selected renderers
    _selected_renderers = List

    def normal_left_down(self, event):
        if not self.component.is_in(event.x, event.y):
            return

        plots = get_hit_plots(self.component, event)

        if len(plots) > 0:
            plot = plots[0]

            if event.shift_down:
                # User in multi-select mode by using [shift] key.
                if plot in self._selected_renderers:
                    self._selected_renderers.remove(plot)
                else:
                    self._selected_renderers.append(plot)

            else:
                # User in single-select mode.
                add_plot = plot not in self._selected_renderers
                self._selected_renderers = []
                if add_plot:
                    self._selected_renderers.append(plot)

            if self._selected_renderers:
                self._set_states(self.component.plots)
            else:
                self._reset_selects(self.component.plots)
            plot.request_redraw()

        event.handled = True

    def _reset_selects(self, plots):
        """ Set all renderers to their default values. """
        for plot in sm.reduce(operator.add, six.itervalues(plots)):
            if not hasattr(plot, '_orig_alpha'):
                plot._orig_alpha = plot.alpha
                plot._orig_line_width = plot.line_width
            plot.alpha = plot._orig_alpha
            plot.line_width = plot._orig_line_width
        return

    def _set_states(self, plots):
        """ Decorates a plot to indicate it is selected """
        for plot in sm.reduce(operator.add, six.itervalues(plots)):
            if not hasattr(plot, '_orig_alpha'):
                # FIXME: These attributes should be put into the class def.
                plot._orig_alpha = plot.alpha
                plot._orig_line_width = plot.line_width
            if plot in self._selected_renderers:
                plot.line_width = plot._orig_line_width * self.line_scale
                plot.alpha = plot._orig_alpha
            else:
                plot.alpha = plot._orig_alpha / self.dim_factor
                plot.line_width = plot._orig_line_width / self.line_scale
        # Move the selected renderers to the front
        if len(self._selected_renderers) > 0:
            container = self._selected_renderers[0].container
            components = container.components[:]
            for renderer in self._selected_renderers:
                components.remove(renderer)
            components += self._selected_renderers
            container._components = components
