
import pdb, unittest

from enthought.traits.api import Tuple

from enthought.chaco2.api import HPlotContainer, OverlayPlotContainer, PlotComponent, \
                                 VPlotContainer, GridContainer


class ContainerTestCase(unittest.TestCase):
    def assert_tuple(self, t1, t2):
        self.assertEquals(t1[0], t2[0])
        self.assertEquals(t1[1], t2[1])


class StaticPlotComponent(PlotComponent):
    """ A plotcomponent with fixed dimensions """
    def __init__(self, bounds, *args, **kw):
        kw["bounds"] = bounds
        if not kw.has_key("resizable"):
            kw["resizable"] = ""
        PlotComponent.__init__(self, *args, **kw)
        return


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
        #pdb.set_trace()
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


class GridContainerTestCase(ContainerTestCase):

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

    

def test_suite(level=1):
    suites = []
    suites.append(unittest.makeSuite(OverlayPlotContainerTestCase, "test_"))
    suites.append(unittest.makeSuite(HPlotContainerTestCase, "test_"))
    suites.append(unittest.makeSuite(VPlotContainerTestCase, "test_"))
    suites.append(unittest.makeSuite(GridContainerTestCase, "test_"))
    return unittest.TestSuite(suites)

def test(level=10):
    all_tests = test_suite(level)
    runner = unittest.TextTestRunner()
    runner.run(all_tests)
    return runner

if __name__ == "__main__":
    test()

# EOF
