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
from matplotlib.widgets import Cursor


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

class SamplerateFuncFormatter(plt.FuncFormatter):
    """
    The regular FuncFormatter calls our SampleToTimestampFormatter functor with
    the ``(val, pos)`` signature. Crucially, it doesn't include information on
    which axis is calling it, or any of the other attributes like sample rate.

    Since axes that share the x-axis will also share the formatter, the regular
    FuncFormatter makes impossible to have axes with different samplerates
    being "aligned".

    This class fixes it by calling the formatter with the
    ``(val, pos, samplerate)`` signature.

    References:
    https://matplotlib.org/3.1.0/_modules/matplotlib/ticker.html#FuncFormatter
    """
    def __call__(self, x, pos=None):
        """
        Call self.func with a different signature.
        """
        # print(">>>>>", self.axis.__dict__.keys())
        samplerate = self.axis.axes.samplerate
        # print(">>>>>", self.axis.axes, samplerate)
        return self.func(x, pos, samplerate)


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
    TICK_FONTSIZE = 7
    NUM_XTICKS = 15
    NUM_YTICKS = 10
    TICK_ROT_DEG = 15
    NUM_DECIMALS = 3
    SHOW_IDX = True
    # FIG_ASPECT_RATIO = (10, 8)
    # FIG_MARGINS = {"top": 0.95, "bottom": 0.1, "left": 0.1, "right": 0.95,
    #                "hspace": 0.5, "wspace": 0.05}
    # plt.rcParams["patch.force_edgecolor"] = True
    # FIG_WIDTH_RATIOS = [5, 5]
    # # FIG_HEIGHT_RATIOS = [10,3,10] # line, margin, line
    # FIG_MARGINS = {"top":0.8, "bottom":0.2, "left":0.1, "right":0.9}
    # FOR 1.0, THE AXIS WILL COVER EXACTLY UNTIL THE MAXIMUM
    # RATIO_RANGE_AXIS = 1.15
    # 0.05 MEANS THE DISTANCE BETWEEN BARS AND LABELS IS 5% OF THE AXIS
    # RATIO_LABELS_DISTANCE = 0.02
    # #
    # FIG_TITLE_FONTSIZE = 15
    # AX_TITLE_FONTSIZE = 18
    # # TABLE_FONTSIZE = 9
    # TICKS_FONTSIZE = 7
    # CONFMAT_NUMBER_COLOR = "cyan"
    # CONFMAT_NUMBER_FONTSIZE = 12
    # NUM_YTICKS = 13
    # LABELS_FONTSIZE = 12
    # LEGEND_FONTSIZE = 15
    # BAR_WIDTH = 0.85
    # FPOS_COLOR = "#b0b000"
    # FNEG_COLOR = "#e6194b"

    def __init__(self, y_arrays, samplerates=None, max_datapoints=10000,
                 shared_plots=None, x_arrays=None):
        """
        """
        # check y arrays. Don't set it before checking x arrays!
        self.N = len(y_arrays)
        assert self.N >= 1, "empty array list?"
        assert max_datapoints > 0, "positive max_datapoints expected!"
        # arrays is a "list of lists of arrays"
        for yarrs in y_arrays:
            for yarr in yarrs:
                assert len(yarr.shape) == 1, "1D y_array expected!"
        # check x arrays
        if x_arrays is not None:
            assert len(x_arrays) == self.N, \
                "len(x_arrays) must be equal len(y_arrays)!"
            for yarrs, xarrs in zip(y_arrays, x_arrays):
                assert len(yarrs) == len(xarrs), \
                    "len mismatch between x_arrays and y_arrays!"
                for yarr, xarr in zip(yarrs, xarrs):
                    assert len(xarr.shape) == 1, "1D x_array expected!"
                    assert len(xarr) == len(yarr), \
                        "len mismatch between x_array and y_array!"
        else:  # if x arrays not given, set None
            x_arrays = [[None for _ in y] for y in y_arrays]
        # check remaining parameters
        if samplerates is not None:
            assert len(samplerates) == len(y_arrays),\
                "Number of samplerates must equal number of arrays!"
            for sr in samplerates:
                if sr is not None:
                    assert sr > 0, "all samplerates must be positive!"
        if shared_plots is not None:
            assert len(shared_plots) == len(y_arrays),\
                "Number of shared_plots must equal number of arrays!"
        # now values can be set
        self.arrays = [[DownsamplableFunction(yarr, max_datapoints, xarr)
                        for yarr, xarr in zip(yarrs, xarrs)]
                       for yarrs, xarrs in zip(y_arrays, x_arrays)]
        # these attributes are straightforward
        self.samplerates = ([None for _ in range(self.N)]
                            if samplerates is None else samplerates)
        self.shared_plots = ([False for _ in range(self.N)]
                             if shared_plots is None else shared_plots)
        self.shared_idxs = [idx for idx, b in enumerate(self.shared_plots)
                            if b]
        self.non_shared_idxs = [i for i in range(self.N)
                                if i not in self.shared_idxs]
        # ranges can be tricky due to shared axes and multiple lines per
        # axis. First, find the (min, max) per axis. Then find the (min, max)
        # across all shared axes, and replace every shared range with it.
        arr_maxranges = [(min([arr.x[0] for arr in arrs]),
                          max([arr.x[-1] for arr in arrs]))
                         for arrs in self.arrays]
        shared_mins, shared_maxs = zip(*[arr_maxranges[i]
                                         for i in self.shared_idxs])
        shared_maxrange = (min(shared_mins), max(shared_maxs))
        for i in self.shared_idxs:
            arr_maxranges[i] = shared_maxrange
        self.arr_maxranges = arr_maxranges

    def make_fig(self):
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
        line_lists = [[ax.step(arr.x, arr.y, "-")[0] for arr in arrs]
                      for arrs, ax in zip(self.arrays, axes)]

        # tricky part: tied axes must have tied callbacks. First create the
        # independent functors
        functors = [XlimCallbackFunctor(ax, lns, arrs, verbose=False)
                    for ax, lns, arrs in zip(axes, line_lists, self.arrays)]
        # and then replace the shared ones, if existing:
        if self.shared_idxs:
            shared_f = SharedXlimCallbackFunctor(
                [f for i, f in enumerate(functors) if i in self.shared_idxs])
            functors = [shared_f if i in self.shared_idxs else f
                        for i, f in enumerate(functors)]

        # configure axes ticks and labels
        for ax, sr, fnc, ax_xrange in zip(axes, self.samplerates, functors,
                                          self.arr_maxranges):
            # add samplerate to axis (needed by label formatter due to rigidity
            # of the callback mechanism)
            setattr(ax, "samplerate", sr)
            # set vertical grid
            ax.xaxis.grid(True)

            # number of x and y ticks
            ax.locator_params(axis="x", nbins=self.NUM_XTICKS, integer=True)
            ax.locator_params(axis="y", nbins=self.NUM_YTICKS)

            # alignment, font and rotation of labels
            plt.setp(ax.xaxis.get_majorticklabels(),
                     rotation=self.TICK_ROT_DEG,
                     fontsize=self.TICK_FONTSIZE, family="DejaVu Sans",
                     ha="right")
            plt.setp(ax.yaxis.get_majorticklabels(),
                     fontsize=self.TICK_FONTSIZE, family="DejaVu Sans")

            # optionally adapt labels to given sample rates
            if sr is not None:
                f = SampleToTimestampFormatter(self.NUM_DECIMALS,
                                               self.SHOW_IDX)
                ax.xaxis.set_major_formatter(SamplerateFuncFormatter(f))

            ax.callbacks.connect('xlim_changed', fnc)
            ax.set_xlim(*ax_xrange)

        for quack in axes:
            f = quack.xaxis.get_major_formatter().axis.axes
            print(quack.__repr__(), f.__repr__())
            # print(">>>>>>>>>>>>>>>", f.samplerate, f(1000, 1000))



        fig.subplots_adjust(**self.FIG_MARGINS)
        return fig






















class AudioMvnSynchTool(MultipleDownsampledPlotter1D):
    """
    """

    def __init__(self, audio_array, mvn_arrays, audio_samplerate,
                 mvn_samplerate, max_datapoints=10000):
        """
        """
        assert isinstance(mvn_arrays, list), "mvn_arrays must be of type list!"
        #
        arrays = [[audio_array]] +  mvn_arrays
        samplerates =[audio_samplerate] + [mvn_samplerate for _ in mvn_arrays]
        shared_plots = [True for _ in range(len(arrays))]
        #
        super().__init__(arrays, samplerates, max_datapoints, shared_plots)

    def make_fig(self):
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
            ax.locator_params(axis="x", nbins=self.NUM_XTICKS, integer=True)
            ax.locator_params(axis="y", nbins=self.NUM_YTICKS)

            # alignment, font and rotation of labels
            plt.setp(ax.xaxis.get_majorticklabels(),
                     rotation=self.TICK_ROT_DEG,
                     fontsize=self.TICK_FONTSIZE, family="DejaVu Sans")
            plt.setp(ax.yaxis.get_majorticklabels(),
                     fontsize=self.TICK_FONTSIZE, family="DejaVu Sans")

            # optionally adapt labels to given sample rates
            if sr is not None:
                f = SampleToTimestampFormatter(sr, self.NUM_DECIMALS,
                                               self.SHOW_IDX)
                ax.xaxis.set_major_formatter(plt.FuncFormatter(f))

            ax.callbacks.connect('xlim_changed', fnc)
            ax.set_xlim(0, length)

        fig.subplots_adjust(**self.FIG_MARGINS)
        return fig


# class AudioAndMvnPlotter(DownsampledPlotter1D):
#     """
#     """


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
