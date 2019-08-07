******************************
About the Chaco Scales package
******************************

In the summer of 2007, I spent a few weeks working through the axis  
ticking and labelling problem.  The basic goal was that I wanted to  
create a flexible ticking system that would produce nicely-spaced axis  
labels for arbitrary sets of labels *and* arbitrary intervals.  The  
chaco2.scales package is the result of this effort.  It is an entirely  
standalone package that does not import from any other Enthought  
package (not even traits!), and the idea was that it could be used in  
other plotting packages as well.

The overall idea is that you create a ScaleSystem consisting of  
various Scales.  When the ScaleSystem is presented with a data range  
(low,high) and a screen space amount, it searches through its list of  
scales for the scale that produces the "nicest" set of labels.  It  
takes into account whitespace, the formatted size of labels produced  
by each scale in the ScaleSystem, etc.  So, the basic numerical Scales  
defined in scales.py are:

* FixedScale: Simple scale with a fixed interval; places ticks at
  multiples of the resolution
* DefaultScale: Scale that tries to place ticks at 1,2,5, and 10 so  that
  ticks don't "pop" or suddenly jump when the resolution changes  (when
  zooming)
* LogScale: Dynamic scale that only produces ticks and labels that  work
  well when doing logarithmic plots

By comparison, the default ticking logic in DefaultTickGenerator (in  
ticks.py) is basically just the DefaultScale.  (This is currently the  
default tick generator used by PlotAxis.)

In time_scale.py, I define an additional scale, the TimeScale.   
TimeScale not only handles time-oriented data using units of uniform  
interval (microseconds up to days and weeks), it also handles non- 
uniform calendar units like "day of the month" and "month of the  
year".  So, you can tell Chaco to generate ticks on the 1st of every  
month, and it will give you non-uniformly spaced tick and grid lines.

The scale system mechanism is configurable, so although all of the  
examples use the CalendarScaleSystem, you don't have to use it.  In  
fact, if you look at CalendarScaleSystem.__init__, it just initializes  
its list of scales with ``HMSScales + MDYScales``::

    HMSScales = [TimeScale(microseconds=1), TimeScale(milliseconds=1)] + \
               [TimeScale(seconds=dt) for dt in (1, 5, 15, 30)] + \
               [TimeScale(minutes=dt) for dt in (1, 5, 15, 30)] + \
               [TimeScale(hours=dt) for dt in (1, 2, 3, 4, 6, 12, 24)]

    MDYScales = [TimeScale(day_of_month=range(1,31,3)),
                TimeScale(day_of_month=(1,8,15,22)),
                TimeScale(day_of_month=(1,15)),
                TimeScale(month_of_year=range(1,13)),
                TimeScale(month_of_year=range(1,13,3)),
                TimeScale(month_of_year=(1,7)),
                TimeScale(month_of_year=(1,))]

So, if you wanted to create your own ScaleSystem with days, weeks, and  
whatnot, you could do::

    ExtendedScales = HSMScales + [TimeScale(days=n) for n in (1,7,14,28)]
    MyScaleSystem = CalendarScaleSystem(*ExtendedScales)

To use the Scales package in your Chaco plots, just import :class:`PlotAxis` from
:mod:`chaco2.scales_axis` instead of :mod:`chaco2.axis`.  You will still need to create a
:class:`ScalesTickGenerator` and pass it in.  The financial_plot_dates.py demo is a
good example of how to do this.

