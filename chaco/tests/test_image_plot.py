import os

import tempfile
from contextlib import contextmanager

import six

import unittest

import numpy as np

from traits.etsconfig.api import ETSConfig
from chaco.api import (PlotGraphicsContext, GridDataSource, GridMapper,
                       DataRange2D, ImageData, ImagePlot)


# The Quartz backend rescales pixel values, so use a higher threshold.
MAX_RMS_ERROR = 16 if ETSConfig.kiva_backend == 'quartz' else 1

IMAGE = np.random.random_integers(0, 255, size=(100, 200)).astype(np.uint8)
RGB = np.dstack([IMAGE] * 3)
# Rendering adds rows and columns for some reason.
TRIM_RENDERED = (slice(1, -1), slice(1, -1), 0)


@contextmanager
def temp_image_file(suffix='.tif', prefix='test', dir=None):
    fd, filename = tempfile.mkstemp(suffix=suffix, prefix=prefix, dir=dir)
    try:
        yield filename
    finally:
        os.close(fd)
        os.remove(filename)


def get_image_index_and_mapper(image):
    h, w = image.shape[:2]
    index = GridDataSource(np.arange(h+1), np.arange(w+1))
    index_mapper = GridMapper(range=DataRange2D(low=(0, 0), high=(h, w)))
    return index, index_mapper


def save_renderer_result(renderer, filename):
    renderer.padding = 0
    gc = PlotGraphicsContext(renderer.outer_bounds)
    with gc:
        gc.render_component(renderer)
        gc.save(filename)


def image_from_renderer(renderer, orientation):
    data = renderer.value
    # Set bounding box size and origin to align rendered image with array
    renderer.bounds = (data.get_width() + 1, data.get_height() + 1)
    if orientation == 'v':
        renderer.bounds = renderer.bounds[::-1]
    renderer.position = 0, 0

    with temp_image_file() as filename:
        save_renderer_result(renderer, filename)
        rendered_image = ImageData.fromfile(filename).data[TRIM_RENDERED]
    return rendered_image


def rendered_image_result(image, filename=None, **plot_kwargs):
    data_source = ImageData(data=image)
    index, index_mapper = get_image_index_and_mapper(image)
    renderer = ImagePlot(value=data_source, index=index,
                         index_mapper=index_mapper,
                         **plot_kwargs)
    orientation = plot_kwargs.get('orientation', 'h')
    return image_from_renderer(renderer, orientation)


def calculate_rms(image_result, expected_image):
    """Return root-mean-square error.

    Implementation taken from matplotlib.
    """
    # calculate the per-pixel errors, then compute the root mean square error
    num_values = np.prod(expected_image.shape)
    # Images may be e.g. 8-bit unsigned integer; upcast to default integer size
    # (32 or 64 bit) to reduce likelihood of over-/under-flow.
    abs_diff_image = abs(np.int_(expected_image) - np.int_(image_result))

    histogram = np.bincount(abs_diff_image.ravel(), minlength=256)
    sum_of_squares = np.sum(np.int64(histogram) * np.arange(len(histogram))**2)
    rms = np.sqrt(float(sum_of_squares) / num_values)
    return rms


def plot_comparison(input_image, expected_image, **plot_kwargs):
    import matplotlib.pyplot as plt

    image_result = rendered_image_result(input_image, **plot_kwargs)
    diff = np.int64(expected_image) - np.int64(image_result)
    max_diff = max(abs(diff.min()), abs(diff.max()), 1)

    fig, (ax0, ax1, ax2) = plt.subplots(ncols=3, sharex='all', sharey='all')
    ax0.imshow(expected_image)
    ax1.imshow(image_result)
    im_plot = ax2.imshow(diff, vmin=-max_diff, vmax=max_diff, cmap=plt.cm.bwr)
    fig.colorbar(im_plot)
    plt.show()


class TestResultImage(unittest.TestCase):

    def verify_result_image(self, input_image, expected_image, **plot_kwargs):
        # These tests were written assuming uint8 inputs.
        self.assertEqual(input_image.dtype, np.uint8)
        self.assertEqual(expected_image.dtype, np.uint8)
        image_result = rendered_image_result(input_image, **plot_kwargs)
        rms = calculate_rms(image_result, expected_image)
        self.assertLess(rms, MAX_RMS_ERROR)

    def test_horizontal_top_left(self):
        # Horizontal orientation with top left origin renders original image.
        self.verify_result_image(RGB, IMAGE, origin='top left')

    def test_horizontal_bottom_left(self):
        # Horizontal orientation with bottom left origin renders a vertically
        # flipped image.
        self.verify_result_image(RGB, IMAGE[::-1], origin='bottom left')

    def test_horizontal_top_right(self):
        # Horizontal orientation with top right origin renders a horizontally
        # flipped image.
        self.verify_result_image(RGB, IMAGE[:, ::-1], origin='top right')

    def test_horizontal_bottom_right(self):
        # Horizontal orientation with top right origin renders an image flipped
        # horizontally and vertically.
        self.verify_result_image(RGB, IMAGE[::-1, ::-1], origin='bottom right')

    def test_vertical_top_left(self):
        # Vertical orientation with top left origin renders transposed image.
        self.verify_result_image(RGB, IMAGE.T, origin='top left', orientation='v')

    def test_vertical_bottom_left(self):
        # Vertical orientation with bottom left origin renders transposed image
        # that is vertically flipped.
        self.verify_result_image(RGB, (IMAGE.T)[::-1],
                                 origin='bottom left', orientation='v')

    def test_vertical_top_right(self):
        # Vertical orientation with top right origin renders transposed image
        # that is horizontally flipped.
        self.verify_result_image(RGB, (IMAGE.T)[:, ::-1],
                                 origin='top right', orientation='v')

    def test_vertical_bottom_right(self):
        # Vertical orientation with bottom right origin renders transposed image
        # that is flipped vertically and horizontally.
        self.verify_result_image(RGB, (IMAGE.T)[::-1, ::-1],
                                 origin='bottom right', orientation='v')
