.. _matplotlib2chaco:

##############################
Matplotlib To Chaco Cheatsheet
##############################
As mentioned in the :ref:`Chaco Tutorial <tutorial>`,
`matplotlib <https://matplotlib.org/>`_ and Chaco have different
approaches to plotting (script-oriented vs. application oriented). However, new
users of chaco who have worked with matplotlib in the past may find it useful
to think about mapping "equivalent" code between the two.

The following table lists various plotting related operations one might want to
perform along with code for doing that using either Chaco or Matplotlib. For
the Matplotlib code ``ax`` repesents the Plot Axes
i.e. ``fig, ax = plt.subplots()`` after importing
``import matplotlib.pyplot as plt``. For more details see the
`matplotlib User's Guide <https://matplotlib.org/stable/users/index.html>`_.
For Chaco code, ``p`` is the :class:`~.Plot` instance.

+------------------------+------------------------------------------+------------------------------------------------------------------------+
|          What          |                matplotlib                |                                 Chaco                                  |
+========================+==========================================+========================================================================+
|       Plot lines       |             `ax.plot(x, y)`              |                          `p.plot(('x', 'y'))`                          |
+------------------------+------------------------------------------+------------------------------------------------------------------------+
|        x label         |         `ax.set_xlabel('Time')`          |                        `p.x_axis.title = 'Time'`                       |
+------------------------+------------------------------------------+------------------------------------------------------------------------+
|        y label         |         `ax.set_ylabel('Value')`         |                       `p.y_axis.title = 'Value'`                       |
+------------------------+------------------------------------------+------------------------------------------------------------------------+
|         Title          |          `ax.set_title(title)`           |                           `p.title = title`                            |
+------------------------+------------------------------------------+------------------------------------------------------------------------+
|        X limits        |        `ax.set_xlim((low, high))`        |                   `p.index_range.low_setting = LOW`                    |
|                        |                                          |                   `p.index_range.high_setting = HIGH`                  |
+------------------------+------------------------------------------+------------------------------------------------------------------------+
|        Y limits        |        `ax.set_ylim((low, high))`        |                   `p.value_range.low_setting = LOW`                    |
|                        |                                          |                   `p.value_range.high_setting = HIGH`                  |
+------------------------+------------------------------------------+------------------------------------------------------------------------+
| Label lines for legend |       `ax.plot(…, label=label)`          |                        `p.plot(…, name=name)`                          |
+------------------------+------------------------------------------+------------------------------------------------------------------------+
|       Add legend       |              `ax.legend()`               |                       `p.legend.visible = True`                        |
+------------------------+------------------------------------------+------------------------------------------------------------------------+
|    Legend position     |      `ax.legend(loc='lower left')`       |                      `p.legend_alignment = 'll'`                       |
+------------------------+------------------------------------------+------------------------------------------------------------------------+
|    Background color    |        ax.set_facecolor('white')         |                          `p.bgcolor = 'white'`                         |
+------------------------+------------------------------------------+------------------------------------------------------------------------+
|      Show spines       |      ax.spines.set_color('black')        |                       `p.border_visible = True`                        |
+------------------------+------------------------------------------+------------------------------------------------------------------------+
|       Line width       |         `ax.plot(linewidth=lw)`          |           `p.line_width = 1.1` or `p.plot(…, linewidth=lw)`            |
+------------------------+------------------------------------------+------------------------------------------------------------------------+
|         X grid         |           `ax.grid(axis='x')`            |                       `p.x_axis.visible = True`                        |
+------------------------+------------------------------------------+------------------------------------------------------------------------+
|         Y grid         |           `ax.grid(axis='y')`            |                       `p.y_axis.visible = True`                        |
+------------------------+------------------------------------------+------------------------------------------------------------------------+
|     Second y ticks     |  `ax.yaxis.set_label_position('right')`  |                   `p.y_axis.orientation = "right"`                     |
|                        |         `ax.yaxis.tick_right()`          |                                                                        |
+------------------------+------------------------------------------+------------------------------------------------------------------------+
