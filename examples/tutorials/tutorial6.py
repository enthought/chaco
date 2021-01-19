"""Tutorial 6. Writing a tool

We write an interactor tha prints out all the events it receives.
"""


from chaco.api import AbstractController

from tutorial2 import demo

class EventPrinter(AbstractController):
    def dispatch(self, event, suffix):
        print(suffix, "event received at (%d,%d)" % (event.x, event.y))

plot = demo.plot
plot.tools.append(EventPrinter(plot))

if __name__ == "__main__":
    demo.configure_traits()
