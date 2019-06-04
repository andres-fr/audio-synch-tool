#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
This module contains functionality concerning the adaption of the
XSENS MVN-XML format into our Python setup.

The official explanation can be found in section 14.4 of this document::
  https://usermanual.wiki/Document/MVNUserManual.1147412416.pdf

A copy is stored in this repository.

The following section introduces more informally the contents of the imported
MVN file and the way they can be accessed from Python::

  # load mvn schema https://www.xsens.com/mvn/mvnx/schema.xsd
  MVN_SCHEMA_PATH = "xxx"
  mvn_path = "yyy"
  mmvn = Mvn(mvn_path, MVN_SCHEMA_PATH)

  # These elements contain some small metadata:
  mmvn.mvn.attrib
  mmvn.mvn.comment.attrib
  mmvn.mvn.securityCode.attrib["code"]
  mmvn.mvn.subject.attrib

  # subject.segments contain 3D pos_b labels:
  for ch in mmvn.mvn.subject.segments.iterchildren():
      ch.attrib, [p.attrib for p in ch.points.iterchildren()]

  # Segments can look as follows: ``['Pelvis', 'L5', 'L3', 'T12', 'T8', 'Neck',
  'Head', 'RightShoulder', 'RightUpperArm', 'RightForeArm', 'RightHand',
  'LeftShoulder', 'LeftUpperArm', 'LeftForeArm', 'LeftHand', 'RightUpperLeg',
  'RightLowerLeg', 'RightFoot', 'RightToe', 'LeftUpperLeg', 'LeftLowerLeg',
  'LeftFoot', 'LeftToe']``

  # sensors is basically a list of names
  for s in mmvn.mvn.subject.sensors.iterchildren():
      s.attrib

  #  Joints is a list that connects segment points:
  for j in mmvn.mvn.subject.joints.iterchildren():
      j.attrib["label"], j.getchildren()

  # miscellaneous:
  for j in mmvn.mvn.subject.ergonomicJointAngles.iterchildren():
      j.attrib, j.getchildren()

  for f in mmvn.mvn.subject.footContactDefinition.iterchildren():
      f.attrib, f.getchildren()

  # The bulk of the data is in the frames.
  print("frames_metadata:", mmvn.frames_metadata)
  print("first_frame_type:", mmvn.config_frames[0]["type"])
  print("normal_frames_type:", mmvn.normal_frames[0]["type"])
  print("num_normal_frames:", len(mmvn.normal_frames))

  # Metadata looks like this:
  {'segmentCount': '23', 'sensorCount': '17', 'jointCount': '22'}

  # config frames have the following fields:
  ['orientation', 'position', 'time', 'tc', 'ms', 'type']

  # normal frames have the following fields:
  ['orientation', 'position', 'velocity', 'acceleration',
   'angularVelocity', 'angularAcceleration', 'footContacts',
   'sensorFreeAcceleration', 'sensorMagneticField', 'sensorOrientation',
   'jointAngle', 'jointAngleXZY', 'jointAngleErgo', 'centerOfMass', 'time',
   'index', 'tc', 'ms', 'type']

The following fields contain metadata about the frame:

:time: ms since start (integer). It is close to
  ``int(1000.0 * index / samplerate)``, being equal most of the times and
  at most 1 milisecond away. It is neither truncated nor rounded, maybe it
  is given by the hardware.
:index: starts with 0, +1 each normal frame
:tc: string like '02:23:28:164'
:ms: unix timestamp like 1515983008686 (used to compute time)
:type: one of "identity", "tpose", "tpose-isb", "normal"

# The following fields are float vectors of the following dimensionality:

:orientation: ``segmentCount*4 = 92`` Quaternion vector
:position, velocity, acceleration, angularVelocity, angularAcceleration:
  ``segmentCount*3 = 69`` 3D vectors in ``(x,y,z)`` format
:footContacts: ``4`` 4D boolean vector
:sensorFreeAcceleration, sensorMagneticField: ``sensorCount*3 = 51``
:sensorOrientation: ``sensorCount*4 = 68``
:jointAngle, jointAngleXZY: ``jointCount*3 = 66``
:jointAngleErgo: ``12``
:centerOfMass: ``3``

The units are SI for position, velocity and acceleration. Angular magnitudes
are in radians except the ``jointAngle...`` ones that are in degrees. All 3D
vectors are in ``(x,y,z)`` format, but the ``jointAngle...`` ones differ in
the Euler-rotation order by which they are computed (ZXY, standard or XZY,
for shoulders usually).

"""


__author__ = "Andres FR"


import torch
from lxml import etree, objectify  # https://lxml.de/validation.html
from .utils import make_timestamp


# #############################################################################
# ## GLOBALS
# #############################################################################


# #############################################################################
# ## HELPERS
# #############################################################################


# #############################################################################
# ## MVN CLASS
# #############################################################################

class Mvn(object):
    """
    This class imports and adapts an XML file (expected to be in MVN format)
    to a Python-friendly representation. See this module's docstring for usage
    examples and more information.
    """

    def __init__(self, mvn_path, schema_path=None):
        """
        :param str mvn_path: a valid path pointing to the XML file to load
        :param str schema_path: (optional): a valid path pointing to an MVN
          schema to validate the XML file in mvn_path. If None, validation is
          skipped and this part ignored.
        """
        self.mvn_path = mvn_path
        self.schema_path = schema_path
        #
        mvn = etree.parse(mvn_path)
        # if a schema is given, load it and validate mvn
        if schema_path is not None:
            self.schema = etree.XMLSchema(file=schema_path)
            self.schema.assertValid(mvn)
        #
        self.mvn = objectify.fromstring(etree.tostring(mvn))

    def export(self, filepath, pretty_print=True, extra_comment=""):
        """
        Saves the current ``mvn`` attribute to the given file path as XML and
        adds the ``self.mvn.comment.attrib["export_details"]`` attribute with
        a timestamp.
        """
        #
        with open(filepath, "w") as f:
            msg = "Exported from %s on %s. " % (
                self.__class__.__name__, make_timestamp()) + extra_comment
            self.mvn.comment = objectify.DataElement(msg, _pytype="")
            s = etree.tostring(self.mvn,
                               pretty_print=pretty_print).decode("utf-8")
            f.write(s)
            print("[Mvn] exported to", filepath)

    def set_comment(self, comment):
        """
        Sets a comment that can be found as a string under self.mvn.comment
        """
        self.mvn.comment = objectify.DataElement(comment, _pytype="")

    def set_audio_synch(self, stretch, shift):
        """
        Given the list of normal frames in this Mvn, each one with an "index"
        field, this function adds an ``audio_sample`` attribute to each frame,
        where ``audio_sample = index * stretch + shift``.
        See ``utils.convert_anchors`` for converting anchor points into stretch
        and shift.
        """
        normal_frames = [f for f in self.mvn.subject.frames.getchildren()
                         if f.attrib["type"] == "normal"]
        for f in normal_frames:
            f_idx = float(f.attrib["index"])
            audio_idx = int(f_idx * float(stretch) + float(shift))
            f.attrib["audio_sample"] = str(audio_idx)
        print("finished adding 'audio_sample' attrib to normal frames",
              "with stretch =", stretch, "and shift =", shift)

    def get_audio_synch(self):
        """
        :returns: a list with the ``audio_sample`` attributes for the
          normal frames, or None if there is at least 1 normal frame without
          the ``audio_sample`` attribute. Note that this function assumes that
          the entries are integers in the form '123', so they are retrieved
          int(x). If that is not the case, they may be truncated or even throw
          an exception.
        """
        try:
            return [int(f.attrib["audio_sample"])
                    for f in self.mvn.subject.frames.getchildren()
                    if f.attrib["type"] == "normal"]
        except KeyError:
            return None

    # EXTRACTORS: LIKE "GETTERS" BUT RETURN A MODIFIED COPY OF THE CONTENTS
    def extract_frame_info(self):
        """
        :returns: The tuple ``(frames_metadata, config_frames, normal_frames)``
        """
        f_meta, config_f, normal_f = self.extract_frames(self.mvn)
        frames_metadata = f_meta
        config_frames = config_f
        normal_frames = normal_f
        #
        assert (int(frames_metadata["segmentCount"]) ==
                len(self.extract_segments())), "Inconsistent segmentCount?"
        return frames_metadata, config_frames, normal_frames

    @staticmethod
    def extract_frames(mvn):
        """
        The bulk of the MVN file is the ``mvn->subject->frames`` section.
        This function parses it and returns its information in a
        python-friendly format.

        :param mvn: An XML tree, expected to be in MVN format

        :returns: a tuple ``(frames_metadata, config_frames, normal_frames)``
          where the metadata is a dict in the form ``{'segmentCount': '23',
          'sensorCount': '17', 'jointCount': '22'}``, the config frames are the
          first 3 frame entries (expected to contain special config info)
          and the normal_frames are all frames starting from the 4th. Both
          frame outputs are relational collections of dictionaries that can be
          formatted into tabular form.
        """
        def str_to_vec(x):
            """
            Converts a node with a text like '1.23, 2.34 ...' into a list
            like [1.23, 2.34, ...]
            """
            return [float(y) for y in x.text.split(" ")]

        def frame_to_dict(frame, is_normal):
            """
            A frame node has a dict of ``attribs`` and a dict of ``items``.
            This function merges both and returns a single python dict
            """
            d = {**{k: str_to_vec(v) for k, v in frame.__dict__.items()},
                 **frame.attrib}
            d["time"] = int(d["time"])  # ms since start, i.e. ms_i - ms_0
            d["ms"] = int(d["ms"])  # unix timestamp, ms since epoch
            if is_normal:  # only normal frames have index
                d["index"] = int(d["index"])  # starts by 0, increases by 1
            try:
                d["audio_sample"] = int(d["audio_sample"])
            except KeyError:
                pass
            return d
        #
        frames_metadata = mvn.subject.frames.attrib
        all_frames = mvn.subject.frames.getchildren()
        # first 3 frames are config. types: "identity", "tpose", "tpose-isb"
        # rest of frames contain proper data. type: "normal"
        config_frames = [frame_to_dict(f, False) for f in all_frames[:3]]
        normal_frames = [frame_to_dict(f, True) for f in all_frames[3:]]
        #
        return frames_metadata, config_frames, normal_frames

    def extract_segments(self):
        """
        :returns: A list of the segment names in ``self.mvn.subject.segments``,
          ordered by id (starting at 1 and incrementing +1).
        """
        segments = [ch.attrib["label"] if str(i) == ch.attrib["id"] else None
                    for i, ch in enumerate(
                            self.mvn.subject.segments.iterchildren(), 1)]
        assert all([s is not None for s in segments]),\
            "Segments aren't ordered by id?"
        return segments

    @staticmethod
    def extract_normalframe_magnitudes(normal_frames):
        """
        :returns: A list of the magnitude names in each of the
          ``self.normal_frames``
        """
        result = list(normal_frames[0].keys())
        for i, f in enumerate(normal_frames[1:]):
            assert list(f.keys()) == result, \
                "Inconsistent magnitudes in frame %d?" % i
        return result

    def extract_normalframe_sequences(self, frames_metadata, normal_frames,
                                      device="cpu"):
        """
        :returns: a dict with torch tensors of shape
          ``(num_normalframes, num_channels)`` where the number of channels is
          e.g. 1 for scalar magnitudes, 3 for 3D vectors (in xyz format)...
        """
        # prepare variables and resulting datastructure
        all_magnitudes = self.extract_normalframe_magnitudes(normal_frames)
        n_segments = int(frames_metadata["segmentCount"])
        n_sensors = int(frames_metadata["sensorCount"])
        n_joints = int(frames_metadata["jointCount"])
        result = {m: [] for m in all_magnitudes}
        # loop through all frames collecting the per-magnitude sequences
        for i, f in enumerate(normal_frames):
            assert i == f["index"], \
                "MVN sequence skipped one frame at %s?" % f["index"]

            for mag in f.keys():
                # add string entries:
                if mag in {"tc", "type"}:
                    entry = f[mag]
                # add as-is int scalars:
                elif mag in {"time", "index", "ms", "footContacts",
                             "audio_sample"}:
                    entry = torch.LongTensor([f[mag]])
                # add as-is float vectors:
                elif mag in {"centerOfMass", "jointAngleErgo"}:
                    entry = torch.Tensor([f[mag]])
                # add 3D magment vectors
                elif mag in {"position", "velocity", "acceleration",
                             "angularVelocity", "angularAcceleration"}:
                    entry = torch.Tensor(f[mag]).view(n_segments, 3)
                # add 4D magment vectors
                elif mag == "orientation":
                    entry = torch.Tensor(f[mag]).view(n_segments, 4)
                # add 3D sensor vectors
                elif mag in {"sensorFreeAcceleration",
                             "sensorMagneticField"}:
                    entry = torch.Tensor(f[mag]).view(n_sensors, 3)
                # add 4D magment vectors
                elif mag == "sensorOrientation":
                    entry = torch.Tensor(f[mag]).view(n_sensors, 4)
                # add 3D joint vectors:
                elif mag in {"jointAngle", "jointAngleXZY"}:
                    entry = torch.Tensor(f[mag]).view(n_joints, 3)
                # this should never happen
                else:
                    comp = mag + " should be in " + str(all_magnitudes)
                    raise Exception("Inconsistent frame magnitude? %s" % comp)
                result[mag].append(entry)
        # once the loop is done, convert sequences to tensors and we are done:

        for k, v in result.items():
            try:
                result[k] = torch.stack(v).to(device)
            except TypeError:
                # This will happen for the "string" entries, which cannot be
                # converted to tensors. Just leave them unchanged
                pass
        return result
