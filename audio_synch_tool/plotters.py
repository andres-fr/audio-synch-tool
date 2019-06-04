#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
"""


# os+plt imports right after __future__
import os
import torch
import matplotlib
# if os.environ.get('DISPLAY', '') == '':
#     print('no display found. Using non-interactive Agg backend')
#     matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import gridspec
from matplotlib.widgets import TextBox  # Button
from matplotlib.backend_tools import ToolBase
from mpl_toolkits.axes_grid1 import make_axes_locatable

import soundfile as sf


from .utils import resolve_path
from .utils import DownsamplableFunction
from .utils import IdentityFormatter, SampleToTimestampFormatter
from .utils import SynchedMvnFormatter
from .utils import XlimCallbackFunctor, SharedXlimCallbackFunctor
from .utils import convert_anchors
from .mvn import Mvn

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
        rc["keymap.yscale"] = []  #
        rc["keymap.zoom"] = []  # ['o']


# #############################################################################
# ## HELPERS
# #############################################################################

def add_to_toolbar(fig, *widgets):
    """
    Adds a set of button-like widgets to the toolbar of a given figure.

    :param fig: a ``plt.Figure``
    :param widgets: A number of class names that extend
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
    """
    The class attribute ``plotter`` has to be set to point to an instance of
    ``plt.Figure`` at some point before usage.
    """
    tool_group = "signal_transforms"
    fig = None


class SynchAndSaveMvnButton(SignalTransformButtons):
    """
    Given the current anchors, set the audio_synch info into the MVN
    and save it to the given path.
    ..note::

      This assumes the following textboxes ordering!:
      ``[ori1, dest1, ori2, dest2, outpath]``
    """

    name = "synch_and_save_mvn"
    default_keymap = ""  # "ctrl+up"
    description = ("Given the current anchors, set the audio_synch info into" +
                   " the MVN and save it to the given path")
    image = resolve_path("data", "synch_and_save.png")

    def trigger(self, *args, **kwargs):
        """
        """
        # make sure inputs are correct before continuing
        if any([t.val is None for t in self.fig.textboxes]):
            print("[SynchAndSaveMvnButton] ignored:",
                  "please set all text boxes wit valid values before!")
            return
        #
        tb_ori1, tb_dest1, tb_ori2, tb_dest2, tb_outpath = self.fig.textboxes
        # also check if path works
        try:
            with open(tb_outpath.val, "w") as _:
                pass
        except Exception as e:
            print("[SynchAndSaveMvnButton] wrong path!", e)
            return
        # convert anchors into stretch and shift, then
        # apply stretch, shift and round to every frame idx to get audio sample
        stretch, shift = convert_anchors(tb_ori1.val, tb_dest1.val,
                                         tb_ori2.val, tb_dest2.val)
        mvn = self.fig.mvn
        mvn.set_audio_synch(stretch, shift)
        # finally add wav info
        wav_name = os.path.basename(self.fig.wav_path)
        mvn.mvn.attrib["wav_file"] = wav_name
        print("Added mvn.mvn.attrib['wav_file'] =", wav_name)
        # and save
        mvn.export(tb_outpath.val)


class TextPromptOutPath(TextBox):
    NAME = "OutPath"
    AX_TITLE = "Synched MVNX Out Path:"
    LABEL = ""
    INITIAL_VAL = os.getenv("HOME")
    SIZE_PERCENT = "500%"
    PADDING = 0.5

    def __init__(self, axis):
        """
        """
        super().__init__(axis, self.LABEL, initial=self.INITIAL_VAL)
        axis.set_title(self.AX_TITLE)
        self.val = self.INITIAL_VAL
        self.on_submit(self._submit)

    def _submit(self, txt):
        self.val = txt


class NumberPrompt(TextBox):
    """
    """
    NAME = ""
    AX_TITLE = ""
    LABEL = ""
    INITIAL_VAL = ""
    SIZE_PERCENT = "200%"
    PADDING = 0.1

    def __init__(self, axis):
        """
        """
        super().__init__(axis, self.LABEL)
        self.on_submit(self._submit)
        axis.set_title(self.AX_TITLE)
        # self.on_text_change(lambda _: None)
        self.val = None
        self._update_display()

    def _update_display(self):
        s = "" if self.val is None else str(self.val)
        self.set_val(s)

    def _submit(self, txt):
        try:
            self.val = float(txt)
            # print("[TextBox %s]" % self.NAME, "stored", self.val)
        except ValueError:
            print(txt, "is not a valid number! ignored...")
            self.val = None
        finally:
            self._update_display()


class NumberPromptOri1(NumberPrompt):
    NAME = "Ori 1"
    AX_TITLE = "Origin 1"


class NumberPromptOri2(NumberPrompt):
    NAME = "Ori 2"
    AX_TITLE = "Origin 2"


class NumberPromptDest1(NumberPrompt):
    NAME = "Dest 1"
    AX_TITLE = "Destiny 1"


class NumberPromptDest2(NumberPrompt):
    NAME = "Dest 2"
    AX_TITLE = "Destiny 2"


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
                 shared_plots=None, x_arrays=None, xtick_formatters=None):
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
        if xtick_formatters is not None:
            assert len(xtick_formatters) == len(y_arrays),\
                "Number of xtick_formatters must equal number of arrays!"
        # now values can be set
        self.arrays = [[DownsamplableFunction(yarr, max_datapoints, xarr)
                        for yarr, xarr in zip(yarrs, xarrs)]
                       for yarrs, xarrs in zip(y_arrays, x_arrays)]
        # these attributes are straightforward
        self.samplerates = ([None for _ in range(self.N)]
                            if samplerates is None else samplerates)
        self.shared_plots = ([False for _ in range(self.N)]
                             if shared_plots is None else shared_plots)
        self.xtick_formatters = ([IdentityFormatter() for _ in range(self.N)]
                                 if xtick_formatters is None
                                 else xtick_formatters)
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

    def make_fig(self, textbox_widgets=[], toolbar_widgets=[]):
        """
        :param toolbar_widgets: A list of class names of type
          SignalTransformButtons. Must include a ``fig`` attribute, which
          will be automatically set to be the Figure returned by this method.

        :returns: A matplotlib Figure containing the array given at
          construction. The interactive plot of the figure will react
          to the user's zooming by showing approximately
          ``self.max_datapoints`` number of samples.
        """
        # XOR: either you give both or none!
        if bool(textbox_widgets) ^ bool(toolbar_widgets):
            raise AssertionError(
                "either give both textbox and toolbar or none!")
        #
        hratios = [1 for _ in range(self.N)]
        num_axes = self.N
        if textbox_widgets:
            num_axes += 2
            hratios += [self.TEXTBOX_HEIGHT_RATIO]*2

        # define and configure plt figure
        fig = plt.figure(figsize=self.FIG_ASPECT_RATIO)
        setattr(fig, "plotter", self)
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
        for ax, sr, fnc, ax_xrange, frmtr in zip(axes, self.samplerates,
                                                 functors, self.arr_maxranges,
                                                 self.xtick_formatters):
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
            if frmtr is not None:
                ax.xaxis.set_major_formatter(plt.FuncFormatter(frmtr))
            # if sr is not None:
            #     f = SampleToTimestampFormatter(sr, self.NUM_DECIMALS,
            #                                    self.SHOW_IDX)
            #     ax.xaxis.set_major_formatter(plt.FuncFormatter(f))

            ax.callbacks.connect('xlim_changed', fnc)
            ax.set_xlim(*ax_xrange)
        #
        if textbox_widgets and toolbar_widgets:
            for txtw in textbox_widgets:
                assert issubclass(txtw, TextBox), \
                    "All toolbar_widgets must have type TextBox"
            for toow in toolbar_widgets:
                assert issubclass(toow, SignalTransformButtons), \
                    "All toolbar_widgets must have type SignalTransformButtons"
            # create textboxes
            textboxes = []  # this will be monkeypatched to fig
            axes[-2].axis("off")  # widget space has no axes visible
            axes[-1].axis("off")
            txt_ax = axes[-1]  # here come the text boxes
            divider = make_axes_locatable(txt_ax)  # div. ax for multiple boxes
            for txtw in textbox_widgets:
                axx = divider.append_axes("right", size=txtw.SIZE_PERCENT,
                                          pad=txtw.PADDING)
                textbox = txtw(axx)
                textboxes.append(textbox)
            setattr(fig, "textboxes", textboxes)  # allow toolbar to find text
            # add toolbar buttons and link them to textbox
            add_to_toolbar(fig, *toolbar_widgets)
            for w in toolbar_widgets:
                w.fig = fig
        #
        fig.subplots_adjust(**self.FIG_MARGINS)
        return fig


class AudioMvnSynchToolEditor(MultipleDownsampledPlotter1D):
    """
    """
    TEXTBOX_WIDGET_CLASSES = [NumberPromptOri1, NumberPromptDest1,
                              NumberPromptOri2, NumberPromptDest2,
                              TextPromptOutPath]
    TOOLBAR_BUTTON_CLASSES = [SynchAndSaveMvnButton]

    def __init__(self, wav_path, mvnx_path, mvnx_schema_path=None,
                 max_datapoints=10000):
        """
        """
        self.wav_path = wav_path
        self.mvnx_path = mvnx_path
        self.mvnx_schema_path = mvnx_schema_path
        #
        wav_arr, audio_samplerate = sf.read(wav_path)
        self.mvn = Mvn(mvnx_path, mvnx_schema_path)
        # get mvn samplerate and our desired y arrays
        mvn_samplerate = float(self.mvn.mvn.subject.attrib["frameRate"])
        mvn_arrays = self._get_mvn_arrays()
        y_arrays = [[wav_arr]] + mvn_arrays
        # x-array for audio is trivial
        x_audio = torch.arange(len(wav_arr)).type(torch.float64).numpy()
        # x-array for mvn: if no pre-synched entries use frame indexes.
        x_mvn = self.mvn.get_audio_synch()
        if x_mvn is None:
            x_mvn = [int(f.attrib["index"])
                     for f in self.mvn.mvn.subject.frames.getchildren()
                     if f.attrib["type"] == "normal"]
        x_mvn = torch.Tensor(x_mvn).numpy()

        # bundle plotter inputs:
        x_arrays = [[x_audio]] + [[x_mvn for a in arrs] for arrs in mvn_arrays]
        samplerates = [audio_samplerate] + [mvn_samplerate for _ in mvn_arrays]
        shared_plots = [False] + [True for _ in mvn_arrays]
        xtick_formatters = [SampleToTimestampFormatter(audio_samplerate,
                                                       self.NUM_DECIMALS,
                                                       self.SHOW_IDX)] + [
                                                           IdentityFormatter()
                                                           for _ in mvn_arrays]
        # call plotter
        super().__init__(y_arrays, samplerates, max_datapoints, shared_plots,
                         x_arrays, xtick_formatters)

    def _get_mvn_arrays(self):
        """
        """
        # extract info from mocap
        mocap_segments = self.mvn.extract_segments()
        frames_metadata, _, normal_frames = self.mvn.extract_frame_info()
        frame_sequences = self.mvn.extract_normalframe_sequences(
            frames_metadata, normal_frames, "cpu")
        mocap_accelerations_3d = frame_sequences["acceleration"]
        mocap_accel_norm = torch.norm(mocap_accelerations_3d, 2, dim=-1)
        #
        mvn_arrays = [[
            mocap_accel_norm[:, mocap_segments.index("LeftShoulder")].numpy(),
            mocap_accel_norm[:, mocap_segments.index("LeftForeArm")].numpy(),
            mocap_accel_norm[:, mocap_segments.index("LeftHand")].numpy()],
                      [
            mocap_accel_norm[:, mocap_segments.index("RightShoulder")].numpy(),
            mocap_accel_norm[:, mocap_segments.index("RightForeArm")].numpy(),
            mocap_accel_norm[:, mocap_segments.index("RightHand")].numpy()]]
        return mvn_arrays

    def make_fig(self):
        fig = super().make_fig(self.TEXTBOX_WIDGET_CLASSES,
                               self.TOOLBAR_BUTTON_CLASSES)
        # more monkey patching!
        setattr(fig, "wav_path", self.wav_path)
        setattr(fig, "mvn", self.mvn)
        return fig


class AudioMvnSynchToolChecker(MultipleDownsampledPlotter1D):
    """
    This doesn't modify the synch, just displays it
    """

    def __init__(self, audio_array, audio_samplerate, mvn,
                 max_datapoints=10000):
        """
        """
        assert isinstance(mvn, Mvn), "mvn must be an instance of Mvn!"
        self.mvn = mvn
        # get mvn samplerate and our desired y arrays
        self.mvn_samplerate = float(mvn.mvn.subject.attrib["frameRate"])
        mvn_arrays = self._get_mvn_arrays()
        y_arrays = [[audio_array]] + mvn_arrays
        # x-array for audio is trivial
        x_audio = torch.arange(len(audio_array)).type(torch.float64).numpy()
        # x-array for mvn: if no pre-synched entries use frame indexes.
        x_mvn = self.mvn.get_audio_synch()
        assert x_mvn is not None, "No synch info in mvn file?"
        x_mvn = torch.Tensor(x_mvn).numpy()

        # bundle plotter inputs:
        x_arrays = [[x_audio]] + [[x_mvn for a in arrs] for arrs in mvn_arrays]
        samplerates = [audio_samplerate for _ in y_arrays]
        shared_plots = [True for _ in range(len(y_arrays))]
        xtick_formatters = [SampleToTimestampFormatter(audio_samplerate,
                                                       self.NUM_DECIMALS,
                                                       self.SHOW_IDX)]
        xtick_formatters.extend([SynchedMvnFormatter(self.mvn,
                                                     self.NUM_DECIMALS)
                                 for _ in mvn_arrays])

        # call plotter
        super().__init__(y_arrays, samplerates, max_datapoints, shared_plots,
                         x_arrays, xtick_formatters)

    def _get_mvn_arrays(self):
        """
        """
        # extract info from mocap
        mocap_segments = self.mvn.extract_segments()
        frames_metadata, _, normal_frames = self.mvn.extract_frame_info()
        frame_sequences = self.mvn.extract_normalframe_sequences(
            frames_metadata, normal_frames, "cpu")
        mocap_accelerations_3d = frame_sequences["acceleration"]
        mocap_accel_norm = torch.norm(mocap_accelerations_3d, 2, dim=-1)
        #
        mvn_arrays = [[
            mocap_accel_norm[:, mocap_segments.index("LeftShoulder")].numpy(),
            mocap_accel_norm[:, mocap_segments.index("LeftForeArm")].numpy(),
            mocap_accel_norm[:, mocap_segments.index("LeftHand")].numpy()],
                      [
            mocap_accel_norm[:, mocap_segments.index("RightShoulder")].numpy(),
            mocap_accel_norm[:, mocap_segments.index("RightForeArm")].numpy(),
            mocap_accel_norm[:, mocap_segments.index("RightHand")].numpy()]]
        return mvn_arrays

    def make_fig(self):
        fig = super().make_fig()
        # more monkey patching!
        setattr(fig, "mvn", self.mvn)
        return fig
