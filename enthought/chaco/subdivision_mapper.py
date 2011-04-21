""" Defines the SubdivisionDataMapper and SubdivisionLineDataMapper classes.
"""
# Major library imports
import math
from numpy import array, arange, concatenate, searchsorted, nonzero, transpose, \
                  argsort, zeros, sort, vstack
import numpy

# Enthought library imports
from enthought.traits.api import List, Array, Tuple, Int, Float

# Local, relative imports
from datamapper import AbstractDataMapper, right_shift, left_shift, \
                       sort_points, ArraySortTrait, \
                       array_zip
from subdivision_cells import AbstractCell, Cell, RangedCell, find_runs, \
                              arg_find_runs


class SubdivisionDataMapper(AbstractDataMapper):
    """
    A data mapper that uses a uniform grid of rectangular cells. It doesn't make
    any assumptions about the continuity of the input data set, and explicitly
    stores each point in the data set in its cell.

    If the incoming data is ordered in some fashion such that most cells end
    up with large ranges of data, then it's better to use the
    SubdivisionLineDataMapper subclass.
    """
    celltype = Cell
    _last_region = List(Tuple)
    _cellgrid = Array   # a Numeric array of Cell objects
    _points_per_cell = Int(100)   # number of datapoints/cell to shoot for
    _cell_lefts = Array    # locations of left edge for all cells
    _cell_bottoms = Array  # locations of bottom edge for all cells
    _cell_extents = Tuple(Float, Float)         # the width and height of a cell

    #-------------------------------------------------------------------
    # Public AbstractDataMapper methods
    #-------------------------------------------------------------------

    def get_points_near(self, pointlist, radius=0.0):
        if radius != 0:
            # tmp is a list of list of arrays
            d = 2*radius
            cell_points = [ self.get_points_in_rect((px-radius,py-radius,d,d))
                                for (px,py) in pointlist ]
        else:
            indices = self._get_indices_for_points(pointlist)
            cells = [self._cellgrid[i,j] for (i,j) in indices]
            self._last_region = self._cells_to_rects(indices)
            # unique-ify the list of cells
            cell_points = [c.get_points() for c in set(cells)]
        return vstack(cell_points)


    def get_points_in_rect(self, rect):
        x_span = (rect[0], rect[0]+rect[2])
        y_span = (rect[1], rect[1]+rect[3])
        min_i, max_i = searchsorted(self._cell_lefts, x_span) - 1
        min_j, max_j = searchsorted(self._cell_bottoms, y_span) - 1
        cellpts = [ self._cellgrid[i,j].get_points()
                        for i in range(min_i, max_i+1) \
                            for j in range(min_j, max_j+1) ]
        self._last_region = ( self._cell_lefts[min_i], self._cell_bottoms[min_j], \
                              (max_i - min_i + 1) * self._cell_extents[0], \
                              (max_j - min_j + 1) * self._cell_extents[1] )
        return vstack(cellpts)


    def get_last_region(self):
        return self._last_region

    #-------------------------------------------------------------------
    # AbstractDataMapper's abstract private methods
    #-------------------------------------------------------------------

    def _update_datamap(self):
        self._last_region = []
        # Create a new grid of the appropriate size, initialize it with new
        # Cell instance (of type self.celltype), and perform point insertion
        # on the new data.
        if self._data is None:
            self._cellgrid = array([], dtype=object)
            self._cell_lefts = array([])
            self._cell_bottoms = array([])
        else:
            num_x_cells, num_y_cells = self._calc_grid_dimensions()
            self._cellgrid = zeros((num_x_cells, num_y_cells), dtype=object)
            for i in range(num_x_cells):
                for j in range(num_y_cells):
                    self._cellgrid[i,j] = self.celltype(parent=self)
            ll, ur = self._extents
            cell_width = ur[0]/num_x_cells
            cell_height = ur[1]/num_y_cells

            # calculate the left and bottom edges of all the cells and store
            # them in two arrays
            self._cell_lefts = arange(ll[0], ll[0]+ur[0]-cell_width/2, step=cell_width)
            self._cell_bottoms = arange(ll[1], ll[1]+ur[1]-cell_height/2, step=cell_height)

            self._cell_extents = (cell_width, cell_height)

            # insert the data points
            self._basic_insertion(self.celltype)
        return

    def _clear(self):
        self._last_region = []
        self._cellgrid = []
        self._cell_lefts = []
        self._cell_bottoms = []
        self._cell_extents = (0,0)
        return

    def _sort_order_changed(self, old, new):
        # since trait event notification only happens if the value has changed,
        # and there are only two types of sorting, it's safe to just reverse our
        # internal _data object
        self._data = self._data[::-1]
        for cell in self._cellgrid:
            # since cellgrid is a Numeric array, iterating over it produces
            # a length-1 array
            cell[0].reverse_indices()
        return


    #-------------------------------------------------------------------
    # helper private methods
    #-------------------------------------------------------------------

    def _calc_grid_dimensions(self):
        numpoints = self._data.shape[0]
        numcells = numpoints / self._points_per_cell
        ll, ur = self._extents
        aspect_ratio = (ur[0]-ll[0]) / (ur[1]-ll[1])
        num_y_cells = int(math.sqrt(numcells / aspect_ratio))
        num_x_cells = int(aspect_ratio * num_y_cells)
        if num_y_cells == 0:
            num_y_cells += 1
        if num_y_cells*num_x_cells*self._points_per_cell < numpoints:
            num_x_cells += 1
        return (num_x_cells, num_y_cells)

    def _basic_insertion(self, celltype):
        # generate a list of which cell each point in self._data belongs in
        cell_indices = self._get_indices_for_points(self._data)

        # We now look for ranges of points belonging to the same cell.
        # 1. shift lengthwise and difference; runs of cells with the same
        # (i,j) indices will be zero, and nonzero value for i or j will
        # indicate a transition to a new cell.  (Just like find_runs().)
        differences = cell_indices[1:] - cell_indices[:-1]

        # Since nonzero() only works for 1D arrays, we merge the X and Y columns
        # together to detect any point where either X or Y are nonzero.  We have
        # to add 1 because we shifted cell_indices before differencing (above).
        diff_indices = nonzero(differences[:,0] + differences[:,1])[0] + 1

        start_indices = concatenate([[0], diff_indices])
        end_indices = concatenate([diff_indices, [len(self._data)]])

        for start,end in zip(start_indices, end_indices):
            gridx, gridy = cell_indices[start]  # can use 'end' here just as well
            if celltype == RangedCell:
                self._cellgrid[gridx,gridy].add_ranges([(start,end)])
            else:
                self._cellgrid[gridx,gridy].add_indices(range(start,end))
        return

    def _get_indices_for_points(self, pointlist):
        """
        Given an input Nx2 array of points, returns a list Nx2 corresponding
        to the column and row indices into the cell grid.
        """
        x_array = searchsorted(self._cell_lefts, pointlist[:,0]) - 1
        y_array = searchsorted(self._cell_bottoms, pointlist[:,1]) - 1
        return array_zip(x_array, y_array)


    def _cells_to_rects(self, cells):
        """
        Converts the extents of a list of cell grid coordinates (i,j) into
        a list of rect tuples (x,y,w,h).  The set should be disjoint, but may
        or may not be minimal.
        """
        # Since this function is generally used to generate clipping regions
        # or other screen-related graphics, we should try to return large
        # rectangular blocks if possible.
        # For now, we just look for horizontal runs and return those.
        cells = array(cells)
        y_sorted = sort_points(cells, index=1)  # sort acoording to row
        rownums = sort(array(tuple(set(cells[:,1]))))

        row_start_indices = searchsorted(y_sorted[:,1], rownums)
        row_end_indices = left_shift(row_start_indices, len(cells))

        rects = []
        for rownum, start, end in zip(rownums, row_start_indices, row_end_indices):
            # y_sorted is sorted by the J (row) coordinate, so after we
            # extract the column indices, we need to sort them before
            # passing them to find_runs().
            grid_column_indices = sort(y_sorted[start:end][:,0])
            #pdb.set_trace()
            #print grid_column_indices.shape
            for span in find_runs(grid_column_indices):
                x = self._cell_lefts[span[0]]
                y = self._cell_bottoms[rownum]
                w = (span[-1] - span[0] + 1) * self._cell_extents[0]
                h = self._cell_extents[1]
                rects.append((x,y,w,h))
        return rects

    #~ def _array_insertion(self, celltype):
        #~ # use searchsorted() to determine where the borders split the
        #~ # data array
        #~ x_bins = searchsorted(data[:,0], self._cell_lefts[1:])
        #~ x_bins_rshift = right_shift(x_bins, 0)
        #~ grid_x = 0
        #~ for x_index_range in zip(x_bins_rshift, x_bins):
            #~ # now do the same thing in y; the tricky part is remembering
            #~ # to use axis=1 since everything happens on the y-coordinate
            #~ columnpoints = data[x_index_range[0] : x_index_range[1]]
            #~ columnpoints = take(columnpoints, argsort(columnpoints[:,1]))

            #~ # use searchsorted() to determine where the cell bottoms split the
            #~ # set of column points.
            #~ y_bins = searchsorted(columnpoints[:,1], self._cell_bottoms)
            #~ y_bins_rshift = right_shift(y_bins, 0)
            #~ grid_y = 0
            #~ for startndx, endndx in zip(y_bins_rshift, y_bins):
                #~ if startndx != endndx:
                    #~ cell = self._cellgrid[grid_x, grid_y]
                    #~ cellpts = columnpoints[startndx:endndx]
                    #~ if cell.sort_order == 'none':
                        #~ cell.points = cellpts
                    #~ elif cell.sort_order == 'ascending':
                        #~ cell.points = find_runs(sort_points(cellpts))
                    #~ elif cell.sort_order == 'descending':
                        #~ cell.points = find_runs(sort_points(cellpts)[::-1], 'descending')
                    #~ else:
                        #~ raise RuntimeError, "Invalid sort_order: " + cell.sort_order
        #~ return

class SubdivisionLineDataMapper(SubdivisionDataMapper):
    """ A subdivision data mapper that uses ranged cells.
    """
    celltype = RangedCell


#EOF
