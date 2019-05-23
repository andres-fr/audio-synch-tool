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


def sample_to_timestamp_formatter(val, pos, samplerate):
    """
    This function can be passed to ``plt.FuncFormatter`` to generate custom
    tick labels. It fulfills the interface (val, pos) -> str.

    Specifically, converts ``val`` number representing a sample into a string
    showing the corresponding elapsed time since sample 0, asuming the given
    samplerate.

    :param number val: the axis value where the tick goes
    :param int pos: from 0 (left margin) to num_ticks+2 (right
      margin)
    :param number samplerate: A number so that seconds = val / samplerate
    :returns: A string in the form "{X days} h:m:s.ms"

    Usage example::
      ax.xaxis.set_major_formatter(plt.FuncFormatter(fn))
    """
    ts = Timestamp(val, samplerate)
    ts_str = str(ts)[:-3]  # keep up to miliseconds only
    return ts_str

# #############################################################################
# ## PLOTTER CLASSES
# #############################################################################


class DownsampledPlotter1D(object):
    """
    This class generates matplotlib figures that plot 1-dimensional
    arrays. Since some arrays can be quite long, it features a built-in
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

    @staticmethod
    def _downsample_arr(xstart, xend, x_vals, y_vals, max_datapoints):
        """
        Reference:
        https://matplotlib.org/3.1.0/gallery/event_handling/resample.html
        """
        # get the points in the view range
        mask = (x_vals > xstart) & (x_vals < xend)
        # dilate the mask by one to catch the points just outside
        # of the view range to not truncate the line
        mask = np.convolve([1, 1], mask, mode='same').astype(bool)
        # sort out how many points to drop
        ratio = int(max(np.sum(mask) // max_datapoints, 1))
        print(">>>>>>><", ratio)
        # mask data
        xdata = x_vals[mask]
        ydata = y_vals[mask]
        # downsample data
        xdata = xdata[::ratio]
        ydata = ydata[::ratio]
        print("using {} of {} visible points".format(
            len(ydata), np.sum(mask)))
        return xdata, ydata

    @classmethod
    def _update_ax(cls, ax, ax_line, x_vals, y_vals, max_datapoints):
        """
        Reference:
        https://matplotlib.org/3.1.0/gallery/event_handling/resample.html
        """
        # Update the line
        lims = ax.viewLim
        xstart, xend = lims.intervalx
        ax_line.set_data(*cls._downsample_arr(
            xstart, xend, x_vals, y_vals, max_datapoints))
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
        ax_line, = ax.plot(self.arange, self.arr, '-')
        # set number of ticks
        ax.locator_params(axis="x", nbins=num_xticks)
        ax.locator_params(axis="y", nbins=num_yticks)
        #
        ax.xaxis.tick_top()
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=30,
                 fontsize=tick_fontsize, family="DejaVu Sans", ha="left")
        plt.setp(ax.yaxis.get_majorticklabels(),
                 fontsize=tick_fontsize, family="DejaVu Sans")
        ax.set_autoscale_on(False)  # Otherwise, infinite loop
        ax.callbacks.connect('xlim_changed', lambda axx: self._update_ax(
            axx, ax_line, self.arange, self.arr, self.max_datapoints))
        ax.set_xlim(0, len(self.arr))
        ax.xaxis.grid(True)

        if self.samplerate is not None:
            f = plt.FuncFormatter(lambda val, pos:
                                  sample_to_timestamp_formatter(
                                      val, pos, self.samplerate))
            ax.xaxis.set_major_formatter(f)
        return fig


class MultipleDownsampledPlotter1D(DownsampledPlotter1D):
    """
    """
    FIG_ASPECT_RATIO = (10, 8)
    FIG_MARGINS = {"top": 0.8, "bottom": 0.05, "left": 0.05, "right": 0.95,
                   "hspace": 0.5, "wspace": 0.5}


    def __init__(self, arrays, samplerates=None, max_datapoints=10000,
                 shared_plots=None):
        """
        :param list arrays: a list of N 1-dimensional arrays
        :param list samplerates: If not None, a list of N positive numbers (or
          ``None`` entries), each one corresponding to the nth given array.
          If an entry is ``None``, the x-axis will show sample index. Otherwise
          the sample index will be converted to a timestamp. If the whole
          argument is ``None``, all axes will show sample index.
        :param int max_datapoints: Expected to be a positive integer,
          the number of plotted datapoints that each plot will (approximately)
          have.
        :param list shared_plots: If not None, a list of N boolean values, each
          one corresponding to a given array. All arrays with True value will
          share the same x axis, i.e. when the user scrolls or zooms across
          one of them, the rest will change the same way. If None, all will be
          treated as False, i.e. no x axis will be shared.
        """
        #
        self.N = len(arrays)
        assert self.N >= 1, "empty array list?"
        for arr in arrays:
            assert len(arr.shape) == 1, "1D array expected!"
        assert max_datapoints > 0, "positive max_datapoints expected!"
        if samplerates is not None:
            assert len(samplerates) == len(arrays),\
                "Number of samplerates must equal number of arrays!"
            for sr in samplerates:
                if sr is not None:
                    assert sr > 0, "all samplerates must be positive!"
        if shared_plots is not None:
            assert len(shared_plots) == len(arrays),\
                "Number of shared_plots must equal number of arrays!"
        #

        self.arrays = arrays
        self.aranges = [np.arange(len(arr)) for arr in arrays]
        self.max_datapoints = max_datapoints
        self.samplerates = ([None for _ in range(self.N)]
                            if samplerates is None else samplerates)
        self.shared_plots = ([False for _ in range(self.N)]
                            if shared_plots is None else shared_plots)

        self.shared_idxs = [idx for idx, b in enumerate(self.shared_plots)
                            if b]
        self.non_shared_idxs = [i for i in range(self.N)
                                if i not in self.shared_idxs]


    def make_fig(self, num_xticks=10, num_yticks=10, tick_fontsize=7,
                 tick_rot_deg=30):
        """
        :returns: A matplotlib Figure containing the array given at
          construction. The interactive plot of the figure will react
          to the user's zooming by showing approximately
          ``self.max_datapoints`` number of samples.

        Reference:
        https://matplotlib.org/3.1.0/gallery/event_handling/resample.html
        """
        # define and configure plt figure
        fig = plt.figure(figsize=self.FIG_ASPECT_RATIO)
        gs = list(gridspec.GridSpec(self.N, 1))
        # first create non-shared axes
        axes = [plt.subplot(gs[i]) for i in self.non_shared_idxs]

        # then create the first shared, the rest with share with the first
        if self.shared_idxs:
            shared_axes = [plt.subplot(gs[self.shared_idxs[0]])]
            for idx in self.shared_idxs[1:]:
                shared_axes.insert(idx, plt.subplot(gs[idx],
                                                    sharex=shared_axes[0]))
            for idx, ax in zip(self.shared_idxs, shared_axes):
                axes.insert(idx, ax)

        # plots
        lines = [ax.plot(rng, arr, "-")[0]
                 for arr, rng, ax in zip(self.arrays, self.aranges, axes)]

        # configure axes ticks and labels
        for ax, line, arr, rng, sr in zip(axes, lines, self.arrays,
                                          self.aranges, self.samplerates):
            # set vertical grid
            ax.xaxis.grid(True)

            # number of x and y ticks
            ax.locator_params(axis="x", nbins=num_xticks)
            ax.locator_params(axis="y", nbins=num_yticks)

            # alignment, font and rotation
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=tick_rot_deg,
                     fontsize=tick_fontsize, family="DejaVu Sans", ha="right")
            plt.setp(ax.yaxis.get_majorticklabels(),
                     fontsize=tick_fontsize, family="DejaVu Sans")

            # axes downsampling
            ax.callbacks.connect('xlim_changed', lambda _: self._update_ax(
                ax, line, rng, arr, self.max_datapoints))
            ax.set_xlim(0, len(arr))

            # finally adapt labels to given sample rates
            if sr is not None:

                f = plt.FuncFormatter(lambda val, pos:
                                      sample_to_timestamp_formatter(
                                          val, pos, sr))
                print(">>>>>>>>>>", f.func(100000, None))
                ax.xaxis.set_major_formatter(f)
        #
        fig.subplots_adjust(**self.FIG_MARGINS)
        return fig


# class AudioAndMvnPlotter(DownsampledPlotter1D):
#     """
#     """
#     # plt.rcParams["patch.force_edgecolor"] = True
#     FIG_ASPECT_RATIO = (10, 8)
#     # FIG_WIDTH_RATIOS = [5, 5]
#     # # FIG_HEIGHT_RATIOS = [10,3,10] # line, margin, line
#     # FIG_MARGINS = {"top":0.8, "bottom":0.2, "left":0.1, "right":0.9}
#     FIG_MARGINS = {"top": 0.8, "bottom": 0.05, "left": 0.05, "right": 0.95,
#                    "hspace": 0.5, "wspace": 0.5}
#     # RATIO_RANGE_AXIS = 1.15 # FOR 1.0, THE AXIS WILL COVER EXACTLY UNTIL THE MAXIMUM
#     # RATIO_LABELS_DISTANCE = 0.02 # 0.05 MEANS THE DISTANCE BETWEEN BARS AND LABELS IS 5% OF THE AXIS
#     # #
#     FIG_TITLE_FONTSIZE = 15
#     # AX_TITLE_FONTSIZE = 18
#     # # TABLE_FONTSIZE = 9
#     TICKS_FONTSIZE = 7
#     # CONFMAT_NUMBER_COLOR = "cyan"
#     # CONFMAT_NUMBER_FONTSIZE = 12
#     # NUM_YTICKS = 13
#     # LABELS_FONTSIZE = 12
#     # LEGEND_FONTSIZE = 15
#     # BAR_WIDTH = 0.85
#     # FPOS_COLOR = "#b0b000"
#     # FNEG_COLOR = "#e6194b"


#     def __init__(self, arr, mvn, max_datapoints=10000, samplerate=None):
#         """
#         """
#         super().__init__(arr, max_datapoints, samplerate)
#         self.mvn = mvn

#     # def make_fig(self, fig_title, audio_arr, total, x_shared):
#     #     """
#     #     """
#     #     # define and configure plt figure
#     #     fig = plt.figure(figsize=self.FIG_ASPECT_RATIO)
#     #     gs = list(gridspec.GridSpec(total, 1))
#     #     axes = [plt.subplot(gs[0])]
#     #     # add shared-x axes
#     #     axes += [plt.subplot(gsi, sharex=axes[0])
#     #              for gsi in gs[1: x_shared]]
#     #     # add remaining axes:
#     #     axes += [plt.subplot(gsi) for gsi in gs[x_shared:]]

#     #     #
#     #     info = "\nNo. axes=%d, dep. axes=%d" % (total, x_shared)
#     #     fig.suptitle(fig_title + info, fontsize=self.FIG_TITLE_FONTSIZE,
#     #                  fontweight="bold")
#     #     fig.canvas.set_window_title(fig_title)

#     #     axes[0].plot(audio_arr)

#     #     for ax in axes[1:]:
#     #         ax.plot(range(10), range(10))
#     #     fig.subplots_adjust(**self.FIG_MARGINS)
#     #     return fig


#     def make_fig(self, num_xticks=10, num_yticks=10, tick_fontsize=7):
#         """
#         :returns: A matplotlib Figure containing the array given at
#           construction. The interactive plot of the figure will react
#           to the user's zooming by showing approximately
#           ``self.max_datapoints`` number of samples.

#         Reference:
#         https://matplotlib.org/3.1.0/gallery/event_handling/resample.html
#         """
#         fig, ax = plt.subplots()
#         self.axx, = ax.plot(self.arange, self.arr, '-')
#         # set number of ticks
#         ax.locator_params(axis="x", nbins=num_xticks)
#         ax.locator_params(axis="y", nbins=num_yticks)
#         #
#         ax.xaxis.tick_top()
#         plt.setp(ax.xaxis.get_majorticklabels(), rotation=30,
#                  fontsize=tick_fontsize, family="DejaVu Sans", ha="left")
#         plt.setp(ax.yaxis.get_majorticklabels(),
#                  fontsize=tick_fontsize, family="DejaVu Sans")
#         ax.set_autoscale_on(False)  # Otherwise, infinite loop
#         ax.callbacks.connect('xlim_changed', self._update_ax)
#         ax.set_xlim(0, len(self.arr))
#         ax.xaxis.grid(True)
#         if self.samplerate is not None:
#             f = plt.FuncFormatter(lambda val, pos:
#                                   sample_to_timestamp_formatter(
#                                       val, pos, self.samplerate))
#             ax.xaxis.set_major_formatter(f)
#         #
#         return fig
