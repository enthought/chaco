.. _matplotlib2chaco:

##############################
Matplotlib to Chaco Cheatsheet
##############################
As mentioned in the :ref:`Chaco Tutorial <tutorial>`,
`matplotlib <https://matplotlib.org/>`_ and Chaco have different
approaches to plotting (script-oriented vs. application-oriented). However, new
users of Chaco who have worked with matplotlib in the past may find it useful
to think about mapping "equivalent" code between the two.

The following table lists various plotting related operations one might want to
perform along with code for doing that using either Chaco or matplotlib. For
the matplotlib code ``ax`` represents the Plot Axes
i.e. ``fig, ax = plt.subplots()`` after importing
``import matplotlib.pyplot as plt``. For more details see the
`matplotlib User's Guide <https://matplotlib.org/stable/users/index.html>`_.
For Chaco code, ``p`` is the :class:`~.Plot` instance.  ``x`` and ``y`` are the
data to be plotted. In Chaco, this data needs to be wrapped in a
``PlotData`` object. For example,

::

    import numpy as np
    x = np.linspace(-2*np.pi, 2*np.pi, 100)
    y = sin(x)

    # Chaco only
    pd = ArrayPlotData()
    pd.set_data("x", x)
    pd.set_data("y", y)
    p = Plot(pd)

Note that in the matplotlib column, ``x`` and ``y`` represent the data, but
``'x'`` and ``'y'``, such as in the "X grid" and "Y Grid" rows are simply
options for the ``axis`` argument. In Chaco ``'x'`` and ``'y'`` are the names
the ``PlotData`` object associates with numpy arrays ``x`` and ``y``.

.. list-table:: Matplotlib To Chaco Cheatsheet
    :widths: 25 40 50
    :header-rows: 1

    * - What
      - Matplotlib
      - Chaco
    * - Plot lines
      - ``ax.plot(x, y)``
      - ``p.plot(('x', 'y'))``
    * - x label
      - ``ax.set_xlabel('Time')``
      - ``p.x_axis.title = 'Time'``
    * - y label
      - ``ax.set_ylabel('Value')``
      - ``p.y_axis.title = 'Value'``
    * - Title
      - ``ax.set_title(title)``
      - ``p.title = title``
    * - X limits
      - ``ax.set_xlim((low, high))``
      - ``p.index_range.low_setting = low`` ``p.index_range.high_setting = high``
    * - Y limits
      - ``ax.set_ylim((low, high))``
      - ``p.value_range.low_setting = low`` ``p.value_range.high_setting = high``
    * - Label lines for legend
      - ``ax.plot(…, label=label)``
      - ``p.plot(…, name=name)``
    * - Add legend
      - ``ax.legend()``
      - ``p.legend.visible = True``
    * - Legend position
      - ``ax.legend(loc='lower left')``
      - ``p.legend_alignment = 'll'``
    * - Background color
      - ``ax.set_facecolor('white')``
      - ``p.bgcolor = 'white'``
    * - Show spines
      - ``ax.spines.set_color('black')``
      - ``p.border_visible = True``
    * - Line width
      - ``ax.plot(linewidth=lw)``
      - ``p.line_width = 1.1`` or ``p.plot(…, linewidth=lw)``
    * - X grid
      - ``ax.grid(axis='x')``
      - ``p.x_axis.visible = True``
    * - Y grid
      - ``ax.grid(axis='y')``
      - ``p.y_axis.visible = True``
    * - Second y ticks
      - ``ax.yaxis.set_label_position('right')`` ``ax.yaxis.tick_right()``
      - ``p.y_axis.orientation = "right"``
