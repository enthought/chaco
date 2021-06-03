# (C) Copyright 2005-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Conversion functions between various color spaces.

The implementations and data are mostly taken from the old
scipy.sandbox.image package.

The CIE XYZ tristimulus colorspace with a standard D65 whitepoint is the
default interchange color space for the implementations here. This is
a useful whitepoint for viewing on computer monitors. However, it should
be noted that the dimmer D50 whitepoint is often used in print
applications. Notably, ICC profiles use the XYZ space with a D50
whitepoint as one of its standard interchange color spaces.
"""

import numpy as np
from numpy.linalg import inv, solve


#### Utilities ################################################################


def convert(matrix, TTT, axis=-1):
    """Apply linear matrix transformation to an array of color triples.

    Parameters
    ----------
    matrix : float array (3, 3)
        The transformation to apply.
    TTT : float array
        The set of colors to transform.
    axis : int, optional
        The axis of `TTT` along which the color triples extend.

    Returns
    -------
    OUT : float array
        The transformed colors.
    """
    TTT = np.asarray(TTT)
    if axis != 0:
        TTT = np.swapaxes(TTT, 0, axis)
    oldshape = TTT.shape
    TTT = np.reshape(TTT, (3, -1))
    OUT = np.dot(matrix, TTT)
    OUT.shape = oldshape
    if axis != 0:
        OUT = np.swapaxes(OUT, axis, 0)
    return OUT


def makeslices(n):
    """Return a list of `n` slice objects.

    Each slice object corresponds to [:] without arguments.
    """
    slices = [slice(None)] * n
    return slices


def separate_colors(xyz, axis=-1):
    """Separate an array of color triples into three arrays, one for
    each color axis.

    Parameters
    ----------
    xyz : float array
    axis : int, optional
        The axis along which the color triples extend.

    Returns
    -------
    x : float array
    y : float array
    z : float array
        The separate color arrays.
    axis : int
        The axis along which they need to be reassembled.
    """
    n = len(xyz.shape)
    if axis < 0:
        axis = n + axis
    slices = makeslices(n)
    slices[axis] = 0
    x = xyz[tuple(slices)]
    slices[axis] = 1
    y = xyz[tuple(slices)]
    slices[axis] = 2
    z = xyz[tuple(slices)]

    return x, y, z, axis


def join_colors(c1, c2, c3, axis):
    """Rejoin the separated colors into a single array."""
    c1 = np.asarray(c1)
    c2 = np.asarray(c2)
    c3 = np.asarray(c3)
    newshape = c1.shape[:axis] + (1,) + c1.shape[axis:]
    c1.shape = c2.shape = c3.shape = newshape
    return np.concatenate((c1, c2, c3), axis=axis)


def triwhite(x, y):
    """Convert x,y chromaticity coordinates to XYZ tristimulus values."""
    X = x / y
    Y = 1.0
    Z = (1 - x - y) / y
    return [X, Y, Z]


#### Data #####################################################################

# From the sRGB specification.
xyz_from_rgb = np.array(
    [
        [0.412453, 0.357580, 0.180423],
        [0.212671, 0.715160, 0.072169],
        [0.019334, 0.119193, 0.950227],
    ]
)
rgb_from_xyz = inv(xyz_from_rgb)


# XYZ white-point coordinates
#  from http://en.wikipedia.org/wiki/Standard_illuminant
whitepoints = {
    "CIE A": ["Normal incandescent", triwhite(0.44757, 0.40745)],
    "CIE B": ["Direct sunlight", triwhite(0.34842, 0.35161)],
    "CIE C": ["Average sunlight", triwhite(0.31006, 0.31616)],
    "CIE E": ["Normalized reference", triwhite(1.0 / 3, 1.0 / 3)],
    "D50": ["Bright tungsten", triwhite(0.34567, 0.35850)],
    "D55": ["Cloudy daylight", triwhite(0.33242, 0.34743)],
    "D65": ["Daylight", triwhite(0.31271, 0.32902)],
    "D75": ["?", triwhite(0.29902, 0.31485)],
}


#### Conversion routines ######################################################


def xyz2lab(xyz, axis=-1, wp=whitepoints["D65"][-1]):
    """Convert XYZ tristimulus values to CIE L*a*b*.

    Parameters
    ----------
    xyz : float array
        XYZ values.
    axis : int, optional
        The axis of the XYZ values.
    wp : list of 3 floats, optional
        The XYZ tristimulus values of the whitepoint.

    Returns
    -------
    lab : float array
        The L*a*b* colors.
    """
    x, y, z, axis = separate_colors(xyz, axis)
    xn, yn, zn = x / wp[0], y / wp[1], z / wp[2]

    def f(t):
        eps = 216 / 24389.0
        kap = 24389 / 27.0
        return np.where(t > eps, np.power(t, 1.0 / 3), (kap * t + 16.0) / 116)

    fx, fy, fz = f(xn), f(yn), f(zn)
    L = 116 * fy - 16
    a = 500 * (fx - fy)
    b = 200 * (fy - fz)

    return join_colors(L, a, b, axis)


def lab2xyz(lab, axis=-1, wp=whitepoints["D65"][-1]):
    """Convert CIE L*a*b* colors to XYZ tristimulus values.

    Parameters
    ----------
    lab : float array
        L*a*b* values.
    axis : int, optional
        The axis of the XYZ values.
    wp : list of 3 floats, optional
        The XYZ tristimulus values of the whitepoint.

    Returns
    -------
    xyz : float array
        The XYZ colors.
    """
    lab = np.asarray(lab)
    L, a, b, axis = separate_colors(lab, axis)
    fy = (L + 16) / 116.0
    fz = fy - b / 200.0
    fx = a / 500.0 + fy

    def finv(y):
        eps3 = (216 / 24389.0) ** 3
        kap = 24389 / 27.0
        return np.where(y > eps3, np.power(y, 3), (116 * y - 16) / kap)

    xr, yr, zr = finv(fx), finv(fy), finv(fz)

    return join_colors(xr * wp[0], yr * wp[1], zr * wp[2], axis)


#  RGB values that will be displayed on a screen are always nonlinear
#  R'G'B' values.  To get the XYZ value of the color that will be
#  displayed you need a calibrated monitor with a profile.
#  But, for quick-and-dirty calculation you can often assume the standard
#  sR'G'B' coordinate system for your computer, and so the rgbp2rgb will
#  put you in the linear coordinate system (assuming normalized to [0,1]
#  sR'G'B' coordinates)
#

# sRGB <-> sR'G'B'  equations from
#   http://www.w3.org/Graphics/Color/sRGB
#   http://www.srgb.com/basicsofsrgb.htm

# Macintosh displays are usually gamma = 1.8


def rgb2rgbp(rgb, gamma=None):
    """Convert linear RGB coordinates to nonlinear R'G'B' coordinates.

    Parameters
    ----------
    rgb : float array
    gamma : float, optional
        If provided, then this value of gamma will be used to correct the
        colors. If not provided, then the standard sR'G'B' space will be
        assumed. It is almost, but not quite equivalent to a gamma of 2.2.

    Returns
    -------
    rgbp : float array
    """
    rgb = np.asarray(rgb)
    if gamma is None:
        eps = 0.0031308
        mask = rgb < eps
        rgbp = np.empty_like(rgb)
        rgbp[mask] = 12.92 * rgb[mask]
        rgbp[~mask] = 1.055 * rgb[~mask] ** (1.0 / 2.4) - 0.055
        return rgbp
    else:
        return rgb ** (1.0 / gamma)


def rgbp2rgb(rgbp, gamma=None):
    """Convert nonlinear R'G'B' coordinates to linear RGB coordinates.

    Parameters
    ----------
    rgbp : float array
    gamma : float, optional
        If provided, then this value of gamma will be used to correct the
        colors. If not provided, then the standard sR'G'B' space will be
        assumed. It is almost, but not quite equivalent to a gamma of 2.2.

    Returns
    -------
    rgb : float array
    """
    rgbp = np.asarray(rgbp)
    if gamma is None:
        eps = 0.04045
        mask = rgbp <= eps
        rgb = np.empty_like(rgbp)
        rgb[mask] = rgbp[mask] / 12.92
        rgb[~mask] = ((rgbp[~mask] + 0.055) / 1.055) ** 2.4
        return rgb
    else:
        return rgbp ** gamma


def xyz2rgb(xyz, axis=-1):
    """Convert XYZ tristimulus values to linear RGB coordinates.

    Parameters
    ----------
    xyz : float array
        XYZ values.
    axis : int, optional
        The axis of the XYZ values.

    Returns
    -------
    rgb : float array
        The RGB colors.
    """
    return convert(rgb_from_xyz, xyz, axis)


def rgb2xyz(rgb, axis=-1):
    """Convert linear RGB coordinates to XYZ tristimulus values.

    Parameters
    ----------
    rgb : float array
        RGB values.
    axis : int, optional
        The axis of the XYZ values.

    Returns
    -------
    xyz : float array
        The XYZ colors.
    """
    return convert(xyz_from_rgb, rgb, axis)


def srgb2xyz(srgb, axis=-1):
    """Convert sR'G'B' colors to XYZ.

    Parameters
    ----------
    srgb : float array
        sR'G'B' values.
    axis : int, optional
        The axis of the XYZ values.

    Returns
    -------
    xyz : float array
        The XYZ colors.
    """
    return rgb2xyz(rgbp2rgb(srgb), axis=axis)


def xyz2srgb(xyz, axis=-1):
    """Convert XYZ colors to sR'G'B'.

    Parameters
    ----------
    xyz : float array
        XYZ values.
    axis : int, optional
        The axis of the XYZ values.

    Returns
    -------
    srgb : float array
        The sR'G'B' colors.
    """
    return rgb2rgbp(xyz2rgb(xyz, axis=axis))


def xyz2xyz(xyz):
    """Identity mapping."""
    return xyz


def xyz2msh(xyz, axis=-1, wp=whitepoints["D65"][-1]):
    """Convert XYZ tristimulus values to Msh.

    Msh is a hemispherical coordinate system derived from L*a*b*. The
    origin remains the same. M is the distance from the origin. s is an
    inclination angle from the vertical corresponding to saturation.
    h is the azimuthal angle corresponding to hue.

    Moreland, Kenneth. Diverging Color Maps for Scientific Visualization
    (Expanded).
    http://www.sandia.gov/~kmorel/documents/ColorMaps/ColorMapsExpanded.pdf

    Parameters
    ----------
    xyz : float array
        XYZ values.
    axis : int, optional
        The axis of the XYZ values.
    wp : list of 3 floats, optional
        The XYZ tristimulus values of the whitepoint.

    Returns
    -------
    msh : float array
        The Msh colors.
    """
    L, a, b, axis = separate_colors(xyz2lab(xyz, axis=axis, wp=wp), axis)
    M = np.sqrt(L * L + a * a + b * b)
    s = np.arccos(L / M)
    h = np.arctan2(b, a)

    return join_colors(M, s, h, axis)


def msh2xyz(msh, axis=-1, wp=whitepoints["D65"][-1]):
    """Convert Msh values to XYZ tristimulus values.

    Parameters
    ----------
    msh : float array
        The Msh colors.
    axis : int, optional
        The axis of the XYZ values.
    wp : list of 3 floats, optional
        The XYZ tristimulus values of the whitepoint.

    Returns
    -------
    xyz : float array
        XYZ values.
    """
    M, s, h, axis = separate_colors(msh, axis)
    L = M * np.cos(s)
    a = M * np.sin(s) * np.cos(h)
    b = M * np.sin(s) * np.sin(h)

    return lab2xyz(join_colors(L, a, b, axis), axis=axis, wp=wp)
