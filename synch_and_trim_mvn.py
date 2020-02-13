#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Given:
1. A "longer" wav file
2. A "shorter" wav file subset of 1.
3. An MVN file
4. A set of 2 ori->dest anchor points from the MVN to the "longer" wav
5. An output MVN path
This script saves to the output path a copy of the MVN that extends its
information with:
   a) The "shorter" WAV file it will refer to
   b) The per-frame "shorter WAV" corresponding sample

But the anchors are given by the "longer" wav. Therefore, in order to
do that it has to:
1. Find exactly the start and end points from the "shorter" in the "longer"
2. Compute, for each frame, the "longer" corresponding sample
3. Remove the MVN frames that aren't within the start and end points
4. Subtract "start" from every corresponding sample
5. Export
"""


import os
import argparse
#
import soundfile as sf
#
from audio_synch_tool.utils import convert_anchors
from audio_synch_tool.mvn import Mvn


__author__ = "Andres FR"


# #############################################################################
# ## HELPERS
# #############################################################################

def numpy_find_sublist(arr1, arr2):
    """
    :param ndarray arr1: 1D numpy array
    :param ndarray arr2: 1D numpy array of same dtype as arr1 (e.g. np.float32)
    :returns: a tuple (A, B) where A is the tuple (beg, end) if
      arr2[beg:end]==arr1, and None otherwise. B works the same for arr2.
    """
    result1, result2 = None, None
    #
    assert arr1.dtype == arr2.dtype, "arrays must have same dtype!"
    assert len(arr1.shape) == len(arr2.shape) == 1, "arrays must be 1D!"
    elem_bytes = arr1.itemsize  # should be the same for both
    str1, str2 = arr1.tostring(), arr2.tostring()
    len1, len2 = arr1.shape[0], arr2.shape[0]
    # find if arr1 is a sublist of arr2
    try:
        beg1 = str2.index(str1) // elem_bytes
        result1 = (beg1, beg1 + len1)
    except ValueError:
        pass
    # find if arr2 is a sublist of arr1
    try:
        beg2 = str1.index(str2) // elem_bytes
        result2 = (beg2, beg2 + len2)
    except ValueError:
        pass
    #
    return (result1, result2)


# #############################################################################
# ## MAIN ROUTINE
# #############################################################################

def main():
    """
    See module docstring
    """
    # parse arguments from command line:
    parser = argparse.ArgumentParser(description="Synch and trim MVN")
    parser.add_argument("-v", "--shorter_wav", help="absolute path",
                        required=True)
    parser.add_argument("-w", "--longer_wav", help="absolute path",
                        required=True)
    parser.add_argument("-m", "--mvnx_path", help="absolute path",
                        type=str, required=True)
    parser.add_argument("-V", "--validate_mvnx",
                        help="If given, the MVNX is validated to our schema",
                        action="store_true")
    parser.add_argument("-a", "--anchors",
                        help="A set of 4 numbers: ori1, dest1, ori2, dest2.",
                        type=float, nargs=4, required=True)
    parser.add_argument("-o", "--out_path", help="If none given, name+anchors",
                        type=str, default=None)
    parser.add_argument("-p", "--pretty_print",
                        help="If given, exported MVNX is indented",
                        action="store_true")
    args = parser.parse_args()

    # main globals
    SHORT_WAV_PATH = args.shorter_wav
    LONG_WAV_PATH = args.longer_wav
    MVNX_PATH = args.mvnx_path
    VALIDATE_MVNX = args.validate_mvnx
    ANCHORS = args.anchors
    OUT_PATH = args.out_path
    PRETTY_PRINT = args.pretty_print

    # check anchors and compute stretch and shift
    assert len(ANCHORS) == 4, "Script expects 4 anchor numbers!"
    ori1, dest1, ori2, dest2 = ANCHORS
    assert ori1 < ori2, "Ori1 anchor must be smaller than Ori2 anchor!"
    assert dest1 < dest2, "Dest1 anchor must be smaller than Dest2 anchor!"
    stretch, shift = convert_anchors(ori1, dest1, ori2, dest2)

    # load wav files and check them
    print("loading and checking wav files...")
    short_wav, short_samplerate = sf.read(SHORT_WAV_PATH)
    long_wav, long_samplerate = sf.read(LONG_WAV_PATH)
    if short_samplerate != long_samplerate:
        print("WARNING: mismatching samplerates!", short_samplerate,
              long_samplerate)
        input("press any key to continue")
    positions, _ = numpy_find_sublist(short_wav, long_wav)
    assert positions is not None, "short wav not in long wav?"
    beg, end = positions  # the range of the "long" that contains the "short"
    assert beg < end, "beg >= end? this should never happen"

    # load mvnx and add the audio information
    print("loading MVNX from", MVNX_PATH)
    mocap = Mvn(MVNX_PATH, VALIDATE_MVNX)
    mocap.set_audio_synch(stretch, shift)
    wav_name = os.path.basename(SHORT_WAV_PATH)
    mocap.mvn.attrib["wav_file"] = wav_name
    print("Added mvn.mvn.attrib['wav_file'] =", wav_name)

    # add the audio sample attr to every frame. Also remove all samples above
    # the "end" range, and collect the samples before "beg" for later
    all_frames = mocap.mvn.subject.frames
    left_trim_samples = []
    # right_trim_samples = []
    for f in all_frames.iterchildren():
        if f.attrib["type"] == "normal":
            # for each normal frame, read the index and "long" audio index
            a_idx = int(f.attrib["audio_sample"])
            # subtract the "beg" sample from every audio idx to get the "short"
            f.attrib["audio_sample"] = str(a_idx - beg)
            if a_idx <= beg:
                left_trim_samples.append(f)
            elif a_idx > end:
                all_frames.remove(f)

    # set the last left_trim_sample to 0 (so the audio begins with info) and
    # remove the rest
    max_left_trim = max([s.attrib["audio_sample"] for s in left_trim_samples])
    for s in left_trim_samples:
        saas = s.attrib["audio_sample"]
        if saas == max_left_trim:
            s.attrib["audio_sample"] = "0"  # set the latest non-pos to zero
        else:
            all_frames.remove(s)

    # export modified file:
    if OUT_PATH is None:
        oo1 = str(int(ori1) if ori1.is_integer() else ori1)
        dd1 = str(int(dest1) if dest1.is_integer() else dest1)
        oo2 = str(int(ori2) if ori2.is_integer() else ori2)
        dd2 = str(int(dest2) if dest2.is_integer() else dest2)
        OUT_PATH = MVNX_PATH + "_o1d1o2d2=" + "_".join([oo1, dd1, oo2, dd2])
    mocap.export(OUT_PATH, pretty_print=PRETTY_PRINT, extra_comment="")


if __name__ == "__main__":
    main()
