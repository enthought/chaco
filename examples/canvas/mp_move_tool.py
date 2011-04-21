
from traits.api import Int
from enthought.enable.tools.api import MoveTool

class MPMoveTool(MoveTool):

    cur_bid = Int(-1)

    def normal_blob_down(self, event):
        if self.cur_bid == -1:
            self.cur_bid = event.bid
            self.normal_left_down(event)

    def dragging_blob_up(self, event):
        if event.bid == self.cur_bid:
            self.cur_bid = -1
            self.normal_left_up(event)



