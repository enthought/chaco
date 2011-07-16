"""
This module defines the basic projection classes usable by projection plots.
"""
import numpy

from traits.api import HasTraits, Array


class AbstractProjection(HasTraits):
    """ A Projection is a mapping from a model space into a 2D screen space.
    """
    
    def project(self, model_array):
        """ Project an array of data points from model space to data space, returning an
        array of data space points.
        """
        raise NotImplementedError
    
    def project_line(self, start, end, scale):
        """ Project a coordinate line from model space to data space.  Scale gives a hint
        about how refined curves need to be -  a segment of length scale can be rendered
        as a straight line (eg. it might be pixel-size).  Returns an Nx2 array of x,y points
        in data space.
        """
        raise NotImplementedError


class AffineProjection(AbstractProjection):
    """ A Projection which projects via a simple affine transformation on each point
    """

    # a  matrix that maps a higher dimension space to data space
    matrix = Array

    def project(self, model_array):
        return numpy.dot(matrix, numpy.array(model_array))
    
    def project_line(self, start, end, scale):
        return numpy.array([
            self.project(start),
            self.project(end)
        ])


class MatrixProjection(AffineProjection):
    """ A Projection which projects via a simple matrix transformation on each point
    """

    # a 2xM matrix that maps a higher dimension space to data space
    matrix = Array

    def project(self, model_array):
        return numpy.dot(matrix, numpy.array(model_array))
        

class IdentityProjection(MatrixProjection):
    def project(self, model_array):
        return model_array
    
    def project_line(self, start, end, scale):
        return numpy.array([start, end])


class PolarProjection(AbstractProjection):
    """ A projection which maps r, theta values to x, y values
    """
    def project(self, model_array):
        r = model_array[:,0]
        theta = model_array[:,1]
        x = r*numpy.cos(theta)
        y = r*numpy.sin(theta)
        print x, y
        return numpy.array([x, y]).T
    
    def project_line(self, start, end, scale):
        r1, theta1 = start
        r2, theta2 = end
        
        # here we are estimating the number of steps required.
        # Stepping in the r direction is done with steps of size scale
        # Stepping in the theta direction is done with steps of scale/r, r*theta is arc length
        #   - we use max abs r, rather than something adaptive
        # number of steps is then absolute difference minus step size ie.
        #   max(deleta_r/scale, delta_theta/theta_scale)
        # the following expression is what you get when you simplify for speed of computation.
        n = int(max(abs(r2-r1), abs(theta2-theta1)*max(abs(r1), abs(r2)))/scale) + 1
        
        return numpy.array([numpy.linspace(r1, r2, n), numpy.linspace(theta1, theta2, n)]).T
