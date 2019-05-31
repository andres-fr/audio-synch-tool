#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
"""


# os+plt imports right after __future__
# import os
import matplotlib
# if os.environ.get('DISPLAY', '') == '':
#     print('no display found. Using non-interactive Agg backend')
#     matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import gridspec
from matplotlib.widgets import TextBox  # Button
from matplotlib.backend_tools import ToolBase

from .utils import resolve_path
from .utils import DownsamplableFunction
from .utils import SampleToTimestampFormatter
from .utils import XlimCallbackFunctor, SharedXlimCallbackFunctor


__author__ = "Andres FR"


# #############################################################################
# ## GLOBALS
# #############################################################################

matplotlib.rcParams["toolbar"] = "toolmanager"

def redefine_plt_shortcuts(fig, help_keys=["f1"], save_keys=["ctrl+s"]):
    """
    Some of them collide, some of them are unwanted. This function redefines
    most of the ``matplotlib.rcParams`` entries.
    """
    rc = matplotlib.rcParams
    #
    if rc["toolbar"] == "toolmanager":
        tm = fig.canvas.manager.toolbar.toolmanager
        tm._keys = {}  # delete all preexisting mappings
        for hk in help_keys:
            tm._keys[hk] = "help"
        for sk in save_keys:
            tm._keys[sk] = "save"
    else:
        rc["keymap.all_axes"] = []  # ['a']
        rc["keymap.back"] = []  # ['left', 'c', 'backspace']
        rc["keymap.copy"] = []  # ['ctrl+c', 'cmd+c']
        rc["keymap.forward"] = []  # ['right', 'v']
        rc["keymap.fullscreen"] = []  # ['f', 'ctrl+f']
        rc["keymap.grid"] = []  # ['g']
        rc["keymap.grid_minor"] = []  # ['G']
        rc["keymap.help"] = help_keys
        rc["keymap.home"] = []  # ['h', 'r', 'home']
        rc["keymap.pan"] = []  # ['p']
        rc["keymap.quit"] = []  # ['ctrl+w', 'cmd+w', 'q']
        rc["keymap.quit_all"] = []  # ['W', 'cmd+W', 'Q']
        rc["keymap.save"] = save_keys  # ['s', 'ctrl+s']
        rc["keymap.xscale"] = []  # ['k', 'L']
        rc["keymap.yscale"] = []  # ['l']
        rc["keymap.zoom"] = []  # ['o']


# #############################################################################
# ## HELPERS
# #############################################################################

def add_to_toolbar(fig, *widgets):
    """
    Adds a set of button-like widgets to the toolbar of a given figure.

    :param fig: a ``plt.Figure``
    :param *widgets: A number of class names that extend
      ``mpl.backend_tools.ToolBase``. They must have at least defind the
      ``name`` and ``tool_group`` fields.
    """
    # add widgets
    manager = fig.canvas.manager
    tm = manager.toolmanager
    for w in widgets:
        tm.add_tool(w.name, w)
        manager.toolbar.add_tool(tm.get_tool(w.name), w.tool_group)

# #############################################################################
# ## WIDGETS
# #############################################################################

class SignalTransformButtons(ToolBase):
    tool_group = "signal_transforms"
    textbox = None


class ShiftRightTool(SignalTransformButtons):
    """
    """
    name = "shift_tool"
    default_keymap = ""  # "ctrl+right"
    description = "Shift grouped signals by the given amount"
    image = resolve_path("data", "shift_right.png")

    def trigger(self, *args, **kwargs):
        """
        """
        print("!!!!!!!!!!!!", self.textbox.number)

class StretchRightTool(SignalTransformButtons):
    """
    Stretch tied signals
    """

    name = "stretch_tool"
    default_keymap = ""  # "ctrl+up"
    description = "Stretch grouped signals by the given amount"
    image = resolve_path("data", "stretch_out.png")

    def trigger(self, *args, **kwargs):
        """
        """
        print("%&&&&&&&&", self.textbox.number)


class TextPrompt(TextBox):
    """
    """
    AX_TITLE = "Type a number, press enter and click on the desired operation"
    LABEL = ""
    INITIAL_VAL = ""
    def __init__(self, axis):
        """
        """
        super().__init__(axis, self.LABEL, initial=self.INITIAL_VAL,
                         label_pad=0.001)
        self.on_submit(self._submit)
        self.number = None
        axis.set_title(self.AX_TITLE)
        # self.on_text_change(lambda _: None)

    def _submit(self, txt):
        try:
            self.number = float(txt)
            print("textbox stored", self.number)
        except ValueError:
            print(txt, "is not a valid number! ignored...")
            self.number = None


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
    TEXTBOX_HEIGHT_RATIO = 0.22
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
        self.arr_maxranges = [(min([arr.x[0] for arr in arrs]),
                               max([arr.x[-1] for arr in arrs]))
                              for arrs in self.arrays]
        if self.shared_idxs:
            shared_mins, shared_maxs = zip(*[self.arr_maxranges[i]
                                             for i in self.shared_idxs])
            shared_maxrange = (min(shared_mins), max(shared_maxs))
            for i in self.shared_idxs:
                self.arr_maxranges[i] = shared_maxrange

    def make_fig(self, textbox_widget=None, toolbar_widgets=[]):
        """
        :param toolbar_widgets: must have a textbox attr!

        :returns: A matplotlib Figure containing the array given at
          construction. The interactive plot of the figure will react
          to the user's zooming by showing approximately
          ``self.max_datapoints`` number of samples.
        """
        # XOR: either you give both or none!
        if (textbox_widget is not None) ^ bool(toolbar_widgets):
            raise AssertionError(
                "either give both textbox and toolbar or none!")
        #
        hratios = [1 for _ in range(self.N)]
        num_axes = self.N
        if textbox_widget is not None:
            num_axes += 2
            hratios += [self.TEXTBOX_HEIGHT_RATIO]*2

        # define and configure plt figure
        fig = plt.figure(figsize=self.FIG_ASPECT_RATIO)
        redefine_plt_shortcuts(fig)
        gs = list(gridspec.GridSpec(num_axes, 1, height_ratios=hratios))
        #
        axes = [fig.add_subplot(g) for g in gs]
        shared_axes = {axes[i] for i in self.shared_idxs}
        # plots
        line_lists = [[ax.step(arr.x, arr.y, "-")[0] for arr in arrs]
                      for arrs, ax in zip(self.arrays, axes)]
        # the callback handles downsampling and updating the shared axes.
        # This isn't done by sharing the same x-axis since this wouldn't
        # allow different axes with different samplerates to have different
        # label formatters.
        functors = [XlimCallbackFunctor(ax, lns, arrs, shared_axes,
                                        verbose=False)
                    for ax, lns, arrs in zip(axes, line_lists, self.arrays)]
        # collapse the shared functors, if existing:
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
                f = SampleToTimestampFormatter(sr, self.NUM_DECIMALS,
                                               self.SHOW_IDX)
                ax.xaxis.set_major_formatter(plt.FuncFormatter(f))

            ax.callbacks.connect('xlim_changed', fnc)
            ax.set_xlim(*ax_xrange)
        #
        if (textbox_widget is not None) and toolbar_widgets:
            # create textbox
            axes[-2].axis("off")
            txtbox = textbox_widget(axes[-1])
            setattr(fig, "txtbox", txtbox)
            # add toolbar buttons and link them to textbox
            add_to_toolbar(fig, *toolbar_widgets)
            for w in toolbar_widgets:
                w.textbox = txtbox

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
        arrays = [[audio_array]] + mvn_arrays
        samplerates =[audio_samplerate] + [mvn_samplerate for _ in mvn_arrays]
        shared_plots = [True for _ in range(len(arrays))]
        #
        super().__init__(arrays, samplerates, max_datapoints, shared_plots)

    def make_fig(self):
        super().make_fig(TextPrompt, [ShiftRightTool, StretchRightTool])
