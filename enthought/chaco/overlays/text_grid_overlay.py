""" An overlay containing a TextGrid
"""

from traits.api import Instance
from enthought.enable.text_grid import TextGrid

from aligned_container_overlay import AlignedContainerOverlay

class TextGridOverlay(AlignedContainerOverlay):
    """ Overlay for plots containing a TextGrid

    This subclass of AlignedContainerOverlay has a TextGrid which it
    displays.  Subclasses or users are responsible for the content and
    formatting of the TextGrid.
    """
    # The text grid component we contain.
    text_grid = Instance(TextGrid)

    # XXX put some delegated traits for the text_grid here?

    def _text_grid_changed(self, old, new):
        if old is not None:
            self.remove(old)
        if new is not None:
            self.add(new)

    def _text_grid_default(self):
        text_grid = TextGrid(font='modern 12', cell_border_width=0)
        self.add(text_grid)
        return text_grid
