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



# # #############################################################################
# # ## MAIN ROUTINE
# # #############################################################################

# NUM_TRACKS = 8
# NUM_SHARED = 3
MAX_SAMPLES_PLOTTED = 1e5
NUM_XTICKS = 20

WAV_PATH = os.path.join(os.getenv("HOME"), "SAG_D1_10_M-Jem-2.wav")
MVN_PATH = os.path.join(os.getenv("HOME"), "SAG_D1-003_(snippet)_slate01_2-23-29.701.mvnx")
# MVN_PATH = os.path.join(os.getenv("HOME"), "SAG_D1-003_(snippet)_slate03_2-35-44.759.mvnx")


MVN_SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "data", "mvn_schema_adapted.xsd")


wav_arr, audio_samplerate = sf.read(WAV_PATH)
mocap = Mvn(MVN_PATH, MVN_SCHEMA_PATH)
mocap_samplerate = float(mocap.mvn.subject.attrib["frameRate"])

n_segments = int(mocap.frames_metadata["segmentCount"])
n_sensors = int(mocap.frames_metadata["sensorCount"])
n_joints = int(mocap.frames_metadata["jointCount"])

mocap_segments = mocap.get_segments()
mocap_magnitudes = list(mocap.normal_frames[0].keys())

mocap_accelerations_3d = {seg: [] for seg in mocap_segments}
for i, f in enumerate(mocap.normal_frames):
    assert i == f["index"], \
        "MVN sequence skipped one frame at %s?" % f["index"]
    acc = f["acceleration"]
    assert len(acc) == n_segments * 3, "Malformed acceleration vector?"
    for j, segment in enumerate(mocap_segments):
        segment_3d_vec = torch.Tensor(acc[3 * j : 3 * j + 3])
        mocap_accelerations_3d[segment].append(segment_3d_vec)

mocap_accel_norm = {k: torch.Tensor([torch.norm(vv, 2) for vv in v]).numpy()
                    for k, v in mocap_accelerations_3d.items()}



def test_plot():
    N = 5
    arrays = [[wav_arr] if i == 0 else torch.rand(3, 100000).numpy()
              for i in range(N)]
    samplerates = [audio_samplerate if i == 0 else mocap_samplerate
                   for i in range(N)]
    tied_plots = [False if i == 0 else True for i in range(N)]
    p = MultipleDownsampledPlotter1D(arrays, samplerates, MAX_SAMPLES_PLOTTED,
                                     tied_plots)
    fig = p.make_fig(num_xticks=NUM_XTICKS)
    plt.show()

print(mocap_segments)
arrays = [[wav_arr],
          [mocap_accel_norm["LeftForeArm"], mocap_accel_norm["LeftHand"]],
          [mocap_accel_norm["RightForeArm"], mocap_accel_norm["RightHand"]]]
samplerates = [audio_samplerate, mocap_samplerate, mocap_samplerate]
tied_plots = [False, True, True]
p = MultipleDownsampledPlotter1D(arrays, samplerates, MAX_SAMPLES_PLOTTED,
                                 tied_plots)
fig = p.make_fig()
plt.show()


# for f in mocap.normal_frames:
#     print(len(f["acceleration"]))


# The enumerate thing is to make sure they are ordered by id.
# mvn_segments = [ch.attrib["label"] if str(i) == ch.attrib["id"] else None
#                 for i, ch in enumerate(
#                         mocap.mvn.subject.segments.iterchildren(), 1)]
# assert all([s is not None for s in mvn_segments]),\
#     "Segments aren't ordered by id?"
# test_plot()



# ['orientation', 'position', 'velocity', 'acceleration',
#  'angularVelocity', 'angularAcceleration', 'footContacts',
#  'sensorFreeAcceleration', 'sensorMagneticField', 'sensorOrientation',
#  'jointAngle', 'jointAngleXZY', 'jointAngleErgo', 'centerOfMass', 'time',
#  'index', 'tc', 'ms', 'type']



## acceleration: 69 frames. segmentcount * 3


# for k,v in mocap_accelerations_norm.items():
#     print(k, v)
