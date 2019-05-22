#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
"""

import matplotlib.pyplot as plt

import soundfile as sf
 #import torch

# from .utils import Timestamp
from .plotters import AudioPlotter


__author__ = "Andres FR"


# #############################################################################
# ## GLOBALS
# #############################################################################


# #############################################################################
# ## HELPERS
# #############################################################################


class WavMvnStruct(object):
    """
    This class handles the logic required to synchronize a WAV audio file with
    a MVN motion capture file, both with different sampling rates.
    """
    def __init__(self, wav_arr, mvn_obj):
        """
        """
        self.wav = wav_arr
        self.mvn = mvn_obj



# # #############################################################################
# # ## MAIN ROUTINE
# # #############################################################################

# NUM_TRACKS = 8
# NUM_SHARED = 3
MAX_SAMPLES_PLOTTED = 5e4

wav_path = '/home/a9fb1e/SAG_D1_10_M-Jem-2.wav'

arr, samplerate = sf.read(wav_path)
# tnsr = torch.from_numpy(arr)




# plotter = MultiTrackPlotter()
# fig = plotter.make_fig("Test 1 2 3", arr, NUM_TRACKS, NUM_SHARED)

# fig.show()
# input("quack")




p = AudioPlotter(arr, MAX_SAMPLES_PLOTTED, samplerate)
fig = p.make_fig()
# fig.show()
# input("quack")
plt.show(fig)
