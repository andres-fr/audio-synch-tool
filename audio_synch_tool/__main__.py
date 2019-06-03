#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
"""

import os
import matplotlib.pyplot as plt

import soundfile as sf
import torch

# from .utils import Timestamp
from .plotters import MultipleDownsampledPlotter1D, AudioMvnSynchToolModifier, AudioMvnSynchToolChecker
from .plotters import TextPrompt, ShiftRightTool, StretchRightTool
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

MVN_SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "data", "mvn_schema_adapted.xsd")


# load fiels
wav_arr, audio_samplerate = sf.read(WAV_PATH)
mocap = Mvn(MVN_PATH, MVN_SCHEMA_PATH)

# extract info from mocap
mocap_samplerate = float(mocap.mvn.subject.attrib["frameRate"])
mocap_segments = mocap.extract_segments()
frames_metadata, config_frames, normal_frames = mocap.extract_frame_info()
frame_sequences = mocap.extract_normalframe_sequences(frames_metadata,
                                                      normal_frames, "cpu")
mocap_accelerations_3d = frame_sequences["acceleration"]
mocap_accel_norm = torch.norm(mocap_accelerations_3d, 2, dim=-1)

# mocap.set_audio_synch(10000, 2000000)
# mocap.export("quack.asdf", extra_comment="Bound to audio file XYZ")
# input("asdfasdf")





# {'time': '0', 'tc': '00:00:00:000', 'ms': '0', 'type': 'identity'}
# {'time': '0', 'tc': '00:00:00:000', 'ms': '0', 'type': 'tpose'}
# {'time': '0', 'tc': '00:00:00:000', 'ms': '0', 'type': 'tpose-isb'}
# {'time': '0', 'index': '0', 'tc': '02:23:28:164', 'ms': '1515983008686', 'type': 'normal'}
# {'time': '5', 'index': '1', 'tc': '02:23:28:165', 'ms': '1515983008691', 'type': 'normal'}
# {'time': '9', 'index': '2', 'tc': '02:23:28:166', 'ms': '1515983008695', 'type': 'normal'}
# {'time': '13', 'index': '3', 'tc': '02:23:28:167', 'ms': '1515983008699', 'type': 'normal'}
# {'time': '17', 'index': '4', 'tc': '02:23:28:168', 'ms': '1515983008703', 'type': 'normal'}



# mvn_arrays = [[mocap_accel_norm[:, mocap_segments.index("LeftShoulder")].numpy(),
#                mocap_accel_norm[:, mocap_segments.index("LeftForeArm")].numpy(),
#                mocap_accel_norm[:, mocap_segments.index("LeftHand")].numpy()],
#               [mocap_accel_norm[:, mocap_segments.index("RightShoulder")].numpy(),
#                mocap_accel_norm[:, mocap_segments.index("RightForeArm")].numpy(),
#                mocap_accel_norm[:, mocap_segments.index("RightHand")].numpy()]]
# p = AudioMvnSynchTool(wav_arr, mvn_arrays, audio_samplerate,
#                       mocap_samplerate, MAX_SAMPLES_PLOTTED)

# mocap.set_audio_synch(10000, 2000000)
# p = AudioMvnSynchTool(wav_arr, audio_samplerate, mocap, MAX_SAMPLES_PLOTTED)

p = AudioMvnSynchToolModifier(wav_arr, audio_samplerate, mocap, MAX_SAMPLES_PLOTTED)

# textbox_widget = TextPrompt
# toolbar_widgets = ShiftRightTool, StretchRightTool
# fig = p.make_fig(textbox_widget, toolbar_widgets)


fig = p.make_fig()
plt.show()


# # fig = p.make_fig(textbox_widget, toolbar_widgets)
# fig = p.make_fig()
# plt.show()




# # plot
# y_arrays = [[wav_arr],
#             [mocap_accel_norm[:, mocap_segments.index("LeftShoulder")].numpy(),
#              mocap_accel_norm[:, mocap_segments.index("LeftForeArm")].numpy(),
#              mocap_accel_norm[:, mocap_segments.index("LeftHand")].numpy()],
#             [mocap_accel_norm[:, mocap_segments.index("RightShoulder")].numpy(),
#              mocap_accel_norm[:, mocap_segments.index("RightForeArm")].numpy(),
#              mocap_accel_norm[:, mocap_segments.index("RightHand")].numpy()]]






# x_arrays = [[torch.arange(len(yarr)).numpy() for yarr in yarrs]
#             for yarrs in y_arrays]

# # x_arrays[0][0] -= 8000 * 60

# for a in x_arrays[1]:
#     a *= 50000
# for a in x_arrays[2]:
#     a *= 50000

# samplerates = [audio_samplerate, mocap_samplerate, mocap_samplerate * 2]
# # samplerates = [audio_samplerate, mocap_samplerate, mocap_samplerate]
# tied_plots = [True, True, True] # [False, False, False]
# p = MultipleDownsampledPlotter1D(y_arrays, samplerates, MAX_SAMPLES_PLOTTED,
#                                  tied_plots, x_arrays)


# textbox_widget = TextPrompt
# toolbar_widgets = ShiftRightTool, StretchRightTool


# # fig = p.make_fig(textbox_widget, toolbar_widgets)
# fig = p.make_fig()
# plt.show()
