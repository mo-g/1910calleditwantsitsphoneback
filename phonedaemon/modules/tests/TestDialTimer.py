"""
Unit tests for module DialTimer.

User should add the github root directory to their python site-package.
"""

import unittest
import time
from phonedaemon.modules.DialTimer import DialTimer


class TestDialTimer(unittest.TestCase):
    """
    Includes all tests for the DialTimer class.
    """
    def setUp(self):
        """
        Defines variables for the test cases.
        """
        self.defaultflag = False
        self.timer = None

    def callback(self):
        """
        Sets a flag to True when the timer expires.
        """
        self.defaultflag = True

    def test_default(self):
        """
        Test the basic case: Start a timer and wait for it to expire.
        """
        self.timer = DialTimer()
        self.timer.register_callback(self.callback)
        time.sleep(2)
        self.assertFalse(self.defaultflag)
        time.sleep(2)
        self.assertTrue(self.defaultflag)

    def test_reset(self):
        """
        Test the common case: Start a timer, reset and wait for it to expire.
        """
        self.timer = DialTimer()
        self.timer.register_callback(self.callback)
        time.sleep(2)
        self.assertFalse(self.defaultflag)
        self.timer.reset()
        self.assertFalse(self.defaultflag)
        time.sleep(2)
        self.assertFalse(self.defaultflag)
        time.sleep(2)
        self.assertTrue(self.defaultflag)


if __name__ == '__main__':
    unittest.main()
