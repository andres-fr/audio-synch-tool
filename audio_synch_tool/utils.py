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
# import matplotlib.pyplot as plt
# from matplotlib import gridspec
# import soundfile as sf
# import torch
# import numpy as np

import datetime


__author__ = "Andres FR"


# #############################################################################
# ##
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
