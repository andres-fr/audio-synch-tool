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

from .utils import DownsamplableFunction
from .utils import SampleToTimestampFormatter
from .utils import XlimCallbackFunctor, SharedXlimCallbackFunctor


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

class MultipleDownsampledPlotter1D(object):
    """
    This class generates a matplotlib figure that plots several 1-dimensional
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

    FIG_ASPECT_RATIO = (10, 8)
    FIG_MARGINS = {"top": 0.95, "bottom": 0.1, "left": 0.1, "right": 0.95,
                   "hspace": 0.5, "wspace": 0.05}

    def __init__(self, arrays, samplerates=None, max_datapoints=10000,
                 shared_plots=None):
        """
        """
        #
        self.N = len(arrays)
        assert self.N >= 1, "empty array list?"
        # arrays is a "list of lists of arrays"
        for arrs in arrays:
            for arr in arrs:
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
        self.arrays = [[DownsamplableFunction(arr, max_datapoints)
                        for arr in arrs]
                       for arrs in arrays]
        self.arr_maxlengths = [max([len(arr) for arr in arrs])
                               for arrs in self.arrays]
        self.samplerates = ([None for _ in range(self.N)]
                            if samplerates is None else samplerates)
        self.shared_plots = ([False for _ in range(self.N)]
                             if shared_plots is None else shared_plots)

        self.shared_idxs = [idx for idx, b in enumerate(self.shared_plots)
                            if b]
        self.non_shared_idxs = [i for i in range(self.N)
                                if i not in self.shared_idxs]

    def make_fig(self, num_xticks=15, num_yticks=10, tick_fontsize=7,
                 tick_rot_deg=15, num_decimals=3, show_idx=True):
        """
        :returns: A matplotlib Figure containing the array given at
          construction. The interactive plot of the figure will react
          to the user's zooming by showing approximately
          ``self.max_datapoints`` number of samples.
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
        line_lists = [[ax.plot(arr.x, arr.y, "-")[0] for arr in arrs]
                      for arrs, ax in zip(self.arrays, axes)]

        # tricky part: tied axes must have tied callbacks. First create the
        # independent functors
        functors = [XlimCallbackFunctor(ax, lns, arrs) for ax, lns, arrs in
                    zip(axes, line_lists, self.arrays)]
        # and then replace the shared ones, if existing:
        if self.shared_idxs:
            shared_f = SharedXlimCallbackFunctor(
                [f for i, f in enumerate(functors) if i in self.shared_idxs])
            functors = [shared_f if i in self.shared_idxs else f
                        for i, f in enumerate(functors)]

        # configure axes ticks and labels
        for ax, sr, fnc, length in zip(axes, self.samplerates, functors,
                                       self.arr_maxlengths):
            # set vertical grid
            ax.xaxis.grid(True)

            # number of x and y ticks
            ax.locator_params(axis="x", nbins=num_xticks, integer=True)
            ax.locator_params(axis="y", nbins=num_yticks)

            # alignment, font and rotation of labels
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=tick_rot_deg,
                     fontsize=tick_fontsize, family="DejaVu Sans", ha="right")
            plt.setp(ax.yaxis.get_majorticklabels(),
                     fontsize=tick_fontsize, family="DejaVu Sans")

            # optionally adapt labels to given sample rates
            if sr is not None:
                f = SampleToTimestampFormatter(sr, num_decimals, show_idx)
                ax.xaxis.set_major_formatter(plt.FuncFormatter(f))

            ax.callbacks.connect('xlim_changed', fnc)
            ax.set_xlim(0, length)

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
#     # FOR 1.0, THE AXIS WILL COVER EXACTLY UNTIL THE MAXIMUM
#     # RATIO_RANGE_AXIS = 1.15
#     # 0.05 MEANS THE DISTANCE BETWEEN BARS AND LABELS IS 5% OF THE AXIS
#     # RATIO_LABELS_DISTANCE = 0.02
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
