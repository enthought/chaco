""" Generate parameteric colormaps.

Diverging colormaps can be generated via Kenneth Moreland's procedure using
``generate_diverging_palette()``.

    Moreland, Kenneth. Diverging Color Maps for Scientific Visualization
    (Expanded).
    http://www.sandia.gov/~kmorel/documents/ColorMaps/ColorMapsExpanded.pdf

Dave Green's cubehelix family of colormaps can be generated using
``generate_cubehelix_palette()``.

    Green, D. A., 2011, A colour scheme for the display of astronomical
    intensity images. Bulletin of the Astronomical Society of India, 39, 289.
    (2011BASI...39..289G at ADS.)
    http://adsabs.harvard.edu/abs/2011arXiv1108.5083G
    https://www.mrao.cam.ac.uk/~dag/CUBEHELIX/
"""

import numpy as np

from .color_spaces import msh2xyz, srgb2xyz, xyz2msh, xyz2srgb


def adjust_hue(msh_sat, m_unsat):
    """Adjust the hue when interpolating to an unsaturated color.

    Parameters
    ----------
    msh_sat : float array (3,)
        Saturated Msh color at an endpoint of the colormap.
    m_unsat : float
        The magnitude of the target unsaturated color.

    Returns
    -------
    h_adjusted : float
        The adjusted target hue value.
    """
    m_sat, s_sat, h_sat = msh_sat
    if m_sat >= m_unsat:
        return h_sat
    else:
        spin = (
            s_sat
            * np.sqrt(m_unsat * m_unsat - m_sat * m_sat)
            / (m_sat * np.sin(s_sat))
        )
        if h_sat > -np.pi / 3:
            return h_sat + spin
        else:
            return h_sat - spin


def generate_diverging_palette(srgb1, srgb2, n_colors=256):
    """Generate a diverging color palette with two endpoint colors.

    Parameters
    ----------
    srgb1, srgb2 : float array (3,)
        RGB colors for the endpoints. An unsaturated white/grey color will be
        in the middle.
    n_colors : int, optional
        The number of colors to generate in the palette.

    Returns
    -------
    srgb_palette : float array (n_colors, 3)
        RGB color palette.
    """
    m1, s1, h1 = np.squeeze(xyz2msh(srgb2xyz([srgb1])))
    m2, s2, h2 = np.squeeze(xyz2msh(srgb2xyz([srgb2])))
    mmid = max(m1, m2, 88.0)
    hmid1 = 0.0
    hmid2 = 0.0

    x = np.linspace(0.0, 1.0, n_colors)
    # srgb1 -> white
    half1 = 2 * x[x <= 0.5]
    # white -> srgb2
    half2 = 2 * x[x > 0.5] - 1.0
    if s1 > 0.05:
        hmid1 = adjust_hue((m1, s1, h1), mmid)
    if s2 > 0.05:
        hmid2 = adjust_hue((m2, s2, h2), mmid)

    m_palette = np.hstack(
        [
            half1 * mmid + (1 - half1) * m1,
            half2 * m2 + (1 - half2) * mmid,
        ]
    )
    s_palette = np.hstack(
        [
            (1 - half1) * s1,
            half2 * s2,
        ]
    )
    h_palette = np.hstack(
        [
            half1 * hmid1 + (1 - half1) * h1,
            half2 * h2 + (1 - half2) * hmid2,
        ]
    )
    msh_palette = np.column_stack([m_palette, s_palette, h_palette])
    srgb_palette = xyz2srgb(msh2xyz(msh_palette)).clip(0.0, 1.0)
    return srgb_palette


def generate_cubehelix_palette(
    start=0.5,
    rot=-1.5,
    saturation=1.2,
    lightness_range=(0.0, 1.0),
    gamma=1.0,
    n_colors=256,
):
    """Generate a sequential color palette from black to white spiraling
    through intermediate colors.

    Parameters
    ----------
    start : float between 0.0 and 3.0, optional
        The starting hue. 0 is blue, 1 is red, 2 is green.
    rot : float, optional
        How many rotations to go in hue space.
    saturation : float, optional
        The saturation intensity factor.
    lightness_range : (float, float), optional
        The range of lightness values to interpolate between.
    gamma : float, optional
        The gamma exponent adjustment to apply to the lightness values.
    n_colors : int, optional
        The number of colors to generate in the palette.

    Returns
    -------
    srgb_palette : float array (n_colors, 3)
        RGB color palette.
    """
    x = np.linspace(lightness_range[0], lightness_range[1], n_colors)
    theta = 2.0 * np.pi * (start / 3.0 + rot * x + 1.0)
    x **= gamma
    amplitude = saturation * x * (1 - x) / 2.0
    red = x + amplitude * (-0.14861 * np.cos(theta) + 1.78277 * np.sin(theta))
    green = x + amplitude * (
        -0.29227 * np.cos(theta) - 0.90649 * np.sin(theta)
    )
    blue = x + amplitude * (1.97294 * np.cos(theta))
    srgb_palette = np.column_stack([red, green, blue]).clip(0.0, 1.0)
    return srgb_palette
