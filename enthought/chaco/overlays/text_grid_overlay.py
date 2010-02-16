
from enthought.traits.api import Instance
from enthought.enable.text_grid import TextGrid

from aligned_container_overlay import AlignedContainerOverlay

class TextGridOverlay(AlignedContainerOverlay):

    text_grid = Instance(TextGrid)
    
    def _text_grid_changed(self, old, new):
        print 'text_grid', old, new
        if old is not None:
            self.remove(old)
        if new is not None:
            self.add(new)
    
    def _text_grid_default(self):
        text_grid = TextGrid(font='modern 12', cell_border_width=0)
        self.add(text_grid)
        return text_grid