#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
This module contains functionality concerning the adaption of the
XSENS MVN format into our Python setup.


The following section introduces the contents of the imported MVN file and the
way they can be accessed from Python::

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

:orientation: ``segmentCount*4 = 92``
:position, velocity, acceleration, angularVelocity, angularAcceleration:
  ``segmentCount*3 = 69``
:footContacts: ``4``
:sensorFreeAcceleration, sensorMagneticField: ``sensorCount*3 = 51``
:sensorOrientation: ``sensorCount*4 = 68``
:jointAngle, jointAngleXZY: ``jointCount*3 = 66``
:jointAngleErgo: ``12``
:centerOfMass: ``3``
"""

__author__ = "Andres FR"


from lxml import etree, objectify  # https://lxml.de/validation.html


# #############################################################################
# ## GLOBALS
# #############################################################################


# #############################################################################
# ## HELPERS
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
        mvn = etree.parse(mvn_path)
        # if a schema is given, load it and validate mvn
        self.schema_path = schema_path
        if schema_path is not None:
            self.schema = etree.XMLSchema(file=schema_path)
            assert self.schema.validate(mvn),\
                "[Mvn]: Given schema didn't validate given mvn!"
        #
        self.mvn = objectify.fromstring(etree.tostring(mvn))
        f_meta, config_f, normal_f = self._extract_mvn_frames(self.mvn)
        self.frames_metadata = f_meta
        self.config_frames = config_f
        self.normal_frames = normal_f

    def _extract_mvn_frames(self, mvn):
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

    def get_segments(self):
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