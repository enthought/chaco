## ex_chaco_myTP.range_01.py

# standard imports
import inspect, os
import numpy as np

# Enthought imports
from enable.api import ComponentEditor
from traits.api import HasTraits
from traitsui.api import Item, Group, View
from chaco.api import Plot, ArrayPlotData

# defines
windowSize = (800,600)

# window title is file name
windowTitle = os.path.split(__file__)[1]

class TraitedPlot( HasTraits ):

  numPoints = 100
  extent = 2.0 * np.pi
  phaseA = np.linspace( -extent,extent,numPoints )
  amplitudeA = np.sin( phaseA ) * np.exp(-abs( phaseA ))

  myTADP = ArrayPlotData()
  myTADP.set_data( 'X',phaseA )
  myTADP.set_data( 'Y',amplitudeA )

  myTP = Plot( myTADP )
  myTP.plot(
      ("X", "Y"),
      type = 'line',
  )

  # The actual value of the lower left/upper right bounds of this range as (x,y)
  # points. To set them, use low_setting/high_setting.
  myTP.range2d.low
  myTP.range2d.high

  # a 2-tuple of lower left/upper right (x,y) bounds. Either can be set to
  # 'auto', causing the range to autocalculate
  myTP.range2d.low_setting
  myTP.range2d.high_setting

  # Sets all the bounds of the range simultaneously. Lower left/upper right
  # corners of the data range.
  # Ex. myTP.range2d.set_bounds( (1,2), (3,4) ) sets the lower left to (1,2) and
  # the upper right to (3,4)
  myTP.range2d.set_bounds

  # ranges in the x- and y- dimensions. These are DataRange1D objects, one for
  # the x- axis and one for the y- axis
  myTP.range2d.x_range
  myTP.range2d.y_range

  # the low/high values for the x-/y- axes. can be set to
  #   'auto': The lower bound is automatically set at or below the minimum
  #     of the data.
  #   'track': The lower bound tracks the upper bound by tracking_amount.
  #   CFloat: An explicit value for the lower bound
  # set with the appropriate _setting method
  myTP.range2d.x_range.low
  myTP.range2d.x_range.high
  myTP.range2d.y_range.low
  myTP.range2d.y_range.high

  myTP.range2d.x_range.low_setting
  myTP.range2d.x_range.high_setting
  myTP.range2d.y_range.low_setting
  myTP.range2d.y_range.high_setting

  # Do 'auto' bounds imply an exact fit to the data? (One Boolean per dimension)
  # If False, the bounds pad a little bit of margin on either side. Setting
  # the range2d.tight_bounds does not work (i.e. myTP.range2d.tight_bounds =
  # (False,False)) does nothing. Defaults to (True,True) which causes the axes
  # bounds to exactly correspond to the data
  myTP.range2d.x_range.tight_bounds = False
  myTP.range2d.y_range.tight_bounds = False

  # The minimum percentage difference between low and high for each dimension.
  # That is, (high-low) >= epsilon * low.
  myTP.range2d.epsilon

  # If any of the bounds is 'auto', this method refreshes the actual low and
  # high values from the set of the view filters' data sources.
  myTP.range2d.refresh()

  # Resets the bounds of this range.
  myTP.range2d.reset()

  traits_view = View(
      Group(
          Item(
              'myTP',
              editor = ComponentEditor(size = windowSize),
              show_label = False,
          ),
          orientation = "vertical",
      ),
      resizable = True,
      title = windowTitle,
  )

if __name__ == "__main__":

  tp = TraitedPlot()
  tp.configure_traits()

  print( tp.myTP.range2d )

  myMethods = inspect.getmembers(tp.myTP.range2d)
  myPublics = [thisItem for thisItem in myMethods if thisItem[0][0] != '_']
  print( myPublics )

  tp.myTP.range2d.print_traits()
