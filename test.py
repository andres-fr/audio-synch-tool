#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
The goal of this module is to provide an interface between MVNX and MMC, both
in JSON and BSON format.

1. Have a proper definition of MMC
2. load MVNX into an XML tree
3. convert logical data into MMC
4. export/import MMC both as JSON and BSON
5. convert logical data back into XML tree

"""


__author__ = "Andres FR"


from audio_synch_tool.mmc import mvn_to_json
import json
import bson

# #############################################################################
# ## TODO:
# #############################################################################


# 1. Clean/Revise Mvn class to have minimal clean interface
# 2. Objectify imported JSON into a class that behaves like the Mvn
# 3. Enable full comparation between "objectified" JSON and MVNX.
# 4. Test that conversion between MVNX, JSON and BSON works in all ways.
# 5. At this point MMC should be OK. Convert all data to BSON using server
# 6. adapt functionality on top? should expect objectified, so any data should work.


# #############################################################################
# ## HELPERS
# #############################################################################


# #############################################################################
# ## MVN CLASS
# #############################################################################




mvn_path = "/home/a9fb1e/SAG_D1-003_(snippet)_slate01_2-23-29.701.mvnx"
mvn_schema_path = "/home/a9fb1e/github-work/audio-synch-tool/audio_synch_tool/data/mvn_schema_adapted.xsd"
js_path = "/tmp/test.json"
BSON = True

mvn_to_json(mvn_path, js_path, mvn_schema_path, write_as_binary=BSON)

if BSON:
    with open(js_path, "rb") as f:
        data = bson.loads(f.read())
        print(">>>", data.keys())
else:
    with open(js_path, "r") as f:
        data = json.load(f)
        print(">>>>", data.keys())
