#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
"""


# os+plt imports right after __future__
# import os
# import matplotlib as mpl
# if os.environ.get('DISPLAY', '') == '':
#     print('no display found. Using non-interactive Agg backend')
#     mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import gridspec

import numpy as np

from .utils import Timestamp

__author__ = "Andres FR"


# #############################################################################
# ## GLOBALS
# #############################################################################


# #############################################################################
# ## HELPERS
# #############################################################################


# #############################################################################
# ## PLOTTER CLASSES
# #############################################################################


class AudioPlotter(object):
    """
    This class generates matplotlib figures that plot 1-dimensional
    arrays. Since audio arrays can be quite long, it features a built-in
    downsampling mechanism that plots a (configurable) number of points
    at most. The downsampling mechanism is based on this code:

    https://matplotlib.org/3.1.0/gallery/event_handling/resample.html

    .. note::

      The downsampling mechanism only affects the display, not the data,
      and is refreshed every time the user changes the perspective.
      If the user zooms close enough the data will be displayed in its
      original form. Therefore downsampling helps to provide a quicker
      interaction when scrolling large files, while allowing for
      sample-precise inspection.
    """

    def __init__(self, arr, max_datapoints=10000, samplerate=None):
        """
        :param ndarray arr: Expected to be a 1-dimensional numpy array
          holding the sequence to be displayed
        :param int max_datapoints: Expected to be a positive integer,
          the number of plotted datapoints for a given view of the array
          will (approximately) match this number.
        :param int samplerate: (optional). If not None, the x-axis
          will be displayed in seconds, 1 second corresponding to
          this number of samples. If None, the x-axis will be in samples.
        """
        assert len(arr.shape) == 1, "1D array expected!"
        assert max_datapoints > 0, "positive max_datapoints expected"
        self.arr = arr
        self.arange = np.arange(len(arr))
        self.max_datapoints = max_datapoints
        self.samplerate = samplerate

    def _downsample_arr(self, xstart, xend):
        """
        Reference:
        https://matplotlib.org/3.1.0/gallery/event_handling/resample.html
        """
        # get the points in the view range
        mask = (self.arange > xstart) & (self.arange < xend)
        # dilate the mask by one to catch the points just outside
        # of the view range to not truncate the line
        mask = np.convolve([1, 1], mask, mode='same').astype(bool)
        # sort out how many points to drop
        ratio = int(max(np.sum(mask) // self.max_datapoints, 1))
        # mask data
        xdata = self.arange[mask]
        ydata = self.arr[mask]
        # downsample data
        xdata = xdata[::ratio]
        ydata = ydata[::ratio]
        print("using {} of {} visible points".format(
            len(ydata), np.sum(mask)))
        return xdata, ydata

    def _update_ax(self, ax):
        """
        Reference:
        https://matplotlib.org/3.1.0/gallery/event_handling/resample.html
        """
        # Update the line
        lims = ax.viewLim
        xstart, xend = lims.intervalx
        self.axx.set_data(*self._downsample_arr(xstart, xend))
        ax.figure.canvas.draw_idle()

    def make_fig(self, num_xticks=10, num_yticks=10, tick_fontsize=7):
        """
        :returns: A matplotlib Figure containing the array given at
          construction. The interactive plot of the figure will react
          to the user's zooming by showing approximately
          ``self.max_datapoints`` number of samples.

        Reference:
        https://matplotlib.org/3.1.0/gallery/event_handling/resample.html
        """
        fig, ax = plt.subplots()
        self.axx, = ax.plot(self.arange, self.arr, '-')
        # set number of ticks
        ax.locator_params(axis="x", nbins=num_xticks)
        ax.locator_params(axis="y", nbins=num_yticks)
        #
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=30,
                 fontsize=tick_fontsize, family="DejaVu Sans", ha="right")
        plt.setp(ax.yaxis.get_majorticklabels(),
                 fontsize=tick_fontsize, family="DejaVu Sans")

        ax.set_autoscale_on(False)  # Otherwise, infinite loop
        ax.callbacks.connect('xlim_changed', self._update_ax)
        ax.set_xlim(0, len(self.arr))
        ax.xaxis.grid(True)


        if self.samplerate is not None:
            def formatter(val, pos):
                """
                This function can be passed to ``plt.FuncFormatter``
                to generate custom tick labels. It fulfills the interface
                (val, pos) -> str.

                Specifically, given a ``val`` representing a sample,
                returns a string showing the corresponding elapsed time
                since sample 0, asuming ``self.samplerate``.

                :param number val: the axis value where the tick goes
                :param int pos: from 0 (left margin) to num_ticks+2 (right
                  margin)
                :returns: A string in the form "{X days} h:m:s.ms"

                Usage example::
                  ax.xaxis.set_major_formatter(plt.FuncFormatter(fn))
                """
                ts = Timestamp(val, self.samplerate)
                ts_str = str(ts)[:-3]  # keep up to miliseconds only
                return ts_str
            ax.xaxis.set_major_formatter(plt.FuncFormatter(formatter))
        return fig




class MultiTrackPlotter(object):
    """
    """
    # plt.rcParams["patch.force_edgecolor"] = True
    FIG_ASPECT_RATIO = (10, 8)
    # FIG_WIDTH_RATIOS = [5, 5]
    # # FIG_HEIGHT_RATIOS = [10,3,10] # line, margin, line
    # FIG_MARGINS = {"top":0.8, "bottom":0.2, "left":0.1, "right":0.9}
    FIG_MARGINS = {"top": 0.8, "bottom": 0.05, "left": 0.05, "right": 0.95,
                   "hspace": 0.5, "wspace": 0.5}
    # RATIO_RANGE_AXIS = 1.15 # FOR 1.0, THE AXIS WILL COVER EXACTLY UNTIL THE MAXIMUM
    # RATIO_LABELS_DISTANCE = 0.02 # 0.05 MEANS THE DISTANCE BETWEEN BARS AND LABELS IS 5% OF THE AXIS
    # #
    FIG_TITLE_FONTSIZE = 15
    # AX_TITLE_FONTSIZE = 18
    # # TABLE_FONTSIZE = 9
    # TICKS_FONTSIZE = 15
    # CONFMAT_NUMBER_COLOR = "cyan"
    # CONFMAT_NUMBER_FONTSIZE = 12
    # NUM_YTICKS = 13
    # LABELS_FONTSIZE = 12
    # LEGEND_FONTSIZE = 15
    # BAR_WIDTH = 0.85
    # FPOS_COLOR = "#b0b000"
    # FNEG_COLOR = "#e6194b"


    def __init__(self):
        """
        """
        pass

    def make_fig(self, fig_title, audio_arr, total, x_shared):
        """
        """
        # define and configure plt figure
        fig = plt.figure(figsize=self.FIG_ASPECT_RATIO)
        gs = list(gridspec.GridSpec(total, 1))
        axes = [plt.subplot(gs[0])]
        # add shared-x axes
        axes += [plt.subplot(gsi, sharex=axes[0])
                 for gsi in gs[1: x_shared]]
        # add remaining axes:
        axes += [plt.subplot(gsi) for gsi in gs[x_shared:]]

        #
        info = "\nNo. axes=%d, dep. axes=%d" % (total, x_shared)
        fig.suptitle(fig_title + info, fontsize=self.FIG_TITLE_FONTSIZE,
                     fontweight="bold")
        fig.canvas.set_window_title(fig_title)

        axes[0].plot(audio_arr)

        for ax in axes[1:]:
            ax.plot(range(10), range(10))
        fig.subplots_adjust(**self.FIG_MARGINS)
        return fig



        #     # add ticks with class names to the conf matrix
        # y_ticks = [nm + " (acc="+ self._float_to_str(acc) + ")"
        #            for nm, acc in tickdata]
        # x_ticks = [nm for nm, _ in tickdata]
        # ax.set_yticks(range(conf_arr.shape[0]))
        # ax.set_yticklabels(y_ticks, fontsize=self.TICKS_FONTSIZE,
        #                    family="DejaVu Sans")
        # ax.set_xticks(range(conf_arr.shape[1]))
        # ax.set_xticklabels(x_ticks, fontsize=self.TICKS_FONTSIZE,
        #                    family="DejaVu Sans", rotation=30, ha="right")
