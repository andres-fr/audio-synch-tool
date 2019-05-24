#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
"""

import os
import matplotlib.pyplot as plt

import soundfile as sf
import torch

# from .utils import Timestamp
from .plotters import MultipleDownsampledPlotter1D
from .mvn import Mvn

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


# #############################################################################
# ## MAIN ROUTINE
# #############################################################################

# NUM_TRACKS = 8
# NUM_SHARED = 3
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MAX_SAMPLES_PLOTTED = 1e5
NUM_XTICKS = 20

# define paths
WAV_PATH = os.path.join(os.getenv("HOME"), "SAG_D1_10_M-Jem-2.wav")
MVN_PATH = os.path.join(os.getenv("HOME"),
                        "SAG_D1-003_(snippet)_slate01_2-23-29.701.mvnx")
# MVN_PATH = os.path.join(os.getenv("HOME"),
#                       "SAG_D1-003_(snippet)_slate03_2-35-44.759.mvnx")
MVN_SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "data", "mvn_schema_adapted.xsd")

# load fiels
wav_arr, audio_samplerate = sf.read(WAV_PATH)
mocap = Mvn(MVN_PATH, MVN_SCHEMA_PATH)

# extract info from mocap
mocap_samplerate = float(mocap.mvn.subject.attrib["frameRate"])
mocap_segments = mocap.get_segments()
frame_sequences = mocap.get_normalframe_sequences("cpu")
mocap_accelerations_3d = frame_sequences["acceleration"]
mocap_accel_norm = torch.norm(mocap_accelerations_3d, 2, dim=-1)

# plot
arrays = [[wav_arr],
          [mocap_accel_norm[:, mocap_segments.index("LeftShoulder")].numpy(),
           mocap_accel_norm[:, mocap_segments.index("LeftForeArm")].numpy(),
           mocap_accel_norm[:, mocap_segments.index("LeftHand")].numpy()],
          [mocap_accel_norm[:, mocap_segments.index("RightShoulder")].numpy(),
           mocap_accel_norm[:, mocap_segments.index("RightForeArm")].numpy(),
           mocap_accel_norm[:, mocap_segments.index("RightHand")].numpy()]]
samplerates = [audio_samplerate, mocap_samplerate, mocap_samplerate]
tied_plots = [False, True, True]
p = MultipleDownsampledPlotter1D(arrays, samplerates, MAX_SAMPLES_PLOTTED,
                                 tied_plots)
fig = p.make_fig()
plt.show()
