"""
Unit tests for module DialTimer.
"""

import unittest
import time
from 1910calleditwantsitsphoneback.modules.DialTimer import DialTimer


class TestDialTimer(unittest.TestCase):
    def setUp(self):
        self.defaultflag = None
        self.timer = None
    def callback(self):
        self.defaultflag = True
    def test_default(self):
        self.timer = DialTimer()
        self.timer.register_callback(self.callback)
        time.sleep(4)
        self.assertTrue(self.defaultflag)


if __name__ == '__main__':
    unittest.main()
