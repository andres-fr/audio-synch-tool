#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
"""

import os
import datetime
import pytz
import torch
#
from . import __path__ as PACKAGE_ROOT_PATH  # path of the __init__ file


__author__ = "Andres FR"


# #############################################################################
# ## LOGIC
# #############################################################################

def resolve_path(*path_elements):
    """
    A convenience path wrapper to find elements in this package. Retrieves
    the absolute path, given the OS-agnostic path relative to the package
    root path (by bysically joining the path elements via ``os.path.join``).
    E.g., the following call retrieves the absolute path for
    ``<PACKAGE_ROOT>/a/b/test.txt``::

       resolve_path("a", "b", "test.txt")

    :params strings path_elements: From left to right, the path nodes,
       the last one being the filename.
    :rtype: str
    """
    p = tuple(PACKAGE_ROOT_PATH) + path_elements
    return os.path.join(*p)


def make_timestamp(timezone="Europe/Berlin"):
    """
    Output example: day, month, year, hour, min, sec, milisecs:
    10_Feb_2018_20:10:16.151
    """
    ts = datetime.datetime.now(tz=pytz.timezone(timezone)).strftime(
        "%d_%b_%Y_%H:%M:%S.%f")[:-3]
    return "%s (%s)" % (ts, timezone)


class Timedelta(object):
    """
    """
    def __init__(self, sample_nr, samplerate):
        """
        :param number sample_nr: Current sample number
        :param number samplerate: No. of samples per second (must be positive)
        """
        assert samplerate >= 0, "Only non-negative samplerate allowed!"
        self._is_negative = sample_nr < 0
        self._sample_nr = sample_nr
        self._samplerate = samplerate
        self._total_seconds = float(sample_nr) / samplerate
        # NOTE: to enforce symmetry around zero, compute for positive value
        # and then flip the sign
        td = datetime.timedelta(seconds=abs(self._total_seconds))
        d = td.days
        h = td.seconds // 3600
        m = (td.seconds // 60) % 60
        s = int(td.seconds % 60)
        mms = td.microseconds
        td_str = str(td)
        #
        self._days = -d if self._is_negative else d
        self._hours = -h if self._is_negative else h
        self._mins = -m if self._is_negative else m
        self._secs = -s if self._is_negative else s
        self._microsecs = -mms if self._is_negative else mms
        #
        self._timestamp = "-" + td_str if self._is_negative else td_str

    # "read-only" attributes:
    @property
    def sample_nr(self):
        return self._sample_nr

    @property
    def samplerate(self):
        return self._samplerate

    @property
    def total_seconds(self):
        return self._total_seconds

    @property
    def days(self):
        return self._days

    @property
    def hours(self):
        return self._hours

    @property
    def mins(self):
        return self._mins

    @property
    def secs(self):
        return self._secs

    @property
    def microsecs(self):
        return self._microsecs

    def as_tuple(self):
        """
        :returns: the tuple of integers (days, hours, mins, secs, microsecs)
        """
        return (self.days, self.hours, self.mins, self.secs, self.microsecs)

    def __str__(self):
        """
        Returns a string in the form "{X days} h:m:s.microseconds"
        """
        return self._timestamp


def convert_anchors(ori1, dest1, ori2, dest2):
    """
    Given a signal that we want to shift and stretch on the x axis, this affine
    operation can be defined by picking 2 points of the signal (ori1 and ori2,
    called here "anchors"), and mapping them to other 2 points (dest1 and
    dest2). For the given anchors, this function returns the corresponding
    stretching ratio and shifting amount (after stretching) needed to match the
    given anchors. This is given by solving the formula::

      ``[dest1, dest2] = shift + stretch * [ori1, ori2]``

    :param number ori1: any real-valued number. Same for ori2, dest1, dest2.
    :returns: a tuple (stretch, shift) with 2 real-valued numbers.
    """
    o1, d1, o2, d2 = float(ori1), float(dest1), float(ori2), float(dest2)
    stretch = (d1 - d2) / (o1 - o2)
    shift = d1 - stretch * o1
    return stretch, shift

# #############################################################################
# ## MATPLOTLIB-RELATED
# #############################################################################


class IdentityFormatter(object):
    """
    This functor can be passed to ``plt.FuncFormatter`` to generate
    custom tick labels. It fulfills the interface (val, pos)->str.

    Specifically, for a given ``val`` returns ``str(val)``. In most cases this
    is the default matplotlib behaviour, but using this formatter forces it to
    behave ALWAYS like this and avoid some other smart conversions like
    scientific notation for big numbers.
    """
    def __call__(self, val, pos):
        """
        :param number val: the axis value where the tick goes
        :param int pos: from 0 (left margin) to num_ticks+2 (right
          margin)
        :returns: ``str(val)``
        """
        return str(val)


class SynchedMvnFormatter(object):
    """
    This functor can be passed to ``plt.FuncFormatter`` to generate
    custom tick labels. It fulfills the interface (val, pos)->str.

    Specifically, it looks in the MVN file for the frame index with the
    given ``val`` and, if found, returns the string ``val [frame_idx]``
    (otherwise just val). For that, it expects that the frame has defined the
    ``audio_sample`` attribute.
    """
    def __init__(self, mvn, num_decimals=3):
        """
        :param int num_decimals: number of decimals to show for each number
        :param Mvn mvn: expected to be the Mvn instance used in the plot.
        """
        self.float_form = "{:.%df}" % num_decimals
        self.mvn = mvn
        #
        normal_frames = [f for f in mvn.mvn.subject.frames.getchildren()
                         if f.attrib["type"] == "normal"]
        self.mapping = {float(f.attrib["audio_sample"]): i
                        for i, f in enumerate(normal_frames)}

    def __call__(self, val, pos):
        """
        :param number val: the axis value where the tick goes
        :param int pos: from 0 (left margin) to num_ticks+2 (right
          margin)
        :returns: ``str(val)``
        """
        result = (str(int(val)) if val.is_integer() else
                  self.float_form.format(val))
        try:
            frame_str = " [" + str(self.mapping[float(val)]) + "]"
            result += frame_str
        except KeyError:
            pass
        return result


class ProportionalFormatter(object):
    """
    This functor can be passed to ``plt.FuncFormatter`` to generate
    custom tick labels. It fulfills the interface (val, pos)->str.

    Specifically, converts ``val`` number representing a sample into a string
    in the form ``val [val2]`` where ``val2 = val * ratio``.
    This can be useful e.g. to show the original values if the signal was
    resampled.
    """

    def __init__(self, ratio, num_decimals=3):
        """
        :param int num_decimals: number of decimals to show for each number
        :param number ratio: A number so that val2 = val * ratio
        """
        assert 0 <= num_decimals <= 6, "num_decimals must be in [0, ..., 6]!"
        self.ratio = ratio
        self.float_form = "{:.%df}" % num_decimals

    def __call__(self, val, pos):
        """
        :param number val: the axis value where the tick goes
        :param int pos: from 0 (left margin) to num_ticks+2 (right
          margin)
        :returns: A string in the form "val [val2]"
        """
        val_str = (str(int(val)) if val.is_integer() else
                   self.float_form.format(val))
        val2 = val * self.ratio
        val2_str = (str(int(val2)) if val2.is_integer() else
                    self.float_form.format(val2))
        return val_str + " [" + val2_str + "]"


class SampleToTimestampFormatter(object):
    """
    This functor can be passed to ``plt.FuncFormatter`` to generate
    custom tick labels. It fulfills the interface (val, pos)->str.

    Specifically, converts ``val`` number representing a sample into a string
    showing the corresponding elapsed time since sample 0, asuming the given
    samplerate.
    Usage example::

      ax.xaxis.set_major_formatter(plt.FuncFormatter(
                                   SampleToTimestampFormatter(sr)))
    """
    def __init__(self, samplerate, num_decimals=3, show_idx=True):
        """
        :param int num_decimals: An integer between 0 and 6.
        :param bool show_idx: If true, the sample index will be also shown.
        :param number samplerate: A number so that seconds = val / samplerate
        """
        assert 0 <= num_decimals <= 6, "num_decimals must be in [0, ..., 6]!"
        self.num_decimals = num_decimals
        self._n_remove = 6 - num_decimals
        self.show_idx = show_idx
        self.samplerate = samplerate

    def __call__(self, val, pos):
        """
        :param number val: the axis value where the tick goes
        :param int pos: from 0 (left margin) to num_ticks+2 (right
          margin)
        :returns: A string in the form "{X days} h:m:s.ms"
        """
        ts = Timedelta(val, self.samplerate)
        ts_str = str(ts)
        if ts.microsecs > 0:
            ts_str = ts_str[: - self._n_remove]
        if self.show_idx:
            if isinstance(val, float) and val.is_integer():
                val = int(val)
            ts_str = str(val) + " (" + ts_str + ")"
        return ts_str


class DownsamplableFunction(object):
    """
    Encapsulates the downsampling functionality to prevent side effects,
    and reduce code verbosity in plotter.
    """
    def __init__(self, y_arr, max_datapoints, x_arr=None):
        """
        Given an array representing a function, the original x and y values can
        be accessed via ``self.x, self.y``, and the downsampled values via
        ``self.downsampled(xstart, xend)``.

        :param y_arr: A non-empty, one-dimensional array representing the
          y values of the function
        :param int max_datapoints: A positive number. See docstring for
          the downsampled method.
        :param x_arr: A non-empty, one-dimensional array representing the
          x values of the function. If None, it is assumed that it
          starts on 0 and increments by 1.

        .. note::

          The x-array will be sorted in ascending order.
        """
        assert max_datapoints > 0, "max_datapoints must be positive!"
        assert len(y_arr.shape) == 1, "Only 1D arrays expected!"
        self._len_y = len(y_arr)
        assert self._len_y > 0, "Empty array?"
        self.y = y_arr
        #
        if x_arr is not None:
            assert len(x_arr.shape) == 1, "Only 1D arrays expected!"
            self._len_x = len(x_arr)
            assert self._len_x == self._len_y, "len(x) must equal len(y)!"
            self.x = torch.Tensor(x_arr).sort()[0].numpy()
        else:
            self.x = torch.arange(self._len_y).numpy()
            self._len_x = self._len_y
        self.max_datapoints = max_datapoints

    def __len__(self):
        return self._len_y

    def downsampled(self, xstart, xend, verbose=False):
        """
        This function performs downsampling by reading one sample every
        ``(xend-xstart)//max_datapoints`` from x_vals and y_vals.
        """
        assert xstart <= xend, "malformed downsampling range!"
        #
        start = int(max(xstart, self.x[0]))
        end = int(min(xend, self.x[-1]))
        start_idx = self.x.searchsorted(start)
        end_idx = self.x.searchsorted(end)
        ratio = int(max(1, (end_idx - start_idx) // self.max_datapoints))
        #
        x_down = self.x[start_idx:end_idx + 1:ratio]
        y_down = self.y[start_idx:end_idx + 1:ratio]
        #
        if verbose:
            print("using", x_down.shape[0], "points")
        return x_down, y_down


class XlimCallbackFunctor(object):
    """
    Encapsulates the downsampling callback functionality to prevent side
    effects. Instances of this functor can be passed to an axis like
    this::

      ``ax.callbacks.connect('xlim_changed',
                       DownsamplingCallbackFunctor(ax, [line1..], [arr1...]))``
    """

    def __init__(self, axis, lines, arrays, shared_axes, verbose=False):
        """
        """
        self.ax = axis
        assert len(lines) == len(arrays), "error: len(lines) != len(arrays)"
        self.lines = lines
        self.arrays = arrays
        self.shared_axes = shared_axes
        self.verbose = verbose

    @staticmethod
    def _update_xlims(ax, xmin, xmax):
        """
        Calling ``ax.set_xlim(xmin, xmax)`` triggers the callback functor, so
        the limits can't be updated that way within the functor (it causes an
        infinite recursion). This updates the values directly, avoiding the
        loop.
        """
        ax.viewLim.x0 = xmin
        ax.viewLim.x1 = xmax

    def __call__(self, ax_limits):
        """
        See also::
        https://matplotlib.org/3.1.0/gallery/event_handling/resample.html
        """
        lims = ax_limits.viewLim
        xstart, xend = lims.intervalx
        self._update_xlims(self.ax, xstart, xend)
        for l, a in zip(self.lines, self.arrays):
            l.set_data(*a.downsampled(xstart, xend, self.verbose))
        self.ax.figure.canvas.draw_idle()


class SharedXlimCallbackFunctor(object):
    """
    If multiple axes share the x-limits, calling the functor from one of
    them triggers a call for every one of them.
    """
    def __init__(self, functors):
        """
        """
        self.functors = functors

    def __call__(self, ax_limits):
        for f in self.functors:
            f(ax_limits)
