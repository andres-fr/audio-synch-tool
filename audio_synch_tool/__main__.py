#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
"""

import matplotlib.pyplot as plt

import soundfile as sf
import torch

# from .utils import Timestamp
from .plotters import DownsampledPlotter1D, MultipleDownsampledPlotter1D


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
MAX_SAMPLES_PLOTTED = 10000
MVN_SAMPLERATE = 240

wav_path = '/home/a9fb1e/SAG_D1_10_M-Jem-2.wav'

arr, audio_samplerate = sf.read(wav_path)
# tnsr = torch.from_numpy(arr)




# plotter = MultiTrackPlotter()
# fig = plotter.make_fig("Test 1 2 3", arr, NUM_TRACKS, NUM_SHARED)

# fig.show()
# input("quack")





# p = DownsampledPlotter1D(arr, MAX_SAMPLES_PLOTTED, samplerate)
# fig = p.make_fig()
# plt.show(fig)





N = 2
arrays = [arr if i == 0 else torch.rand(100000).numpy()
          for i in range(N)]
samplerates = [audio_samplerate if i == 0 else MVN_SAMPLERATE
               for i in range(N)]
# # samplerates = [None for i in range(N)]
# samplerates = [1000 if i == 0 else 100
#                for i in range(N)]


tied_plots = [False if i == 0 else True for i in range(N)]
# tied_plots = [i%2 == 1 for i in range(N)]


p = MultipleDownsampledPlotter1D(arrays, samplerates, MAX_SAMPLES_PLOTTED,
                                 tied_plots)
fig = p.make_fig(tick_rot_deg=20)

# for ax in fig.get_axes():
#     fn = ax.xaxis.get_major_formatter().func
#     print(">>>>>>>>>>", fn(10000, None))

plt.show(fig)
