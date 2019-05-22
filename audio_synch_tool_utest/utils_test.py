# -*- coding:utf-8 -*-


"""
Unit testing of the utils module. Doc:
https://docs.python.org/3/library/unittest.html#assert-methods

"""

import random
import unittest
import audio_synch_tool.utils as uts


class TimestampTest(unittest.TestCase):
    """
    Contains a simple test that always passes
    """

    def test_field_retrieval(self):
        """
        Test that input fields can be retrieved
        """
        SAMPLE_NR, SAMPLERATE = 1234.5678, 1000
        ts = uts.Timestamp(SAMPLE_NR, SAMPLERATE)
        self.assertEqual(SAMPLE_NR, ts.sample_nr)
        self.assertEqual(SAMPLERATE, ts.samplerate)

    def test_neg_sr(self):
        """
        Constructor asserts whether samplerate is non-negative.
        """
        self.assertRaises(AssertionError, uts.Timestamp,
                          1234.5678, -1000)

    def test_neg_sn(self):
        """
        Modulo arithmetic can be tricky if sample nr is negative.
        This test ensures proper behaviour (symmetrical around zero)
        """
        NUM_ITERS = 1000
        for _ in range(NUM_ITERS):
            SAMPLE_NR = random.randint(0, 1e15)
            SAMPLE_NR_NEG = -SAMPLE_NR
            SAMPLERATE = random.randint(0, 1e10)
            ts = uts.Timestamp(SAMPLE_NR, SAMPLERATE)
            ts_neg = uts.Timestamp(SAMPLE_NR_NEG, SAMPLERATE)
            #
            d, h, m, s, mms = ts.as_tuple()
            d_neg, h_neg, m_neg, s_neg, mms_neg = ts_neg.as_tuple()
            #
            self.assertEqual(d, -d_neg)
            self.assertEqual(h, -h_neg)
            self.assertEqual(m, -m_neg)
            self.assertEqual(s, -s_neg)
            self.assertEqual(mms, -mms_neg)
            self.assertEqual("-" + str(ts), str(ts_neg))

    def test_set_error(self):
        """
        Property attributes can't be set
        """
        SAMPLE_NR, SAMPLERATE = 1234.5678, 1000
        ts = uts.Timestamp(SAMPLE_NR, SAMPLERATE)
        # setting these attributes will trigger the exception
        with self.assertRaises(AttributeError):
            ts.sample_nr = None
        with self.assertRaises(AttributeError):
            ts.samplerate = None
        with self.assertRaises(AttributeError):
            ts.total_seconds = None
            ts.days = None
        with self.assertRaises(AttributeError):
            ts.hours = None
        with self.assertRaises(AttributeError):
            ts.mins = None
        with self.assertRaises(AttributeError):
            ts.secs = None
        with self.assertRaises(AttributeError):
            ts.microsecs = None

    def test_time_decomposition(self):
        """
        Check for some random numbers that the decomposition works.
        """
        NUM_ITERS = 100
        for _ in range(NUM_ITERS):
            SAMPLE_NR = random.randint(-1e15, 1e15)
            SAMPLERATE = random.randint(0, 1e10)
            ts = uts.Timestamp(SAMPLE_NR, SAMPLERATE)
            d, h, m, s, mms = ts.as_tuple()
            total = ts.total_seconds
            recomp = mms * 1e-6 + s + m * 60 + h * 3600 + d * 24 * 3600
            #
            self.assertAlmostEqual(total, recomp, places=3)

    def test_samplerate_conversion(self):
        """
        Check that time * samplerate = num_samples
        """
        NUM_ITERS = 100
        for _ in range(NUM_ITERS):
            SAMPLE_NR = random.randint(0, 1e15)
            SAMPLERATE = random.randint(0, 1e14)
            ts = uts.Timestamp(SAMPLE_NR, SAMPLERATE)
            # ignore all decimal noise, integer parts must be same
            self.assertAlmostEqual(SAMPLE_NR, ts.total_seconds * SAMPLERATE,
                                   places=0)
