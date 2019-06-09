# -*- coding:utf-8 -*-


"""
Unit testing of the utils module. Doc:
https://docs.python.org/3/library/unittest.html#assert-methods

"""

import random
import unittest
import audio_synch_tool.utils as uts


class TimedeltaTest(unittest.TestCase):
    """
    Contains a simple test that always passes
    """

    def test_field_retrieval(self):
        """
        Test that input fields can be retrieved
        """
        SAMPLE_NR, SAMPLERATE = 1234.5678, 1000
        ts = uts.Timedelta(SAMPLE_NR, SAMPLERATE)
        self.assertEqual(SAMPLE_NR, ts.sample_nr)
        self.assertEqual(SAMPLERATE, ts.samplerate)

    def test_neg_sr(self):
        """
        Constructor asserts whether samplerate is non-negative.
        """
        self.assertRaises(AssertionError, uts.Timedelta,
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
            ts = uts.Timedelta(SAMPLE_NR, SAMPLERATE)
            ts_neg = uts.Timedelta(SAMPLE_NR_NEG, SAMPLERATE)
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
        ts = uts.Timedelta(SAMPLE_NR, SAMPLERATE)
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
            ts = uts.Timedelta(SAMPLE_NR, SAMPLERATE)
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
            ts = uts.Timedelta(SAMPLE_NR, SAMPLERATE)
            # ignore all decimal noise, integer parts must be same
            self.assertAlmostEqual(SAMPLE_NR, ts.total_seconds * SAMPLERATE,
                                   places=0)


class ConvertAnchorsTest(unittest.TestCase):
    """
    """
    AUDIO_SAMPLERATE = 48000
    MVN_SAMPLERATE = 240
    NUM_TESTS = 1000
    LOW_SEC_MAX = 10  # first anchor will be at most this seconds
    HI_SEC_MIN = 15 * 60  # last anchor will be at least this seconds

    def test_precision(self):
        """
        This function tests the precision of the stretch and shift
        values returned by ``utils.convert_anchors``, by feeding
        some big integers and checking for equality.
        """
        for _ in range(self.NUM_TESTS):
            # create anchors far away from each other
            o1 = random.randint(0, self.MVN_SAMPLERATE * self.LOW_SEC_MAX)
            d1 = random.randint(0, self.AUDIO_SAMPLERATE * self.LOW_SEC_MAX)
            o2 = random.randint(self.MVN_SAMPLERATE * self.HI_SEC_MIN,
                                self.MVN_SAMPLERATE * self.HI_SEC_MIN * 2)
            d2 = random.randint(self.AUDIO_SAMPLERATE * self.HI_SEC_MIN,
                                self.AUDIO_SAMPLERATE * self.HI_SEC_MIN * 2)
            # convert anchors and test for equality
            stretch, shift = uts.convert_anchors(o1, d1, o2, d2)
            result1 = round(stretch * o1 + shift)
            result2 = round(stretch * o2 + shift)
            self.assertEqual(result1, d1)
            self.assertEqual(result2, d2)
