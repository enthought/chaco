import sys
import unittest

import nose

from enthought.chaco.api import HPlotContainer, OverlayPlotContainer, \
                                PlotComponent, VPlotContainer, GridContainer
from enthought.traits.api import Any, Tuple

SizePrefs = GridContainer.SizePrefs


class ContainerTestCase(unittest.TestCase):
    def assert_tuple(self, t1, t2):
        self.assertEquals(len(t1), len(t2))
        for i in xrange(len(t1)):
            self.assertEquals(t1[i], t2[i])


class StaticPlotComponent(PlotComponent):
    """ A plotcomponent with fixed dimensions """

    def __init__(self, bounds, *args, **kw):
        kw["bounds"] = bounds
        if not kw.has_key("resizable"):
            kw["resizable"] = ""
        PlotComponent.__init__(self, *args, **kw)
        return

class ResizablePlotComponent(PlotComponent):
    """ A resizable PlotComponent with a fixed preferred size. """

    # An optional trait for expressing the preferred size of this component,
    # regardless of whether or not it is resizable.
    fixed_preferred_size = Any

    # Override default value in PlotComponent
    resizable = "hv"

    def __init__(self, preferred_size=None, *args, **kw):
        if preferred_size is not None:
            self.fixed_preferred_size = preferred_size
        PlotComponent.__init__(self, *args, **kw)

    def get_preferred_size(self):
        if self.fixed_preferred_size is not None:
            return self.fixed_preferred_size
        else:
            return PlotComponent.get_preferred_size(self)


class OverlayPlotContainerTestCase(ContainerTestCase):
    
    def test_basics(self):
        container = OverlayPlotContainer(resizable='', bounds=[100.0,200.0])
        self.assert_tuple(container.get_preferred_size(), (100.0,200.0))
        self.assertEquals(container._layout_needed, True)
        container.do_layout()
        self.assertEquals(container._layout_needed, False)
        return
    
    def test_fixed_size_component(self):
        container = OverlayPlotContainer(resizable='', bounds=[200.0,300.0])
        # non-resizable component
        component = PlotComponent(resizable='', position=[50.0,60.0], bounds=[100.0,110.0])
        self.assertEquals(container._layout_needed, True)
        container.do_layout()
        container.add(component)
        self.assertEquals(container._layout_needed, True)
        container.do_layout()
        self.assertEquals(container._layout_needed, False)
        
        # check the results of the layout
        self.assert_tuple(container.get_preferred_size(), (200.0,300.0))
        self.assert_tuple(component.position, (50.0,60.0))
        self.assert_tuple(component.bounds, (100.0,110.0))
        return

    def test_resizable_component(self):
        container = OverlayPlotContainer(resizable='', bounds=[200.0,300.0])
        component = PlotComponent(resizable='hv', position=[50.0,56.0], bounds=[100.0,110.0])
        container.add(component)
        container.do_layout()
        self.assert_tuple(component.position, (0.0,0.0))
        self.assert_tuple(component.bounds, (200.0,300.0))
        
        comp2 = PlotComponent(resizable="h", position=[10,20], bounds=[100,150])
        container.add(comp2)
        container.do_layout()
        self.assert_tuple(comp2.position, (0.0, 20.0))
        self.assert_tuple(comp2.bounds, (200.0, 150.0))
        
        comp3 = PlotComponent(resizable="v", position=[30,40], bounds=[100,150])
        container.add(comp3)
        container.do_layout()
        self.assert_tuple(comp3.position, (30.0, 0.0))
        self.assert_tuple(comp3.bounds, (100,300))
        return
    
    def test_min_size(self):
        container = OverlayPlotContainer(resizable='', bounds=[50.0,50.0])
        component = PlotComponent(resizable='', position=[50.0,60.0],
                                  bounds=[100.0, 110.0])
        container.add(component)
        container.do_layout()
        self.assert_tuple(component.position, (50.0,60.0))
        self.assert_tuple(component.bounds, (100.0,110.0))
        return
        
    def test_multiple_min_size(self):
        comp1 = StaticPlotComponent([200, 50])
        comp2 = StaticPlotComponent([60, 300])
        container = OverlayPlotContainer(resizable='hv', bounds=[30,30])
        container.fit_components = "hv"
        container.add(comp1, comp2)
        container.do_layout()
        self.assert_tuple(container.get_preferred_size(), (200,300))
        self.assert_tuple(comp1.bounds, (200,50))
        self.assert_tuple(comp2.bounds, (60,300))
        return

class HPlotContainerTestCase(ContainerTestCase):

    def test_stack_nonresize(self):
        # Assuming resizable='' for all plot containers and components
        container = HPlotContainer(bounds=[300,100])
        comp1 = StaticPlotComponent([100,70])
        comp2 = StaticPlotComponent([90,80])
        comp3 = StaticPlotComponent([80,90])
        container.add(comp1, comp2, comp3)
        container.do_layout()
        self.assert_tuple(container.get_preferred_size(), (270,90))
        self.assert_tuple(container.bounds, (300,100))
        self.assert_tuple(comp1.position, (0,0))
        self.assert_tuple(comp2.position, (100,0))
        self.assert_tuple(comp3.position, (190,0))
        return
    
    def test_stack_one_resize(self):
        "Checks stacking with 1 resizable component thrown in"
        container = HPlotContainer(bounds=[300,100])
        comp1 = StaticPlotComponent([100,70])
        comp2 = StaticPlotComponent([90,80])
        comp3 = StaticPlotComponent([80,90], resizable='hv')
        comp4 = StaticPlotComponent([40,50])
        container.add(comp1, comp2, comp3, comp4)
        container.do_layout()
        self.assert_tuple(container.get_preferred_size(), (230,80))
        self.assert_tuple(container.bounds, (300,100))
        self.assert_tuple(comp1.position, (0,0))
        self.assert_tuple(comp2.position, (100,0))
        self.assert_tuple(comp3.position, (190,0))
        self.assert_tuple(comp4.position, (260,0))
        return
    
    def test_valign(self):
        container = HPlotContainer(bounds=[300,200], valign="center")
        comp1 = StaticPlotComponent([200,100])
        container.add(comp1)
        container.do_layout()
        self.failUnlessEqual(comp1.position, [0,50])
        container.valign="top"
        container.do_layout(force=True)
        self.failUnlessEqual(comp1.position, [0,100])
        return


class VPlotContainerTestCase(ContainerTestCase):
    # These tests are mostly transposes of the values in HPlotContainer
    
    def test_stack_nonresize(self):
        container = VPlotContainer(bounds=[100,300])
        comp1 = StaticPlotComponent([70,100])
        comp2 = StaticPlotComponent([80,90])
        comp3 = StaticPlotComponent([90,80])
        container.add(comp1, comp2, comp3)
        container.do_layout()
        self.assert_tuple(container.get_preferred_size(), (90, 270))
        self.assert_tuple(container.bounds, (100,300))
        self.assert_tuple(comp1.position, (0,0))
        self.assert_tuple(comp2.position, (0,100))
        self.assert_tuple(comp3.position, (0,190))
        return
        
    def test_stack_one_resize(self):
        "Checks stacking with 1 resizable component thrown in"
        container = VPlotContainer(bounds=[100,300])
        comp1 = StaticPlotComponent([70,100])
        comp2 = StaticPlotComponent([80,90])
        comp3 = StaticPlotComponent([90,80], resizable='hv')
        comp4 = StaticPlotComponent([50,40])
        container.add(comp1, comp2, comp3, comp4)
        container.do_layout()
        self.assert_tuple(container.get_preferred_size(), (80,230))
        self.assert_tuple(container.bounds, (100,300))
        self.assert_tuple(comp1.position, (0,0))
        self.assert_tuple(comp2.position, (0,100))
        self.assert_tuple(comp3.position, (0,190))
        self.assert_tuple(comp4.position, (0,260))
        return

    def test_halign(self):
        container = VPlotContainer(bounds=[200,300], halign="center")
        comp1 = StaticPlotComponent([100,200])
        container.add(comp1)
        container.do_layout()
        self.failUnlessEqual(comp1.position, [50,0])
        container.halign="right"
        container.do_layout(force=True)
        self.failUnlessEqual(comp1.position, [100,0])
        return

    def test_fit_components(self):
        container = VPlotContainer(bounds=[200,300], resizable="v", fit_components="v")
        comp1 = StaticPlotComponent([50,100], padding=5)
        comp2 = StaticPlotComponent([50,120], padding=5)
        container.add(comp1)
        container.add(comp2)
        self.assert_tuple(container.get_preferred_size(), (200,240))
        # The container should not change its size as a result of its fit_components
        # being set.
        self.assert_tuple(container.bounds, (200,300))
        container.bounds = container.get_preferred_size()
        container.do_layout()

        container.padding = 8
        self.assert_tuple(container.get_preferred_size(), (216,256))
        container.do_layout()
        self.assert_tuple(comp1.outer_position, (0,0))
        self.assert_tuple(comp2.outer_position, (0,110))



class SizePrefsTestCase(unittest.TestCase):
    def assert_tuple(self, t1, t2):
        self.assertEquals(t1[0], t2[0])
        self.assertEquals(t1[1], t2[1])

    def test_sequential_non_resizable(self):
        prefs = SizePrefs(4, "h")
        components = [StaticPlotComponent([100,100]) for i in range(4)]
        for i, c in enumerate(components):
            prefs.update_from_component(c, i)
        pref_size = prefs.get_preferred_size()
        self.assert_tuple(pref_size, (100,100,100,100))
        sizes = prefs.compute_size_array(400)
        self.assert_tuple(sizes, (100,100,100,100))
        sizes2 = prefs.compute_size_array(500)
        self.assert_tuple(sizes, (100,100,100,100))

    def test_overlapping_non_resizable(self):
        prefs = SizePrefs(1, "h")
        prefs.update_from_component(StaticPlotComponent([100,10]), 0)
        prefs.update_from_component(StaticPlotComponent([200,10]), 0)
        prefs.update_from_component(StaticPlotComponent([300,10]), 0)
        pref_size = prefs.get_preferred_size()
        self.assertEquals(pref_size[0], 300)
        sizes = prefs.compute_size_array(400)
        self.assertEquals(sizes[0], 400)

    def test_sequential_resizable(self):
        prefs = SizePrefs(3, "v")
        prefs.update_from_component(ResizablePlotComponent([10,100]), 0)
        prefs.update_from_component(ResizablePlotComponent([10,200]), 1)
        prefs.update_from_component(ResizablePlotComponent([10,300]), 2)
        pref_size = prefs.get_preferred_size()
        self.assert_tuple(pref_size, (100,200,300))
        sizes = prefs.compute_size_array(600)
        self.assert_tuple(sizes, [100, 200, 300])
        sizes2 = prefs.compute_size_array(60)
        self.assert_tuple(sizes2, [10, 20, 30])
        sizes3 = prefs.compute_size_array(6000)
        self.assert_tuple(sizes3, [1000, 2000, 3000])

    def test_overlapping_resizable(self):
        prefs = SizePrefs(2, "h")
        prefs.update_from_component(ResizablePlotComponent([50, 10]), 0)
        prefs.update_from_component(ResizablePlotComponent([100, 10]), 0)
        prefs.update_from_component(ResizablePlotComponent([80, 10]), 1)
        pref_size = prefs.get_preferred_size()
        self.assert_tuple(pref_size, (100,80))
        sizes = prefs.compute_size_array(180)
        self.assert_tuple(sizes, (100, 80))
        sizes2 = prefs.compute_size_array(360)
        self.assert_tuple(sizes2, (200, 160))

    def test_sequential_fully_resizable(self):
        prefs = SizePrefs(3, "h")
        for i in range(3):
            prefs.update_from_component(ResizablePlotComponent(), i)
        pref_size = prefs.get_preferred_size()
        self.assert_tuple(pref_size, (0,0,0))
        sizes = prefs.compute_size_array(60)
        self.assert_tuple(sizes, (20, 20, 20))

    def test_overlapping_fully_resizable(self):
        prefs = SizePrefs(1, "h")
        for i in range(3):
            prefs.update_from_component(ResizablePlotComponent(), 0)
        pref_size = prefs.get_preferred_size()
        self.assertEquals(pref_size[0], 0)
        sizes = prefs.compute_size_array(60)
        self.assertEquals(sizes[0], 60)

    def test_sequential_mixed_resizable(self):
        # Tests a sequence of resizable and fully resizable components.
        prefs = SizePrefs(3, "h")
        prefs.update_from_component(ResizablePlotComponent(), 0)
        prefs.update_from_component(ResizablePlotComponent([100,10]), 1)
        prefs.update_from_component(ResizablePlotComponent(), 2)
        pref_size = prefs.get_preferred_size()
        self.assert_tuple(pref_size, (0, 100, 0))
        sizes = prefs.compute_size_array(50)
        self.assert_tuple(sizes, (0, 50, 0))
        sizes2 = prefs.compute_size_array(100)
        self.assert_tuple(sizes2, (0, 100, 0))
        sizes3 = prefs.compute_size_array(200)
        self.assert_tuple(sizes3, (50, 100, 50))

    def test_overlapping_mixed_resizable(self):
        # Tests a sequence of overlapping resizable and fully resizable components.
        prefs = SizePrefs(4, "h")
        # Slot 1
        prefs.update_from_component(ResizablePlotComponent([100,10]), 0)
        prefs.update_from_component(ResizablePlotComponent(), 0)
        # Slot 2
        prefs.update_from_component(ResizablePlotComponent(), 1)
        prefs.update_from_component(ResizablePlotComponent([50,10]), 1)
        # Slot 3
        prefs.update_from_component(ResizablePlotComponent(), 2)
        prefs.update_from_component(ResizablePlotComponent([40,10]), 2)
        # Slot 4
        prefs.update_from_component(ResizablePlotComponent(), 3)
        prefs.update_from_component(ResizablePlotComponent(), 3)
        pref_size = prefs.get_preferred_size()
        self.assert_tuple(pref_size, (100, 50, 40, 0))
        sizes = prefs.compute_size_array(95)
        self.assert_tuple(sizes, (50, 25, 20, 0))
        sizes2 = prefs.compute_size_array(230)
        self.assert_tuple(sizes2, (100, 50, 40, 40))

    def test_sequential_mixed_resizable_static(self):
        # Tests a sequence of static and resizable components.
        prefs = SizePrefs(3, "h")
        prefs.update_from_component(StaticPlotComponent([100,10]), 0)
        prefs.update_from_component(ResizablePlotComponent([50,10]), 1)
        prefs.update_from_component(ResizablePlotComponent([75,10]), 2)
        pref_size = prefs.get_preferred_size()
        self.assert_tuple(pref_size, (100,50,75))
        sizes = prefs.compute_size_array(225)
        self.assert_tuple(sizes, (100,50,75))
        sizes2 = prefs.compute_size_array(350)
        self.assert_tuple(sizes2, (100,100,150))

    def test_sequential_mixed_resizable_static2(self):
        # Tests a sequence of non-overlapping static, resizable, and fully
        # resizable components.
        prefs = SizePrefs(4, "h")
        prefs.update_from_component(StaticPlotComponent([100,10]), 0)
        prefs.update_from_component(ResizablePlotComponent([50,10]), 1)
        prefs.update_from_component(ResizablePlotComponent([75,10]), 2)
        prefs.update_from_component(ResizablePlotComponent(), 3)
        pref_size = prefs.get_preferred_size()
        self.assert_tuple(pref_size, (100,50,75,0))
        sizes = prefs.compute_size_array(300)
        self.assert_tuple(sizes, (100,50,75,75))

    def test_overlapping_mixed_resizable_static(self):
        prefs = SizePrefs(5, "h")
        # Slot 1 - static and smaller resizable
        prefs.update_from_component(StaticPlotComponent([100,10]), 0)
        prefs.update_from_component(ResizablePlotComponent([50,10]), 0)
        # Slot 2 - static and larger resizable
        prefs.update_from_component(StaticPlotComponent([30,10]), 1)
        prefs.update_from_component(ResizablePlotComponent([60,10]), 1)
        # Slot 3 - static and fully resizable
        prefs.update_from_component(StaticPlotComponent([50,10]), 2)
        prefs.update_from_component(ResizablePlotComponent(), 2)
        # Slot 4 - resizable and fully resizable
        prefs.update_from_component(ResizablePlotComponent([90,10]), 3)
        prefs.update_from_component(ResizablePlotComponent(), 3)
        # Slot 5 - fully resizable
        prefs.update_from_component(ResizablePlotComponent(), 4)

        pref_size = prefs.get_preferred_size()
        self.assert_tuple(pref_size, (100, 60, 50, 90, 0))
        
        # Test scaling down of resizable components in slots 2 and 4
        sizes = prefs.compute_size_array(180 + 60)
        self.assert_tuple(sizes, (100, 30+15, 50, 45, 0))

        # Test scaling up of fully resizable component in slot 5, and proper
        # allocation of slot 2's resizable component's full preferred size.
        sizes2 = prefs.compute_size_array(300 + 35)
        self.assert_tuple(sizes2, (100, 60, 50, 90, 35))



class GridContainerTestCase(ContainerTestCase):

    def test_empty_container(self):
        # FIXME:
        #   This test is failing when run with nosetests and coverage.
        #   Therefore, it is skipped when coverage is imported.
        #   If you want to fix this, please look at:
        #     https://svn.enthought.com/enthought/ticket/1618
        #   where I posted more details about this problem.
        if 'coverage' in sys.modules:
            raise nose.SkipTest
        
        cont = GridContainer(shape=(1,1))
        cont.bounds = [100,100]
        cont.do_layout()
        return

    def test_all_empty_cells(self):
        cont = GridContainer(shape=(2,2), spacing=(0,0))
        cont.component_grid = [[None, None], [None, None]]
        size = cont.get_preferred_size()
        self.assert_tuple(size, (0,0))
        cont.bounds = (100,100)
        cont.do_layout()
        return

    def test_some_empty_cells(self):
        cont = GridContainer(shape=(2,2), spacing=(0,0))
        a = StaticPlotComponent([100,30])
        b = StaticPlotComponent([50,40])
        cont.component_grid = [[a, None], [None, b]]
        size = cont.get_preferred_size()
        self.assert_tuple(size, (150, 70))
        cont.bounds = size
        cont.do_layout()
        self.assert_tuple(a.outer_position, (0, 40))
        self.assert_tuple(a.outer_bounds, (100, 30))
        self.assert_tuple(b.outer_position, (100,0))
        self.assert_tuple(b.outer_bounds, (50, 40))

    def test_single_cell(self):
        cont = GridContainer(shape=(1,1))
        comp1 = StaticPlotComponent([200,300])
        cont.add(comp1)
        cont.do_layout()
        # it would be nice to make all boolean tests here trigger
        # assert failures, maybe using Pypy?
        self.assert_tuple(comp1.position, (0,0))
        self.assert_tuple(comp1.bounds, (200,300))
        return

    def test_nonresizable_container(self):
        cont = GridContainer(shape=(1,1), resizable="")
        comp1 = StaticPlotComponent([200,300])
        cont.add(comp1)
        cont.do_layout()
        self.assert_tuple(comp1.position, (0,0))
        self.assert_tuple(comp1.bounds, (200,300))
        return

    def test_row(self):
        cont = GridContainer(shape=(1,3), halign="center", valign="center")
        c1 = StaticPlotComponent([50,50])
        c2 = StaticPlotComponent([30,30])
        c3 = StaticPlotComponent([0,0], resizable="hv")
        cont.add(c1, c2, c3)
        cont.bounds = list(cont.get_preferred_size())
        cont.do_layout()
        self.assert_tuple(c1.position, (0,0))
        self.assert_tuple(c1.bounds, (50,50))
        self.assert_tuple(c2.position, (50,10))
        self.assert_tuple(c2.bounds, (30,30))
        self.assert_tuple(c3.position, (80,0))
        self.assert_tuple(c3.bounds, (0,50))

        cont.bounds = [100, 50]
        cont.do_layout()
        self.assert_tuple(c1.position, (0,0))
        self.assert_tuple(c1.bounds, (50,50))
        self.assert_tuple(c2.position, (50,10))
        self.assert_tuple(c2.bounds, (30,30))
        self.assert_tuple(c3.position, (80,0))
        self.assert_tuple(c3.bounds, (20,50))
        return

    def test_two_by_two(self):
        """ Tests a 2x2 grid of components """
        cont = GridContainer(shape=(2,2), halign="center", valign="center")
        ul = StaticPlotComponent([50,50])     # upper-left component
        lr = StaticPlotComponent([100,100])   # lower-right component
        top = StaticPlotComponent([0,0], resizable="hv")
        left = StaticPlotComponent([0,0], resizable="hv")
        cont.component_grid = [[ul, top], [left, lr]]
        cont.bounds = [150, 150]
        cont.do_layout()
        self.assert_tuple(ul.position, (0,100))
        self.assert_tuple(ul.bounds, (50,50))
        self.assert_tuple(top.position, (50,100))
        self.assert_tuple(top.bounds, (100, 50))
        self.assert_tuple(left.position, (0,0))
        self.assert_tuple(left.bounds, (50,100))
        self.assert_tuple(lr.position, (50,0))
        self.assert_tuple(lr.bounds, (100,100))
        return

    def test_spacing(self):
        cont = GridContainer(shape=(2,2), spacing=(10,10),
                             halign="center", valign="center")
        ul = StaticPlotComponent([50,50])     # upper-left component
        lr = StaticPlotComponent([100,100])   # lower-right component
        top = StaticPlotComponent([0,0], resizable="hv")
        left = StaticPlotComponent([0,0], resizable="hv")
        cont.component_grid = [[ul, top], [left, lr]]
        cont.bounds = [190, 190]
        cont.do_layout()
        self.assert_tuple(ul.position, (10,130))
        self.assert_tuple(ul.bounds, (50,50))
        self.assert_tuple(top.position, (80,130))
        self.assert_tuple(top.bounds, (100, 50))
        self.assert_tuple(left.position, (10,10))
        self.assert_tuple(left.bounds, (50,100))
        self.assert_tuple(lr.position, (80,10))
        self.assert_tuple(lr.bounds, (100,100))
        return

    def test_resizable(self):
        cont = GridContainer(shape=(2,2), spacing=(0,0),
                             halign="center", valign="center")
        ul = StaticPlotComponent([0,0], resizable="hv")
        lr = StaticPlotComponent([0,0], resizable="hv")
        top = StaticPlotComponent([0,0], resizable="hv")
        left = StaticPlotComponent([0,0], resizable="hv")
        cont.component_grid = [[ul, top], [left, lr]]
        cont.bounds = [200, 200]
        cont.do_layout()
        self.assert_tuple(ul.position, (0,100))
        self.assert_tuple(ul.bounds, (100,100))
        self.assert_tuple(top.position, (100,100))
        self.assert_tuple(top.bounds, (100, 100))
        self.assert_tuple(left.position, (0,0))
        self.assert_tuple(left.bounds, (100,100))
        self.assert_tuple(lr.position, (100,0))
        self.assert_tuple(lr.bounds, (100,100))
        return

    def test_resizable2(self):
        # Tests a resizable component that also has a preferred size
        cont = GridContainer(shape=(2,2), spacing=(0,0),
                             halign="center", valign="center")
        ul = StaticPlotComponent([150,150], resizable="hv")
        lr = StaticPlotComponent([0,0], resizable="hv")
        top = StaticPlotComponent([0,0], resizable="hv")
        left = StaticPlotComponent([0,0], resizable="hv")
        cont.component_grid = [[ul, top], [left, lr]]
        cont.bounds = [200, 200]
        cont.do_layout()
        self.assert_tuple(ul.position, (0,100))
        self.assert_tuple(ul.bounds, (100,100))
        self.assert_tuple(top.position, (100,100))
        self.assert_tuple(top.bounds, (100,100))
        self.assert_tuple(left.position, (0,0))
        self.assert_tuple(left.bounds, (100,100))
        self.assert_tuple(lr.position, (100,0))
        self.assert_tuple(lr.bounds, (100,100))

    def test_resizable_mixed(self):
        """ Tests mixing resizable and non-resizable components """
        cont = GridContainer(shape=(2,2), spacing=(10,10),
                             halign="center", valign="center")
        ul = StaticPlotComponent([0,0], resizable="hv")
        lr = StaticPlotComponent([0,0], resizable="hv")
        top = StaticPlotComponent([0,0], resizable="hv")
        left = StaticPlotComponent([100,100], resizable="")
        cont.component_grid = [[ul, top], [left, lr]]
        cont.bounds = [240, 240]
        cont.do_layout()
        self.assert_tuple(ul.position, (10,130))
        self.assert_tuple(ul.bounds, (100,100))
        self.assert_tuple(top.position, (130,130))
        self.assert_tuple(top.bounds, (100, 100))
        self.assert_tuple(left.position, (10,10))
        self.assert_tuple(left.bounds, (100,100))
        self.assert_tuple(lr.position, (130,10))
        self.assert_tuple(lr.bounds, (100,100))
        return

    def test_resizable_mixed2(self):
        # Tests laying out resizable components with preferred
        # sized alongside non-resizable components.
        cont = GridContainer(shape=(2,2), spacing=(0,0),
                             halign="center", valign="center")
        ul = ResizablePlotComponent([150,150])
        lr = StaticPlotComponent([50,50], resizable="")
        top = StaticPlotComponent([0,0], resizable="hv")
        left = StaticPlotComponent([0,0], resizable="hv")
        cont.component_grid = [[ul, top], [left, lr]]
        cont.bounds = [200, 200]
        cont.do_layout()
        self.assert_tuple(ul.position, (0,50))
        self.assert_tuple(ul.bounds, (150,150))
        self.assert_tuple(top.position, (150,50))
        self.assert_tuple(top.bounds, (50,150))
        self.assert_tuple(left.position, (0,0))
        self.assert_tuple(left.bounds, (150,50))
        self.assert_tuple(lr.position, (150,0))
        self.assert_tuple(lr.bounds, (50,50))

    def test_resizable_mixed_h(self):
        # Tests the layout of a non-resizable component, a resizable with a
        # preferred size, and a fully resizable component in a horizontal
        # GridContainer
        cont = GridContainer(shape=(3,1), spacing=(0,0),
                             halign="center", valign="center")
        left = StaticPlotComponent([50,10], resizable="")
        middle = ResizablePlotComponent([100,10])
        right = StaticPlotComponent([0,0], resizable="hv")
        
        cont.component_grid = [[left, middle, right]]
        cont.bounds = [200, 10]
        cont.do_layout()
        self.assert_tuple(left.position, (0,0))
        self.assert_tuple(left.bounds, (50,10))
        self.assert_tuple(middle.position, (50,0))
        self.assert_tuple(middle.bounds, (100,10))
        self.assert_tuple(right.position, (150,0))
        self.assert_tuple(right.bounds, (50,10))

    def test_non_resizable(self):
        cont = GridContainer(shape=(2,2), spacing=(10,10),
                             halign="center", valign="center")
        ul = StaticPlotComponent([100,100], resizable="")
        ur = StaticPlotComponent([100,100], resizable="")
        ll = StaticPlotComponent([100,100], resizable="")
        lr = StaticPlotComponent([100,100], resizable="")
        cont.component_grid = [[ul, ur], [ll, lr]]

        cont.bounds = [240, 240]
        cont.do_layout()
        self.assert_tuple(ul.position, (10,130))
        self.assert_tuple(ul.bounds, (100,100))
        self.assert_tuple(ur.position, (130,130))
        self.assert_tuple(ur.bounds, (100, 100))
        self.assert_tuple(ll.position, (10,10))
        self.assert_tuple(ll.bounds, (100,100))
        self.assert_tuple(lr.position, (130,10))
        self.assert_tuple(lr.bounds, (100,100))

        cont.bounds = [280, 280]
        cont.do_layout()
        self.assert_tuple(ul.position, (20,160))
        self.assert_tuple(ul.bounds, (100,100))
        self.assert_tuple(ur.position, (160,160))
        self.assert_tuple(ur.bounds, (100, 100))
        self.assert_tuple(ll.position, (20,20))
        self.assert_tuple(ll.bounds, (100,100))
        self.assert_tuple(lr.position, (160,20))
        self.assert_tuple(lr.bounds, (100,100))

if __name__ == '__main__':
    import nose
    nose.run()
