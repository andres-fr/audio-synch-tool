#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
.. warning::
  Since BSON can be bigger than JSON (see https://stackoverflow.com/a/24116464)
  this module is abandoned until a better solution comes up.

The goal of this module is to provide an interface between MVNX and MMC, both
in JSON and BSON format.

1. Have a proper definition of MMC
2. load MVNX into an XML tree
3. convert logical data into MMC
4. export/import MMC both as JSON and BSON
5. convert logical data back into XML tree
"""


__author__ = "Andres FR"

import lxml
import json
import bson
# import jsonschema
from audio_synch_tool.mvn import Mvn
from collections import OrderedDict

# import torch
# from lxml import etree, objectify  # https://lxml.de/validation.html
# from .utils import make_timestamp


# #############################################################################
# ## GLOBALS
# #############################################################################


# #############################################################################
# ## HELPERS
# #############################################################################


# #############################################################################
# ## CONVERTER
# #############################################################################

class ObjectifiedMvnToJsonEncoder(json.JSONEncoder):
    """
    This encoder handles the conversion from an MVNX object that follows our
    modified schema and has been imported via ``lxml.objectify``, into a
    JSON object. It can be passed to ``json.dumps`` to create a JSON string
    that can be then exported as plain text or BSON.
    """

    EXPECTED_TYPES = [lxml.etree._Attrib, lxml.objectify.StringElement,
                      lxml.objectify.ObjectifiedElement]
    ALL_ARRAYS_AS_FLOAT = True

    @classmethod
    def process_string(self, s):
        """
        """
        # handle empty strings
        if not s:
            return ""
        # handle vectors as strings:
        try:
            # assume a list like '1.23 2.5 3.14 5 6' and try to extract nums
            result = [float(x) for x in s.split(" ")]
            # if the list had one scalar, return it as int or float
            if len(result) == 1:
                try:
                    return int(s)
                except ValueError:
                    return result[0]
                return result
            # if the string had multiple scalars, return as list
            if not self.ALL_ARRAYS_AS_FLOAT:
                # if desired, convert int arrays to int type (otherwise float)
                if all([x % 1 == 0 for x in result]):
                    result = [int(x) for x in result]
            return result
        # if the str was neither empty nor a vector, return it
        except ValueError:
            return s

    @classmethod
    def process_attrib(self, atts):
        """
        """
        result = {}
        for k, v in atts.items():
            try:
                result[k] = self.process_string(v)
            except Exception:
                result[k] = v
        return result

    def default(self, o):
        """
        This function doesn't need to be recursive, that is handled
        by the encoder itself.
        """
        assert type(o) in self.EXPECTED_TYPES, \
            "JSON encoder wasn't prepared for this type. Please revise: " + \
            str(type(o))

        # XML attributes are plain info, so retrieve directly:
        if type(o) is lxml.etree._Attrib:
            return dict(o)
        # XML string elements may contain attributes:
        if type(o) is lxml.objectify.StringElement:
            s = self.process_string(str(o))
            try:
                result = {}
                atts = self.process_attrib(o.attrib)
                if atts:
                    result["attributes"] = atts
                if s:
                    result["content"] = s
                return result if result else ""
            except AttributeError:
                return s
        # otherwise we have potentially nested info, with __dict__ and .attrib:
        result = OrderedDict()
        try:
            if o.attrib:
                result["attributes"] = self.process_attrib(o.attrib)
        except AttributeError:
            pass
        try:
            if o.__dict__:
                result["children"] = o.__dict__
                for k, v in result["children"].items():
                    try:
                        val_list = list(iter(v))
                        if len(val_list) > 1:
                            result["children"][k] = val_list
                    except TypeError:  # not iterable, leave alone
                        pass
        except AttributeError:
            pass
        #
        return result


def mvn_to_json(mvn_in_path, json_out_path, validate_mvn=False,
                write_as_binary=True):
    """
    """
    print("loading mvnx...")
    mocap = Mvn(mvn_in_path, validate_mvn)
    print("converting mvnx to JSON...")
    json_str = json.dumps(mocap.mvn, cls=ObjectifiedMvnToJsonEncoder)
    del mocap
    # write as plain text
    if not write_as_binary:
        with open(json_out_path, "w") as f:
            f.write(json_str)  # .replace("\\\\", "\\"))
            print("wrote JSON to", json_out_path)
    else:  # write as binary
        print("converting JSON to BSON...")
        json_data = json.loads(json_str)
        del json_str
        #
        bson_data = bson.dumps(json_data)
        del json_data
        with open(json_out_path, "wb") as f:
            f.write(bson_data)
            print("wrote BSON to", json_out_path)


# #############################################################################
# ## MAIN ROUTINE?
# #############################################################################

def test(mvn_path, mvn_schema_path, out_path="/tmp/test.json", as_bson=False):
    """
    """
    mvn_to_json(mvn_path, out_path, mvn_schema_path, write_as_binary=as_bson)
    if as_bson:
        with open(out_path, "rb") as f:
            data = bson.loads(f.read())
            print(">>>", data.keys())
    else:
        with open(out_path, "r") as f:
            data = json.load(f)
            print(">>>>", data.keys())
