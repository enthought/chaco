
from __future__ import with_statement

import os
import numpy

from chaco.api import GridMapper
from traits.api import Property, Enum, Str, cached_property

from status_layer import StatusLayer

class SvgRangeSelectionOverlay(StatusLayer):
    """ This is a primitive range selection overlay which uses
        a SVG to define the overlay.

        TODO: not inherit from StatusLayer, this was a convenience for a
            quick prototype

        TODO: use 2 svgs, one which defines the border and does not scale, and
            the other which defines the fill.
    """



    filename = os.path.join(os.path.dirname(__file__), 'data',
                                            'range_selection.svg')

    alpha = 0.5

    # The axis to which this tool is perpendicular.
    axis = Enum("index", "value")

    axis_index = Property(depends_on='axis')

    # Mapping from screen space to data space. By default, it is just
    # self.component.
    plot = Property(depends_on='component')

    # The mapper (and associated range) that drive this RangeSelectionOverlay.
    # By default, this is the mapper on self.plot that corresponds to self.axis.
    mapper = Property(depends_on='plot')

    # The name of the metadata to look at for dataspace bounds. The metadata
    # can be either a tuple (dataspace_start, dataspace_end) in "selections" or
    # a boolean array mask of seleted dataspace points with any other name
    metadata_name = Str("selections")

    def overlay(self, component, gc, view_bounds=None, mode="normal"):
        """ Draws this component overlaid on another component.

        Overrides AbstractOverlay.
        """
        # Draw the selection
        coords = self._get_selection_screencoords()

        if len(coords) == 0:
            return

        with gc:
            gc.set_alpha(self.alpha)

            plot_width = self.component.width
            plot_height = self.component.height

            origin_x = self.component.padding_left
            origin_y = self.component.padding_top

            if self.axis == 'index':
                if isinstance(self.mapper, GridMapper):
                    scale_width = (coords[-1][0] - coords[0][0])/self.doc_width
                else:
                    scale_width = (coords[0][-1] - coords[0][0])/self.doc_width
                scale_height = float(plot_height)/self.doc_height
                gc.translate_ctm(coords[0][0], origin_y + plot_height)
            else:
                scale_height = (coords[0][-1] - coords[0][0])/self.doc_height
                scale_width = float(plot_width)/self.doc_width
                gc.translate_ctm(origin_x, coords[0][0])

            # SVG origin is the upper right with y positive down, so
            # we need to flip everything
            gc.scale_ctm(scale_width, -scale_height)

            self.document.render(gc)

            self._draw_component(gc, view_bounds, mode)

        return

    def _get_selection_screencoords(self):
        """ Returns a tuple of (x1, x2) screen space coordinates of the start
        and end selection points.

        If there is no current selection, then returns None.
        """
        ds = getattr(self.plot, self.axis)
        selection = ds.metadata[self.metadata_name]

        # "selections" metadata must be a tuple
        if self.metadata_name == "selections":
            if selection is not None and len(selection) == 2:
                return [self.mapper.map_screen(numpy.array(selection))]
            else:
                return []
        # All other metadata is interpreted as a mask on dataspace
        else:
            ar = numpy.arange(0,len(selection), 1)
            runs = arg_find_runs(ar[selection])
            coords = []
            for inds in runs:
                start = ds._data[ar[selection][inds[0]]]
                end = ds._data[ar[selection][inds[1]-1]]
                coords.append(self.map_screen(numpy.array((start, end))))
            return coords

    @cached_property
    def _get_plot(self):
        return self.component

    @cached_property
    def _get_axis_index(self):
        if self.axis == 'index':
            return 0
        else:
            return 1

    @cached_property
    def _get_mapper(self):
        # If the plot's mapper is a GridMapper, return either its
        # x mapper or y mapper

        mapper = getattr(self.plot, self.axis + "_mapper")

        if isinstance(mapper, GridMapper):
            if self.axis == 'index':
                return mapper._xmapper
            else:
                return mapper._ymapper
        else:
            return mapper
