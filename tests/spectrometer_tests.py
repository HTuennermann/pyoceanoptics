__author__ = 'henrik'
from nose.tools import *
import pyoceanoptics

def test_get_spectrometer():
    assert_equal(pyoceanoptics.get_spectrometers(), [])

def test_get_spectrometer_byid():
    assert_equal(pyoceanoptics.get_spectrometer_by_id("wawa"), None)


