
from numpy import array

from enthought.enable2.api import white_color_trait
from enthought.kiva import STROKE, font_metrics_provider
from enthought.kiva.traits.kiva_font_trait import KivaFont
from enthought.traits.api import Any, Dict, Enum, false, HasTraits, Int, \
                                 Instance, List, true, Trait

# Local relative imports
from abstract_overlay import AbstractOverlay
from label import Label
from lineplot import LinePlot
from plot_component import PlotComponent
from scatterplot import ScatterPlot


class AbstractCompositeIconRenderer(HasTraits):

    def render_icon(self, plots, gc, x, y, width, height):
        """ Render an icon representing the given list of plots onto the
        GC, using the given dimensions and at the specified position.
        """
        raise NotImplementedError



class CompositeIconRenderer(AbstractCompositeIconRenderer):

    def render_icon(self, plots, *render_args):
        """ Takes a list of plots and renders an icon for them """
        types = set(map(type, plots))
        if types == set([ScatterPlot]):
            self._render_scatterplots(plots, *render_args)
        elif types == set([LinePlot]):
            self._render_lineplots(plots, *render_args)
        elif types == set([ScatterPlot, LinePlot]):
            self._render_line_scatter(plots, *render_args)
        else:
            raise ValueError("Don't know how to render combination plot with " +\
                             "renderers " + str(types))
        return

    def _render_scatterplots(self, plots, gc, x, y, width, height):
        # Don't support this for now
        pass

    def _render_lineplots(self, plots, gc, x, y, width, height):
        # Assume they are all the same color/appearance and use the first one
        plots[0]._render_icon(gc, x, y, width, height)

    def _render_line_scatter(self, plots, gc, x, y, width, height):
        # Separate plots into line and scatter renderers; render one of each
        scatter = [p for p in plots if type(p) == ScatterPlot]
        line = [p for p in plots if type(p) == LinePlot]
        line[0]._render_icon(gc, x, y, width, height)
        scatter[0]._render_icon(gc, x, y, width, height)



class Legend(AbstractOverlay):

    # The font to use for the legend text
    font = KivaFont("modern 12")

    # The amount of space between the content of the legend and the border
    border_padding = Int(10)

    # Override the default border_visible setting (inherited from enable2.Component)
    border_visible = True

    # The background color of the legend
    bgcolor = white_color_trait

    # The position of the legend with respect to its overlaid component.  (Only
    # applies if the legend is used as an overlay.)
    #   ur = Upper Right
    #   ul = Upper Left
    #   ll = Lower Left
    #   lr = Lower Right
    align = Enum("ur", "ul", "ll", "lr")

    # The amount of space between each legend item
    line_spacing = Int(3)

    # The size of the icon/marker area drawn next to the label
    icon_bounds = List([24, 24])

    # Amount of spacing between each label and its icon
    icon_spacing = Int(5)

    # Maps labels (strings) to plot instances or lists of plot instances.  The
    # Legend determines the appropriate rendering of each plot's marker/line.
    plots = Dict

    # The list of labels to show and the order to show them in.  If this
    # list is blank, then the keys of self.plots is used and displayed in
    # alphabetical order.  Otherwise, only the items in the "labels"
    # list are down in the legend.  Labels are ordered from top to bottom.
    labels = List

    # This function takes a list of plot instances and returns a _render_icon()
    # function/icon.  This function should have the same signature as
    # AbstractPlotRenderer._render_icon().
    composite_icon_renderer = Instance(AbstractCompositeIconRenderer)

    # When the legend encounters a plot whose icon it cannot render, should it:
    #   - skip it altogether and not render its name
    #   - render the name but leave the icon blank (color=self.bgcolor)
    #   - render a "question mark" icon
    error_icon = Enum("skip", "blank", "questionmark")

    # Override the default value of this trait.
    # TODO: Make this work when the legend is standalone, by setting this
    # to "hv", then having the Legend manually reset its bounds and position
    # from the container-given bounds, using the 'align' setting.
    resizable = ""

    unified_draw = True
    draw_layer = "overlay"

    #------------------------------------------------------------------------
    # Private Traits
    #------------------------------------------------------------------------

    # A list of Label instances
    _cached_labels = List

    _cached_label_sizes = Any

    _cached_label_names = List


    def overlay(self, component, gc, view_bounds=None, mode="normal"):
        self.do_layout()
        valign, halign = self.align
        if valign == "u":
            y = component.y2 - self.outer_height
        else:
            y = component.y
        if halign == "r":
            x = component.x2 - self.outer_width
        else:
            x = component.x
        self.outer_position = [x, y]
        PlotComponent._draw(self, gc, view_bounds, mode)
        return


    def _draw_overlay(self, gc, view_bounds=None, mode="normal"):
        # Determine the position we are going to draw at from our alignment
        # corner and the corresponding outer_padding parameters.  (Position
        # refers to the lower-left corner of our border.)

        # First draw the border, if necesssary.  This sort of duplicates
        # the code in PlotComponent._draw_overlay, which is unfortunate;
        # on the other hand, overlays of overlays seem like a rather obscure
        # feature.

        gc.save_state()
        try:

            edge_space = self.border_width + self.border_padding
            icon_width, icon_height = self.icon_bounds

            icon_x = self.x + edge_space
            text_x = icon_x + icon_width + self.icon_spacing
            y = self.y2 - edge_space

            for i, label_name in enumerate(self._cached_label_names):
                # Compute the current label's position
                label_height = self._cached_label_sizes[i][1]
                y -= label_height

                # Try to render the icon
                icon_y = y + (label_height - icon_height) / 2
                plots = self.plots[label_name]
                render_args = (gc, icon_x, icon_y, icon_width, icon_height)

                try:
                    if isinstance(plots, list) or isinstance(plots, tuple):
                        if len(plots) == 1:
                            plots[0]._render_icon(*render_args)
                        else:
                            self.composite_icon_renderer.render_icon(plots, *render_args)
                    else:
                        # Single plot
                        plots._render_icon(*render_args)

                    icon_drawn = True
                except:
                    icon_drawn = self._render_error(*render_args)

                if icon_drawn:
                    # Render the text
                    gc.translate_ctm(text_x, y)
                    gc.set_antialias(0)
                    self._cached_labels[i].draw(gc)
                    gc.set_antialias(1)
                    gc.translate_ctm(-text_x, -y)

                    # Advance y to the next label's baseline
                    y -= self.line_spacing

        finally:
            gc.restore_state()

        return

    def _render_error(self, gc, icon_x, icon_y, icon_width, icon_height):
        """ Renders an error icon or performs some other action when a
        plot was unable to render its icon.  Returns True if something
        was actually drawn (and hence the legends needs to advance the line)
        or False if nothing was drawn.
        """
        if self.error_icon == "skip":
            return False
        elif self.error_icon == "blank" or self.error_icon == "questionmark":
            gc.save_state()
            gc.set_fill_color(self.bgcolor_)
            gc.rect(icon_x, icon_y, icon_width, icon_height)
            gc.fill_path()
            gc.restore_state()
            return True
        else:
            return False


    def _do_layout(self):
        """
        Computes the size and position of the legend based on the maximum size of
        the labels, the alignment, and position of the component to overlay.
        """

        # Gather the names of all the labels we will create
        label_names = self.labels
        if len(label_names) == 0:
            if len(self.plots) > 0:
                label_names = self.plots.keys()
                label_names.sort()
            else:
                self._cached_labels = []
                self._cached_label_sizes = []
                self._cached_label_names = []
                self.outer_bounds = [0, 0]
                return

        # Create the labels
        labels = [Label(text=text, font=self.font, margin=0, bgcolor="transparent",
                        border_width=0) for text in label_names]

        # We need a dummy GC in order to get font metrics
        dummy_gc = font_metrics_provider()
        label_sizes = array([label.get_width_height(dummy_gc) for label in labels])

        max_label_width = max(label_sizes[:, 0])
        total_label_height = sum(label_sizes[:, 1]) + (len(label_sizes)-1)*self.line_spacing

        legend_width = max_label_width + self.icon_spacing + self.icon_bounds[0] \
                        + self.hpadding + 2*self.border_padding
        legend_height = total_label_height + self.vpadding + 2*self.border_padding

        self.outer_bounds = [legend_width, legend_height]

        self._cached_labels = labels
        self._cached_label_sizes = label_sizes
        self._cached_label_names = label_names
        return

    def _composite_icon_renderer_default(self):
        return CompositeIconRenderer()

    def _anytrait_changed(self, name, old, new):
        if name in ("font", "border_padding", "padding", "line_spacing", "icon_bounds",
                    "icon_spacing", "labels", "plots", "plots_items", "labels_items",
                    "border_width", "align"):
            self._layout_needed = True
        return




# EOF
