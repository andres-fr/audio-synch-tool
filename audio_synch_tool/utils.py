#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
"""


import datetime
import torch


__author__ = "Andres FR"


# #############################################################################
# ## LOGIC
# #############################################################################

class Timestamp(object):
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


# #############################################################################
# ## MATPLOTLIB-RELATED
# #############################################################################

class SampleToTimestampFormatter(object):
    """
    This functor can be passed to ``plt.FuncFormatter`` to generate custom
    tick labels. It fulfills the interface (val, pos) -> str.

    Specifically, converts ``val`` number representing a sample into a string
    showing the corresponding elapsed time since sample 0, asuming the given
    samplerate.
    Usage example::

      ax.xaxis.set_major_formatter(plt.FuncFormatter(
                                   SampleToTimestampFormatter(sr)))
    """
    def __init__(self, samplerate, num_decimals=3, show_idx=True):
        """
        :param number samplerate: A number so that seconds = val / samplerate
        :param int num_decimals: An integer between 0 and 6.
        :param bool show_idx: If true, the sample index will be also shown.
        :returns: A string in the form "{X days} h:m:s.ms"
        """
        assert 0 <= num_decimals <= 6, "num_decimals must be in [0, ..., 6]!"
        self.samplerate = samplerate
        self.num_decimals = num_decimals
        self._n_remove = 6 - num_decimals
        self.show_idx = show_idx

    def __call__(self, val, pos):
        """
        :param number val: the axis value where the tick goes
        :param int pos: from 0 (left margin) to num_ticks+2 (right
          margin)
        """
        ts = Timestamp(val, self.samplerate)
        ts_str = str(ts)
        if ts.microsecs > 0:
            ts_str = ts_str[: - self._n_remove]
        if self.show_idx:
            if val.is_integer():
                val = int(val)
            ts_str = str(val) + " (" + ts_str + ")"
        return ts_str


class DownsamplableFunction(object):
    """
    Encapsulates the downsampling functionality to prevent side effects,
    and reduce code verbosity in plotter.
    """
    def __init__(self, arr, max_datapoints):
        """
        Given an array representing a function, the original x and y values can
        be accessed via ``self.x, self.y``, and the downsampled values via
        ``self.downsampled(xstart, xend)``.

        :param arr: A non-empty, one-dimensional array
        :param int max_datapoints: A positive number. See docstring for
          the downsampled method.
        """
        assert len(arr.shape) == 1, "Only 1D arrays expected!"
        assert max_datapoints > 0, "max_datapoints must be positive!"
        self._len = len(arr)
        assert self._len > 0, "Empty array?"
        self.y = arr
        self.x = torch.arange(self._len).numpy()
        self.max_datapoints = max_datapoints

    def __len__(self):
        return self._len

    def downsampled(self, xstart, xend):
        """
        This function performs downsampling by reading one sample every
        ``(xend-xstart)//max_datapoints`` from x_vals and y_vals.
        """
        assert xstart <= xend, "malformed downsampling range!"
        #
        start = int(max(xstart, 0))
        end = int(min(xend, self._len))
        ratio = int(max(1, (end - start) // self.max_datapoints))
        #
        x_down = self.x[start:end + 1:ratio]
        y_down = self.y[start:end + 1:ratio]
        #
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

    def __init__(self, axis, lines, arrays):
        """
        """
        self.ax = axis
        assert len(lines) == len(arrays), "error: len(lines) != len(arrays)"
        self.lines = lines
        self.arrays = arrays

    def __call__(self, ax_limits):
        """
        See also::
        https://matplotlib.org/3.1.0/gallery/event_handling/resample.html
        """
        lims = ax_limits.viewLim
        xstart, xend = lims.intervalx
        for l, a in zip(self.lines, self.arrays):
            l.set_data(*a.downsampled(xstart, xend))
        self.ax.figure.canvas.draw_idle()


class SharedXlimCallbackFunctor(object):
    """
    If multiple axes share
    """
    def __init__(self, functors):
        """
        """
        self.functors = functors

    def __call__(self, ax_limits):
        for f in self.functors:
            f(ax_limits)
