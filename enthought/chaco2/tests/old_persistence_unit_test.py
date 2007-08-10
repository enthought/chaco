"""
Test of persistence of core chaco2 data/plotting components and their
relationships to one another.
"""

from cPickle import loads, dumps
import unittest
import pdb

from numpy import arange, array, ones, zeros
from enthought.traits.trait_handlers import TraitListObject
from enthought.chaco2.api import ArrayDataSource, PointDataSource, DataRange, \
                             LinearMapper, LogMapper, PlotComponent, \
                             BasePlotFrame, SimplePlotFrame, \
                             BasePlotContainer, OverlayPlotContainer, \
                             HPlotContainer, VPlotContainer, AbstractPlotRenderer, \
                             BaseXYPlot, ScatterPlot, LinePlot, PlotAxis, PlotGrid


class BaseTestCase(unittest.TestCase):
    """ Defines various comparison methods for subclasses to use """

    simple_plot_frame_attribs = list(SimplePlotFrame._pickles) \
                                    + list(BasePlotFrame._pickles) \
                                    + list(PlotComponent._pickles)

    base_plot_container_attribs = list(BasePlotContainer._pickles) \
                                    + list(PlotComponent._pickles)

    hpc_attribs = base_plot_container_attribs + list(HPlotContainer._pickles)

    vpc_attribs = base_plot_container_attribs + list(VPlotContainer._pickles)
    
    opc_attribs = base_plot_container_attribs + list(OverlayPlotContainer._pickles)
    
    
    def compare(self, a, b):
        """
        Dispatch method to compare objects a and b.  Looks at their types and
        makes sure they are equal; then dispatches to a method named
        self.compare_%s where %s is filled in with the name of the class of
        a and b.
        """
        cls = a.__class__
        self.assert_(cls == b.__class__)

        # Check for simple types:
        if a is None:
            self.assert_(b is None)
        elif type(a) in (list, tuple, str, int, float, bool, TraitListObject):
            self.assert_(a == b)
        elif (type(a) == dict) and (a != b):
            # a simple boneheaded dict compare didn't work
            for key, val in a.items():
                self.compare(val, b[key])
        else:
            func_name = "compare_" + cls.__name__
            if hasattr(self, func_name):
                method = getattr(self, func_name)
                method(a, b)
            else:
                raise RuntimeError, "Unable to find comparison method for objects of type " + cls.__name__
    
    def _compare_attribs(self, a, b, attribs):
        """
        Utility method to compare all the listed attributes of objects a and b.
        """
        for name in attribs:
            try:
                self.compare(getattr(a, name), getattr(b, name))
            except:
                print "\n*** attrib:", name, "a:", getattr(a,name), "\tb:", \
                      getattr(b, name)
                raise
        return
    
    def compare_ArrayDataSource(self, a, b):
        self.assert_(a.sort_order == b.sort_order)
        self.assert_(a.metadata == b.metadata)
        self.assert_(a.persist_data == b.persist_data)
        if a.persist_data:
            self.assert_(a._data == b._data)
        return

    def compare_DataRange(self, a, b):
        # Check shadow traits first, then check the values as exposed by Properties
        private_attribs = ("_low_setting", "_low_value", "_high_setting", "_high_value")
        self._compare_attribs(a, b, private_attribs)
        public_attribs = ("low", "low_setting", "high", "high_setting")
        self._compare_attribs(a, b, public_attribs)
        
        # Now compare the datasources.  This is somewhat tricky, but we do the best
        # we can.
        self.assert_(len(a.sources) == len(b.sources))
        for i in range(len(a.sources)):
            ds_a = a.sources[i]
            ds_b = b.sources[i]
            if ds_a == ds_b:
                continue
            else:
                self.compare(ds_a, ds_b)
        return

    def compare_LinearMapper(self, a, b):
        self.assert_(a.low_pos == b.low_pos)
        self.assert_(a.high_pos == b.high_pos)
        if a.range is not None:
            self.compare(a.range, b.range)
        return

    def compare_LogMapper(self, a, b):
        self.compare_LinearMapper(a, b)
        return
    
    def compare_SimplePlotFrame(self, a, b):
        attribs = self.simple_plot_frame_attribs[:]
        # We can't compare _components because
        #attribs.remove("_frame_slots")
        attribs.remove("_components")
        self._compare_attribs(a, b, attribs)
        for slot_name, container in a._frame_slots.items():
            if container is None:
                self.assert_(getattr(b, slot_name) is None)
            else:
                self.compare(container, getattr(b, slot_name))
        return

    def compare_BasePlotContainer(self, a, b):
        attribs = self.base_plot_container_attribs[:]
        attribs.remove("container")
        self._compare_attribs(a, b, attribs)
        return
    
    def compare_HPlotContainer(self, a, b):
        attribs = self.hpc_attribs[:]
        attribs.remove("container")
        self._compare_attribs(a, b, attribs)
        return

    def compare_VPlotContainer(self, a, b):
        attribs = self.vpc_attribs[:]
        attribs.remove("container")
        self._compare_attribs(a, b, attribs)
        return

    def compare_OverlayPlotContainer(self, a, b):
        attribs = self.opc_attribs[:]
        attribs.remove("container")
        self._compare_attribs(a, b, attribs)
        return

    def compare_LinePlot(self, a, b):
        attribs = list(LinePlot._pickles) + list(BaseXYPlot._pickles) + \
                  list(AbstractPlotRenderer._pickles) + list(PlotComponent._pickles)
        self._compare_attribs(a, b, attribs)
        return

    def compare_PlotAxis(self, a, b):
        pass

class DataTestCase(BaseTestCase):
    
    def test_array_data_source(self):
        myarray = arange(10.0)
        ds = ArrayDataSource(myarray)
        ds.persist_data = False
        ds2 = loads(dumps(ds))
        self.compare(ds, ds2)
        ds.persist_data = True
        ds3 = loads(dumps(ds))
        self.compare(ds, ds3)
        return

    def test_data_range(self):
        myarray = array([5, 6, 7, 8, 9])
        ds = ArrayDataSource(myarray)
        r = DataRange(ds)
        ds2 = loads(dumps(ds))
        self.compare(ds, ds2)
        # Change the bounds setting and persist again
        ds.low = 0.5
        ds.high = 12.9
        ds2 = loads(dumps(ds))
        self.compare(ds, ds2)
        return
    
    def test_linear_mapper(self):
        myarray = array([5, 6, 7, 8, 9])
        ds = ArrayDataSource(myarray)
        r = DataRange(ds)
        mapper = LinearMapper()
        mapper.range = r
        m2 = loads(dumps(mapper))
        self.compare(mapper, m2)
        return

    def test_log_mapper(self):
        myarray = array([5, 6, 7, 8, 9])
        ds = ArrayDataSource(myarray)
        r = DataRange(ds)
        mapper = LogMapper()
        mapper.range = r
        m2 = loads(dumps(mapper))
        self.compare(mapper, m2)
        return
    

class PlotPrimitivesTestCase(BaseTestCase):

    def test_linear_mapper(self):
        mapper = LinearMapper()
        mapper2 = loads(dumps(mapper))
        self.compare(mapper, mapper2)
        
        range = DataRange(low=5.0, high=10.0)
        mapper3 = LinearMapper(range=range)
        mapper4 = loads(dumps(mapper3))
        self.compare(mapper3, mapper4)
        return
    
    def test_plot_frame(self):
        frame = SimplePlotFrame()
        frame.bounds = [400, 500]
        frame2 = loads(dumps(frame))
        self.compare(frame, frame2)
        
        frame3 = SimplePlotFrame()
        frame3.bounds = [300, 400]
        frame3.set_visible_slots = ("right", "center")
        frame3.left_width = 20
        frame3.right_width = 12
        frame4 = loads(dumps(frame3))
        self.compare(frame3, frame4)
        return
    
    def test_base_plot_container(self):
        c = BasePlotContainer()
        c2 = loads(dumps(c))
        self.compare(c, c2)
        
        c3 = BasePlotContainer(bounds=[200,300], position=[5,10], 
                              use_backbuffer = False, resizable = False,
                              halign = "center", valign = "center",
                              bgcolor = "green")
        c4 = loads(dumps(c3))
        self.compare(c3, c4)
        return
    
    def test_plot_containers(self):
        for cls in (HPlotContainer, VPlotContainer):
            c = cls()
            c2 = loads(dumps(c))
            self.compare(c, c2)
            
            c3 = cls(bounds=[200,300], position=[5,10], use_backbuffer = False,
                    resizable = False, halign = "center", valign = "center",
                    bgcolor = "green", spacing = 10.0)
            c4 = loads(dumps(c3))
            self.compare(c3, c4)
        return
    
    def create_simple_line_plot(self):
        x_ary = array([1,2,3,4,5])
        y_ary = array([10,20,30,40,50])
        ds_x = ArrayDataSource(x_ary)
        ds_y = ArrayDataSource(y_ary)
        r_x = DataRange(ds_x)
        r_y = DataRange(ds_y)
        mapper_x = LinearMapper(range=r_x)
        mapper_y = LinearMapper(range=r_y)
        plot = LinePlot(index=ds_x, value=ds_y, index_mapper=mapper_x,
                        value_mapper=mapper_y, orientation="v",
                        index_direction = "flipped")
        return plot
    
    def test_line_plot(self):
        plot = self.create_simple_line_plot()
        plot2 = loads(dumps(plot))
        self.compare(plot, plot2)
        return
    
    def test_axis(self):
        axis = PlotAxis()
        ary = arange(10.0)
        ds = ArrayDataSource(ary)
        r = DataRange(ds)
        mapper = LinearMapper(range = r)
        axis.mapper = mapper
        axis2 = loads(dumps(axis))
        self.compare(axis, axis2)
        return
    

class SimpleLinePlotTestCase(BaseTestCase):
    
    pass


def test_suite(level=1):
    suites = []
    suites.append(unittest.makeSuite(DataTestCase, "test_"))
    suites.append(unittest.makeSuite(PlotPrimitivesTestCase, "test_"))
    return unittest.TestSuite(suites)

def test(level=10):
    all_tests = test_suite(level)
    runner = unittest.TextTestRunner()
    runner.run(all_tests)
    return runner

if __name__ == "__main__":
    test()



# EOF
