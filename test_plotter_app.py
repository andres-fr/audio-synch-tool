#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
python test_plotter_app.py -w ~/SAG_D1_10_M-Jem-2.wav
-m ~/SAG_D1-003_(snippet)_slate01_2-23-29.701.mvnx
-S ./audio_synch_tool/data/mvn_schema_adapted.xsd -n 10000 -x 20
"""

import argparse

import matplotlib.pyplot as plt
import soundfile as sf

from audio_synch_tool.plotters import AudioMvnSynchToolChecker
from audio_synch_tool.mvn import Mvn

__author__ = "Andres FR"


# #############################################################################
# ## HELPERS
# #############################################################################

def run_test_gui(wav_path, mvnx_path, mvnx_schema_path, max_samples_plotted,
                 num_xticks):
    """
    """
    wav_arr, audio_samplerate = sf.read(wav_path)
    mocap = Mvn(mvnx_path, mvnx_schema_path)

    plotter = AudioMvnSynchToolChecker(wav_arr, audio_samplerate, mocap,
                                       max_samples_plotted)
    plotter.NUM_XTICKS = num_xticks
    _ = plotter.make_fig()  # returns fig, but unused
    plt.show()


# #############################################################################
# ## MAIN ROUTINE
# #############################################################################

def main():
    """
    This main routine performs the following tasks:

    1. Parse arguments
    2. Load ground truth and predictions
    3. Compute metrics
    4. Render plot
    5. Optionally export plot and metrics
    6. Optionally show interactive plot
    7. Send plot and metrics to TensorBoard
    """
    # parse arguments from command line:
    parser = argparse.ArgumentParser(description="GUI to test WAV-MVNX synch")
    parser.add_argument("-w", "--wav_path", help="absolute path",
                        required=True)
    parser.add_argument("-m", "--mvnx_path", help="absolute path",
                        type=str, required=True)
    parser.add_argument("-S", "--mvnx_schema_path",
                        help="If given, the MVNX is validated to this schema",
                        type=str, default=None)
    parser.add_argument("-n", "--max_samples_plotted",
                        help="no. of samples per track to show (helps speed)",
                        type=int, default=10000)
    parser.add_argument("-x", "--num_xticks",
                        help="no. of labels on the x axis",
                        type=int, default=20)
    args = parser.parse_args()

    # main globals
    WAV_PATH = args.wav_path
    MVNX_PATH = args.mvnx_path
    MVNX_SCHEMA_PATH = args.mvnx_schema_path
    MAX_SAMPLES_PLOTTED = args.max_samples_plotted
    NUM_XTICKS = args.num_xticks
    #
    run_test_gui(WAV_PATH, MVNX_PATH, MVNX_SCHEMA_PATH, MAX_SAMPLES_PLOTTED,
                 NUM_XTICKS)


if __name__ == "__main__":
    main()
